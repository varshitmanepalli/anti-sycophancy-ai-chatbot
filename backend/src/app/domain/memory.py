"""Domain entities for long-term conversation memory."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class GoalStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class OpinionStance(StrEnum):
    SUPPORT = "support"
    OPPOSE = "oppose"
    NEUTRAL = "neutral"
    UNCERTAIN = "uncertain"


class ContradictionSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MemorySourceType(StrEnum):
    FACT = "fact"
    OPINION = "opinion"
    MESSAGE = "message"
    GOAL = "goal"


@dataclass
class UserFact:
    """An extracted fact about the user."""

    user_id: str
    content: str
    id: UUID = field(default_factory=uuid4)
    conversation_id: UUID | None = None
    message_id: UUID | None = None
    category: str | None = None
    confidence: float = 1.0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class UserOpinion:
    """A tracked opinion held by or attributed to the user."""

    user_id: str
    topic: str
    opinion: str
    id: UUID = field(default_factory=uuid4)
    conversation_id: UUID | None = None
    message_id: UUID | None = None
    stance: OpinionStance = OpinionStance.NEUTRAL
    confidence: float = 1.0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class UserGoal:
    """A goal the user has expressed."""

    user_id: str
    content: str
    id: UUID = field(default_factory=uuid4)
    conversation_id: UUID | None = None
    status: GoalStatus = GoalStatus.ACTIVE
    priority: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class MemoryContradiction:
    """A detected contradiction between two statements."""

    user_id: str
    statement_a: str
    statement_b: str
    id: UUID = field(default_factory=uuid4)
    conversation_id: UUID | None = None
    statement_a_source_type: MemorySourceType | None = None
    statement_a_source_id: UUID | None = None
    statement_b_source_type: MemorySourceType | None = None
    statement_b_source_id: UUID | None = None
    description: str | None = None
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    resolved: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ConversationMemory:
    """Aggregated memory snapshot for a user or conversation."""

    messages: list[dict[str, str]] = field(default_factory=list)
    facts: list[UserFact] = field(default_factory=list)
    opinions: list[UserOpinion] = field(default_factory=list)
    goals: list[UserGoal] = field(default_factory=list)
    contradictions: list[MemoryContradiction] = field(default_factory=list)
