"""ContradictionDetector unit tests."""

from unittest.mock import AsyncMock

import pytest

from app.config.settings import Settings
from app.prompts.manager import PromptManager
from app.services.contradictions.detector import ContradictionDetector

SAMPLE_OUTPUT = """
{
  "contradictions": [
    {
      "memory_statement": "User prefers Python",
      "new_statement": "I've switched entirely to Rust",
      "memory_source": "opinion",
      "description": "Language preference may have changed.",
      "severity": "medium",
      "clarification_question": "Are you still using Python alongside Rust, or have you fully switched?",
      "confidence": 0.85
    }
  ],
  "clarification_question": "Are you still using Python alongside Rust, or have you fully switched?",
  "summary": "Language preference contradiction."
}
"""


@pytest.fixture
def mock_model():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(return_value=SAMPLE_OUTPUT)
    return manager


@pytest.fixture
def detector(mock_model) -> ContradictionDetector:
    return ContradictionDetector(
        model_manager=mock_model,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestContradictionDetector:
    @pytest.mark.asyncio
    async def test_detect_calls_llm(self, detector: ContradictionDetector, mock_model):
        result = await detector.detect(
            "I've switched entirely to Rust",
            memory_context="Stored opinions:\n- [languages] User prefers Python",
        )
        assert len(result.contradictions) == 1
        mock_model.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_detect_clarification(self, detector: ContradictionDetector):
        result = await detector.detect("I've switched entirely to Rust", memory_context="...")
        assert "Python" in result.clarification_question

    def test_parse_raw(self, detector: ContradictionDetector):
        result = detector.parse_raw(SAMPLE_OUTPUT)
        assert result.has_contradictions
