"""ClaimExtractor unit tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config.settings import Settings
from app.prompts.manager import PromptManager
from app.services.claims.extractor import ClaimExtractor

SAMPLE_MODEL_OUTPUT = """
{
  "main_claims": [{"text": "AI will replace most jobs", "confidence": 0.85}],
  "supporting_claims": [{"text": "Automation is advancing rapidly", "confidence": 0.8}],
  "hidden_assumptions": [{"text": "Job categories remain static", "confidence": 0.6}],
  "evidence_provided": [],
  "unknown_information": [{"text": "Timeline of displacement", "confidence": 0.7}]
}
"""


@pytest.fixture
def mock_model_manager():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(return_value=SAMPLE_MODEL_OUTPUT)
    return manager


@pytest.fixture
def extractor(mock_model_manager) -> ClaimExtractor:
    return ClaimExtractor(
        model_manager=mock_model_manager,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestClaimExtractor:
    @pytest.mark.asyncio
    async def test_extract_calls_model(self, extractor: ClaimExtractor, mock_model_manager):
        result = await extractor.extract("AI will replace most jobs soon.")
        assert len(result.main_claims) == 1
        assert result.main_claims[0].text == "AI will replace most jobs"
        mock_model_manager.generate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_extract_parses_assumptions(self, extractor: ClaimExtractor):
        result = await extractor.extract("AI will replace most jobs soon.")
        assert len(result.hidden_assumptions) == 1
        assert "static" in result.hidden_assumptions[0].text

    @pytest.mark.asyncio
    async def test_extract_unknown_information(self, extractor: ClaimExtractor):
        result = await extractor.extract("AI will replace most jobs soon.")
        assert len(result.unknown_information) == 1

    @pytest.mark.asyncio
    async def test_extract_loads_model_if_needed(self, mock_model_manager):
        mock_model_manager.is_loaded = False
        mock_model_manager.load = AsyncMock()
        extractor = ClaimExtractor(
            model_manager=mock_model_manager,
            settings=Settings(),
        )
        await extractor.extract("test message")
        mock_model_manager.load.assert_awaited_once()

    def test_parse_raw_without_model(self, extractor: ClaimExtractor):
        result = extractor.parse_raw(SAMPLE_MODEL_OUTPUT)
        assert len(result.main_claims) == 1

    @pytest.mark.asyncio
    async def test_prompt_rendered_with_context(self, extractor: ClaimExtractor):
        pm = MagicMock(wraps=extractor._prompts)
        extractor._prompts = pm
        await extractor.extract("test", context="prior discussion about AI")
        pm.render.assert_called_once()
        call_kwargs = pm.render.call_args
        assert call_kwargs.kwargs["variables"]["context"] == "prior discussion about AI"
