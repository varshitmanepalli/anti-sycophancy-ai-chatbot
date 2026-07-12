"""Claim extraction API schemas."""

from pydantic import BaseModel, Field


class ExtractedItemSchema(BaseModel):
    """A single extracted item in API responses."""

    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str | None = None


class ClaimExtractionRequest(BaseModel):
    """Request to extract claims from a message."""

    message: str = Field(..., min_length=1, max_length=32_000)
    context: str = ""


class ClaimExtractionResponse(BaseModel):
    """Structured claim extraction result."""

    main_claims: list[ExtractedItemSchema] = Field(default_factory=list)
    supporting_claims: list[ExtractedItemSchema] = Field(default_factory=list)
    hidden_assumptions: list[ExtractedItemSchema] = Field(default_factory=list)
    evidence_provided: list[ExtractedItemSchema] = Field(default_factory=list)
    unknown_information: list[ExtractedItemSchema] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, result) -> "ClaimExtractionResponse":
        def map_items(items):
            return [
                ExtractedItemSchema(
                    text=i.text,
                    confidence=i.confidence,
                    source=i.source,
                )
                for i in items
            ]

        return cls(
            main_claims=map_items(result.main_claims),
            supporting_claims=map_items(result.supporting_claims),
            hidden_assumptions=map_items(result.hidden_assumptions),
            evidence_provided=map_items(result.evidence_provided),
            unknown_information=map_items(result.unknown_information),
        )
