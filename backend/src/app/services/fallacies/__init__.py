"""Logical fallacy detection services."""

from app.services.fallacies.detector import LogicalFallacyDetector
from app.services.fallacies.parser import FallacyDetectionParser

__all__ = ["LogicalFallacyDetector", "FallacyDetectionParser"]
