"""Chat service — primary use-case orchestrator.

Coordinates:
  1. Loading conversation memory
  2. Building anti-sycophancy prompts
  3. Calling the LLM via the model layer
  4. Persisting messages to PostgreSQL

Business logic is intentionally not implemented yet.
"""

from uuid import UUID

from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    """Handles the end-to-end chat flow for a single conversation."""

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message and return the model's response.

        Args:
            request: Validated chat request containing message and context.

        Returns:
            ChatResponse with the assistant's reply and conversation metadata.
        """
        raise NotImplementedError("ChatService.process_message is not yet implemented.")

    async def get_conversation_history(self, conversation_id: UUID) -> list[dict]:
        """Retrieve prior messages for context window assembly."""
        raise NotImplementedError(
            "ChatService.get_conversation_history is not yet implemented."
        )
