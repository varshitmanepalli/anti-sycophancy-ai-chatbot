"""Parse structured JSON from Support Agent output."""

import json
import re
from typing import Any

from app.domain.support_agent import SupportAgentResult, SupportingArgument
from app.logging.setup import get_logger

logger = get_logger(__name__)

_VALID_SOURCES = {
    "user_message",
    "user_facts",
    "conversation_summary",
    "known_facts",
    "inference",
}


class SupportAgentParser:
    """Parse raw LLM text into a validated ``SupportAgentResult``."""

    def parse(self, raw: str) -> SupportAgentResult:
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
                logger.warning("Failed to parse support agent JSON: %s", exc)

        logger.warning("No valid JSON found in support agent output")
        return {}

    def normalize(self, data: dict[str, Any]) -> SupportAgentResult:
        return SupportAgentResult(
            arguments=self._parse_arguments(data.get("arguments", [])),
            position_summary=str(data.get("position_summary", "")).strip(),
            summary=str(data.get("summary", "")).strip(),
            missing_information=self._parse_strings(data.get("missing_information", [])),
        )

    def _parse_arguments(self, items: Any) -> list[SupportingArgument]:
        if not isinstance(items, list):
            return []

        parsed: list[SupportingArgument] = []
        for item in items:
            argument = self._parse_single_argument(item)
            if argument is not None:
                parsed.append(argument)
        return parsed

    def _parse_single_argument(self, item: Any) -> SupportingArgument | None:
        if isinstance(item, str):
            text = item.strip()
            return SupportingArgument(text=text) if text else None

        if not isinstance(item, dict):
            return None

        text = str(item.get("text", item.get("argument", ""))).strip()
        if not text:
            return None

        evidence = item.get("evidence")
        evidence_str = str(evidence).strip() if evidence is not None else None
        if evidence_str == "":
            evidence_str = None

        source = item.get("source")
        source_str = str(source).strip().lower().replace("-", "_") if source else None
        if source_str and source_str not in _VALID_SOURCES:
            source_str = None

        return SupportingArgument(
            text=text,
            evidence=evidence_str,
            confidence=self._clamp_confidence(item.get("confidence", 0.5)),
            source=source_str,
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
    def empty() -> SupportAgentResult:
        return SupportAgentResult()
