"""ModelManager unit tests."""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config.settings import Settings
from app.models.backend_types import BackendType, ModelInfo
from app.models.base import BaseLLMClient, GenerationConfig
from app.models.model_manager import ModelManager


class FakeBackend(BaseLLMClient):
    """Lightweight stub backend for tests."""

    def __init__(self, model_path: str, backend: BackendType, device: str = "test") -> None:
        self._info = ModelInfo(
            model_id=model_path,
            resolved_path=model_path,
            backend=backend,
            device=device,
        )
        self.unloaded = False

    @property
    def info(self) -> ModelInfo:
        return self._info

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        return "fake response"

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        for token in ("fake", " ", "stream"):
            yield token

    async def unload(self) -> None:
        self.unloaded = True


@pytest.fixture(autouse=True)
def reset_singleton():
    ModelManager.reset_instance()
    yield
    ModelManager.reset_instance()


@pytest.fixture
def settings() -> Settings:
    return Settings(
        model_name="Qwen/Qwen3-14B",
        model_backend="vllm_server",
        prefer_vllm=True,
    )


@pytest.mark.asyncio
async def test_singleton_returns_same_instance(settings: Settings):
    a = await ModelManager.get_instance(settings)
    b = await ModelManager.get_instance()
    assert a is b


@pytest.mark.asyncio
async def test_load_vllm_server_backend(settings: Settings):
    manager = await ModelManager.get_instance(settings)
    fake = FakeBackend("Qwen/Qwen3-14B", BackendType.VLLM_SERVER)

    with patch.object(manager, "_build_vllm_server", return_value=fake):
        info = await manager.load(backend="vllm_server")

    assert info.backend == BackendType.VLLM_SERVER
    assert manager.is_loaded
    assert manager.info == info


@pytest.mark.asyncio
async def test_generate_delegates_to_backend(settings: Settings):
    manager = await ModelManager.get_instance(settings)
    fake = FakeBackend("Qwen/Qwen3-14B", BackendType.VLLM_SERVER)
    manager._backend = fake  # noqa: SLF001

    result = await manager.generate([{"role": "user", "content": "hi"}])
    assert result == "fake response"


@pytest.mark.asyncio
async def test_generate_stream_yields_tokens(settings: Settings):
    manager = await ModelManager.get_instance(settings)
    fake = FakeBackend("Qwen/Qwen3-14B", BackendType.VLLM_SERVER)
    manager._backend = fake  # noqa: SLF001

    tokens = []
    async for token in manager.generate_stream([{"role": "user", "content": "hi"}]):
        tokens.append(token)

    assert tokens == ["fake", " ", "stream"]


@pytest.mark.asyncio
async def test_swap_model_unloads_previous(settings: Settings):
    manager = await ModelManager.get_instance(settings)
    first = FakeBackend("Qwen/Qwen3-14B", BackendType.VLLM_SERVER)
    second = FakeBackend("Qwen/Qwen3-8B", BackendType.TRANSFORMERS)

    with patch.object(manager, "_build_vllm_server", return_value=first):
        await manager.load(backend="vllm_server")

    with patch.object(
        manager,
        "_build_transformers",
        return_value=second,
    ):
        info = await manager.swap_model("Qwen/Qwen3-8B", backend="transformers")

    assert first.unloaded
    assert info.model_id == "Qwen/Qwen3-8B"
    assert manager.info.backend == BackendType.TRANSFORMERS


@pytest.mark.asyncio
async def test_auto_select_prefers_vllm_server(settings: Settings):
    manager = await ModelManager.get_instance(settings)
    fake = FakeBackend("Qwen/Qwen3-14B", BackendType.VLLM_SERVER)

    with (
        patch(
            "app.models.model_manager.is_vllm_server_reachable",
            new=AsyncMock(return_value=True),
        ),
        patch.object(manager, "_build_vllm_server", return_value=fake) as build,
    ):
        info = await manager.load(backend="auto")

    build.assert_called_once()
    assert info.backend == BackendType.VLLM_SERVER


@pytest.mark.asyncio
async def test_generate_raises_when_not_loaded(settings: Settings):
    manager = await ModelManager.get_instance(settings)

    with pytest.raises(Exception, match="No model loaded"):
        await manager.generate([{"role": "user", "content": "hi"}])
