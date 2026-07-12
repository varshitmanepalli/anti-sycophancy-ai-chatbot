#!/usr/bin/env python3
"""Run benchmark evaluation and generate reports.

Usage:
    python scripts/run_eval.py \\
        --benchmark data/benchmarks/anti_sycophancy_benchmark.json \\
        --output-dir data/eval_reports

Outputs:
    report.json   - structured results
    report.md     - markdown summary
    report.html   - HTML dashboard
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from app.config.settings import get_settings
from app.config.training import get_training_settings
from app.logging.setup import configure_logging, get_logger
from app.training.eval.metrics.base import DEFAULT_METRIC_NAMES
from app.training.eval.pipeline import EvalPipeline

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run benchmark evaluation")
    parser.add_argument(
        "--benchmark",
        required=True,
        help="Path to benchmark JSON or JSONL file",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for generated reports (default: training eval_output_dir)",
    )
    parser.add_argument(
        "--metrics",
        nargs="*",
        default=None,
        help="Metrics to run (default: all)",
    )
    parser.add_argument(
        "--formats",
        nargs="*",
        choices=["json", "md", "html"],
        default=None,
        help="Report formats to generate",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging(get_settings())
    args = parse_args()
    settings = get_training_settings()

    output_dir = Path(args.output_dir) if args.output_dir else settings.eval_output_dir
    metrics = args.metrics or list(settings.eval_metrics)
    report_formats = tuple(args.formats or settings.eval_report_formats)

    try:
        result = EvalPipeline(settings=settings).run(
            args.benchmark,
            output_dir=output_dir,
            metrics=metrics,
            report_formats=report_formats,
        )
    except ValueError as exc:
        logger.error("Evaluation failed: %s", exc)
        return 1

    report = result.report
    logger.info("Benchmark: %s v%s", report.benchmark_name, report.benchmark_version)
    logger.info("Cases evaluated: %d", len(report.case_results))
    for path in result.report_paths:
        logger.info("Report written: %s", path)
    for name, metric in report.aggregate.items():
        logger.info(
            "Metric %s: score=%.2f%% pass_rate=%.2f%%",
            name,
            metric.mean_score * 100,
            metric.rate * 100,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
