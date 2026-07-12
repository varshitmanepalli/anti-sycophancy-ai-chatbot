"""Repository CRUD tests with mocked async session."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.database.repositories.user_fact_repository import SQLUserFactRepository
from app.domain.memory import UserFact


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.mark.asyncio
async def test_create_fact(mock_session):
    repo = SQLUserFactRepository(mock_session)
    fact = UserFact(user_id="user-1", content="Lives in Toronto")

    result = await repo.create(fact)

    assert result.user_id == "user-1"
    assert result.content == "Lives in Toronto"
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_soft_delete_fact(mock_session):
    repo = SQLUserFactRepository(mock_session)
    fact_id = uuid4()
    orm = MagicMock()
    orm.is_active = True
    mock_session.get = AsyncMock(return_value=orm)

    deleted = await repo.delete(fact_id, soft=True)

    assert deleted is True
    assert orm.is_active is False
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none(mock_session):
    repo = SQLUserFactRepository(mock_session)
    mock_session.get = AsyncMock(return_value=None)

    result = await repo.get_by_id(uuid4())

    assert result is None
