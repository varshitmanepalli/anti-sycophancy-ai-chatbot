"""Domain interfaces (ports).

Abstract protocols that infrastructure adapters must implement. Keeps the
domain and service layers decoupled from vLLM, SQLAlchemy, etc.
"""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Conversation, Message


class LLMProvider(Protocol):
    """Port for language-model inference backends."""

    async def generate(self, messages: list[dict[str, str]], **kwargs) -> str:
        """Generate a completion from a list of chat-formatted messages."""
        ...

    async def generate_stream(self, messages: list[dict[str, str]], **kwargs):
        """Yield completion tokens as an async iterator."""
        ...


class ConversationRepository(Protocol):
    """Port for conversation persistence."""

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        ...

    async def save(self, conversation: Conversation) -> Conversation:
        ...

    async def add_message(self, conversation_id: UUID, message: Message) -> Message:
        ...
