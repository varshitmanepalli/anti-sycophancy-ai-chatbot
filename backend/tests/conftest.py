"""Shared pytest fixtures for the backend test suite."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client wired to the FastAPI test app."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
