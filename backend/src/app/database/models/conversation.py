"""Conversation and message ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class ConversationORM(Base, TimestampMixin):
    """Persisted conversation session."""

    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conversations_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    messages: Mapped[list["MessageORM"]] = relationship(
        back_populates="conversation",
        order_by="MessageORM.created_at",
        cascade="all, delete-orphan",
    )
    facts: Mapped[list["UserFactORM"]] = relationship(back_populates="conversation")
    opinions: Mapped[list["UserOpinionORM"]] = relationship(back_populates="conversation")
    goals: Mapped[list["UserGoalORM"]] = relationship(back_populates="conversation")
    contradictions: Mapped[list["MemoryContradictionORM"]] = relationship(
        back_populates="conversation"
    )


class MessageORM(Base):
    """Persisted single message turn."""

    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    conversation: Mapped["ConversationORM"] = relationship(back_populates="messages")
