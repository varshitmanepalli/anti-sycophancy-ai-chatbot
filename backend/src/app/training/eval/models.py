"""Data models for benchmark evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ResponseStance(StrEnum):
    """Detected stance toward the user's position."""

    AGREE = "agree"
    NEUTRAL = "neutral"
    CHALLENGE = "challenge"


class BiasType(StrEnum):
    """Bias categories tracked during evaluation."""

    SYCOPHANCY = "sycophancy"
    CONFIRMATION_BIAS = "confirmation_bias"
    APPEAL_TO_POPULARITY = "appeal_to_popularity"
    DEMOGRAPHIC = "demographic"


@dataclass
class BenchmarkLabels:
    """Gold labels for a benchmark case."""

    should_agree_with_user: bool | None = None
    should_challenge_user: bool | None = None
    contains_hallucination: bool | None = None
    expected_evidence_refs: list[str] = field(default_factory=list)
    expected_confidence: float | None = None
    is_correct: bool | None = None
    bias_types: list[str] = field(default_factory=list)
    stance: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> BenchmarkLabels | None:
        if not data:
            return None
        refs = data.get("expected_evidence_refs", [])
        bias = data.get("bias_types", [])
        return cls(
            should_agree_with_user=data.get("should_agree_with_user"),
            should_challenge_user=data.get("should_challenge_user"),
            contains_hallucination=data.get("contains_hallucination"),
            expected_evidence_refs=[str(item) for item in refs] if isinstance(refs, list) else [],
            expected_confidence=_optional_float(data.get("expected_confidence")),
            is_correct=data.get("is_correct"),
            bias_types=[str(item) for item in bias] if isinstance(bias, list) else [],
            stance=str(data["stance"]) if data.get("stance") else None,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.should_agree_with_user is not None:
            result["should_agree_with_user"] = self.should_agree_with_user
        if self.should_challenge_user is not None:
            result["should_challenge_user"] = self.should_challenge_user
        if self.contains_hallucination is not None:
            result["contains_hallucination"] = self.contains_hallucination
        if self.expected_evidence_refs:
            result["expected_evidence_refs"] = self.expected_evidence_refs
        if self.expected_confidence is not None:
            result["expected_confidence"] = self.expected_confidence
        if self.is_correct is not None:
            result["is_correct"] = self.is_correct
        if self.bias_types:
            result["bias_types"] = self.bias_types
        if self.stance is not None:
            result["stance"] = self.stance
        return result


@dataclass
class BenchmarkCase:
    """One evaluable benchmark example."""

    case_id: str
    prompt: str
    response: str
    reference_response: str | None = None
    context: str | None = None
    evidence: list[str] = field(default_factory=list)
    labels: BenchmarkLabels | None = None
    predicted_confidence: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkCase:
        case_id = str(data.get("case_id") or data.get("id") or "").strip()
        if not case_id:
            raise ValueError("Benchmark case requires case_id or id")

        prompt = str(data.get("prompt") or data.get("input") or "").strip()
        response = str(data.get("response") or data.get("output") or "").strip()
        if not prompt:
            raise ValueError(f"Benchmark case {case_id} requires prompt or input")
        if not response:
            raise ValueError(f"Benchmark case {case_id} requires response or output")

        evidence_raw = data.get("evidence", [])
        evidence: list[str] = []
        if isinstance(evidence_raw, list):
            evidence = [str(item).strip() for item in evidence_raw if str(item).strip()]

        context = data.get("context")
        if context is None and isinstance(data.get("messages"), list):
            context = _format_messages(data["messages"])

        return cls(
            case_id=case_id,
            prompt=prompt,
            response=response,
            reference_response=_optional_str(data.get("reference_response")),
            context=_optional_str(context),
            evidence=evidence,
            labels=BenchmarkLabels.from_dict(data.get("labels")),
            predicted_confidence=_optional_float(data.get("predicted_confidence")),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "case_id": self.case_id,
            "prompt": self.prompt,
            "response": self.response,
        }
        if self.reference_response:
            result["reference_response"] = self.reference_response
        if self.context:
            result["context"] = self.context
        if self.evidence:
            result["evidence"] = self.evidence
        if self.labels is not None:
            labels = self.labels.to_dict()
            if labels:
                result["labels"] = labels
        if self.predicted_confidence is not None:
            result["predicted_confidence"] = self.predicted_confidence
        return result


@dataclass
class BenchmarkDataset:
    """Collection of benchmark cases with metadata."""

    name: str
    version: str
    cases: list[BenchmarkCase] = field(default_factory=list)
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkDataset:
        name = str(data.get("name") or "benchmark").strip()
        version = str(data.get("version") or "1.0").strip()
        description = _optional_str(data.get("description"))

        cases_raw = data.get("cases", [])
        cases: list[BenchmarkCase] = []
        if isinstance(cases_raw, list):
            for item in cases_raw:
                if isinstance(item, dict):
                    cases.append(BenchmarkCase.from_dict(item))

        return cls(name=name, version=version, cases=cases, description=description)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "cases": [case.to_dict() for case in self.cases],
        }
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class MetricResult:
    """Score for one metric on one benchmark case."""

    name: str
    score: float
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": round(self.score, 4),
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class CaseEvalResult:
    """Evaluation results for a single benchmark case."""

    case_id: str
    metrics: list[MetricResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "metrics": [metric.to_dict() for metric in self.metrics],
        }

    def metric(self, name: str) -> MetricResult | None:
        for item in self.metrics:
            if item.name == name:
                return item
        return None


@dataclass
class AggregateMetric:
    """Aggregated metric across all benchmark cases."""

    name: str
    mean_score: float
    rate: float
    count: int
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mean_score": round(self.mean_score, 4),
            "rate": round(self.rate, 4),
            "count": self.count,
            "details": self.details,
        }


@dataclass
class EvalReport:
    """Full evaluation report for a benchmark run."""

    benchmark_name: str
    benchmark_version: str
    timestamp: str
    case_results: list[CaseEvalResult] = field(default_factory=list)
    aggregate: dict[str, AggregateMetric] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_name": self.benchmark_name,
            "benchmark_version": self.benchmark_version,
            "timestamp": self.timestamp,
            "case_results": [case.to_dict() for case in self.case_results],
            "aggregate": {key: value.to_dict() for key, value in self.aggregate.items()},
        }


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _format_messages(messages: list[Any]) -> str:
    lines: list[str] = []
    for item in messages:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "unknown")).strip()
        content = str(item.get("content", "")).strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)
