"""Base memory store interface."""

from abc import ABC, abstractmethod
from uuid import UUID


class BaseMemoryStore(ABC):
    """Abstract interface for conversation memory backends."""

    @abstractmethod
    async def get_history(
        self,
        conversation_id: UUID,
        max_turns: int | None = None,
    ) -> list[dict[str, str]]:
        """Return prior messages formatted for the LLM context window."""
        ...

    @abstractmethod
    async def append(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> None:
        """Persist a new message turn."""
        ...

    @abstractmethod
    async def clear(self, conversation_id: UUID) -> None:
        """Remove all messages for a conversation."""
        ...
