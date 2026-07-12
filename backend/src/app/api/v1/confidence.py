"""Confidence scoring endpoint."""

from fastapi import APIRouter

from app.api.deps import ConfidenceEngineDep, CurrentUserDep
from app.schemas.confidence import ConfidenceScoreRequest, ConfidenceScoreResponse

router = APIRouter()


@router.post(
    "/score",
    response_model=ConfidenceScoreResponse,
    summary="Score reasoning confidence across four dimensions",
)
async def score_confidence(
    payload: ConfidenceScoreRequest,
    engine: ConfidenceEngineDep,
    user: CurrentUserDep,
) -> ConfidenceScoreResponse:
    """Evaluate evidence quality, reasoning, sources, uncertainty, and overall confidence."""
    result = await engine.score(
        payload.message,
        context=payload.context,
        response=payload.response,
    )
    return ConfidenceScoreResponse.from_domain(result)
