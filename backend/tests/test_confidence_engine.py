"""ConfidenceEngine unit tests."""

from unittest.mock import AsyncMock

import pytest

from app.config.settings import Settings
from app.prompts.manager import PromptManager
from app.services.confidence.engine import ConfidenceEngine

SAMPLE_OUTPUT = """
{
  "evidence_quality": {"score": 80, "explanation": "Strong cited evidence."},
  "reasoning_strength": {"score": 75, "explanation": "Coherent logic."},
  "source_reliability": {"score": 70, "explanation": "Mostly reliable sources."},
  "uncertainty": {"score": 30, "explanation": "Few major unknowns."},
  "confidence": 76,
  "explanation": "Well-supported overall with minor gaps."
}
"""


@pytest.fixture
def mock_model():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(return_value=SAMPLE_OUTPUT)
    return manager


@pytest.fixture
def engine(mock_model) -> ConfidenceEngine:
    return ConfidenceEngine(
        model_manager=mock_model,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestConfidenceEngine:
    @pytest.mark.asyncio
    async def test_score_calls_llm(self, engine: ConfidenceEngine, mock_model):
        result = await engine.score("Remote work improves productivity.")
        assert result.confidence == 76
        mock_model.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_score_dimensions(self, engine: ConfidenceEngine):
        result = await engine.score("Remote work improves productivity.")
        assert result.evidence_quality.score == 80
        assert result.reasoning_strength.score == 75
        assert "Well-supported" in result.explanation

    @pytest.mark.asyncio
    async def test_loads_model_if_needed(self, mock_model):
        mock_model.is_loaded = False
        mock_model.load = AsyncMock()
        engine = ConfidenceEngine(model_manager=mock_model, settings=Settings())
        await engine.score("test")
        mock_model.load.assert_awaited_once()

    def test_parse_raw(self, engine: ConfidenceEngine):
        result = engine.parse_raw(SAMPLE_OUTPUT)
        assert result.confidence == 76
