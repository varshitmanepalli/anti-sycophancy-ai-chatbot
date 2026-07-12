"""vLLM OpenAI-compatible server client.

Communicates with a remote vLLM server over HTTP for high-throughput GPU
inference. Supports async completion and Server-Sent Events streaming.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.models.backend_types import BackendType, ModelInfo
from app.models.base import BaseLLMClient, GenerationConfig
from app.logging.setup import get_logger

logger = get_logger(__name__)


class VLLMServerClient(BaseLLMClient):
    """Async HTTP client for a vLLM OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str,
        model_name: str,
        *,
        timeout: float = 300.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
        )
        self._info = ModelInfo(
            model_id=model_name,
            resolved_path=model_name,
            backend=BackendType.VLLM_SERVER,
            device="remote",
        )

    @property
    def info(self) -> ModelInfo:
        return self._info

    def _build_payload(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig,
        *,
        stream: bool,
    ) -> dict:
        payload: dict = {
            "model": self._model_name,
            "messages": messages,
            "stream": stream,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        if config.stop:
            payload["stop"] = config.stop
        return payload

    async def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> str:
        """Send a non-streaming chat completion request."""
        cfg = config or GenerationConfig()
        payload = self._build_payload(messages, cfg, stream=False)

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream completion tokens via SSE."""
        cfg = config or GenerationConfig()
        payload = self._build_payload(messages, cfg, stream=True)

        async with self._client.stream(
            "POST", "/chat/completions", json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue

                data = line.removeprefix("data: ").strip()
                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    logger.debug("Skipping malformed SSE chunk: %s", data)
                    continue

                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content

    async def unload(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
        logger.info("vLLM server client closed for model %s", self._model_name)


# Backward-compatible alias
VLLMClient = VLLMServerClient
