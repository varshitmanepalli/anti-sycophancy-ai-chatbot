"""Report rendering and persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from app.logging.setup import get_logger
from app.training.eval.io import write_html_report, write_json_report, write_markdown_report
from app.training.eval.models import EvalReport
from app.training.eval.report import render_html_report, render_markdown_report

logger = get_logger(__name__)

ReportFormat = Literal["json", "md", "html"]


@dataclass
class ReportWriter:
    """Compose report rendering with file output."""

    formats: tuple[ReportFormat, ...] = ("json", "md", "html")
    output_dir: Path = Path("data/eval_reports")
    _written_paths: list[Path] = field(default_factory=list, init=False)

    def write(self, report: EvalReport) -> list[Path]:
        """Render and persist reports for all configured formats."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._written_paths.clear()
        paths: list[Path] = []

        if "json" in self.formats:
            path = self.output_dir / "report.json"
            write_json_report(report.to_dict(), path)
            paths.append(path)
            logger.info("Wrote JSON report: %s", path)

        if "md" in self.formats:
            path = self.output_dir / "report.md"
            write_markdown_report(render_markdown_report(report), path)
            paths.append(path)
            logger.info("Wrote markdown report: %s", path)

        if "html" in self.formats:
            path = self.output_dir / "report.html"
            write_html_report(render_html_report(report), path)
            paths.append(path)
            logger.info("Wrote HTML report: %s", path)

        self._written_paths = paths
        return paths

    @property
    def written_paths(self) -> tuple[Path, ...]:
        """Return paths written during the last call."""
        return tuple(self._written_paths)
