"""Metric protocol and registry."""

from __future__ import annotations

from typing import Protocol

from app.training.eval.models import BenchmarkCase, MetricResult


class Metric(Protocol):
    """Protocol for evaluation metrics."""

    name: str

    def evaluate(self, case: BenchmarkCase) -> MetricResult:
        """Score one benchmark case."""

    def is_dataset_metric(self) -> bool:
        """Return True if metric requires full dataset aggregation."""


from app.training.constants import DEFAULT_METRIC_NAMES
