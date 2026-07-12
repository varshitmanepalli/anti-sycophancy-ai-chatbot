"""Conversation repository — PostgreSQL implementation.

Implements the ``domain.interfaces.ConversationRepository`` port using
SQLAlchemy async sessions.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Conversation, Message


class SQLConversationRepository:
    """Async SQLAlchemy repository for conversations and messages."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Load a conversation with all its messages."""
        raise NotImplementedError(
            "SQLConversationRepository.get_by_id is not yet implemented."
        )

    async def save(self, conversation: Conversation) -> Conversation:
        """Persist a new or updated conversation."""
        raise NotImplementedError(
            "SQLConversationRepository.save is not yet implemented."
        )

    async def add_message(self, conversation_id: UUID, message: Message) -> Message:
        """Append a message to an existing conversation."""
        raise NotImplementedError(
            "SQLConversationRepository.add_message is not yet implemented."
        )
