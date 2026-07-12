"""ClaimExtractor — extract structured claims from user messages via LLM."""

from app.config.settings import Settings
from app.domain.claims import ClaimExtractionResult
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.claims.parser import ClaimExtractionParser
from app.logging.setup import get_logger

logger = get_logger(__name__)


class ClaimExtractor:
    """Extract main claims, assumptions, evidence, and gaps from text.

    Uses a versioned Jinja2 prompt and parses structured JSON from the model.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        parser: ClaimExtractionParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._parser = parser or ClaimExtractionParser()

    async def extract(
        self,
        message: str,
        *,
        context: str = "",
    ) -> ClaimExtractionResult:
        """Extract structured claims from *message*."""
        prompt_text = self._prompts.render(
            PromptType.CLAIM_EXTRACTOR,
            variables={"message": message, "context": context},
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(
                max_tokens=self._settings.claim_extraction_max_tokens,
                temperature=self._settings.claim_extraction_temperature,
            ),
        )

        result = self._parser.parse(raw)
        logger.debug(
            "Extracted %d main claims, %d assumptions from message[:50]=%r",
            len(result.main_claims),
            len(result.hidden_assumptions),
            message[:50],
        )
        return result

    def parse_raw(self, raw: str) -> ClaimExtractionResult:
        """Parse a raw model response without calling the LLM."""
        return self._parser.parse(raw)
