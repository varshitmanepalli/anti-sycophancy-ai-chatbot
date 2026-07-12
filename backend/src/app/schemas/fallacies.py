"""Logical fallacy detection API schemas."""

from pydantic import BaseModel, Field

from app.domain.fallacies import FallacyType


class DetectedFallacySchema(BaseModel):
    """A single detected fallacy in API responses."""

    fallacy: FallacyType
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    quote: str | None = None


class FallacyDetectionRequest(BaseModel):
    """Request to detect logical fallacies in a message."""

    message: str = Field(..., min_length=1, max_length=32_000)
    context: str = ""


class FallacyDetectionResponse(BaseModel):
    """Structured fallacy detection result."""

    fallacies: list[DetectedFallacySchema] = Field(default_factory=list)
    summary: str = ""

    @classmethod
    def from_domain(cls, result) -> "FallacyDetectionResponse":
        return cls(
            fallacies=[
                DetectedFallacySchema(
                    fallacy=f.fallacy,
                    confidence=f.confidence,
                    explanation=f.explanation,
                    quote=f.quote,
                )
                for f in result.fallacies
            ],
            summary=result.summary,
        )
