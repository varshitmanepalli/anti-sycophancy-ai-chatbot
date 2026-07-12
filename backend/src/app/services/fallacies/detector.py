"""LogicalFallacyDetector — detect fallacies in reasoning via LLM."""

from app.config.settings import Settings
from app.domain.fallacies import FallacyDetectionResult
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.fallacies.parser import FallacyDetectionParser
from app.logging.setup import get_logger

logger = get_logger(__name__)


class LogicalFallacyDetector:
    """Detect logical fallacies in user messages using an LLM.

    Identifies hasty generalization, false dilemma, slippery slope,
    appeals to emotion/popularity, circular reasoning, confirmation bias,
    and post hoc errors.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        parser: FallacyDetectionParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._parser = parser or FallacyDetectionParser()

    async def detect(
        self,
        message: str,
        *,
        context: str = "",
    ) -> FallacyDetectionResult:
        """Analyze *message* for logical fallacies."""
        prompt_text = self._prompts.render(
            PromptType.FALLACY_DETECTOR,
            variables={"message": message, "context": context},
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(
                max_tokens=self._settings.fallacy_detection_max_tokens,
                temperature=self._settings.fallacy_detection_temperature,
            ),
        )

        result = self._parser.parse(raw)
        logger.debug(
            "Detected %d fallacies in message[:50]=%r",
            len(result.fallacies),
            message[:50],
        )
        return result

    def parse_raw(self, raw: str) -> FallacyDetectionResult:
        """Parse a raw model response without calling the LLM."""
        return self._parser.parse(raw)
