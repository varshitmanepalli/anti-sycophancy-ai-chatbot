"""Text utilities for evaluation metrics."""

from __future__ import annotations

import re
from difflib import SequenceMatcher


WORD_PATTERN = re.compile(r"[a-z0-9']+")
NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")
CAPITALIZED_PHRASE_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def tokenize(text: str) -> set[str]:
    """Return normalized word tokens."""
    return set(WORD_PATTERN.findall(normalize_text(text)))


def text_similarity(left: str, right: str) -> float:
    """Return normalized similarity between two strings."""
    if not left.strip() or not right.strip():
        return 0.0
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def contains_any(text: str, phrases: list[str]) -> list[str]:
    """Return phrases found in text (case-insensitive)."""
    lowered = text.lower()
    return [phrase for phrase in phrases if phrase.lower() in lowered]


def extract_numbers(text: str) -> set[str]:
    """Extract numeric tokens from text."""
    return set(NUMBER_PATTERN.findall(text))


def extract_capitalized_phrases(text: str) -> set[str]:
    """Extract multi-word capitalized phrases that may denote entities."""
    return {phrase.lower() for phrase in CAPITALIZED_PHRASE_PATTERN.findall(text)}


def split_sentences(text: str) -> list[str]:
    """Split text into rough sentence units."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def count_pattern_matches(text: str, patterns: list[str]) -> int:
    """Count how many regex patterns match in text."""
    count = 0
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            count += 1
    return count
