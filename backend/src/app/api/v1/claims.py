"""Claim extraction endpoint."""

from fastapi import APIRouter

from app.api.deps import ClaimExtractorDep, CurrentUserDep
from app.schemas.claims import ClaimExtractionRequest, ClaimExtractionResponse

router = APIRouter()


@router.post(
    "/extract",
    response_model=ClaimExtractionResponse,
    summary="Extract claims, assumptions, and evidence from a message",
)
async def extract_claims(
    payload: ClaimExtractionRequest,
    extractor: ClaimExtractorDep,
    user: CurrentUserDep,
) -> ClaimExtractionResponse:
    """Parse a user message into structured claims and return JSON."""
    result = await extractor.extract(payload.message, context=payload.context)
    return ClaimExtractionResponse.from_domain(result)
