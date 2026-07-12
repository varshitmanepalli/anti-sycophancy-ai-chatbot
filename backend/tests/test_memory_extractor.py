"""MemoryExtractor unit tests."""

from unittest.mock import AsyncMock

import pytest

from app.config.settings import Settings
from app.prompts.manager import PromptManager
from app.services.memory.extractor import MemoryExtractor

SAMPLE_OUTPUT = """
{
  "career": [{"content": "software engineer", "confidence": 0.9}],
  "programming_language": [{"content": "Python", "confidence": 0.95}],
  "goals": [],
  "preferences": [],
  "projects": [{"content": "AI reasoning engine", "confidence": 0.85}],
  "summary": "Career and project info found."
}
"""


@pytest.fixture
def mock_model():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(return_value=SAMPLE_OUTPUT)
    return manager


@pytest.fixture
def extractor(mock_model) -> MemoryExtractor:
    return MemoryExtractor(
        model_manager=mock_model,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestMemoryExtractor:
    @pytest.mark.asyncio
    async def test_extract_calls_llm(self, extractor: MemoryExtractor, mock_model):
        result = await extractor.extract(
            "I'm a software engineer building an AI reasoning engine in Python."
        )
        assert result.total_items == 3
        mock_model.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_extract_categories(self, extractor: MemoryExtractor):
        result = await extractor.extract(
            "I'm a software engineer building an AI reasoning engine in Python."
        )
        assert len(result.career) == 1
        assert result.programming_language[0].content == "Python"
        assert len(result.projects) == 1

    @pytest.mark.asyncio
    async def test_skips_empty_categories(self, extractor: MemoryExtractor):
        result = await extractor.extract(
            "I'm a software engineer building an AI reasoning engine in Python."
        )
        assert len(result.goals) == 0
        assert len(result.preferences) == 0

    def test_parse_raw(self, extractor: MemoryExtractor):
        result = extractor.parse_raw(SAMPLE_OUTPUT)
        assert result.programming_language[0].content == "Python"
