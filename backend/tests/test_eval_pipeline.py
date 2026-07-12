"""Evaluation pipeline tests."""

import json
from pathlib import Path

from app.config.training import TrainingSettings
from app.training.eval.pipeline import EvalPipeline
from app.training.eval.registry import MetricRegistry


class TestEvalPipeline:
    def test_runs_benchmark_and_writes_reports(self, tmp_path: Path):
        benchmark_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "benchmarks"
            / "anti_sycophancy_benchmark.json"
        )
        settings = TrainingSettings(
            eval_output_dir=tmp_path,
            eval_report_formats=["json", "md"],
            eval_metrics=["agreement_rate", "logical_consistency"],
        )
        pipeline = EvalPipeline(settings=settings, registry=MetricRegistry(settings))
        result = pipeline.run(benchmark_path)

        assert result.report.benchmark_name == "anti_sycophancy_benchmark"
        assert len(result.report.case_results) == 5
        assert (tmp_path / "report.json").exists()
        assert (tmp_path / "report.md").exists()

        payload = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
        assert "aggregate" in payload
        assert "agreement_rate" in payload["aggregate"]

    def test_rejects_empty_benchmark(self, tmp_path: Path):
        empty_benchmark = tmp_path / "empty.json"
        empty_benchmark.write_text(
            json.dumps({"name": "empty", "version": "1.0", "cases": []}),
            encoding="utf-8",
        )
        pipeline = EvalPipeline(
            settings=TrainingSettings(eval_output_dir=tmp_path),
        )
        try:
            pipeline.run(empty_benchmark)
            raise AssertionError("Expected ValueError")
        except ValueError as exc:
            assert "no cases" in str(exc).lower()
