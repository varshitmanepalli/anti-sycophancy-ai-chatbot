"""Evaluation pipeline composing loader, runner, and report writer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config.training import TrainingSettings, get_training_settings
from app.logging.setup import get_logger
from app.training.eval.io import load_benchmark_dataset
from app.training.eval.models import EvalReport
from app.training.eval.registry import MetricRegistry
from app.training.eval.report_writer import ReportWriter
from app.training.eval.runner import EvaluationRunner

logger = get_logger(__name__)


@dataclass
class EvalPipelineResult:
    """Artifacts produced by a full evaluation run."""

    report: EvalReport
    report_paths: tuple[Path, ...] = field(default_factory=tuple)


class EvalPipeline:
    """Orchestrate benchmark loading, evaluation, and report generation."""

    def __init__(
        self,
        *,
        settings: TrainingSettings | None = None,
        registry: MetricRegistry | None = None,
        runner: EvaluationRunner | None = None,
        report_writer: ReportWriter | None = None,
    ) -> None:
        self._settings = settings or get_training_settings()
        self._registry = registry or MetricRegistry(self._settings)
        self._runner = runner or EvaluationRunner(
            metrics=self._registry.build(),
            registry=self._registry,
        )
        self._report_writer = report_writer or ReportWriter(
            formats=tuple(self._settings.eval_report_formats),
            output_dir=self._settings.eval_output_dir,
        )

    def run(
        self,
        benchmark_path: str | Path,
        *,
        output_dir: Path | None = None,
        metrics: list[str] | None = None,
        report_formats: tuple[str, ...] | None = None,
    ) -> EvalPipelineResult:
        """Load a benchmark, evaluate it, and write reports."""
        dataset = load_benchmark_dataset(benchmark_path)
        if not dataset.cases:
            raise ValueError("Benchmark dataset contains no cases")

        logger.info(
            "Starting evaluation: benchmark=%s version=%s cases=%d",
            dataset.name,
            dataset.version,
            len(dataset.cases),
        )

        if metrics is not None:
            self._runner = EvaluationRunner(
                metrics=self._registry.build(metrics),
                registry=self._registry,
            )

        report = self._runner.run(dataset)

        writer = self._report_writer
        if output_dir is not None or report_formats is not None:
            writer = ReportWriter(
                formats=tuple(report_formats or self._settings.eval_report_formats),
                output_dir=output_dir or self._settings.eval_output_dir,
            )

        paths = writer.write(report)
        logger.info(
            "Evaluation complete: benchmark=%s cases=%d reports=%d",
            dataset.name,
            len(dataset.cases),
            len(paths),
        )
        return EvalPipelineResult(report=report, report_paths=tuple(paths))
