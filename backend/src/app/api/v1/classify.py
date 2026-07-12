"""Input classification endpoint."""

from fastapi import APIRouter

from app.api.deps import CurrentUserDep, InputClassifierDep
from app.schemas.classification import ClassifyRequest, ClassifyResponse

router = APIRouter()


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Classify a user message",
)
async def classify_message(
    payload: ClassifyRequest,
    classifier: InputClassifierDep,
    user: CurrentUserDep,
) -> ClassifyResponse:
    """Categorize a message into fact, opinion, programming, etc."""
    result = await classifier.classify(payload.message)
    return ClassifyResponse(
        category=result.category,
        confidence=result.confidence,
        scores=result.scores,
        method=result.method,
    )
