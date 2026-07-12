"""Chat endpoints.

Handles conversation creation, message submission, and streaming responses.
Delegates all orchestration to ``ChatService`` in the services layer.
"""

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_message(payload: ChatRequest) -> ChatResponse:
    """Submit a user message and receive an anti-sycophancy response.

    Business logic is intentionally deferred — this endpoint returns a
    placeholder until ``ChatService`` is implemented.
    """
    # TODO: inject ChatService via deps and delegate
    return ChatResponse(
        conversation_id=payload.conversation_id,
        message="[placeholder] Anti-sycophancy response not yet implemented.",
    )
