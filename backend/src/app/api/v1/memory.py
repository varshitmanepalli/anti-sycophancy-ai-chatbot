"""Long-term memory extraction endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUserDep, DbSession, MemoryExtractorDep, MemoryRepositoryDep
from app.schemas.memory_extraction import (
    MemoryExtractionRequest,
    MemoryExtractionResponse,
    MemoryStoreRequest,
    MemoryStoreResponse,
)
from app.services.memory.store import MemoryStore

router = APIRouter()


@router.post(
    "/extract",
    response_model=MemoryExtractionResponse,
    summary="Extract long-term user information from a message",
)
async def extract_memory(
    payload: MemoryExtractionRequest,
    extractor: MemoryExtractorDep,
    user: CurrentUserDep,
) -> MemoryExtractionResponse:
    """Extract career, languages, goals, preferences, and projects without storing."""
    result = await extractor.extract(payload.message, context=payload.context)
    return MemoryExtractionResponse.from_domain(result)


@router.post(
    "/store",
    response_model=MemoryStoreResponse,
    summary="Extract and store long-term user information",
)
async def extract_and_store_memory(
    payload: MemoryStoreRequest,
    extractor: MemoryExtractorDep,
    memory_repo: MemoryRepositoryDep,
    session: DbSession,
    user: CurrentUserDep,
) -> MemoryStoreResponse:
    """Extract durable user information and persist to separate memory tables."""
    extracted = await extractor.extract(payload.message, context=payload.context)
    store = MemoryStore(memory_repo)
    result = await store.store(
        payload.user_id,
        extracted,
        conversation_id=payload.conversation_id,
        message_id=payload.message_id,
    )
    await session.commit()
    return MemoryStoreResponse.from_domain(result)
