"""Chat endpoint tests."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_chat_service, get_db
from app.config.settings import get_settings
from app.main import create_app
from app.services.chat_service import ChatService


@pytest.fixture
async def chat_client(mock_db_session, sample_chat_response):
    """Client with mocked ChatService."""
    from unittest.mock import AsyncMock

    mock_service = AsyncMock(spec=ChatService)
    mock_service.process_message = AsyncMock(return_value=sample_chat_response)

    async def override_chat_service():
        return mock_service

    app = create_app()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_chat_service] = override_chat_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_service

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_send_message(chat_client):
    client, mock_service = chat_client
    conversation_id = uuid4()

    response = await client.post(
        "/api/v1/chat/",
        json={"message": "Is this a good idea?", "conversation_id": str(conversation_id)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "This is a direct, honest response."
    assert data["model"] == "Qwen/Qwen3-14B"
    mock_service.process_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_message_validation_error(chat_client):
    client, _ = chat_client

    response = await client.post("/api/v1/chat/", json={"message": ""})

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


@pytest.mark.asyncio
async def test_auth_rejects_invalid_key(mock_db_session, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("API_KEY", "secret-key")

    app = create_app()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/",
            json={"message": "hello"},
            headers={"X-API-Key": "wrong-key"},
        )

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"
    app.dependency_overrides.clear()
    get_settings.cache_clear()
