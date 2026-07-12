"""LLM-backed input classifier using structured JSON output."""

import json
import re

from app.domain.classification import ALL_CATEGORIES, ClassificationResult, InputCategory
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.logging.setup import get_logger

logger = get_logger(__name__)

_VALID_CATEGORIES = {c.value for c in InputCategory}


class LLMClassifier:
    """Classify messages via the language model with a structured prompt."""

    def __init__(
        self,
        model_manager: ModelManager,
        prompt_manager: PromptManager | None = None,
    ) -> None:
        self._model = model_manager
        self._prompts = prompt_manager or PromptManager()

    async def classify(self, message: str) -> ClassificationResult:
        """Send message to LLM and parse structured classification."""
        categories_list = ", ".join(c.value for c in ALL_CATEGORIES)
        prompt_text = self._prompts.render(
            PromptType.INPUT_CLASSIFIER,
            variables={
                "message": message,
                "categories": categories_list,
            },
        )

        if not self._model.is_loaded:
            await self._model.load()

        raw = await self._model.generate(
            [{"role": "user", "content": prompt_text}],
            GenerationConfig(max_tokens=256, temperature=0.1),
        )

        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> ClassificationResult:
        """Extract JSON classification from model output."""
        data = self._extract_json(raw)

        category_str = str(data.get("category", "general_chat")).lower().strip()
        if category_str not in _VALID_CATEGORIES:
            category_str = "general_chat"

        confidence = float(data.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        scores_raw = data.get("scores", {})
        scores: dict[str, float] = {}
        for cat in ALL_CATEGORIES:
            val = scores_raw.get(cat.value, 0.0)
            scores[cat.value] = max(0.0, min(1.0, float(val)))

        if not scores:
            scores = {category_str: confidence}

        return ClassificationResult(
            category=InputCategory(category_str),
            confidence=confidence,
            scores=scores,
            method="llm",
        )

    @staticmethod
    def _extract_json(raw: str) -> dict:
        """Pull JSON object from model response, tolerating markdown fences."""
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1)

        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group())
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM classification JSON")

        return {"category": "general_chat", "confidence": 0.5}
