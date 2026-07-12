"""Logical fallacy detection endpoint."""

from fastapi import APIRouter

from app.api.deps import FallacyDetectorDep, CurrentUserDep
from app.schemas.fallacies import FallacyDetectionRequest, FallacyDetectionResponse

router = APIRouter()


@router.post(
    "/detect",
    response_model=FallacyDetectionResponse,
    summary="Detect logical fallacies in reasoning",
)
async def detect_fallacies(
    payload: FallacyDetectionRequest,
    detector: FallacyDetectorDep,
    user: CurrentUserDep,
) -> FallacyDetectionResponse:
    """Analyze a message for hasty generalization, false dilemma, and other fallacies."""
    result = await detector.detect(payload.message, context=payload.context)
    return FallacyDetectionResponse.from_domain(result)
