"""Domain types for memory contradiction checking."""

from dataclasses import dataclass, field
from typing import Any

from app.domain.memory import ContradictionSeverity, MemorySourceType


@dataclass
class DetectedContradiction:
    """A contradiction between stored memory and a new statement."""

    memory_statement: str
    new_statement: str
    description: str
    clarification_question: str
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    memory_source: MemorySourceType | None = None
    memory_source_id: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "memory_statement": self.memory_statement,
            "new_statement": self.new_statement,
            "description": self.description,
            "clarification_question": self.clarification_question,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 4),
        }
        if self.memory_source is not None:
            result["memory_source"] = self.memory_source.value
        if self.memory_source_id is not None:
            result["memory_source_id"] = self.memory_source_id
        return result


@dataclass
class ContradictionCheckResult:
    """Result of comparing a new message against stored memory."""

    contradictions: list[DetectedContradiction] = field(default_factory=list)
    clarification_question: str | None = None
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "contradictions": [c.to_dict() for c in self.contradictions],
            "clarification_question": self.clarification_question,
            "summary": self.summary,
        }

    @property
    def has_contradictions(self) -> bool:
        return bool(self.contradictions)

    @property
    def is_empty(self) -> bool:
        return not self.contradictions and not self.clarification_question
