"""Chat pipeline request/response schemas."""

from pydantic import BaseModel, Field

from app.domain.classification import InputCategory


class ChatPipelineRequest(BaseModel):
    """Incoming payload for POST /chat."""

    user_id: str = ""
    conversation_id: str = ""
    message: str = Field(..., min_length=1, max_length=32_000)


class ReasoningStep(BaseModel):
    """A single step in the model's reasoning trace."""

    label: str
    content: str = ""


class ChatPipelineResponse(BaseModel):
    """Structured response from the chat pipeline."""

    response: str = ""
    confidence: float = 0.0
    category: InputCategory | None = None
    reasoning_steps: list[ReasoningStep] = Field(default_factory=list)
