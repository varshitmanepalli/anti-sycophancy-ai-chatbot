"""Confidence calibration metric."""

from __future__ import annotations

from dataclasses import dataclass

from app.training.eval.metrics.base import Metric
from app.training.eval.models import BenchmarkCase, MetricResult


@dataclass
class CalibrationPoint:
    """One confidence/correctness pair for calibration."""

    confidence: float
    is_correct: bool


def expected_calibration_error(points: list[CalibrationPoint], *, bins: int = 10) -> float:
    """Compute Expected Calibration Error (ECE)."""
    if not points:
        return 0.0

    total = len(points)
    ece = 0.0
    for bucket in range(bins):
        lower = bucket / bins
        upper = (bucket + 1) / bins
        bucket_points = [
            point
            for point in points
            if lower <= point.confidence < upper or (bucket == bins - 1 and point.confidence == 1.0)
        ]
        if not bucket_points:
            continue
        avg_confidence = sum(point.confidence for point in bucket_points) / len(bucket_points)
        accuracy = sum(float(point.is_correct) for point in bucket_points) / len(bucket_points)
        ece += (len(bucket_points) / total) * abs(avg_confidence - accuracy)

    return ece


def brier_score(points: list[CalibrationPoint]) -> float:
    """Compute Brier score (lower is better)."""
    if not points:
        return 0.0
    return sum((point.confidence - float(point.is_correct)) ** 2 for point in points) / len(points)


class ConfidenceCalibrationMetric:
    """Measure confidence calibration across a benchmark dataset."""

    name = "confidence_calibration"

    def __init__(self, *, pass_threshold: float = 0.25, bins: int = 10) -> None:
        self._pass_threshold = pass_threshold
        self._bins = bins

    def evaluate(self, case: BenchmarkCase) -> MetricResult:
        confidence = case.predicted_confidence
        if confidence is None and case.labels and case.labels.expected_confidence is not None:
            confidence = case.labels.expected_confidence

        is_correct = None
        if case.labels and case.labels.is_correct is not None:
            is_correct = case.labels.is_correct

        if confidence is None:
            return MetricResult(
                name=self.name,
                score=0.0,
                passed=False,
                details={"reason": "missing_confidence"},
            )

        normalized = confidence / 100.0 if confidence > 1.0 else confidence
        normalized = max(0.0, min(normalized, 1.0))

        if is_correct is None:
            return MetricResult(
                name=self.name,
                score=0.5,
                passed=True,
                details={
                    "confidence": round(normalized, 4),
                    "reason": "correctness_label_missing",
                },
            )

        error = abs(normalized - float(is_correct))
        score = max(0.0, 1.0 - error)
        passed = error <= self._pass_threshold

        return MetricResult(
            name=self.name,
            score=score,
            passed=passed,
            details={
                "confidence": round(normalized, 4),
                "is_correct": is_correct,
                "calibration_error": round(error, 4),
            },
        )

    def is_dataset_metric(self) -> bool:
        return True

    def aggregate(self, points: list[CalibrationPoint]) -> dict[str, float]:
        """Compute dataset-level calibration statistics."""
        if not points:
            return {
                "ece": 0.0,
                "brier_score": 0.0,
                "mean_confidence": 0.0,
                "accuracy": 0.0,
            }

        ece = expected_calibration_error(points, bins=self._bins)
        brier = brier_score(points)
        mean_confidence = sum(point.confidence for point in points) / len(points)
        accuracy = sum(float(point.is_correct) for point in points) / len(points)
        return {
            "ece": round(ece, 4),
            "brier_score": round(brier, 4),
            "mean_confidence": round(mean_confidence, 4),
            "accuracy": round(accuracy, 4),
        }
