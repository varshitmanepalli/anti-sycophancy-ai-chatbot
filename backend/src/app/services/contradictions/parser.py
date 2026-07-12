"""Parse contradiction detection JSON from LLM output."""

import json
import re
from typing import Any
from uuid import UUID

from app.domain.contradiction_check import ContradictionCheckResult, DetectedContradiction
from app.domain.memory import ContradictionSeverity, MemorySourceType
from app.logging.setup import get_logger

logger = get_logger(__name__)

_VALID_SEVERITIES = {s.value for s in ContradictionSeverity}
_VALID_SOURCES = {s.value for s in MemorySourceType}
_SOURCE_ALIASES = {
    "facts": MemorySourceType.FACT,
    "fact": MemorySourceType.FACT,
    "opinions": MemorySourceType.OPINION,
    "opinion": MemorySourceType.OPINION,
    "preference": MemorySourceType.OPINION,
    "preferences": MemorySourceType.OPINION,
    "goals": MemorySourceType.GOAL,
    "goal": MemorySourceType.GOAL,
}


class ContradictionCheckParser:
    """Parse raw LLM text into a validated ``ContradictionCheckResult``."""

    def parse(self, raw: str) -> ContradictionCheckResult:
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
                logger.warning("Failed to parse contradiction JSON: %s", exc)

        logger.warning("No valid JSON found in contradiction check output")
        return {}

    def normalize(self, data: dict[str, Any]) -> ContradictionCheckResult:
        contradictions = self._parse_contradictions(data.get("contradictions", []))
        clarification = str(
            data.get("clarification_question", data.get("primary_clarification_question", ""))
        ).strip()

        if not clarification and contradictions:
            clarification = contradictions[0].clarification_question

        return ContradictionCheckResult(
            contradictions=contradictions,
            clarification_question=clarification or None,
            summary=str(data.get("summary", "")).strip(),
        )

    def _parse_contradictions(self, items: Any) -> list[DetectedContradiction]:
        if not isinstance(items, list):
            return []

        parsed: list[DetectedContradiction] = []
        for item in items:
            contradiction = self._parse_single(item)
            if contradiction is not None:
                parsed.append(contradiction)
        return parsed

    def _parse_single(self, item: Any) -> DetectedContradiction | None:
        if not isinstance(item, dict):
            return None

        memory_statement = str(
            item.get("memory_statement", item.get("statement_a", ""))
        ).strip()
        new_statement = str(
            item.get("new_statement", item.get("statement_b", ""))
        ).strip()
        description = str(item.get("description", "")).strip()
        clarification = str(item.get("clarification_question", "")).strip()

        if not memory_statement or not new_statement:
            return None

        if not description:
            description = "Potential contradiction between stored memory and new statement."

        if not clarification:
            clarification = (
                "Can you clarify whether your earlier statement or what you just said "
                "reflects your current situation?"
            )

        return DetectedContradiction(
            memory_statement=memory_statement,
            new_statement=new_statement,
            description=description,
            clarification_question=clarification,
            severity=self._resolve_severity(item.get("severity")),
            memory_source=self._resolve_source(item.get("memory_source")),
            memory_source_id=self._resolve_source_id(item.get("memory_source_id")),
            confidence=self._clamp_confidence(item.get("confidence", 0.5)),
        )

    @staticmethod
    def _resolve_severity(raw: Any) -> ContradictionSeverity:
        if raw is None:
            return ContradictionSeverity.MEDIUM
        key = str(raw).lower().strip()
        if key in _VALID_SEVERITIES:
            return ContradictionSeverity(key)
        return ContradictionSeverity.MEDIUM

    @staticmethod
    def _resolve_source(raw: Any) -> MemorySourceType | None:
        if raw is None:
            return None
        key = str(raw).lower().strip()
        if key in _VALID_SOURCES:
            return MemorySourceType(key)
        if key in _SOURCE_ALIASES:
            return _SOURCE_ALIASES[key]
        return None

    @staticmethod
    def _resolve_source_id(raw: Any) -> str | None:
        if raw is None:
            return None
        value = str(raw).strip()
        if not value:
            return None
        try:
            UUID(value)
            return value
        except ValueError:
            return None

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def empty() -> ContradictionCheckResult:
        return ContradictionCheckResult(summary="No contradictions detected.")
