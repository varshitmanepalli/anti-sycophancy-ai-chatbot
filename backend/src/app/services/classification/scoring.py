"""Score normalization utilities."""

import math

from app.domain.classification import ALL_CATEGORIES, InputCategory


def softmax(scores: dict[InputCategory, float], temperature: float = 1.0) -> dict[str, float]:
    """Convert raw scores to normalized probabilities."""
    if not scores:
        return {c.value: 1.0 / len(ALL_CATEGORIES) for c in ALL_CATEGORIES}

    scaled = {k: v / temperature for k, v in scores.items()}
    max_score = max(scaled.values())
    exp_scores = {k: math.exp(v - max_score) for k, v in scaled.items()}
    total = sum(exp_scores.values()) or 1.0
    return {k.value: exp_scores[k] / total for k in exp_scores}


def top_category(
    probabilities: dict[str, float],
) -> tuple[InputCategory, float]:
    """Return the highest-probability category and its confidence."""
    best = max(probabilities.items(), key=lambda item: item[1])
    return InputCategory(best[0]), best[1]
