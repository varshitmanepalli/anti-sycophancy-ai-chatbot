"""Domain types for logical fallacy detection."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FallacyType(StrEnum):
    """Supported logical fallacy categories."""

    HASTY_GENERALIZATION = "hasty_generalization"
    FALSE_DILEMMA = "false_dilemma"
    SLIPPERY_SLOPE = "slippery_slope"
    APPEAL_TO_EMOTION = "appeal_to_emotion"
    APPEAL_TO_POPULARITY = "appeal_to_popularity"
    CIRCULAR_REASONING = "circular_reasoning"
    CONFIRMATION_BIAS = "confirmation_bias"
    POST_HOC = "post_hoc"


ALL_FALLACIES: tuple[FallacyType, ...] = tuple(FallacyType)

# Human-readable labels for prompts and API display
FALLACY_LABELS: dict[FallacyType, str] = {
    FallacyType.HASTY_GENERALIZATION: "Hasty Generalization",
    FallacyType.FALSE_DILEMMA: "False Dilemma",
    FallacyType.SLIPPERY_SLOPE: "Slippery Slope",
    FallacyType.APPEAL_TO_EMOTION: "Appeal to Emotion",
    FallacyType.APPEAL_TO_POPULARITY: "Appeal to Popularity",
    FallacyType.CIRCULAR_REASONING: "Circular Reasoning",
    FallacyType.CONFIRMATION_BIAS: "Confirmation Bias",
    FallacyType.POST_HOC: "Post Hoc",
}


@dataclass
class DetectedFallacy:
    """A single logical fallacy found in the text."""

    fallacy: FallacyType
    confidence: float
    explanation: str
    quote: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "fallacy": self.fallacy.value,
            "fallacy_label": FALLACY_LABELS[self.fallacy],
            "confidence": round(self.confidence, 4),
            "explanation": self.explanation,
        }
        if self.quote is not None:
            result["quote"] = self.quote
        return result


@dataclass
class FallacyDetectionResult:
    """Structured output from the logical fallacy detector."""

    fallacies: list[DetectedFallacy] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "fallacies": [f.to_dict() for f in self.fallacies],
            "summary": self.summary,
        }

    @property
    def is_empty(self) -> bool:
        return not self.fallacies and not self.summary

    def by_type(self, fallacy_type: FallacyType) -> list[DetectedFallacy]:
        return [f for f in self.fallacies if f.fallacy == fallacy_type]
