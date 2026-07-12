"""Domain types for assumption and bias detection."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DetectedIssue:
    """A single detected assumption, bias, or reasoning flaw."""

    text: str
    confidence: float = 1.0
    quote: str | None = None
    severity: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.quote is not None:
            result["quote"] = self.quote
        if self.severity is not None:
            result["severity"] = self.severity
        return result


@dataclass
class AssumptionDetectionResult:
    """Structured output from the assumption detector."""

    unsupported_assumptions: list[DetectedIssue] = field(default_factory=list)
    emotional_reasoning: list[DetectedIssue] = field(default_factory=list)
    confirmation_bias: list[DetectedIssue] = field(default_factory=list)
    mind_reading: list[DetectedIssue] = field(default_factory=list)
    overconfidence: list[DetectedIssue] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "unsupported_assumptions": [i.to_dict() for i in self.unsupported_assumptions],
            "emotional_reasoning": [i.to_dict() for i in self.emotional_reasoning],
            "confirmation_bias": [i.to_dict() for i in self.confirmation_bias],
            "mind_reading": [i.to_dict() for i in self.mind_reading],
            "overconfidence": [i.to_dict() for i in self.overconfidence],
            "summary": self.summary,
        }

    @property
    def total_issues(self) -> int:
        return (
            len(self.unsupported_assumptions)
            + len(self.emotional_reasoning)
            + len(self.confirmation_bias)
            + len(self.mind_reading)
            + len(self.overconfidence)
        )

    @property
    def is_empty(self) -> bool:
        return self.total_issues == 0 and not self.summary
