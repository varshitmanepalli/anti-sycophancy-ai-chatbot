"""LLM provider port."""

from typing import Protocol


class LLMProvider(Protocol):
    """Port for language-model inference backends."""

    async def generate(self, messages: list[dict[str, str]], **kwargs) -> str:
        """Generate a completion from a list of chat-formatted messages."""
        ...

    async def generate_stream(self, messages: list[dict[str, str]], **kwargs):
        """Yield completion tokens as an async iterator."""
        ...
