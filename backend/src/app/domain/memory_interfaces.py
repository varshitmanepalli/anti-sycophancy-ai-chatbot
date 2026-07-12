"""Repository ports for conversation memory persistence."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Conversation, Message
from app.domain.memory import (
    ConversationMemory,
    MemoryContradiction,
    UserFact,
    UserGoal,
    UserOpinion,
)


class ConversationRepository(Protocol):
    """Port for conversation and message persistence."""

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None: ...

    async def save(self, conversation: Conversation) -> Conversation: ...

    async def add_message(self, conversation_id: UUID, message: Message) -> Message: ...

    async def get_messages(
        self,
        conversation_id: UUID,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Message]: ...

    async def delete(self, conversation_id: UUID) -> bool: ...


class UserFactRepository(Protocol):
    """Port for user fact CRUD."""

    async def create(self, fact: UserFact) -> UserFact: ...
    async def get_by_id(self, fact_id: UUID) -> UserFact | None: ...
    async def update(self, fact: UserFact) -> UserFact: ...
    async def delete(self, fact_id: UUID, *, soft: bool = True) -> bool: ...
    async def list_by_user(
        self, user_id: str, *, active_only: bool = True, limit: int = 100, offset: int = 0
    ) -> list[UserFact]: ...
    async def list_by_conversation(
        self, conversation_id: UUID, *, active_only: bool = True
    ) -> list[UserFact]: ...


class UserOpinionRepository(Protocol):
    """Port for user opinion CRUD."""

    async def create(self, opinion: UserOpinion) -> UserOpinion: ...
    async def get_by_id(self, opinion_id: UUID) -> UserOpinion | None: ...
    async def update(self, opinion: UserOpinion) -> UserOpinion: ...
    async def delete(self, opinion_id: UUID, *, soft: bool = True) -> bool: ...
    async def list_by_user(
        self, user_id: str, *, active_only: bool = True, limit: int = 100, offset: int = 0
    ) -> list[UserOpinion]: ...
    async def list_by_conversation(
        self, conversation_id: UUID, *, active_only: bool = True
    ) -> list[UserOpinion]: ...


class UserGoalRepository(Protocol):
    """Port for user goal CRUD."""

    async def create(self, goal: UserGoal) -> UserGoal: ...
    async def get_by_id(self, goal_id: UUID) -> UserGoal | None: ...
    async def update(self, goal: UserGoal) -> UserGoal: ...
    async def delete(self, goal_id: UUID, *, soft: bool = True) -> bool: ...
    async def list_by_user(
        self, user_id: str, *, active_only: bool = True, limit: int = 100, offset: int = 0
    ) -> list[UserGoal]: ...
    async def list_by_conversation(
        self, conversation_id: UUID, *, active_only: bool = True
    ) -> list[UserGoal]: ...


class ContradictionRepository(Protocol):
    """Port for contradiction CRUD."""

    async def create(self, contradiction: MemoryContradiction) -> MemoryContradiction: ...
    async def get_by_id(self, contradiction_id: UUID) -> MemoryContradiction | None: ...
    async def update(self, contradiction: MemoryContradiction) -> MemoryContradiction: ...
    async def delete(self, contradiction_id: UUID) -> bool: ...
    async def list_by_user(
        self,
        user_id: str,
        *,
        unresolved_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MemoryContradiction]: ...
    async def list_by_conversation(
        self, conversation_id: UUID, *, unresolved_only: bool = False
    ) -> list[MemoryContradiction]: ...


class MemoryRepository(Protocol):
    """Facade port that loads aggregated memory for a conversation."""

    async def load_conversation_memory(
        self,
        *,
        user_id: str,
        conversation_id: UUID,
        message_limit: int = 50,
    ) -> ConversationMemory: ...

    async def load_user_memory(
        self,
        user_id: str,
        *,
        message_limit: int = 50,
    ) -> ConversationMemory: ...
