"""PostgreSQL-backed conversation memory store.

Implements ``BaseMemoryStore`` using the repository layer for message
persistence. Structured memory (facts, opinions, goals, contradictions)
is accessed via ``SQLMemoryRepository``.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.conversation_repository import SQLConversationRepository
from app.database.repositories.memory_repository import SQLMemoryRepository
from app.domain.entities import Message, MessageRole
from app.memory.base import BaseMemoryStore


class PostgresMemoryStore(BaseMemoryStore):
    """Persist conversation turns and expose aggregated memory."""

    def __init__(self, session: AsyncSession) -> None:
        self._conversations = SQLConversationRepository(session)
        self._memory = SQLMemoryRepository(session)

    @property
    def repository(self) -> SQLMemoryRepository:
        """Access the full memory repository facade."""
        return self._memory

    async def get_history(
        self,
        conversation_id: UUID,
        max_turns: int | None = None,
    ) -> list[dict[str, str]]:
        messages = await self._conversations.get_messages(
            conversation_id,
            limit=max_turns,
        )
        return [{"role": m.role.value, "content": m.content} for m in messages]

    async def append(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> None:
        message = Message(content=content, role=MessageRole(role))
        await self._conversations.add_message(conversation_id, message)

    async def clear(self, conversation_id: UUID) -> None:
        await self._conversations.delete(conversation_id)
