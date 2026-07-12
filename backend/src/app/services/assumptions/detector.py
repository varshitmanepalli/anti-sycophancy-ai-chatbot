"""AssumptionDetector — detect reasoning flaws via LLM."""

from app.config.settings import Settings
from app.domain.assumptions import AssumptionDetectionResult
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.assumptions.parser import AssumptionDetectionParser
from app.logging.setup import get_logger

logger = get_logger(__name__)

# Structured JSON prompt version
_PROMPT_VERSION = "2"


class AssumptionDetector:
    """Detect unsupported assumptions, biases, and reasoning flaws in text.

    Uses the v2 ``assumption_detector`` Jinja2 template and parses
    structured JSON from the model response.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        parser: AssumptionDetectionParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._parser = parser or AssumptionDetectionParser()

    async def detect(
        self,
        message: str,
        *,
        context: str = "",
    ) -> AssumptionDetectionResult:
        """Analyze *message* for assumptions and reasoning flaws."""
        prompt_text = self._prompts.render(
            PromptType.ASSUMPTION_DETECTOR,
            version=_PROMPT_VERSION,
            variables={"message": message, "context": context},
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(
                max_tokens=self._settings.assumption_detection_max_tokens,
                temperature=self._settings.assumption_detection_temperature,
            ),
        )

        result = self._parser.parse(raw)
        logger.debug(
            "Detected %d issues across 5 categories for message[:50]=%r",
            result.total_issues,
            message[:50],
        )
        return result

    def parse_raw(self, raw: str) -> AssumptionDetectionResult:
        """Parse a raw model response without calling the LLM."""
        return self._parser.parse(raw)
