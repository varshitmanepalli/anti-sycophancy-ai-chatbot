"""Domain types for long-term memory extraction."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MemoryCategory(StrEnum):
    """Categories of long-term user information."""

    CAREER = "career"
    PROGRAMMING_LANGUAGE = "programming_language"
    GOALS = "goals"
    PREFERENCES = "preferences"
    PROJECTS = "projects"


ALL_MEMORY_CATEGORIES: tuple[MemoryCategory, ...] = tuple(MemoryCategory)


@dataclass
class ExtractedMemoryItem:
    """A single piece of long-term user information."""

    content: str
    category: MemoryCategory
    confidence: float = 0.8
    topic: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "content": self.content,
            "category": self.category.value,
            "confidence": round(self.confidence, 4),
        }
        if self.topic is not None:
            result["topic"] = self.topic
        return result


@dataclass
class MemoryExtractionResult:
    """Structured long-term memory extracted from a message."""

    career: list[ExtractedMemoryItem] = field(default_factory=list)
    programming_language: list[ExtractedMemoryItem] = field(default_factory=list)
    goals: list[ExtractedMemoryItem] = field(default_factory=list)
    preferences: list[ExtractedMemoryItem] = field(default_factory=list)
    projects: list[ExtractedMemoryItem] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "career": [item.to_dict() for item in self.career],
            "programming_language": [item.to_dict() for item in self.programming_language],
            "goals": [item.to_dict() for item in self.goals],
            "preferences": [item.to_dict() for item in self.preferences],
            "projects": [item.to_dict() for item in self.projects],
            "summary": self.summary,
        }

    @property
    def is_empty(self) -> bool:
        return not any(
            (
                self.career,
                self.programming_language,
                self.goals,
                self.preferences,
                self.projects,
            )
        )

    @property
    def total_items(self) -> int:
        return (
            len(self.career)
            + len(self.programming_language)
            + len(self.goals)
            + len(self.preferences)
            + len(self.projects)
        )

    def items_for_category(self, category: MemoryCategory) -> list[ExtractedMemoryItem]:
        return getattr(self, category.value)


@dataclass
class StoredMemoryCounts:
    """Counts of items persisted per storage table."""

    facts: int = 0
    goals: int = 0
    opinions: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "facts": self.facts,
            "goals": self.goals,
            "opinions": self.opinions,
        }


@dataclass
class MemoryStoreResult:
    """Result of persisting extracted memory."""

    extracted: MemoryExtractionResult
    stored: StoredMemoryCounts

    def to_dict(self) -> dict[str, Any]:
        return {
            "extracted": self.extracted.to_dict(),
            "stored": self.stored.to_dict(),
        }
