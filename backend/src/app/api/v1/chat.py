"""Chat endpoints.

Handles message submission and streaming responses. Delegates orchestration
to ``ChatService`` and enforces authentication via dependency injection.
"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.deps import ChatServiceDep, CurrentUserDep
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send a chat message",
)
async def send_message(
    payload: ChatRequest,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> ChatResponse | StreamingResponse:
    """Submit a user message and receive an anti-sycophancy response.

    Set ``stream=true`` in the request body to receive Server-Sent Events.
    """
    if payload.stream:
        return StreamingResponse(
            _stream_events(chat_service, payload),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return await chat_service.process_message(payload)


@router.post(
    "/stream",
    response_model=None,
    summary="Stream a chat response (SSE)",
)
async def stream_message(
    payload: ChatRequest,
    chat_service: ChatServiceDep,
    user: CurrentUserDep,
) -> StreamingResponse:
    """Dedicated streaming endpoint — always returns Server-Sent Events."""
    return StreamingResponse(
        _stream_events(chat_service, payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_events(chat_service: ChatService, payload: ChatRequest):
    """Yield SSE-formatted JSON events."""
    async for conversation_id, token, done in chat_service.stream_message(payload):
        event = {
            "conversation_id": str(conversation_id),
            "token": token,
            "done": done,
        }
        yield f"data: {json.dumps(event)}\n\n"
