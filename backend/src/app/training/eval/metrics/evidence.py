"""Evidence usage metric."""

from __future__ import annotations

import re

from app.training.eval.metrics.base import Metric
from app.training.eval.models import BenchmarkCase, MetricResult
from app.training.eval.text_utils import contains_any, tokenize

CITATION_PATTERNS = [
    r"\baccording to\b",
    r"\bas (?:shown|cited|reported|documented)\b",
    r"\bthe (?:data|study|report|evidence) (?:shows|indicates|suggests)\b",
    r"\b(?:source|reference|citation)\b",
    r"\[\d+\]",
]


def evidence_overlap(response: str, evidence: list[str]) -> float:
    """Return fraction of evidence items referenced in the response."""
    if not evidence:
        return 1.0

    matched = 0
    response_tokens = tokenize(response)
    for item in evidence:
        item_tokens = tokenize(item)
        if not item_tokens:
            continue
        overlap = len(item_tokens & response_tokens) / len(item_tokens)
        if overlap >= 0.35 or item.lower() in response.lower():
            matched += 1

    return matched / len(evidence)


class EvidenceUsageMetric:
    """Measure whether the response uses provided evidence."""

    name = "evidence_usage"

    def evaluate(self, case: BenchmarkCase) -> MetricResult:
        evidence_items = case.evidence
        expected_refs = []
        if case.labels and case.labels.expected_evidence_refs:
            expected_refs = case.labels.expected_evidence_refs

        overlap_score = evidence_overlap(case.response, evidence_items)
        ref_score = 1.0
        matched_refs: list[str] = []
        if expected_refs:
            matched_refs = contains_any(case.response, expected_refs)
            ref_score = len(matched_refs) / len(expected_refs)

        citation_count = sum(
            1 for pattern in CITATION_PATTERNS if re.search(pattern, case.response, re.IGNORECASE)
        )
        citation_bonus = min(citation_count * 0.1, 0.2)

        if expected_refs and evidence_items:
            score = (overlap_score + ref_score) / 2.0 + citation_bonus
        elif expected_refs:
            score = ref_score + citation_bonus
        elif evidence_items:
            score = overlap_score + citation_bonus
        else:
            score = 0.5 + citation_bonus

        score = min(score, 1.0)
        passed = score >= 0.5

        return MetricResult(
            name=self.name,
            score=score,
            passed=passed,
            details={
                "evidence_overlap": round(overlap_score, 4),
                "expected_refs_matched": matched_refs,
                "expected_refs_total": len(expected_refs),
                "citation_signals": citation_count,
                "evidence_items_total": len(evidence_items),
            },
        )

    def is_dataset_metric(self) -> bool:
        return False
