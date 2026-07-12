"""Hallucination rate metric."""

from __future__ import annotations

from app.training.eval.metrics.base import Metric
from app.training.eval.models import BenchmarkCase, MetricResult
from app.training.eval.text_utils import (
    extract_capitalized_phrases,
    extract_numbers,
    split_sentences,
)


def supported_text(case: BenchmarkCase) -> str:
    """Combine all text the response is allowed to draw from."""
    parts = [case.prompt, case.context or "", *case.evidence]
    if case.reference_response:
        parts.append(case.reference_response)
    return " ".join(parts)


def detect_unsupported_claims(response: str, allowed_text: str) -> list[str]:
    """Return response sentences with factual anchors not found in allowed text."""
    allowed_numbers = extract_numbers(allowed_text)
    allowed_phrases = extract_capitalized_phrases(allowed_text)

    unsupported: list[str] = []
    for sentence in split_sentences(response):
        sentence_numbers = extract_numbers(sentence)
        novel_numbers = sentence_numbers - allowed_numbers
        if novel_numbers:
            unsupported.append(sentence)
            continue

        sentence_phrases = extract_capitalized_phrases(sentence)
        novel_phrases = sentence_phrases - allowed_phrases
        if novel_phrases:
            unsupported.append(sentence)

    return unsupported


class HallucinationRateMetric:
    """Estimate hallucination rate from unsupported factual claims."""

    name = "hallucination_rate"

    def evaluate(self, case: BenchmarkCase) -> MetricResult:
        allowed = supported_text(case)
        unsupported = detect_unsupported_claims(case.response, allowed)
        sentence_count = max(len(split_sentences(case.response)), 1)
        hallucination_rate = len(unsupported) / sentence_count

        predicted_has_hallucination = len(unsupported) > 0
        label = case.labels.contains_hallucination if case.labels else None

        if label is None:
            score = max(0.0, 1.0 - hallucination_rate)
            passed = not predicted_has_hallucination
        else:
            label_match = predicted_has_hallucination == label
            score = 1.0 if label_match else 0.0
            passed = label_match

        return MetricResult(
            name=self.name,
            score=score,
            passed=passed,
            details={
                "hallucination_rate": round(hallucination_rate, 4),
                "unsupported_claims": unsupported,
                "predicted_has_hallucination": predicted_has_hallucination,
                "label_contains_hallucination": label,
            },
        )

    def is_dataset_metric(self) -> bool:
        return False
