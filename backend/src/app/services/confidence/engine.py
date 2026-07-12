"""ConfidenceEngine — score reasoning confidence via LLM."""

from app.config.settings import Settings
from app.domain.confidence import ConfidenceResult
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.confidence.parser import ConfidenceScoreParser
from app.logging.setup import get_logger

logger = get_logger(__name__)


class ConfidenceEngine:
    """Score evidence quality, reasoning strength, source reliability, and uncertainty.

    Returns an overall 0–100 confidence score with explanations.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        parser: ConfidenceScoreParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._parser = parser or ConfidenceScoreParser()

    async def score(
        self,
        message: str,
        *,
        context: str = "",
        response: str = "",
    ) -> ConfidenceResult:
        """Score confidence for *message* and optional *response*."""
        prompt_text = self._prompts.render(
            PromptType.CONFIDENCE_SCORER,
            variables={
                "message": message,
                "context": context,
                "response": response,
            },
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(
                max_tokens=self._settings.confidence_scoring_max_tokens,
                temperature=self._settings.confidence_scoring_temperature,
            ),
        )

        result = self._parser.parse(raw)
        logger.debug(
            "Confidence score=%d for message[:50]=%r",
            result.confidence,
            message[:50],
        )
        return result

    def parse_raw(self, raw: str) -> ConfidenceResult:
        """Parse a raw model response without calling the LLM."""
        return self._parser.parse(raw)
