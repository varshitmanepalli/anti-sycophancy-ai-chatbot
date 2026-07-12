"""Domain types for confidence scoring."""

from dataclasses import dataclass
from typing import Any


@dataclass
class DimensionScore:
    """Score and explanation for a single confidence dimension."""

    score: int
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "explanation": self.explanation,
        }


@dataclass
class ConfidenceResult:
    """Structured confidence assessment."""

    evidence_quality: DimensionScore
    reasoning_strength: DimensionScore
    source_reliability: DimensionScore
    uncertainty: DimensionScore
    confidence: int
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_quality": self.evidence_quality.to_dict(),
            "reasoning_strength": self.reasoning_strength.to_dict(),
            "source_reliability": self.source_reliability.to_dict(),
            "uncertainty": self.uncertainty.to_dict(),
            "confidence": self.confidence,
            "explanation": self.explanation,
        }

    @property
    def normalized_confidence(self) -> float:
        """Return confidence on a 0.0–1.0 scale."""
        return self.confidence / 100.0
