"""Rate limiting middleware tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db
from app.config.settings import get_settings
from app.core.middleware.rate_limit import reset_rate_limit_store
from app.main import create_app


@pytest.fixture(autouse=True)
def clear_rate_limits():
    reset_rate_limit_store()
    get_settings.cache_clear()
    yield
    reset_rate_limit_store()
    get_settings.cache_clear()


@pytest.fixture
async def rate_limited_client(mock_db_session, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    get_settings.cache_clear()

    app = create_app()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_rate_limit_blocks_excess_requests(rate_limited_client: AsyncClient):
    # Health endpoints are excluded from rate limiting — use OpenAPI schema
    for _ in range(2):
        response = await rate_limited_client.get("/api/openapi.json")
        assert response.status_code == 200

    response = await rate_limited_client.get("/api/openapi.json")
    assert response.status_code == 429
    assert response.json()["error_code"] == "rate_limit_exceeded"
