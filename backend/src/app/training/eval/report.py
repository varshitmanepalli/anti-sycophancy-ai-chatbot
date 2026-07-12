"""Evaluation report generation."""

from __future__ import annotations

from html import escape

from app.training.eval.models import EvalReport


METRIC_LABELS = {
    "agreement_rate": "Agreement Rate",
    "hallucination_rate": "Hallucination Rate",
    "evidence_usage": "Evidence Usage",
    "logical_consistency": "Logical Consistency",
    "bias_detection": "Bias Detection",
    "confidence_calibration": "Confidence Calibration",
}


def render_markdown_report(report: EvalReport) -> str:
    """Render a human-readable markdown summary."""
    lines = [
        f"# Evaluation Report: {report.benchmark_name}",
        "",
        f"- **Version:** {report.benchmark_version}",
        f"- **Generated:** {report.timestamp}",
        f"- **Cases evaluated:** {len(report.case_results)}",
        "",
        "## Aggregate Metrics",
        "",
        "| Metric | Mean Score | Pass Rate | Count |",
        "| --- | ---: | ---: | ---: |",
    ]

    for name, metric in report.aggregate.items():
        label = METRIC_LABELS.get(name, name)
        lines.append(
            f"| {label} | {metric.mean_score:.2%} | {metric.rate:.2%} | {metric.count} |"
        )

    calibration = report.aggregate.get("confidence_calibration")
    if calibration and calibration.details:
        lines.extend(
            [
                "",
                "### Confidence Calibration Details",
                "",
                f"- ECE: `{calibration.details.get('ece', 'n/a')}`",
                f"- Brier score: `{calibration.details.get('brier_score', 'n/a')}`",
                f"- Mean confidence: `{calibration.details.get('mean_confidence', 'n/a')}`",
                f"- Accuracy: `{calibration.details.get('accuracy', 'n/a')}`",
            ]
        )

    hallucination = report.aggregate.get("hallucination_rate")
    if hallucination and hallucination.details.get("mean_hallucination_rate") is not None:
        lines.extend(
            [
                "",
                f"Mean hallucination rate: `{hallucination.details['mean_hallucination_rate']}`",
            ]
        )

    lines.extend(["", "## Per-Case Results", ""])
    for case in report.case_results:
        lines.append(f"### {case.case_id}")
        lines.append("")
        lines.append("| Metric | Score | Passed |")
        lines.append("| --- | ---: | :---: |")
        for metric in case.metrics:
            label = METRIC_LABELS.get(metric.name, metric.name)
            passed = "yes" if metric.passed else "no"
            lines.append(f"| {label} | {metric.score:.2%} | {passed} |")
        lines.append("")

    return "\n".join(lines)


def render_html_report(report: EvalReport) -> str:
    """Render an HTML evaluation summary."""
    aggregate_rows = []
    for name, metric in report.aggregate.items():
        label = escape(METRIC_LABELS.get(name, name))
        aggregate_rows.append(
            "<tr>"
            f"<td>{label}</td>"
            f"<td>{metric.mean_score:.2%}</td>"
            f"<td>{metric.rate:.2%}</td>"
            f"<td>{metric.count}</td>"
            "</tr>"
        )

    case_sections = []
    for case in report.case_results:
        metric_rows = []
        for metric in case.metrics:
            label = escape(METRIC_LABELS.get(metric.name, metric.name))
            passed = "yes" if metric.passed else "no"
            metric_rows.append(
                "<tr>"
                f"<td>{label}</td>"
                f"<td>{metric.score:.2%}</td>"
                f"<td>{passed}</td>"
                "</tr>"
            )
        case_sections.append(
            "<section>"
            f"<h3>{escape(case.case_id)}</h3>"
            "<table>"
            "<thead><tr><th>Metric</th><th>Score</th><th>Passed</th></tr></thead>"
            f"<tbody>{''.join(metric_rows)}</tbody>"
            "</table>"
            "</section>"
        )

    calibration = report.aggregate.get("confidence_calibration")
    calibration_block = ""
    if calibration and calibration.details:
        calibration_block = (
            "<section>"
            "<h2>Confidence Calibration</h2>"
            "<ul>"
            f"<li>ECE: {escape(str(calibration.details.get('ece', 'n/a')))}</li>"
            f"<li>Brier score: {escape(str(calibration.details.get('brier_score', 'n/a')))}</li>"
            f"<li>Mean confidence: {escape(str(calibration.details.get('mean_confidence', 'n/a')))}</li>"
            f"<li>Accuracy: {escape(str(calibration.details.get('accuracy', 'n/a')))}</li>"
            "</ul>"
            "</section>"
        )

    return (
        "<!DOCTYPE html>"
        "<html lang='en'>"
        "<head>"
        "<meta charset='utf-8'/>"
        f"<title>Evaluation Report: {escape(report.benchmark_name)}</title>"
        "<style>"
        "body{font-family:Segoe UI,Arial,sans-serif;margin:2rem;color:#1f2937;}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0;}"
        "th,td{border:1px solid #d1d5db;padding:0.5rem 0.75rem;text-align:left;}"
        "th{background:#f3f4f6;}"
        "section{margin-bottom:2rem;}"
        "h1,h2,h3{color:#111827;}"
        "</style>"
        "</head>"
        "<body>"
        f"<h1>Evaluation Report: {escape(report.benchmark_name)}</h1>"
        f"<p><strong>Version:</strong> {escape(report.benchmark_version)}</p>"
        f"<p><strong>Generated:</strong> {escape(report.timestamp)}</p>"
        f"<p><strong>Cases evaluated:</strong> {len(report.case_results)}</p>"
        "<section>"
        "<h2>Aggregate Metrics</h2>"
        "<table>"
        "<thead><tr><th>Metric</th><th>Mean Score</th><th>Pass Rate</th><th>Count</th></tr></thead>"
        f"<tbody>{''.join(aggregate_rows)}</tbody>"
        "</table>"
        "</section>"
        f"{calibration_block}"
        "<section><h2>Per-Case Results</h2>"
        f"{''.join(case_sections)}"
        "</section>"
        "</body></html>"
    )
