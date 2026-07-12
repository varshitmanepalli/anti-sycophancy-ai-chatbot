"""MemoryExtractor — extract long-term user information via LLM."""

from app.config.settings import Settings
from app.domain.memory_extraction import MemoryExtractionResult
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.memory.parser import MemoryExtractionParser
from app.logging.setup import get_logger

logger = get_logger(__name__)


class MemoryExtractor:
    """Extract durable user profile information from messages.

    Identifies career details, programming languages, goals, preferences,
    and projects. Ignores temporary conversational content.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        parser: MemoryExtractionParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._parser = parser or MemoryExtractionParser()

    async def extract(
        self,
        message: str,
        *,
        context: str = "",
    ) -> MemoryExtractionResult:
        """Extract long-term memory items from *message*."""
        prompt_text = self._prompts.render(
            PromptType.MEMORY_EXTRACTOR,
            variables={"message": message, "context": context},
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(
                max_tokens=self._settings.memory_extraction_max_tokens,
                temperature=self._settings.memory_extraction_temperature,
            ),
        )

        result = self._parser.parse(raw)
        logger.debug(
            "Extracted %d long-term memory items from message[:50]=%r",
            result.total_items,
            message[:50],
        )
        return result

    def parse_raw(self, raw: str) -> MemoryExtractionResult:
        """Parse a raw model response without calling the LLM."""
        return self._parser.parse(raw)
