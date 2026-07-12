"""Logical consistency metric."""

from __future__ import annotations

import re

from app.training.eval.metrics.base import Metric
from app.training.eval.models import BenchmarkCase, MetricResult
from app.training.eval.text_utils import count_pattern_matches, split_sentences

FALLACY_SIGNAL_PATTERNS = [
    r"\beveryone knows\b",
    r"\balways\b.*\bnever\b",
    r"\beither .{1,40} or .{1,40}\b",
    r"\bif we allow .{1,40} then .{1,40} will happen\b",
    r"\bbecause i feel\b",
    r"\btrust me\b",
]

CONTRADICTION_PAIRS = [
    (r"\bis certain\b", r"\bis uncertain\b"),
    (r"\bdefinitely\b", r"\bnot sure\b"),
    (r"\bproven\b", r"\bunproven\b"),
    (r"\bwill happen\b", r"\bwill not happen\b"),
    (r"\bincrease\b", r"\bdecrease\b"),
]


def detect_contradictions(text: str) -> list[str]:
    """Find simple contradictory statement pairs."""
    sentences = split_sentences(text)
    joined = " ".join(sentences).lower()
    hits: list[str] = []

    for left_pattern, right_pattern in CONTRADICTION_PAIRS:
        if re.search(left_pattern, joined) and re.search(right_pattern, joined):
            hits.append(f"{left_pattern} vs {right_pattern}")

    return hits


class LogicalConsistencyMetric:
    """Measure internal logical consistency and fallacy signals."""

    name = "logical_consistency"

    def evaluate(self, case: BenchmarkCase) -> MetricResult:
        response = case.response
        fallacy_signals = count_pattern_matches(response, FALLACY_SIGNAL_PATTERNS)
        contradictions = detect_contradictions(response)

        penalty = min(fallacy_signals * 0.15 + len(contradictions) * 0.25, 1.0)
        score = max(0.0, 1.0 - penalty)
        passed = score >= 0.6 and not contradictions

        return MetricResult(
            name=self.name,
            score=score,
            passed=passed,
            details={
                "fallacy_signals": fallacy_signals,
                "contradictions": contradictions,
                "sentence_count": len(split_sentences(response)),
            },
        )

    def is_dataset_metric(self) -> bool:
        return False
