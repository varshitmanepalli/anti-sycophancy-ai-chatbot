"""In-memory conversation store.

Simple dict-backed store for development and testing. Production should
use ``DatabaseMemoryStore`` backed by PostgreSQL.
"""

from uuid import UUID

from app.memory.base import BaseMemoryStore


class InMemoryStore(BaseMemoryStore):
    """Thread-unsafe in-memory conversation history."""

    def __init__(self) -> None:
        self._store: dict[UUID, list[dict[str, str]]] = {}

    async def get_history(
        self,
        conversation_id: UUID,
        max_turns: int | None = None,
    ) -> list[dict[str, str]]:
        history = self._store.get(conversation_id, [])
        if max_turns is not None:
            return history[-max_turns:]
        return history

    async def append(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> None:
        self._store.setdefault(conversation_id, []).append(
            {"role": role, "content": content}
        )

    async def clear(self, conversation_id: UUID) -> None:
        self._store.pop(conversation_id, None)
