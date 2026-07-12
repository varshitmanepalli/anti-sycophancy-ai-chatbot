"""Format stored memory and orchestrate contradiction checking."""

from app.database.repositories.memory_repository import SQLMemoryRepository
from app.domain.contradiction_check import ContradictionCheckResult
from app.domain.memory import ConversationMemory
from app.services.contradictions.detector import ContradictionDetector
from app.logging.setup import get_logger

logger = get_logger(__name__)


class MemoryContradictionChecker:
    """Load user memory, detect contradictions, and optionally persist them."""

    def __init__(
        self,
        detector: ContradictionDetector,
        memory_repository: SQLMemoryRepository,
    ) -> None:
        self._detector = detector
        self._memory = memory_repository

    async def check(
        self,
        user_id: str,
        message: str,
    ) -> ContradictionCheckResult:
        """Compare *message* against the user's stored memory."""
        memory = await self._memory.load_user_memory(user_id)
        memory_context = self.format_memory_context(memory)
        result = await self._detector.detect(message, memory_context=memory_context)

        logger.info(
            "Contradiction check user=%s found=%d",
            user_id,
            len(result.contradictions),
        )
        return result

    @staticmethod
    def format_memory_context(memory: ConversationMemory) -> str:
        """Render stored memory for the contradiction prompt."""
        parts: list[str] = []

        if memory.facts:
            parts.append("Stored facts:")
            for fact in memory.facts:
                category = fact.category or "fact"
                parts.append(f"- [{category}] {fact.content} (id: {fact.id})")

        if memory.opinions:
            parts.append("Stored opinions/preferences:")
            for opinion in memory.opinions:
                parts.append(
                    f"- [{opinion.topic}] {opinion.opinion} (id: {opinion.id})"
                )

        if memory.goals:
            parts.append("Stored goals:")
            for goal in memory.goals:
                parts.append(f"- {goal.content} (id: {goal.id})")

        if not parts:
            return "No stored long-term memory for this user."

        return "\n".join(parts)
