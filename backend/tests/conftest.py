"""Shared pytest fixtures for the backend test suite."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db
from app.main import create_app
from app.schemas.chat import ChatRequest, ChatResponse


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def mock_db_session():
    """Mock async DB session that passes SELECT 1."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock())
    return session


@pytest.fixture
async def client(mock_db_session):
    """Async HTTP client wired to the FastAPI test app."""

    async def override_get_db() -> AsyncGenerator:
        yield mock_db_session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_chat_response() -> ChatResponse:
    return ChatResponse(
        conversation_id=uuid4(),
        message="This is a direct, honest response.",
        model="Qwen/Qwen3-14B",
    )
