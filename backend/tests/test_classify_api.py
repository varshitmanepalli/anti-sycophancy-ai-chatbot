"""Classification API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_classify_programming(client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        json={"message": "How do I debug a Python FastAPI application?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "programming"
    assert data["confidence"] > 0.0
    assert data["method"] == "rules"


@pytest.mark.asyncio
async def test_classify_fact(client: AsyncClient):
    response = await client.post(
        "/api/v1/classify",
        json={"message": "What is the population of Tokyo?"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "fact"


@pytest.mark.asyncio
async def test_classify_validation(client: AsyncClient):
    response = await client.post("/api/v1/classify", json={"message": ""})
    assert response.status_code == 422
