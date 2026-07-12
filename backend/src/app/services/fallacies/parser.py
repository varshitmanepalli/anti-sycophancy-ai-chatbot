"""Parse logical fallacy detection JSON from LLM output."""

import json
import re
from typing import Any

from app.domain.fallacies import (
    DetectedFallacy,
    FallacyDetectionResult,
    FallacyType,
)
from app.logging.setup import get_logger

logger = get_logger(__name__)

_VALID_FALLACIES = {f.value for f in FallacyType}
# Aliases the model might use
_FALLACY_ALIASES: dict[str, FallacyType] = {
    "hasty generalization": FallacyType.HASTY_GENERALIZATION,
    "false dilemma": FallacyType.FALSE_DILEMMA,
    "either or": FallacyType.FALSE_DILEMMA,
    "either-or": FallacyType.FALSE_DILEMMA,
    "slippery slope": FallacyType.SLIPPERY_SLOPE,
    "appeal to emotion": FallacyType.APPEAL_TO_EMOTION,
    "appeal to popularity": FallacyType.APPEAL_TO_POPULARITY,
    "bandwagon": FallacyType.APPEAL_TO_POPULARITY,
    "ad populum": FallacyType.APPEAL_TO_POPULARITY,
    "circular reasoning": FallacyType.CIRCULAR_REASONING,
    "begging the question": FallacyType.CIRCULAR_REASONING,
    "confirmation bias": FallacyType.CONFIRMATION_BIAS,
    "cherry picking": FallacyType.CONFIRMATION_BIAS,
    "post hoc": FallacyType.POST_HOC,
    "post_hoc_ergo_propter_hoc": FallacyType.POST_HOC,
    "correlation causation": FallacyType.POST_HOC,
}


class FallacyDetectionParser:
    """Parse raw LLM text into a validated ``FallacyDetectionResult``."""

    def parse(self, raw: str) -> FallacyDetectionResult:
        data = self.extract_json(raw)
        return self.normalize(data)

    @staticmethod
    def extract_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                return {"fallacies": parsed}
        except json.JSONDecodeError:
            pass

        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                parsed = json.loads(brace_match.group())
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse fallacy detection JSON: %s", exc)

        array_match = re.search(r"\[.*\]", text, re.DOTALL)
        if array_match:
            try:
                parsed = json.loads(array_match.group())
                if isinstance(parsed, list):
                    return {"fallacies": parsed}
            except json.JSONDecodeError:
                pass

        logger.warning("No valid JSON found in fallacy detection output")
        return {}

    def normalize(self, data: dict[str, Any]) -> FallacyDetectionResult:
        items = data.get("fallacies", [])
        return FallacyDetectionResult(
            fallacies=self._parse_fallacies(items),
            summary=str(data.get("summary", "")).strip(),
        )

    def _parse_fallacies(self, items: Any) -> list[DetectedFallacy]:
        if not isinstance(items, list):
            return []
        parsed: list[DetectedFallacy] = []
        for item in items:
            fallacy = self._parse_single(item)
            if fallacy is not None:
                parsed.append(fallacy)
        return parsed

    def _parse_single(self, item: Any) -> DetectedFallacy | None:
        if not isinstance(item, dict):
            return None

        fallacy_type = self._resolve_fallacy_type(item.get("fallacy", ""))
        if fallacy_type is None:
            return None

        explanation = str(item.get("explanation", "")).strip()
        if not explanation:
            return None

        confidence = self._clamp_confidence(item.get("confidence", 0.5))
        quote = item.get("quote")
        quote_str = str(quote).strip() if quote is not None else None

        return DetectedFallacy(
            fallacy=fallacy_type,
            confidence=confidence,
            explanation=explanation,
            quote=quote_str,
        )

    @staticmethod
    def _resolve_fallacy_type(raw: Any) -> FallacyType | None:
        if raw is None:
            return None
        key = str(raw).lower().strip().replace("-", " ").replace("_", " ")

        # Direct enum value match (with underscores)
        normalized = key.replace(" ", "_")
        if normalized in _VALID_FALLACIES:
            return FallacyType(normalized)

        if key in _FALLACY_ALIASES:
            return _FALLACY_ALIASES[key]

        return None

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def empty() -> FallacyDetectionResult:
        return FallacyDetectionResult()
