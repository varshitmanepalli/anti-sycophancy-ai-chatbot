"""Aggregated memory repository facade."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.conversation_repository import SQLConversationRepository
from app.database.repositories.contradiction_repository import SQLContradictionRepository
from app.database.repositories.user_fact_repository import SQLUserFactRepository
from app.database.repositories.user_goal_repository import SQLUserGoalRepository
from app.database.repositories.user_opinion_repository import SQLUserOpinionRepository
from app.domain.memory import ConversationMemory


class SQLMemoryRepository:
    """Loads aggregated conversation memory across all memory tables."""

    def __init__(self, session: AsyncSession) -> None:
        self._conversations = SQLConversationRepository(session)
        self._facts = SQLUserFactRepository(session)
        self._opinions = SQLUserOpinionRepository(session)
        self._goals = SQLUserGoalRepository(session)
        self._contradictions = SQLContradictionRepository(session)

    @property
    def facts(self) -> SQLUserFactRepository:
        return self._facts

    @property
    def opinions(self) -> SQLUserOpinionRepository:
        return self._opinions

    @property
    def goals(self) -> SQLUserGoalRepository:
        return self._goals

    @property
    def contradictions(self) -> SQLContradictionRepository:
        return self._contradictions

    @property
    def conversations(self) -> SQLConversationRepository:
        return self._conversations

    async def load_conversation_memory(
        self,
        *,
        user_id: str,
        conversation_id: UUID,
        message_limit: int = 50,
    ) -> ConversationMemory:
        """Load all memory layers for a specific conversation."""
        messages = await self._conversations.get_messages(
            conversation_id, limit=message_limit
        )
        return ConversationMemory(
            messages=[{"role": m.role.value, "content": m.content} for m in messages],
            facts=await self._facts.list_by_conversation(conversation_id),
            opinions=await self._opinions.list_by_conversation(conversation_id),
            goals=await self._goals.list_by_conversation(conversation_id),
            contradictions=await self._contradictions.list_by_conversation(conversation_id),
        )

    async def load_user_memory(
        self,
        user_id: str,
        *,
        message_limit: int = 50,
    ) -> ConversationMemory:
        """Load user-level memory across all conversations."""
        return ConversationMemory(
            facts=await self._facts.list_by_user(user_id, limit=message_limit),
            opinions=await self._opinions.list_by_user(user_id, limit=message_limit),
            goals=await self._goals.list_by_user(user_id, limit=message_limit),
            contradictions=await self._contradictions.list_by_user(
                user_id, limit=message_limit
            ),
        )
