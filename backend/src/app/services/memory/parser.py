"""Parse memory extraction JSON from LLM output."""

import json
import re
from typing import Any

from app.domain.memory_extraction import (
    ALL_MEMORY_CATEGORIES,
    ExtractedMemoryItem,
    MemoryCategory,
    MemoryExtractionResult,
)
from app.logging.setup import get_logger

logger = get_logger(__name__)

_CATEGORY_ALIASES: dict[str, MemoryCategory] = {
    "career": MemoryCategory.CAREER,
    "job": MemoryCategory.CAREER,
    "programming_language": MemoryCategory.PROGRAMMING_LANGUAGE,
    "programming language": MemoryCategory.PROGRAMMING_LANGUAGE,
    "language": MemoryCategory.PROGRAMMING_LANGUAGE,
    "goals": MemoryCategory.GOALS,
    "goal": MemoryCategory.GOALS,
    "preferences": MemoryCategory.PREFERENCES,
    "preference": MemoryCategory.PREFERENCES,
    "projects": MemoryCategory.PROJECTS,
    "project": MemoryCategory.PROJECTS,
}


class MemoryExtractionParser:
    """Parse raw LLM text into a validated ``MemoryExtractionResult``."""

    def parse(self, raw: str) -> MemoryExtractionResult:
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
                logger.warning("Failed to parse memory extraction JSON: %s", exc)

        logger.warning("No valid JSON found in memory extraction output")
        return {}

    def normalize(self, data: dict[str, Any]) -> MemoryExtractionResult:
        buckets: dict[str, list[ExtractedMemoryItem]] = {
            category.value: [] for category in ALL_MEMORY_CATEGORIES
        }

        for category in ALL_MEMORY_CATEGORIES:
            items = data.get(category.value, [])
            buckets[category.value] = self._parse_category_items(items, category)

        return MemoryExtractionResult(
            career=buckets["career"],
            programming_language=buckets["programming_language"],
            goals=buckets["goals"],
            preferences=buckets["preferences"],
            projects=buckets["projects"],
            summary=str(data.get("summary", "")).strip(),
        )

    def _parse_category_items(
        self,
        items: Any,
        category: MemoryCategory,
    ) -> list[ExtractedMemoryItem]:
        if not isinstance(items, list):
            return []

        parsed: list[ExtractedMemoryItem] = []
        for item in items:
            memory_item = self._parse_single_item(item, category)
            if memory_item is not None:
                parsed.append(memory_item)
        return parsed

    def _parse_single_item(
        self,
        item: Any,
        default_category: MemoryCategory,
    ) -> ExtractedMemoryItem | None:
        if isinstance(item, str):
            content = item.strip()
            if content:
                return ExtractedMemoryItem(content=content, category=default_category)
            return None

        if not isinstance(item, dict):
            return None

        content = str(item.get("content", item.get("text", ""))).strip()
        if not content:
            return None

        category = self._resolve_category(item.get("category"), default_category)
        topic = item.get("topic")
        topic_str = str(topic).strip() if topic is not None else None
        if topic_str == "":
            topic_str = None

        return ExtractedMemoryItem(
            content=content,
            category=category,
            confidence=self._clamp_confidence(item.get("confidence", 0.8)),
            topic=topic_str,
        )

    @staticmethod
    def _resolve_category(raw: Any, default: MemoryCategory) -> MemoryCategory:
        if raw is None:
            return default
        key = str(raw).lower().strip().replace("-", "_")
        if key in {c.value for c in MemoryCategory}:
            return MemoryCategory(key)
        if key in _CATEGORY_ALIASES:
            return _CATEGORY_ALIASES[key]
        return default

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.8
        return max(0.0, min(1.0, confidence))

    @staticmethod
    def empty() -> MemoryExtractionResult:
        return MemoryExtractionResult()
