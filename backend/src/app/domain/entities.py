"""Domain entities.

Plain dataclasses / Pydantic models representing core business objects.
These are independent of SQLAlchemy ORM models and API schemas.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class MessageRole(StrEnum):
    """Speaker role in a conversation turn."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """A single turn in a conversation."""

    content: str
    role: MessageRole
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Conversation:
    """A multi-turn dialogue session."""

    id: UUID = field(default_factory=uuid4)
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
