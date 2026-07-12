"""Metric registry for dependency injection."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from app.training.eval.metrics import (
    AgreementRateMetric,
    BiasDetectionMetric,
    ConfidenceCalibrationMetric,
    EvidenceUsageMetric,
    HallucinationRateMetric,
    LogicalConsistencyMetric,
)
from app.training.eval.metrics.base import DEFAULT_METRIC_NAMES, Metric

if TYPE_CHECKING:
    from app.config.training import TrainingSettings


MetricFactory = Callable[[], Metric]


class MetricRegistry:
    """Build evaluation metrics by name (Open/Closed: register without changing runner)."""

    def __init__(self, settings: TrainingSettings | None = None) -> None:
        from app.config.training import get_training_settings

        self._settings = settings or get_training_settings()
        self._factories: dict[str, MetricFactory] = {
            "agreement_rate": lambda: AgreementRateMetric(),
            "hallucination_rate": lambda: HallucinationRateMetric(),
            "evidence_usage": lambda: EvidenceUsageMetric(),
            "logical_consistency": lambda: LogicalConsistencyMetric(),
            "bias_detection": lambda: BiasDetectionMetric(),
            "confidence_calibration": lambda: ConfidenceCalibrationMetric(
                pass_threshold=self._settings.eval_calibration_pass_threshold,
                bins=self._settings.eval_calibration_bins,
            ),
        }

    def register(self, name: str, factory: MetricFactory) -> None:
        """Register a custom metric factory."""
        self._factories[name] = factory

    def build(self, names: list[str] | None = None) -> list[Metric]:
        """Instantiate metrics by name."""
        selected = names or list(self._settings.eval_metrics or DEFAULT_METRIC_NAMES)
        metrics: list[Metric] = []
        for name in selected:
            factory = self._factories.get(name)
            if factory is None:
                raise ValueError(f"Unknown metric: {name}")
            metrics.append(factory())
        return metrics

    @property
    def available_metrics(self) -> tuple[str, ...]:
        """Return registered metric names."""
        return tuple(self._factories.keys())


def build_metrics(
    names: list[str] | None = None,
    *,
    registry: MetricRegistry | None = None,
) -> list[Metric]:
    """Convenience wrapper for metric construction."""
    active_registry = registry or MetricRegistry()
    return active_registry.build(names)
