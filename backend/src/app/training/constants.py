"""Shared constants for training and evaluation modules."""

DEFAULT_METRIC_NAMES: tuple[str, ...] = (
    "agreement_rate",
    "hallucination_rate",
    "evidence_usage",
    "logical_consistency",
    "bias_detection",
    "confidence_calibration",
)
