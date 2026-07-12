"""Local vLLM inference via AsyncLLMEngine.

Uses the vLLM Python package for in-process GPU serving when a remote
vLLM server is not available but the package and GPU are present.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from app.models.backend_types import BackendType, ModelInfo
from app.models.base import BaseLLMClient, GenerationConfig
from app.logging.setup import get_logger

logger = get_logger(__name__)


class VLLMLocalClient(BaseLLMClient):
    """In-process vLLM AsyncLLMEngine wrapper."""

    def __init__(
        self,
        model_path: str,
        *,
        tensor_parallel_size: int = 1,
        gpu_memory_utilization: float = 0.9,
        max_model_len: int | None = None,
    ) -> None:
        from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams  # noqa: PLC0415

        self._SamplingParams = SamplingParams
        self._model_path = model_path

        engine_args = AsyncEngineArgs(
            model=model_path,
            tensor_parallel_size=tensor_parallel_size,
            gpu_memory_utilization=gpu_memory_utilization,
            max_model_len=max_model_len,
            trust_remote_code=True,
        )
        self._engine = AsyncLLMEngine.from_engine_args(engine_args)
        self._info = ModelInfo(
            model_id=model_path,
            resolved_path=model_path,
            backend=BackendType.VLLM_LOCAL,
            device="cuda",
        )
        logger.info("vLLM local engine loaded: %s", model_path)

    @property
    def info(self) -> ModelInfo:
        return self._info

    def _to_prompt(self, messages: list[dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string.

        vLLM local engine accepts raw prompts; for chat models we rely on
        the model's chat template when a tokenizer is available on the engine.
        """
        # Prefer the engine tokenizer's chat template when available.
        tokenizer = getattr(self._engine, "tokenizer", None)
        if tokenizer is not None and hasattr(tokenizer, "apply_chat_template"):
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        # Fallback: simple role-tagged concatenation.
        parts: list[str] = []
        for msg in messages:
            parts.append(f"{msg['role'].upper()}: {msg['content']}")
        parts.append("ASSISTANT:")
        return "\n".join(parts)

    def _sampling_params(self, config: GenerationConfig) -> object:
        kwargs: dict = {
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        if config.stop:
            kwargs["stop"] = config.stop
        return self._SamplingParams(**kwargs)

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Generate a complete response via the local vLLM engine."""
        cfg = config or GenerationConfig()
        prompt = self._to_prompt(messages)
        sampling = self._sampling_params(cfg)
        request_id = str(uuid.uuid4())

        final_text = ""
        async for output in self._engine.generate(prompt, sampling, request_id):
            if output.outputs:
                final_text = output.outputs[0].text

        return final_text

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream incremental text from the local vLLM engine."""
        cfg = config or GenerationConfig()
        prompt = self._to_prompt(messages)
        sampling = self._sampling_params(cfg)
        request_id = str(uuid.uuid4())

        previous = ""
        async for output in self._engine.generate(prompt, sampling, request_id):
            if not output.outputs:
                continue
            current = output.outputs[0].text
            delta = current[len(previous) :]
            previous = current
            if delta:
                yield delta

    async def unload(self) -> None:
        """Shut down the vLLM engine."""
        shutdown = getattr(self._engine, "shutdown", None)
        if callable(shutdown):
            shutdown()
        logger.info("vLLM local engine unloaded: %s", self._model_path)
