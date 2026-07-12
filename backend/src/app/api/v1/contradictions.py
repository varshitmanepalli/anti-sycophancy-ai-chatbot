"""Memory contradiction detection endpoints."""

from fastapi import APIRouter

from app.api.deps import (
    ContradictionCheckerDep,
    CurrentUserDep,
    DbSession,
    MemoryRepositoryDep,
)
from app.schemas.contradiction_check import (
    ContradictionCheckRequest,
    ContradictionCheckResponse,
    ContradictionStoreRequest,
    ContradictionStoreResponse,
)
from app.services.contradictions.store import ContradictionStore

router = APIRouter()


@router.post(
    "/check",
    response_model=ContradictionCheckResponse,
    summary="Compare a message against stored user memory",
)
async def check_contradictions(
    payload: ContradictionCheckRequest,
    checker: ContradictionCheckerDep,
    user: CurrentUserDep,
) -> ContradictionCheckResponse:
    """Detect contradictions and generate a clarification question."""
    result = await checker.check(payload.user_id, payload.message)
    return ContradictionCheckResponse.from_domain(result)


@router.post(
    "/check-and-store",
    response_model=ContradictionStoreResponse,
    summary="Detect contradictions and persist them",
)
async def check_and_store_contradictions(
    payload: ContradictionStoreRequest,
    checker: ContradictionCheckerDep,
    memory_repo: MemoryRepositoryDep,
    session: DbSession,
    user: CurrentUserDep,
) -> ContradictionStoreResponse:
    """Detect contradictions, generate clarification questions, and save to DB."""
    result = await checker.check(payload.user_id, payload.message)
    stored_count = 0
    if result.has_contradictions:
        store = ContradictionStore(memory_repo)
        stored_count = await store.persist(
            payload.user_id,
            result,
            conversation_id=payload.conversation_id,
        )
        await session.commit()
    return ContradictionStoreResponse.from_result(result, stored_count)
