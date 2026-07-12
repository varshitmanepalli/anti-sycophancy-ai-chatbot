"""Chat-related API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the client."""

    message: str = Field(..., min_length=1, max_length=32_000)
    conversation_id: UUID | None = None


class ChatResponse(BaseModel):
    """Assistant reply returned to the client."""

    conversation_id: UUID | None = None
    message: str


class MessageSchema(BaseModel):
    """A single message in conversation history."""

    role: str
    content: str


class ConversationSchema(BaseModel):
    """Full conversation with message history."""

    id: UUID
    messages: list[MessageSchema] = []
