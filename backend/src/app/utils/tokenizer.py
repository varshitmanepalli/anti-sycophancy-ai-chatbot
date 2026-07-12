"""Token counting utilities for context window management."""

# TODO: integrate tiktoken or the model's tokenizer for accurate counts.


def estimate_token_count(text: str) -> int:
    """Rough token estimate (4 chars ≈ 1 token). Replace with real tokenizer."""
    return len(text) // 4
