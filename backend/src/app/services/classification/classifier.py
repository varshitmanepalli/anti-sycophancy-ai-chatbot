"""InputClassifier — unified message categorization facade."""

from app.config.settings import Settings
from app.domain.classification import ClassificationResult
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.services.classification.llm_classifier import LLMClassifier
from app.services.classification.rule_based import RuleBasedClassifier
from app.logging.setup import get_logger

logger = get_logger(__name__)


class InputClassifier:
    """Classify user messages into semantic categories with confidence.

    Supports three modes (via ``settings.classifier_mode``):
      - ``rules``  — fast pattern matching (default)
      - ``llm``    — model-based classification
      - ``hybrid`` — rules first; LLM when confidence is below threshold
    """

    def __init__(
        self,
        settings: Settings,
        model_manager: ModelManager | None = None,
        prompt_manager: PromptManager | None = None,
    ) -> None:
        self._settings = settings
        self._rules = RuleBasedClassifier()
        self._llm: LLMClassifier | None = None

        if model_manager is not None:
            self._llm = LLMClassifier(
                model_manager=model_manager,
                prompt_manager=prompt_manager,
            )

    async def classify(self, message: str) -> ClassificationResult:
        """Classify *message* and return category with confidence score."""
        mode = self._settings.classifier_mode

        if mode == "llm":
            return await self._classify_llm(message)

        if mode == "hybrid":
            rule_result = self._rules.classify(message)
            if rule_result.confidence >= self._settings.classifier_confidence_threshold:
                return rule_result
            logger.debug(
                "Hybrid fallback to LLM (rule confidence %.2f < %.2f)",
                rule_result.confidence,
                self._settings.classifier_confidence_threshold,
            )
            try:
                return await self._classify_llm(message)
            except Exception as exc:
                logger.warning("LLM classification failed, using rules: %s", exc)
                return rule_result

        return self._rules.classify(message)

    async def _classify_llm(self, message: str) -> ClassificationResult:
        if self._llm is None:
            logger.warning("LLM classifier unavailable — falling back to rules")
            return self._rules.classify(message)
        return await self._llm.classify(message)
