"""Domain interfaces (ports).

Abstract protocols that infrastructure adapters must implement. Keeps the
domain and service layers decoupled from vLLM, SQLAlchemy, etc.
"""

from app.domain.memory_interfaces import (
    ContradictionRepository,
    ConversationRepository,
    MemoryRepository,
    UserFactRepository,
    UserGoalRepository,
    UserOpinionRepository,
)
from app.domain.llm_interface import LLMProvider

__all__ = [
    "LLMProvider",
    "ConversationRepository",
    "UserFactRepository",
    "UserOpinionRepository",
    "UserGoalRepository",
    "ContradictionRepository",
    "MemoryRepository",
]
