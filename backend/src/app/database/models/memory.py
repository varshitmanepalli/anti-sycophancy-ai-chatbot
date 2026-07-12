"""Long-term conversation memory ORM models.

Tables are partitioned by concern (facts, opinions, goals, contradictions)
so each can scale and be indexed independently.
"""

import uuid

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class UserFactORM(Base, TimestampMixin):
    """Extracted fact about a user."""

    __tablename__ = "user_facts"
    __table_args__ = (
        Index("ix_user_facts_user_active", "user_id", "is_active"),
        Index("ix_user_facts_conversation", "conversation_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    conversation: Mapped["ConversationORM | None"] = relationship(back_populates="facts")


class UserOpinionORM(Base, TimestampMixin):
    """Tracked user opinion on a topic."""

    __tablename__ = "user_opinions"
    __table_args__ = (
        Index("ix_user_opinions_user_active", "user_id", "is_active"),
        Index("ix_user_opinions_topic", "user_id", "topic"),
        Index("ix_user_opinions_conversation", "conversation_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    opinion: Mapped[str] = mapped_column(Text, nullable=False)
    stance: Mapped[str] = mapped_column(String(32), default="neutral", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    conversation: Mapped["ConversationORM | None"] = relationship(back_populates="opinions")


class UserGoalORM(Base, TimestampMixin):
    """User-stated goal."""

    __tablename__ = "user_goals"
    __table_args__ = (
        Index("ix_user_goals_user_status", "user_id", "status"),
        Index("ix_user_goals_user_active", "user_id", "is_active"),
        Index("ix_user_goals_conversation", "conversation_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    conversation: Mapped["ConversationORM | None"] = relationship(back_populates="goals")


class MemoryContradictionORM(Base, TimestampMixin):
    """Detected contradiction between two statements."""

    __tablename__ = "memory_contradictions"
    __table_args__ = (
        Index("ix_contradictions_user_resolved", "user_id", "resolved"),
        Index("ix_contradictions_conversation", "conversation_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    statement_a: Mapped[str] = mapped_column(Text, nullable=False)
    statement_b: Mapped[str] = mapped_column(Text, nullable=False)
    statement_a_source_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    statement_a_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    statement_b_source_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    statement_b_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    conversation: Mapped["ConversationORM | None"] = relationship(
        back_populates="contradictions"
    )
