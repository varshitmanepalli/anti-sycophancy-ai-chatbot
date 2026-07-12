"""Singleton model lifecycle manager.

Central entry point for loading, swapping, and running inference against
Qwen3 (or any Hugging Face model). Automatically selects the best
available backend:

  1. vLLM server  (remote OpenAI-compatible API)
  2. vLLM local   (in-process AsyncLLMEngine, GPU)
  3. Transformers (local GPU via PyTorch)
  4. Transformers (CPU fallback)
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import ClassVar, Literal

from app.config.settings import Settings, get_settings
from app.core.exceptions import ModelInferenceError
from app.models.backend_types import BackendType, ModelInfo
from app.models.base import BaseLLMClient, GenerationConfig
from app.models.device import (
    detect_torch_device,
    is_vllm_package_available,
    is_vllm_server_reachable,
    resolve_model_path,
)
from app.logging.setup import get_logger

logger = get_logger(__name__)

BackendPreference = Literal["auto", "vllm_server", "vllm_local", "transformers"]


class ModelManager:
    """Thread-safe async singleton that owns the active LLM backend.

    Usage::

        manager = await ModelManager.get_instance()
        await manager.load()
        reply = await manager.generate([{"role": "user", "content": "Hello"}])

        async for token in manager.generate_stream(messages):
            print(token, end="")

        await manager.swap_model("Qwen/Qwen3-8B")
    """

    _instance: ClassVar[ModelManager | None] = None
    _instance_lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._backend: BaseLLMClient | None = None
        self._operation_lock = asyncio.Lock()
        self._initialized = True

    # ------------------------------------------------------------------
    # Singleton access
    # ------------------------------------------------------------------

    @classmethod
    async def get_instance(cls, settings: Settings | None = None) -> ModelManager:
        """Return the global ``ModelManager``, creating it on first call."""
        if cls._instance is None:
            async with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(settings=settings)
                    logger.info("ModelManager singleton created")
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Destroy the singleton — intended for tests only."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_loaded(self) -> bool:
        return self._backend is not None

    @property
    def info(self) -> ModelInfo | None:
        return self._backend.info if self._backend else None

    @property
    def settings(self) -> Settings:
        return self._settings

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def load(
        self,
        *,
        model_name: str | None = None,
        model_path: str | None = None,
        backend: BackendPreference | None = None,
        force_reload: bool = False,
    ) -> ModelInfo:
        """Load a model, auto-selecting the best backend unless specified.

        Args:
            model_name: Hugging Face model ID (defaults to settings).
            model_path: Optional local directory override.
            backend: Force a specific backend instead of auto-detection.
            force_reload: Unload and reload even if the same model is active.
        """
        async with self._operation_lock:
            resolved_name = model_name or self._settings.model_name
            resolved_path = resolve_model_path(
                resolved_name,
                model_path or self._settings.model_path,
            )
            preference = backend or self._settings.model_backend

            if (
                self._backend is not None
                and not force_reload
                and self._backend.info.resolved_path == resolved_path
            ):
                logger.info("Model already loaded: %s", resolved_path)
                return self._backend.info

            if self._backend is not None:
                await self._unload_locked()

            self._backend = await self._create_backend(resolved_path, preference)
            logger.info("Model loaded: %s", self._backend.info)
            return self._backend.info

    async def swap_model(
        self,
        model_name_or_path: str,
        *,
        backend: BackendPreference | None = None,
    ) -> ModelInfo:
        """Unload the current model and load a new one.

        Accepts either a Hugging Face model ID or a local filesystem path.
        """
        from pathlib import Path

        path = Path(model_name_or_path).expanduser()
        if path.exists():
            return await self.load(
                model_path=str(path),
                backend=backend,
                force_reload=True,
            )
        return await self.load(
            model_name=model_name_or_path,
            backend=backend,
            force_reload=True,
        )

    async def unload(self) -> None:
        """Release the active model and free resources."""
        async with self._operation_lock:
            await self._unload_locked()

    async def _unload_locked(self) -> None:
        if self._backend is None:
            return
        await self._backend.unload()
        self._backend = None
        logger.info("ModelManager unloaded active backend")

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Generate a complete response."""
        backend = self._require_backend()
        try:
            return await backend.generate(messages, config)
        except Exception as exc:
            raise ModelInferenceError(str(exc)) from exc

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream response tokens."""
        backend = self._require_backend()
        try:
            async for token in backend.generate_stream(messages, config):
                yield token
        except Exception as exc:
            raise ModelInferenceError(str(exc)) from exc

    def _require_backend(self) -> BaseLLMClient:
        if self._backend is None:
            raise ModelInferenceError(
                "No model loaded. Call await ModelManager.load() first."
            )
        return self._backend

    def get_active_backend(self) -> BaseLLMClient:
        """Return the loaded backend (raises if none loaded)."""
        return self._require_backend()

    # ------------------------------------------------------------------
    # Backend selection
    # ------------------------------------------------------------------

    async def _create_backend(
        self,
        model_path: str,
        preference: BackendPreference,
    ) -> BaseLLMClient:
        """Instantiate the requested (or best available) backend."""
        if preference == "auto":
            return await self._auto_select_backend(model_path)

        builders = {
            BackendType.VLLM_SERVER: lambda: self._build_vllm_server(model_path),
            BackendType.VLLM_LOCAL: lambda: self._build_vllm_local(model_path),
            BackendType.TRANSFORMERS: lambda: self._build_transformers(model_path),
        }
        backend_type = BackendType(preference)
        return builders[backend_type]()

    async def _auto_select_backend(self, model_path: str) -> BaseLLMClient:
        """Try backends in priority order with graceful fallback."""
        errors: list[str] = []

        if self._settings.prefer_vllm:
            if await is_vllm_server_reachable(self._settings.vllm_base_url):
                try:
                    return self._build_vllm_server(model_path)
                except Exception as exc:
                    errors.append(f"vllm_server: {exc}")

            if is_vllm_package_available() and detect_torch_device() == "cuda":
                try:
                    return self._build_vllm_local(model_path)
                except Exception as exc:
                    errors.append(f"vllm_local: {exc}")

        try:
            return self._build_transformers(model_path, prefer_gpu=True)
        except Exception as exc:
            errors.append(f"transformers_gpu: {exc}")

        if self._settings.allow_cpu_fallback:
            try:
                return self._build_transformers(model_path, prefer_gpu=False)
            except Exception as exc:
                errors.append(f"transformers_cpu: {exc}")

        detail = "; ".join(errors) or "no backends available"
        raise ModelInferenceError(f"Failed to load model {model_path!r}: {detail}")

    def _build_vllm_server(self, model_path: str):
        from app.models.vllm_client import VLLMServerClient

        return VLLMServerClient(
            base_url=self._settings.vllm_base_url,
            model_name=model_path,
            timeout=self._settings.vllm_timeout,
        )

    def _build_vllm_local(self, model_path: str):
        from app.models.vllm_local import VLLMLocalClient

        return VLLMLocalClient(
            model_path=model_path,
            tensor_parallel_size=self._settings.vllm_tensor_parallel_size,
            gpu_memory_utilization=self._settings.vllm_gpu_memory_utilization,
            max_model_len=self._settings.vllm_max_model_len,
        )

    def _build_transformers(
        self,
        model_path: str,
        *,
        prefer_gpu: bool = True,
    ):
        from app.models.transformers_client import TransformersClient

        device = "auto" if prefer_gpu else "cpu"
        return TransformersClient(
            model_path=model_path,
            device=device,
            allow_cpu_fallback=self._settings.allow_cpu_fallback,
            torch_dtype=self._settings.transformers_torch_dtype,
        )
