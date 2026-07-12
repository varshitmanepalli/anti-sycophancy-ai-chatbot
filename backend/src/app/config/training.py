"""Training and evaluation configuration separate from runtime app settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.training.constants import DEFAULT_METRIC_NAMES

ReportFormat = Literal["json", "md", "html"]


def _default_sft_instruction() -> str:
    from app.training.sft.templates import DEFAULT_INSTRUCTION

    return DEFAULT_INSTRUCTION


class TrainingSettings(BaseSettings):
    """Configuration for SFT dataset generation and benchmark evaluation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="training_",
    )

    # SFT dataset generation
    sft_output_dir: Path = Path("data/sft")
    sft_val_ratio: float = Field(default=0.1, ge=0.0, le=1.0)
    sft_seed: int = 42
    sft_instruction: str = Field(default_factory=_default_sft_instruction)
    sft_include_metadata: bool = False

    # Benchmark evaluation
    eval_output_dir: Path = Path("data/eval_reports")
    eval_report_formats: list[ReportFormat] = Field(
        default_factory=lambda: ["json", "md", "html"]
    )
    eval_metrics: list[str] = Field(default_factory=lambda: list(DEFAULT_METRIC_NAMES))
    eval_calibration_bins: int = Field(default=10, ge=2, le=100)
    eval_calibration_pass_threshold: float = Field(default=0.25, ge=0.0, le=1.0)


@lru_cache
def get_training_settings() -> TrainingSettings:
    """Return cached training settings for CLI and pipeline use."""
    return TrainingSettings()
