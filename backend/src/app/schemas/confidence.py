"""Confidence scoring API schemas."""

from pydantic import BaseModel, Field


class DimensionScoreSchema(BaseModel):
    """Score and explanation for one dimension."""

    score: int = Field(..., ge=0, le=100)
    explanation: str


class ConfidenceScoreRequest(BaseModel):
    """Request to score confidence in a message or response."""

    message: str = Field(..., min_length=1, max_length=32_000)
    context: str = ""
    response: str = ""


class ConfidenceScoreResponse(BaseModel):
    """Structured confidence score result."""

    evidence_quality: DimensionScoreSchema
    reasoning_strength: DimensionScoreSchema
    source_reliability: DimensionScoreSchema
    uncertainty: DimensionScoreSchema
    confidence: int = Field(..., ge=0, le=100)
    explanation: str

    @classmethod
    def from_domain(cls, result) -> "ConfidenceScoreResponse":
        return cls(
            evidence_quality=DimensionScoreSchema(
                score=result.evidence_quality.score,
                explanation=result.evidence_quality.explanation,
            ),
            reasoning_strength=DimensionScoreSchema(
                score=result.reasoning_strength.score,
                explanation=result.reasoning_strength.explanation,
            ),
            source_reliability=DimensionScoreSchema(
                score=result.source_reliability.score,
                explanation=result.source_reliability.explanation,
            ),
            uncertainty=DimensionScoreSchema(
                score=result.uncertainty.score,
                explanation=result.uncertainty.explanation,
            ),
            confidence=result.confidence,
            explanation=result.explanation,
        )
