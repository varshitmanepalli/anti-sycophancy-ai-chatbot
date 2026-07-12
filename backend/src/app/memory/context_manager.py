"""Context window manager.

Trims conversation history to fit within the model's token budget and
applies summarization strategies when history exceeds the limit.
"""

from uuid import UUID

from app.memory.base import BaseMemoryStore


class ContextManager:
    """Manages what prior turns are included in each LLM request."""

    def __init__(
        self,
        memory_store: BaseMemoryStore,
        max_turns: int = 20,
        max_tokens: int | None = None,
    ) -> None:
        self._store = memory_store
        self._max_turns = max_turns
        self._max_tokens = max_tokens

    async def build_context(self, conversation_id: UUID) -> list[dict[str, str]]:
        """Return history trimmed to fit context constraints."""
        history = await self._store.get_history(
            conversation_id, max_turns=self._max_turns
        )

        if self._max_tokens is not None:
            # TODO: implement token-budget trimming
            pass

        return history
