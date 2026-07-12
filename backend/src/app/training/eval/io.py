"""Load benchmark datasets and write evaluation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.training.eval.models import BenchmarkCase, BenchmarkDataset


def load_benchmark_dataset(path: str | Path) -> BenchmarkDataset:
    """Load a benchmark dataset from JSON or JSONL."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Benchmark file is empty: {file_path}")

    if file_path.suffix.lower() == ".jsonl":
        return _load_jsonl_dataset(text, default_name=file_path.stem)

    data = json.loads(text)
    if isinstance(data, list):
        return BenchmarkDataset(
            name=file_path.stem,
            version="1.0",
            cases=[BenchmarkCase.from_dict(item) for item in data if isinstance(item, dict)],
        )
    if isinstance(data, dict):
        return BenchmarkDataset.from_dict(data)

    raise ValueError(f"Unsupported benchmark format: {file_path}")


def _load_jsonl_dataset(text: str, *, default_name: str) -> BenchmarkDataset:
    cases: list[BenchmarkCase] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            cases.append(BenchmarkCase.from_dict(payload))
    return BenchmarkDataset(name=default_name, version="1.0", cases=cases)


def write_json_report(report_data: dict[str, Any], path: str | Path) -> None:
    """Write structured evaluation report as JSON."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown_report(markdown: str, path: str | Path) -> None:
    """Write markdown evaluation report."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(markdown, encoding="utf-8")


def write_html_report(html: str, path: str | Path) -> None:
    """Write HTML evaluation report."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(html, encoding="utf-8")
