"""Chat pipeline request/response schemas."""

from pydantic import BaseModel, Field

from app.domain.classification import InputCategory


class ChatPipelineRequest(BaseModel):
    """Incoming payload for POST /chat."""

    user_id: str = ""
    conversation_id: str = ""
    message: str = Field(..., min_length=1, max_length=32_000)


class ReasoningStep(BaseModel):
    """Internal pipeline trace step — not for user-facing chain-of-thought display."""

    label: str
    content: str = ""


class ReasoningItem(BaseModel):
    """A single structured reasoning item returned to the client."""

    text: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source: str | None = None


class StructuredReasoning(BaseModel):
    """User-facing structured reasoning — no chain-of-thought."""

    facts: list[ReasoningItem] = Field(default_factory=list)
    assumptions: list[ReasoningItem] = Field(default_factory=list)
    evidence: list[ReasoningItem] = Field(default_factory=list)
    counterarguments: list[ReasoningItem] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    alternative_explanations: list[ReasoningItem] = Field(default_factory=list)


class ChatPipelineResponse(BaseModel):
    """Structured response from the chat pipeline."""

    response: str = ""
    confidence: float = 0.0
    category: InputCategory | None = None
    reasoning_steps: list[ReasoningStep] = Field(default_factory=list)
    structured_reasoning: StructuredReasoning | None = None
