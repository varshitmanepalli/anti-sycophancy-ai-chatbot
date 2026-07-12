"""LogicalFallacyDetector unit tests."""

from unittest.mock import AsyncMock

import pytest

from app.config.settings import Settings
from app.domain.fallacies import FallacyType
from app.prompts.manager import PromptManager
from app.services.fallacies.detector import LogicalFallacyDetector

SAMPLE_OUTPUT = """
{
  "fallacies": [
    {
      "fallacy": "appeal_to_popularity",
      "confidence": 0.92,
      "explanation": "Claims truth based on widespread belief.",
      "quote": "everyone knows"
    },
    {
      "fallacy": "false_dilemma",
      "confidence": 0.8,
      "explanation": "Only two options presented.",
      "quote": "either support it or you're against progress"
    }
  ],
  "summary": "Appeal to popularity and false dilemma detected."
}
"""


@pytest.fixture
def mock_model():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(return_value=SAMPLE_OUTPUT)
    return manager


@pytest.fixture
def detector(mock_model) -> LogicalFallacyDetector:
    return LogicalFallacyDetector(
        model_manager=mock_model,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestLogicalFallacyDetector:
    @pytest.mark.asyncio
    async def test_detect_calls_llm(self, detector: LogicalFallacyDetector, mock_model):
        result = await detector.detect("Everyone knows we must choose progress or stagnation.")
        assert len(result.fallacies) == 2
        mock_model.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_detect_fallacy_types(self, detector: LogicalFallacyDetector):
        result = await detector.detect("Everyone knows we must choose progress or stagnation.")
        types = {f.fallacy for f in result.fallacies}
        assert FallacyType.APPEAL_TO_POPULARITY in types
        assert FallacyType.FALSE_DILEMMA in types

    @pytest.mark.asyncio
    async def test_detect_explanation_and_confidence(self, detector: LogicalFallacyDetector):
        result = await detector.detect("Everyone knows we must choose progress or stagnation.")
        item = result.fallacies[0]
        assert item.explanation
        assert 0.0 <= item.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_detect_summary(self, detector: LogicalFallacyDetector):
        result = await detector.detect("Everyone knows we must choose progress or stagnation.")
        assert "false dilemma" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_loads_model_if_needed(self, mock_model):
        mock_model.is_loaded = False
        mock_model.load = AsyncMock()
        detector = LogicalFallacyDetector(model_manager=mock_model, settings=Settings())
        await detector.detect("test")
        mock_model.load.assert_awaited_once()

    def test_parse_raw(self, detector: LogicalFallacyDetector):
        result = detector.parse_raw(SAMPLE_OUTPUT)
        assert len(result.fallacies) == 2
