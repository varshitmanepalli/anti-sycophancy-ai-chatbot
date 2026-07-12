"""Assumption detection API schemas."""

from pydantic import BaseModel, Field


class DetectedIssueSchema(BaseModel):
    """A single detected issue in API responses."""

    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    quote: str | None = None
    severity: str | None = None


class AssumptionDetectionRequest(BaseModel):
    """Request to detect assumptions and reasoning flaws."""

    message: str = Field(..., min_length=1, max_length=32_000)
    context: str = ""


class AssumptionDetectionResponse(BaseModel):
    """Structured assumption detection result."""

    unsupported_assumptions: list[DetectedIssueSchema] = Field(default_factory=list)
    emotional_reasoning: list[DetectedIssueSchema] = Field(default_factory=list)
    confirmation_bias: list[DetectedIssueSchema] = Field(default_factory=list)
    mind_reading: list[DetectedIssueSchema] = Field(default_factory=list)
    overconfidence: list[DetectedIssueSchema] = Field(default_factory=list)
    summary: str = ""

    @classmethod
    def from_domain(cls, result) -> "AssumptionDetectionResponse":
        def map_items(items):
            return [
                DetectedIssueSchema(
                    text=i.text,
                    confidence=i.confidence,
                    quote=i.quote,
                    severity=i.severity,
                )
                for i in items
            ]

        return cls(
            unsupported_assumptions=map_items(result.unsupported_assumptions),
            emotional_reasoning=map_items(result.emotional_reasoning),
            confirmation_bias=map_items(result.confirmation_bias),
            mind_reading=map_items(result.mind_reading),
            overconfidence=map_items(result.overconfidence),
            summary=result.summary,
        )
