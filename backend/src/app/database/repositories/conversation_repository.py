"""Conversation repository — PostgreSQL implementation."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.conversation import ConversationORM, MessageORM
from app.database.repositories.base import BaseRepository
from app.database.repositories.mappers import (
    conversation_to_domain,
    message_to_domain,
    message_to_orm,
)
from app.domain.entities import Conversation, Message


class SQLConversationRepository(BaseRepository[ConversationORM]):
    """Async SQLAlchemy repository for conversations and messages."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ConversationORM)

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        stmt = (
            select(ConversationORM)
            .where(ConversationORM.id == conversation_id)
            .options(selectinload(ConversationORM.messages))
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return conversation_to_domain(orm) if orm else None

    async def save(self, conversation: Conversation, *, user_id: str = "") -> Conversation:
        orm = ConversationORM(
            id=conversation.id,
            user_id=user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return conversation_to_domain(orm)

    async def add_message(self, conversation_id: UUID, message: Message) -> Message:
        orm = message_to_orm(message, conversation_id)
        self._session.add(orm)
        await self._session.flush()
        return message_to_domain(orm)

    async def get_messages(
        self,
        conversation_id: UUID,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(MessageORM)
            .where(MessageORM.conversation_id == conversation_id)
            .order_by(MessageORM.created_at)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return [message_to_domain(m) for m in result.scalars().all()]

    async def delete(self, conversation_id: UUID) -> bool:
        return await self._delete_orm(conversation_id)
