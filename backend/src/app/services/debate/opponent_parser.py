"""Parse structured JSON from Opposition Agent output."""

import json
import re
from typing import Any

from app.domain.opponent_agent import (
    AlternativeExplanation,
    ChallengedAssumption,
    LogicalGap,
    OpponentAgentResult,
    Weakness,
)
from app.logging.setup import get_logger

logger = get_logger(__name__)

_VALID_GAP_TYPES = {
    "missing_premise",
    "non_sequitur",
    "overgeneralization",
    "false_cause",
    "other",
}


class OpponentAgentParser:
    """Parse raw LLM text into a validated ``OpponentAgentResult``."""

    def parse(self, raw: str) -> OpponentAgentResult:
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
        except json.JSONDecodeError:
            pass

        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                parsed = json.loads(brace_match.group())
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse opponent agent JSON: %s", exc)

        logger.warning("No valid JSON found in opponent agent output")
        return {}

    def normalize(self, data: dict[str, Any]) -> OpponentAgentResult:
        return OpponentAgentResult(
            weaknesses=self._parse_weaknesses(data.get("weaknesses", [])),
            alternative_explanations=self._parse_alternatives(
                data.get("alternative_explanations", [])
            ),
            challenged_assumptions=self._parse_assumptions(
                data.get("challenged_assumptions", [])
            ),
            logical_gaps=self._parse_gaps(data.get("logical_gaps", [])),
            summary=str(data.get("summary", "")).strip(),
            missing_information=self._parse_strings(data.get("missing_information", [])),
        )

    def _parse_weaknesses(self, items: Any) -> list[Weakness]:
        if not isinstance(items, list):
            return []
        parsed: list[Weakness] = []
        for item in items:
            weakness = self._parse_weakness(item)
            if weakness is not None:
                parsed.append(weakness)
        return parsed

    def _parse_weakness(self, item: Any) -> Weakness | None:
        if isinstance(item, str):
            text = item.strip()
            return Weakness(text=text) if text else None
        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        target = item.get("target")
        target_str = str(target).strip() if target is not None else None
        if target_str == "":
            target_str = None

        return Weakness(
            text=text,
            target=target_str,
            confidence=self._clamp_confidence(item.get("confidence", 0.5)),
        )

    def _parse_alternatives(self, items: Any) -> list[AlternativeExplanation]:
        if not isinstance(items, list):
            return []
        parsed: list[AlternativeExplanation] = []
        for item in items:
            alternative = self._parse_alternative(item)
            if alternative is not None:
                parsed.append(alternative)
        return parsed

    def _parse_alternative(self, item: Any) -> AlternativeExplanation | None:
        if isinstance(item, str):
            text = item.strip()
            return AlternativeExplanation(text=text) if text else None
        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        evidence = item.get("evidence")
        evidence_str = str(evidence).strip() if evidence is not None else None
        if evidence_str == "":
            evidence_str = None

        return AlternativeExplanation(
            text=text,
            evidence=evidence_str,
            confidence=self._clamp_confidence(item.get("confidence", 0.5)),
        )

    def _parse_assumptions(self, items: Any) -> list[ChallengedAssumption]:
        if not isinstance(items, list):
            return []
        parsed: list[ChallengedAssumption] = []
        for item in items:
            assumption = self._parse_assumption(item)
            if assumption is not None:
                parsed.append(assumption)
        return parsed

    def _parse_assumption(self, item: Any) -> ChallengedAssumption | None:
        if isinstance(item, str):
            text = item.strip()
            return ChallengedAssumption(text=text) if text else None
        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        quote = item.get("quote")
        quote_str = str(quote).strip() if quote is not None else None
        if quote_str == "":
            quote_str = None

        return ChallengedAssumption(
            text=text,
            quote=quote_str,
            confidence=self._clamp_confidence(item.get("confidence", 0.5)),
        )

    def _parse_gaps(self, items: Any) -> list[LogicalGap]:
        if not isinstance(items, list):
            return []
        parsed: list[LogicalGap] = []
        for item in items:
            gap = self._parse_gap(item)
            if gap is not None:
                parsed.append(gap)
        return parsed

    def _parse_gap(self, item: Any) -> LogicalGap | None:
        if isinstance(item, str):
            text = item.strip()
            return LogicalGap(text=text) if text else None
        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        gap_type = item.get("gap_type")
        gap_type_str = str(gap_type).strip().lower().replace("-", "_") if gap_type else None
        if gap_type_str and gap_type_str not in _VALID_GAP_TYPES:
            gap_type_str = "other"

        return LogicalGap(
            text=text,
            gap_type=gap_type_str,
            confidence=self._clamp_confidence(item.get("confidence", 0.5)),
        )

    @staticmethod
    def _parse_strings(items: Any) -> list[str]:
        if not isinstance(items, list):
            return []
        return [str(item).strip() for item in items if str(item).strip()]

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def empty() -> OpponentAgentResult:
        return OpponentAgentResult()
