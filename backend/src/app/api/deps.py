"""FastAPI dependency injection.

Provides reusable ``Depends()`` callables for database sessions, service
instances, and authentication. Keeps route handlers free of wiring code.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session per request."""
    async for session in get_async_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]

# Service dependencies will be added here once business logic is implemented.
# Example:
#   ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
