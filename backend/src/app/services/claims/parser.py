"""Parse and validate claim extraction JSON from model output."""

import json
import re
from typing import Any

from app.domain.claims import ClaimExtractionResult, ExtractedItem
from app.logging.setup import get_logger

logger = get_logger(__name__)

_EXTRACTION_KEYS = (
    "main_claims",
    "supporting_claims",
    "hidden_assumptions",
    "evidence_provided",
    "unknown_information",
)


class ClaimExtractionParser:
    """Parse raw LLM text into a validated ``ClaimExtractionResult``."""

    def parse(self, raw: str) -> ClaimExtractionResult:
        """Extract and normalize claim extraction JSON."""
        data = self.extract_json(raw)
        return self.normalize(data)

    @staticmethod
    def extract_json(raw: str) -> dict[str, Any]:
        """Pull a JSON object from model output, tolerating markdown fences."""
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
                logger.warning("Failed to parse claim extraction JSON: %s", exc)

        logger.warning("No valid JSON found in claim extraction output")
        return {}

    def normalize(self, data: dict[str, Any]) -> ClaimExtractionResult:
        """Map raw dict keys to a validated ``ClaimExtractionResult``."""
        return ClaimExtractionResult(
            main_claims=self._parse_items(data.get("main_claims", [])),
            supporting_claims=self._parse_items(data.get("supporting_claims", [])),
            hidden_assumptions=self._parse_items(data.get("hidden_assumptions", [])),
            evidence_provided=self._parse_items(
                data.get("evidence_provided", []), include_source=True
            ),
            unknown_information=self._parse_items(data.get("unknown_information", [])),
        )

    def _parse_items(
        self,
        items: Any,
        *,
        include_source: bool = False,
    ) -> list[ExtractedItem]:
        if not isinstance(items, list):
            return []

        parsed: list[ExtractedItem] = []
        for item in items:
            extracted = self._parse_single_item(item, include_source=include_source)
            if extracted is not None:
                parsed.append(extracted)
        return parsed

    @staticmethod
    def _parse_single_item(item: Any, *, include_source: bool) -> ExtractedItem | None:
        if isinstance(item, str):
            text = item.strip()
            if text:
                return ExtractedItem(text=text)
            return None

        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        confidence = ClaimExtractionParser._clamp_confidence(item.get("confidence", 1.0))
        source = None
        if include_source:
            raw_source = item.get("source")
            if raw_source is not None:
                source = str(raw_source).strip() or None

        return ExtractedItem(text=text, confidence=confidence, source=source)

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 1.0
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def empty() -> ClaimExtractionResult:
        """Return an empty result for fallback scenarios."""
        return ClaimExtractionResult()
