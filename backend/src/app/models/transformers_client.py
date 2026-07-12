"""Hugging Face Transformers inference client.

Loads models locally for development or CPU/GPU fallback. Supports async
wrapping and token streaming via ``TextIteratorStreamer``.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from threading import Thread
from typing import Any

from app.models.backend_types import BackendType, ModelInfo
from app.models.base import BaseLLMClient, GenerationConfig
from app.models.device import detect_torch_device
from app.logging.setup import get_logger

logger = get_logger(__name__)


def _import_torch():
    import torch

    return torch


def _import_transformers():
    from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

    return AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer


class TransformersClient(BaseLLMClient):
    """Local inference using Hugging Face Transformers."""

    def __init__(
        self,
        model_path: str,
        *,
        device: str | None = None,
        allow_cpu_fallback: bool = True,
        torch_dtype: str = "auto",
    ) -> None:
        self._model_path = model_path
        self._requested_device = device
        self._allow_cpu_fallback = allow_cpu_fallback
        self._torch_dtype = torch_dtype

        self._device = self._resolve_device()
        self._model: Any
        self._tokenizer: Any
        self._model, self._tokenizer = self._load_model_and_tokenizer()
        self._info = ModelInfo(
            model_id=model_path,
            resolved_path=model_path,
            backend=BackendType.TRANSFORMERS,
            device=self._device,
        )
        logger.info("Transformers model loaded: %s on %s", model_path, self._device)

    @property
    def info(self) -> ModelInfo:
        return self._info

    def _resolve_device(self) -> str:
        """Pick device with optional CPU fallback."""
        torch = _import_torch()

        if self._requested_device and self._requested_device not in ("auto", ""):
            requested = self._requested_device
            if requested == "cpu":
                return "cpu"
            if requested == "cuda" and torch.cuda.is_available():
                return "cuda"
            if requested == "mps" and hasattr(torch.backends, "mps"):
                if torch.backends.mps.is_available():
                    return "mps"
            if not self._allow_cpu_fallback:
                raise RuntimeError(
                    f"Requested device {requested!r} unavailable and CPU fallback disabled"
                )
            logger.warning("Device %r unavailable — falling back to CPU", requested)
            return "cpu"

        detected = detect_torch_device()
        if detected == "cpu" or self._allow_cpu_fallback:
            return detected
        raise RuntimeError("No GPU available and CPU fallback disabled")

    def _resolve_dtype(self):
        torch = _import_torch()

        if self._torch_dtype == "auto":
            if self._device == "cuda":
                return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            return torch.float32
        mapping = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        return mapping.get(self._torch_dtype, torch.float32)

    def _load_model_and_tokenizer(self) -> tuple[Any, Any]:
        AutoModelForCausalLM, AutoTokenizer, _ = _import_transformers()
        dtype = self._resolve_dtype()
        tokenizer = AutoTokenizer.from_pretrained(
            self._model_path,
            trust_remote_code=True,
        )

        load_kwargs: dict = {
            "pretrained_model_name_or_path": self._model_path,
            "torch_dtype": dtype,
            "trust_remote_code": True,
        }

        if self._device == "cpu":
            load_kwargs["device_map"] = "cpu"
            load_kwargs["low_cpu_mem_usage"] = True
        else:
            load_kwargs["device_map"] = "auto"

        model = AutoModelForCausalLM.from_pretrained(**load_kwargs)
        model.eval()
        return model, tokenizer

    def _build_prompt(self, messages: list[dict[str, str]]) -> str:
        if hasattr(self._tokenizer, "apply_chat_template"):
            return self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        parts = [f"{m['role'].upper()}: {m['content']}" for m in messages]
        parts.append("ASSISTANT:")
        return "\n".join(parts)

    def _generation_kwargs(self, config: GenerationConfig) -> dict:
        kwargs: dict = {
            "max_new_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "do_sample": config.temperature > 0,
        }
        if config.stop:
            kwargs["stop_strings"] = config.stop
        return kwargs

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Run local model inference and return the full response."""
        torch = _import_torch()
        cfg = config or GenerationConfig()
        prompt = self._build_prompt(messages)

        def _run() -> str:
            inputs = self._tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self._model.device) for k, v in inputs.items()}
            with torch.inference_mode():
                output_ids = self._model.generate(
                    **inputs,
                    **self._generation_kwargs(cfg),
                    pad_token_id=self._tokenizer.eos_token_id,
                )
            new_tokens = output_ids[0, inputs["input_ids"].shape[1] :]
            return self._tokenizer.decode(new_tokens, skip_special_tokens=True)

        return await asyncio.to_thread(_run)

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from local model inference."""
        _, _, TextIteratorStreamer = _import_transformers()
        cfg = config or GenerationConfig()
        prompt = self._build_prompt(messages)
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[str | None] = asyncio.Queue()

        def _generate_in_thread() -> None:
            inputs = self._tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self._model.device) for k, v in inputs.items()}
            streamer = TextIteratorStreamer(
                self._tokenizer,
                skip_prompt=True,
                skip_special_tokens=True,
            )
            gen_kwargs = {
                **inputs,
                **self._generation_kwargs(cfg),
                "streamer": streamer,
                "pad_token_id": self._tokenizer.eos_token_id,
            }

            gen_thread = Thread(target=self._model.generate, kwargs=gen_kwargs)
            gen_thread.start()

            for token in streamer:
                future = asyncio.run_coroutine_threadsafe(queue.put(token), loop)
                future.result()

            gen_thread.join()
            asyncio.run_coroutine_threadsafe(queue.put(None), loop).result()

        worker = Thread(target=_generate_in_thread, daemon=True)
        worker.start()

        while True:
            token = await queue.get()
            if token is None:
                break
            yield token

        await asyncio.to_thread(worker.join)

    async def unload(self) -> None:
        """Free GPU/CPU memory held by the model."""
        torch = _import_torch()
        del self._model
        del self._tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Transformers model unloaded: %s", self._model_path)
