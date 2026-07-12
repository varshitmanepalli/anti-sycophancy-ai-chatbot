"""Hugging Face Transformers inference client.

Loads models locally via ``transformers`` for development, testing, or
environments without a dedicated GPU server. Not recommended for
high-throughput production serving — use ``VLLMClient`` instead.
"""

from collections.abc import AsyncIterator

from app.models.base import BaseLLMClient, GenerationConfig


class TransformersClient(BaseLLMClient):
    """Local inference using Hugging Face Transformers."""

    def __init__(self, model_id: str, device: str = "auto") -> None:
        self._model_id = model_id
        self._device = device

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Run local model inference and return the full response."""
        raise NotImplementedError(
            "TransformersClient.generate is not yet implemented."
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from local model inference."""
        raise NotImplementedError(
            "TransformersClient.generate_stream is not yet implemented."
        )
        yield  # pragma: no cover
