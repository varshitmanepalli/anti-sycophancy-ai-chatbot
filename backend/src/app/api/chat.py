"""POST /chat endpoint.

Accepts a user message and runs it through the chat pipeline. Response
generation is not yet implemented — the pipeline returns a skeleton payload.
"""

from fastapi import APIRouter

from app.api.deps import ChatPipelineDep, CurrentUserDep
from app.schemas.chat_pipeline import ChatPipelineRequest, ChatPipelineResponse

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatPipelineResponse,
    summary="Process a chat message through the reasoning pipeline",
)
async def chat(
    payload: ChatPipelineRequest,
    pipeline: ChatPipelineDep,
    user: CurrentUserDep,
) -> ChatPipelineResponse:
    """Run the message through all pipeline stages and return structured output."""
    return await pipeline.run(payload)
