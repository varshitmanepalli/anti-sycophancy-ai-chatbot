"""Evaluation runner."""

from __future__ import annotations

from app.logging.setup import get_logger
from app.training.eval.metrics.base import Metric
from app.training.eval.metrics.calibration import CalibrationPoint, ConfidenceCalibrationMetric
from app.training.eval.models import (
    AggregateMetric,
    BenchmarkDataset,
    CaseEvalResult,
    EvalReport,
    MetricResult,
)
from app.training.eval.registry import MetricRegistry, build_metrics
from app.utils.helpers import utc_now

logger = get_logger(__name__)


class EvaluationRunner:
    """Run benchmark evaluation and aggregate results."""

    def __init__(
        self,
        metrics: list[Metric] | None = None,
        *,
        registry: MetricRegistry | None = None,
    ) -> None:
        self._registry = registry or MetricRegistry()
        self.metrics = metrics or self._registry.build()
        self._calibration_stats: dict[str, float] = {}

    def run(self, dataset: BenchmarkDataset) -> EvalReport:
        """Evaluate all cases in a benchmark dataset."""
        logger.info(
            "Running evaluation on %s v%s (%d cases)",
            dataset.name,
            dataset.version,
            len(dataset.cases),
        )

        per_case_metrics = [metric for metric in self.metrics if not metric.is_dataset_metric()]
        dataset_metrics = [metric for metric in self.metrics if metric.is_dataset_metric()]

        case_results: list[CaseEvalResult] = []
        for case in dataset.cases:
            results = [metric.evaluate(case) for metric in per_case_metrics]
            case_results.append(CaseEvalResult(case_id=case.case_id, metrics=results))

        for metric in dataset_metrics:
            if isinstance(metric, ConfidenceCalibrationMetric):
                self._apply_calibration(dataset, case_results, metric)

        aggregate = self._aggregate(case_results)
        if self._calibration_stats and "confidence_calibration" in aggregate:
            aggregate["confidence_calibration"].details.update(self._calibration_stats)

        logger.info(
            "Evaluation finished for %s (%d cases, %d metrics)",
            dataset.name,
            len(dataset.cases),
            len(aggregate),
        )
        return EvalReport(
            benchmark_name=dataset.name,
            benchmark_version=dataset.version,
            timestamp=utc_now().isoformat(),
            case_results=case_results,
            aggregate=aggregate,
        )

    def _apply_calibration(
        self,
        dataset: BenchmarkDataset,
        case_results: list[CaseEvalResult],
        metric: ConfidenceCalibrationMetric,
    ) -> None:
        calibration_points: list[CalibrationPoint] = []

        for case, case_result in zip(dataset.cases, case_results, strict=True):
            result = metric.evaluate(case)
            case_result.metrics.append(result)

            confidence = result.details.get("confidence")
            is_correct = result.details.get("is_correct")
            if confidence is not None and is_correct is not None:
                calibration_points.append(
                    CalibrationPoint(confidence=float(confidence), is_correct=bool(is_correct))
                )

        self._calibration_stats = metric.aggregate(calibration_points)

    @staticmethod
    def _aggregate(case_results: list[CaseEvalResult]) -> dict[str, AggregateMetric]:
        grouped: dict[str, list[MetricResult]] = {}
        for case in case_results:
            for metric in case.metrics:
                grouped.setdefault(metric.name, []).append(metric)

        aggregate: dict[str, AggregateMetric] = {}
        for name, results in grouped.items():
            if not results:
                continue
            mean_score = sum(item.score for item in results) / len(results)
            pass_rate = sum(float(item.passed) for item in results) / len(results)
            details: dict[str, object] = {}

            if name == "hallucination_rate":
                rates = [
                    float(item.details["hallucination_rate"])
                    for item in results
                    if "hallucination_rate" in item.details
                ]
                if rates:
                    details["mean_hallucination_rate"] = round(sum(rates) / len(rates), 4)

            aggregate[name] = AggregateMetric(
                name=name,
                mean_score=mean_score,
                rate=pass_rate,
                count=len(results),
                details=details,
            )

        return aggregate


__all__ = ["EvaluationRunner", "build_metrics"]
