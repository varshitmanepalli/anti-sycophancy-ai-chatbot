"""Persist extracted memory to separate storage tables."""

from uuid import UUID

from app.database.repositories.memory_repository import SQLMemoryRepository
from app.domain.memory import UserFact, UserGoal, UserOpinion
from app.domain.memory_extraction import (
    MemoryCategory,
    MemoryExtractionResult,
    MemoryStoreResult,
    StoredMemoryCounts,
)
from app.logging.setup import get_logger

logger = get_logger(__name__)

_FACT_CATEGORIES = {
    MemoryCategory.CAREER,
    MemoryCategory.PROGRAMMING_LANGUAGE,
    MemoryCategory.PROJECTS,
}


class MemoryStore:
    """Store extracted memory items in the appropriate tables."""

    def __init__(self, memory_repository: SQLMemoryRepository) -> None:
        self._memory = memory_repository

    async def store(
        self,
        user_id: str,
        result: MemoryExtractionResult,
        *,
        conversation_id: UUID | None = None,
        message_id: UUID | None = None,
    ) -> MemoryStoreResult:
        """Persist extracted items to facts, goals, and opinions tables."""
        counts = StoredMemoryCounts()

        for category in _FACT_CATEGORIES:
            for item in result.items_for_category(category):
                await self._memory.facts.create(
                    UserFact(
                        user_id=user_id,
                        content=item.content,
                        category=category.value,
                        confidence=item.confidence,
                        conversation_id=conversation_id,
                        message_id=message_id,
                    )
                )
                counts.facts += 1

        for item in result.goals:
            await self._memory.goals.create(
                UserGoal(
                    user_id=user_id,
                    content=item.content,
                    conversation_id=conversation_id,
                )
            )
            counts.goals += 1

        for item in result.preferences:
            await self._memory.opinions.create(
                UserOpinion(
                    user_id=user_id,
                    topic=item.topic or "preference",
                    opinion=item.content,
                    confidence=item.confidence,
                    conversation_id=conversation_id,
                    message_id=message_id,
                )
            )
            counts.opinions += 1

        logger.info(
            "Stored memory for user=%s facts=%d goals=%d opinions=%d",
            user_id,
            counts.facts,
            counts.goals,
            counts.opinions,
        )
        return MemoryStoreResult(extracted=result, stored=counts)
