"""Metric registry tests."""

import pytest

from app.config.training import TrainingSettings
from app.training.eval.metrics.calibration import ConfidenceCalibrationMetric
from app.training.eval.registry import MetricRegistry, build_metrics


class TestMetricRegistry:
    def test_builds_all_default_metrics(self):
        registry = MetricRegistry()
        metrics = registry.build()
        names = {metric.name for metric in metrics}
        assert names == set(registry.available_metrics)

    def test_builds_subset(self):
        metrics = build_metrics(["agreement_rate", "evidence_usage"])
        assert len(metrics) == 2
        assert metrics[0].name == "agreement_rate"

    def test_unknown_metric_raises(self):
        registry = MetricRegistry()
        with pytest.raises(ValueError, match="Unknown metric"):
            registry.build(["not_a_metric"])

    def test_calibration_uses_settings(self):
        settings = TrainingSettings(
            eval_calibration_pass_threshold=0.1,
            eval_calibration_bins=5,
        )
        registry = MetricRegistry(settings)
        metrics = registry.build(["confidence_calibration"])
        metric = metrics[0]
        assert isinstance(metric, ConfidenceCalibrationMetric)
        assert metric._pass_threshold == 0.1
        assert metric._bins == 5

    def test_register_custom_metric(self):
        from app.training.eval.models import BenchmarkCase, MetricResult

        class DummyMetric:
            name = "dummy"

            def evaluate(self, case: BenchmarkCase) -> MetricResult:
                return MetricResult(name=self.name, score=1.0, passed=True)

            def is_dataset_metric(self) -> bool:
                return False

        registry = MetricRegistry()
        registry.register("dummy", DummyMetric)
        metrics = registry.build(["dummy"])
        assert metrics[0].name == "dummy"
