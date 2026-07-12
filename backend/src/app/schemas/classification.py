"""Classification API schemas."""

from pydantic import BaseModel, Field

from app.domain.classification import InputCategory


class ClassifyRequest(BaseModel):
    """Request to classify a user message."""

    message: str = Field(..., min_length=1, max_length=32_000)


class ClassifyResponse(BaseModel):
    """Classification result returned to the client."""

    category: InputCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    scores: dict[str, float] = Field(default_factory=dict)
    method: str = "rules"
