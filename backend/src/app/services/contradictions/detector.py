"""ContradictionDetector — compare new statements against memory via LLM."""

from app.config.settings import Settings
from app.domain.contradiction_check import ContradictionCheckResult
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.contradictions.parser import ContradictionCheckParser
from app.logging.setup import get_logger

logger = get_logger(__name__)


class ContradictionDetector:
    """Detect contradictions between a new message and stored user memory."""

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        parser: ContradictionCheckParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._parser = parser or ContradictionCheckParser()

    async def detect(
        self,
        message: str,
        *,
        memory_context: str = "",
    ) -> ContradictionCheckResult:
        """Compare *message* against formatted *memory_context*."""
        prompt_text = self._prompts.render(
            PromptType.CONTRADICTION_DETECTOR,
            variables={"message": message, "memory_context": memory_context},
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(
                max_tokens=self._settings.contradiction_detection_max_tokens,
                temperature=self._settings.contradiction_detection_temperature,
            ),
        )

        result = self._parser.parse(raw)
        logger.debug(
            "Detected %d contradictions for message[:50]=%r",
            len(result.contradictions),
            message[:50],
        )
        return result

    def parse_raw(self, raw: str) -> ContradictionCheckResult:
        """Parse a raw model response without calling the LLM."""
        return self._parser.parse(raw)
