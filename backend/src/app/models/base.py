"""Base LLM client interface and shared types."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.models.backend_types import BackendType, ModelInfo


@dataclass
class GenerationConfig:
    """Parameters passed to the model at inference time."""

    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    stop: list[str] | None = None


class BaseLLMClient(ABC):
    """Abstract base for all LLM inference backends."""

    @property
    @abstractmethod
    def info(self) -> ModelInfo:
        """Metadata about the loaded model and backend."""
        ...

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Return a complete model response."""
        ...

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Yield response tokens one at a time."""
        ...
        yield  # pragma: no cover

    @abstractmethod
    async def unload(self) -> None:
        """Release model resources."""
        ...
