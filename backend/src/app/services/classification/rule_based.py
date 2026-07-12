"""Rule-based input classifier using weighted keyword and regex patterns."""

from app.domain.classification import ALL_CATEGORIES, ClassificationResult, InputCategory
from app.services.classification.patterns import CATEGORY_PATTERNS, COMPILED_PATTERNS
from app.services.classification.scoring import softmax, top_category
from app.logging.setup import get_logger

logger = get_logger(__name__)

# Minimum raw score to avoid defaulting everything to general_chat
_MIN_SIGNAL_SCORE = 0.5
# Base prior so general_chat wins only when nothing else matches
_BASE_PRIOR = 0.1


class RuleBasedClassifier:
    """Fast, deterministic classifier using pattern matching."""

    def classify(self, message: str) -> ClassificationResult:
        """Classify *message* and return category with confidence."""
        text = message.strip().lower()
        raw_scores = self._score_all(text)

        if max(raw_scores.values()) < _MIN_SIGNAL_SCORE:
            raw_scores[InputCategory.GENERAL_CHAT] += 1.0

        probabilities = softmax(raw_scores, temperature=0.8)
        category, confidence = top_category(probabilities)

        logger.debug(
            "Rule classification: %s (%.2f) for message[:50]=%r",
            category.value,
            confidence,
            message[:50],
        )

        return ClassificationResult(
            category=category,
            confidence=confidence,
            scores=probabilities,
            method="rules",
        )

    def _score_all(self, text: str) -> dict[InputCategory, float]:
        scores: dict[InputCategory, float] = {cat: _BASE_PRIOR for cat in ALL_CATEGORIES}

        for category in ALL_CATEGORIES:
            spec = CATEGORY_PATTERNS[category]
            scores[category] += self._keyword_score(text, spec.keywords, spec.keyword_weight)
            scores[category] += self._pattern_score(text, COMPILED_PATTERNS[category])

        return scores

    @staticmethod
    def _keyword_score(text: str, keywords: tuple[str, ...], weight: float) -> float:
        total = 0.0
        for keyword in keywords:
            if keyword in text:
                total += weight
        return total

    @staticmethod
    def _pattern_score(
        text: str, patterns: list[tuple]
    ) -> float:
        total = 0.0
        for pattern, weight in patterns:
            if pattern.search(text):
                total += weight
        return total
