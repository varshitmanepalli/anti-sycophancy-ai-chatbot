"""Assumption detection endpoint."""

from fastapi import APIRouter

from app.api.deps import AssumptionDetectorDep, CurrentUserDep
from app.schemas.assumptions import AssumptionDetectionRequest, AssumptionDetectionResponse

router = APIRouter()


@router.post(
    "/detect",
    response_model=AssumptionDetectionResponse,
    summary="Detect assumptions, biases, and reasoning flaws",
)
async def detect_assumptions(
    payload: AssumptionDetectionRequest,
    detector: AssumptionDetectorDep,
    user: CurrentUserDep,
) -> AssumptionDetectionResponse:
    """Analyze a message for unsupported assumptions and cognitive biases."""
    result = await detector.detect(payload.message, context=payload.context)
    return AssumptionDetectionResponse.from_domain(result)
