"""General-purpose helper functions."""

import hashlib
from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(UTC)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max_length, appending suffix if trimmed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def hash_content(content: str) -> str:
    """Return a SHA-256 hex digest of the given string."""
    return hashlib.sha256(content.encode()).hexdigest()
