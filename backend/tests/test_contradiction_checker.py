"""MemoryContradictionChecker unit tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.contradiction_check import ContradictionCheckResult, DetectedContradiction
from app.domain.memory import ConversationMemory, UserFact
from app.services.contradictions.checker import MemoryContradictionChecker


@pytest.fixture
def mock_detector():
    detector = AsyncMock()
    detector.detect = AsyncMock(
        return_value=ContradictionCheckResult(
            contradictions=[
                DetectedContradiction(
                    memory_statement="Works in backend",
                    new_statement="Now doing frontend",
                    description="Role conflict.",
                    clarification_question="Has your role changed?",
                )
            ],
            clarification_question="Has your role changed?",
            summary="One contradiction.",
        )
    )
    return detector


@pytest.fixture
def mock_memory_repo():
    repo = AsyncMock()
    repo.load_user_memory = AsyncMock(
        return_value=ConversationMemory(
            facts=[
                UserFact(
                    user_id="user-1",
                    content="Works in backend",
                    category="career",
                    id=uuid4(),
                )
            ]
        )
    )
    return repo


@pytest.fixture
def checker(mock_detector, mock_memory_repo) -> MemoryContradictionChecker:
    return MemoryContradictionChecker(mock_detector, mock_memory_repo)


class TestMemoryContradictionChecker:
    @pytest.mark.asyncio
    async def test_check_loads_memory_and_detects(self, checker, mock_detector, mock_memory_repo):
        result = await checker.check("user-1", "Now doing frontend")

        mock_memory_repo.load_user_memory.assert_awaited_once_with("user-1")
        mock_detector.detect.assert_awaited_once()
        assert result.has_contradictions

    def test_format_memory_context(self):
        memory = ConversationMemory(
            facts=[UserFact(user_id="u", content="Python dev", category="career", id=uuid4())],
        )
        text = MemoryContradictionChecker.format_memory_context(memory)
        assert "Python dev" in text
        assert "Stored facts" in text

    def test_format_empty_memory(self):
        text = MemoryContradictionChecker.format_memory_context(ConversationMemory())
        assert "No stored long-term memory" in text
