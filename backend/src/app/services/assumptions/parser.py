"""Parse assumption detection JSON from LLM output."""

import json
import re
from typing import Any

from app.domain.assumptions import AssumptionDetectionResult, DetectedIssue
from app.logging.setup import get_logger

logger = get_logger(__name__)

_ISSUE_KEYS = (
    "unsupported_assumptions",
    "emotional_reasoning",
    "confirmation_bias",
    "mind_reading",
    "overconfidence",
)

_VALID_SEVERITIES = {"low", "medium", "high"}


class AssumptionDetectionParser:
    """Parse raw LLM text into a validated ``AssumptionDetectionResult``."""

    def parse(self, raw: str) -> AssumptionDetectionResult:
        data = self.extract_json(raw)
        return self.normalize(data)

    @staticmethod
    def extract_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1)

        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                parsed = json.loads(brace_match.group())
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse assumption detection JSON: %s", exc)

        logger.warning("No valid JSON found in assumption detection output")
        return {}

    def normalize(self, data: dict[str, Any]) -> AssumptionDetectionResult:
        return AssumptionDetectionResult(
            unsupported_assumptions=self._parse_issues(data.get("unsupported_assumptions", [])),
            emotional_reasoning=self._parse_issues(data.get("emotional_reasoning", [])),
            confirmation_bias=self._parse_issues(data.get("confirmation_bias", [])),
            mind_reading=self._parse_issues(data.get("mind_reading", [])),
            overconfidence=self._parse_issues(data.get("overconfidence", [])),
            summary=str(data.get("summary", "")).strip(),
        )

    def _parse_issues(self, items: Any) -> list[DetectedIssue]:
        if not isinstance(items, list):
            return []
        parsed: list[DetectedIssue] = []
        for item in items:
            issue = self._parse_single(item)
            if issue is not None:
                parsed.append(issue)
        return parsed

    @staticmethod
    def _parse_single(item: Any) -> DetectedIssue | None:
        if isinstance(item, str):
            text = item.strip()
            return DetectedIssue(text=text) if text else None

        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        confidence = AssumptionDetectionParser._clamp_confidence(item.get("confidence", 1.0))
        quote = item.get("quote")
        quote_str = str(quote).strip() if quote is not None else None

        severity = item.get("severity")
        severity_str = None
        if severity is not None:
            s = str(severity).lower().strip()
            if s in _VALID_SEVERITIES:
                severity_str = s

        return DetectedIssue(
            text=text,
            confidence=confidence,
            quote=quote_str,
            severity=severity_str,
        )

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 1.0
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def empty() -> AssumptionDetectionResult:
        return AssumptionDetectionResult()
