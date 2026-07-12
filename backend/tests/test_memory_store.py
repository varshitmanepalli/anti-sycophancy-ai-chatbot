"""MemoryStore unit tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.memory_extraction import (
    ExtractedMemoryItem,
    MemoryCategory,
    MemoryExtractionResult,
)
from app.services.memory.store import MemoryStore


@pytest.fixture
def mock_memory_repo():
    repo = AsyncMock()
    repo.facts = AsyncMock()
    repo.facts.create = AsyncMock(side_effect=lambda fact: fact)
    repo.goals = AsyncMock()
    repo.goals.create = AsyncMock(side_effect=lambda goal: goal)
    repo.opinions = AsyncMock()
    repo.opinions.create = AsyncMock(side_effect=lambda opinion: opinion)
    return repo


@pytest.fixture
def store(mock_memory_repo) -> MemoryStore:
    return MemoryStore(mock_memory_repo)


SAMPLE_RESULT = MemoryExtractionResult(
    career=[ExtractedMemoryItem(content="software engineer", category=MemoryCategory.CAREER)],
    programming_language=[
        ExtractedMemoryItem(content="Python", category=MemoryCategory.PROGRAMMING_LANGUAGE)
    ],
    goals=[ExtractedMemoryItem(content="learn Rust", category=MemoryCategory.GOALS)],
    preferences=[
        ExtractedMemoryItem(
            content="prefers direct answers",
            category=MemoryCategory.PREFERENCES,
            topic="communication",
        )
    ],
    projects=[
        ExtractedMemoryItem(content="AI chatbot", category=MemoryCategory.PROJECTS)
    ],
)


class TestMemoryStore:
    @pytest.mark.asyncio
    async def test_store_separately(self, store: MemoryStore, mock_memory_repo):
        result = await store.store("user-1", SAMPLE_RESULT, conversation_id=uuid4())

        assert result.stored.facts == 3
        assert result.stored.goals == 1
        assert result.stored.opinions == 1
        assert mock_memory_repo.facts.create.await_count == 3
        assert mock_memory_repo.goals.create.await_count == 1
        assert mock_memory_repo.opinions.create.await_count == 1

    @pytest.mark.asyncio
    async def test_facts_use_category(self, store: MemoryStore, mock_memory_repo):
        await store.store("user-1", SAMPLE_RESULT)

        categories = [
            call.args[0].category
            for call in mock_memory_repo.facts.create.await_args_list
        ]
        assert "career" in categories
        assert "programming_language" in categories
        assert "projects" in categories

    @pytest.mark.asyncio
    async def test_empty_result_stores_nothing(self, store: MemoryStore, mock_memory_repo):
        result = await store.store("user-1", MemoryExtractionResult())

        assert result.stored.facts == 0
        assert result.stored.goals == 0
        assert result.stored.opinions == 0
