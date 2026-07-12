"""vLLM inference client.

Communicates with a vLLM OpenAI-compatible server for high-throughput
GPU inference. Preferred backend for production deployments.
"""

from collections.abc import AsyncIterator

from app.models.base import BaseLLMClient, GenerationConfig


class VLLMClient(BaseLLMClient):
    """HTTP client for a vLLM OpenAI-compatible API."""

    def __init__(self, base_url: str, model_name: str) -> None:
        self._base_url = base_url
        self._model_name = model_name

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Send a chat completion request to the vLLM server."""
        raise NotImplementedError("VLLMClient.generate is not yet implemented.")

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from the vLLM server."""
        raise NotImplementedError("VLLMClient.generate_stream is not yet implemented.")
        yield  # pragma: no cover
