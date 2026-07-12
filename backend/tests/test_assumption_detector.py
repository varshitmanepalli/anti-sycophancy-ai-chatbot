"""AssumptionDetector unit tests."""

from unittest.mock import AsyncMock

import pytest

from app.config.settings import Settings
from app.prompts.manager import PromptManager
from app.services.assumptions.detector import AssumptionDetector

SAMPLE_OUTPUT = """
{
  "unsupported_assumptions": [
    {"text": "Assumes partner's intent without evidence", "confidence": 0.9, "severity": "high"}
  ],
  "emotional_reasoning": [
    {"text": "Decision driven by hurt feelings", "confidence": 0.85, "severity": "medium"}
  ],
  "confirmation_bias": [],
  "mind_reading": [
    {"text": "Claims partner doesn't care", "confidence": 0.8, "quote": "he doesn't care", "severity": "high"}
  ],
  "overconfidence": [
    {"text": "Absolute prediction about future", "confidence": 0.7, "severity": "medium"}
  ],
  "summary": "Heavy emotional reasoning and mind reading detected."
}
"""


@pytest.fixture
def mock_model():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(return_value=SAMPLE_OUTPUT)
    return manager


@pytest.fixture
def detector(mock_model) -> AssumptionDetector:
    return AssumptionDetector(
        model_manager=mock_model,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestAssumptionDetector:
    @pytest.mark.asyncio
    async def test_detect_calls_llm(self, detector: AssumptionDetector, mock_model):
        result = await detector.detect("He doesn't care about me at all.")
        assert result.total_issues == 4
        mock_model.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_detect_mind_reading(self, detector: AssumptionDetector):
        result = await detector.detect("He doesn't care about me at all.")
        assert len(result.mind_reading) == 1

    @pytest.mark.asyncio
    async def test_detect_emotional_reasoning(self, detector: AssumptionDetector):
        result = await detector.detect("He doesn't care about me at all.")
        assert len(result.emotional_reasoning) == 1

    @pytest.mark.asyncio
    async def test_detect_summary(self, detector: AssumptionDetector):
        result = await detector.detect("He doesn't care about me at all.")
        assert "mind reading" in result.summary

    @pytest.mark.asyncio
    async def test_loads_model_if_needed(self, mock_model):
        mock_model.is_loaded = False
        mock_model.load = AsyncMock()
        detector = AssumptionDetector(model_manager=mock_model, settings=Settings())
        await detector.detect("test")
        mock_model.load.assert_awaited_once()

    def test_parse_raw(self, detector: AssumptionDetector):
        result = detector.parse_raw(SAMPLE_OUTPUT)
        assert len(result.overconfidence) == 1
