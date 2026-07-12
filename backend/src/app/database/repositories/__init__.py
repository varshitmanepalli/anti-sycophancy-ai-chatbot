"""Database repositories — data access objects."""

from app.database.repositories.base import BaseRepository
from app.database.repositories.conversation_repository import SQLConversationRepository
from app.database.repositories.contradiction_repository import SQLContradictionRepository
from app.database.repositories.memory_repository import SQLMemoryRepository
from app.database.repositories.user_fact_repository import SQLUserFactRepository
from app.database.repositories.user_goal_repository import SQLUserGoalRepository
from app.database.repositories.user_opinion_repository import SQLUserOpinionRepository

__all__ = [
    "BaseRepository",
    "SQLConversationRepository",
    "SQLUserFactRepository",
    "SQLUserOpinionRepository",
    "SQLUserGoalRepository",
    "SQLContradictionRepository",
    "SQLMemoryRepository",
]
