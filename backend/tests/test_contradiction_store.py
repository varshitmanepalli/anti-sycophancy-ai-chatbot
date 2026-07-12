"""ContradictionStore unit tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.contradiction_check import ContradictionCheckResult, DetectedContradiction
from app.domain.memory import ContradictionSeverity, MemorySourceType
from app.services.contradictions.store import ContradictionStore


@pytest.fixture
def mock_memory_repo():
    repo = AsyncMock()
    repo.contradictions = AsyncMock()
    repo.contradictions.create = AsyncMock(side_effect=lambda c: c)
    return repo


@pytest.fixture
def store(mock_memory_repo) -> ContradictionStore:
    return ContradictionStore(mock_memory_repo)


SAMPLE_RESULT = ContradictionCheckResult(
    contradictions=[
        DetectedContradiction(
            memory_statement="Prefers Python",
            new_statement="Uses Rust only",
            description="Language shift.",
            clarification_question="Still using Python?",
            severity=ContradictionSeverity.MEDIUM,
            memory_source=MemorySourceType.OPINION,
            memory_source_id=str(uuid4()),
        )
    ]
)


class TestContradictionStore:
    @pytest.mark.asyncio
    async def test_persist_creates_records(self, store: ContradictionStore, mock_memory_repo):
        count = await store.persist("user-1", SAMPLE_RESULT, conversation_id=uuid4())

        assert count == 1
        mock_memory_repo.contradictions.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_persist_maps_fields(self, store: ContradictionStore, mock_memory_repo):
        await store.persist("user-1", SAMPLE_RESULT)

        created = mock_memory_repo.contradictions.create.await_args.args[0]
        assert created.statement_a == "Prefers Python"
        assert created.statement_b == "Uses Rust only"
        assert created.statement_a_source_type == MemorySourceType.OPINION

    @pytest.mark.asyncio
    async def test_persist_empty_returns_zero(self, store: ContradictionStore):
        count = await store.persist("user-1", ContradictionCheckResult())
        assert count == 0
