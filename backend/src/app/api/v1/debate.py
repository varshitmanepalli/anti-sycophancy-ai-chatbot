"""Debate engine endpoint."""

from fastapi import APIRouter

from app.api.deps import CurrentUserDep, DebateEngineDep
from app.schemas.debate import DebateRequest, DebateResponse

router = APIRouter()


@router.post(
    "/run",
    response_model=DebateResponse,
    summary="Run the multi-agent debate pipeline",
)
async def run_debate(
    payload: DebateRequest,
    engine: DebateEngineDep,
    user: CurrentUserDep,
) -> DebateResponse:
    """Execute Support → Opponent → Fact Checker → Judge on a user message."""
    result = await engine.run(
        payload.message,
        user_facts=payload.user_facts,
        conversation_summary=payload.conversation_summary,
        conversation_memory=payload.conversation_memory,
        known_facts=payload.known_facts,
    )
    return DebateResponse.from_domain(result)
