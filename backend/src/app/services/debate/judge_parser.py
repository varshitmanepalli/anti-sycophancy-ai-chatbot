"""Parse structured JSON verdicts from Judge Agent output."""

import json
import re
from typing import Any

from app.domain.debate import JudgedItem, JudgeVerdict
from app.logging.setup import get_logger

logger = get_logger(__name__)

_VERDICT_KEYS = ("facts", "assumptions", "evidence", "unknowns")
_VALID_SOURCES = {
    "support",
    "opponent",
    "fact_checker",
    "memory",
    "synthesis",
}


class JudgeVerdictParser:
    """Extract a ``JudgeVerdict`` from raw LLM text."""

    def parse(self, raw: str) -> JudgeVerdict:
        data = self.extract_json(raw)
        return self.normalize(data, raw_output=raw.strip())

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
                logger.warning("Failed to parse judge JSON: %s", exc)

        return {}

    def normalize(self, data: dict[str, Any], *, raw_output: str = "") -> JudgeVerdict:
        final_conclusion = str(
            data.get("final_conclusion", data.get("verdict", ""))
        ).strip()

        if not final_conclusion and raw_output and not data:
            final_conclusion = raw_output[:500]

        return JudgeVerdict(
            facts=self._parse_items(data.get("facts", [])),
            assumptions=self._parse_items(data.get("assumptions", [])),
            evidence=self._parse_items(data.get("evidence", [])),
            unknowns=self._parse_items(data.get("unknowns", [])),
            final_conclusion=final_conclusion,
            confidence=self._clamp_score(data.get("confidence", 0.5)),
            raw_output=raw_output,
        )

    def _parse_items(self, items: Any) -> list[JudgedItem]:
        if not isinstance(items, list):
            return []

        parsed: list[JudgedItem] = []
        for item in items:
            judged = self._parse_single_item(item)
            if judged is not None:
                parsed.append(judged)
        return parsed

    def _parse_single_item(self, item: Any) -> JudgedItem | None:
        if isinstance(item, str):
            text = item.strip()
            return JudgedItem(text=text) if text else None

        if not isinstance(item, dict):
            return None

        text = str(item.get("text", "")).strip()
        if not text:
            return None

        source = item.get("source")
        source_str = str(source).strip().lower() if source is not None else None
        if source_str == "" or source_str == "null":
            source_str = None
        elif source_str and source_str not in _VALID_SOURCES:
            source_str = None

        return JudgedItem(
            text=text,
            source=source_str,
            confidence=self._clamp_score(item.get("confidence", 0.5)),
        )

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, score))
