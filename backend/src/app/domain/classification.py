"""Input classification domain types."""

from dataclasses import dataclass, field
from enum import StrEnum


class InputCategory(StrEnum):
    """Categories for user message classification."""

    FACT = "fact"
    OPINION = "opinion"
    PREDICTION = "prediction"
    PROGRAMMING = "programming"
    RELATIONSHIP = "relationship"
    MEDICAL = "medical"
    BUSINESS = "business"
    POLITICS = "politics"
    EMOTION = "emotion"
    MATH = "math"
    GENERAL_CHAT = "general_chat"


ALL_CATEGORIES: tuple[InputCategory, ...] = tuple(InputCategory)


@dataclass(frozen=True)
class ClassificationResult:
    """Output of the input classifier."""

    category: InputCategory
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)
    method: str = "rules"

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "confidence": round(self.confidence, 4),
            "scores": {k: round(v, 4) for k, v in self.scores.items()},
            "method": self.method,
        }
