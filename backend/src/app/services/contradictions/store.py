"""Persist detected contradictions to the database."""

from uuid import UUID

from app.database.repositories.memory_repository import SQLMemoryRepository
from app.domain.contradiction_check import ContradictionCheckResult, DetectedContradiction
from app.domain.memory import MemoryContradiction, MemorySourceType
from app.logging.setup import get_logger

logger = get_logger(__name__)


class ContradictionStore:
    """Save detected contradictions to ``memory_contradictions``."""

    def __init__(self, memory_repository: SQLMemoryRepository) -> None:
        self._memory = memory_repository

    async def persist(
        self,
        user_id: str,
        result: ContradictionCheckResult,
        *,
        conversation_id: UUID | None = None,
    ) -> int:
        """Persist all detected contradictions. Returns count stored."""
        stored = 0
        for item in result.contradictions:
            await self._memory.contradictions.create(
                self._to_memory_contradiction(user_id, item, conversation_id)
            )
            stored += 1

        logger.debug("Persisted %d contradictions for user=%s", stored, user_id)
        return stored

    @staticmethod
    def _to_memory_contradiction(
        user_id: str,
        item: DetectedContradiction,
        conversation_id: UUID | None,
    ) -> MemoryContradiction:
        source_id = None
        if item.memory_source_id:
            try:
                source_id = UUID(item.memory_source_id)
            except ValueError:
                source_id = None

        return MemoryContradiction(
            user_id=user_id,
            conversation_id=conversation_id,
            statement_a=item.memory_statement,
            statement_b=item.new_statement,
            statement_a_source_type=item.memory_source,
            statement_a_source_id=source_id,
            statement_b_source_type=MemorySourceType.MESSAGE,
            description=item.description,
            severity=item.severity,
        )
