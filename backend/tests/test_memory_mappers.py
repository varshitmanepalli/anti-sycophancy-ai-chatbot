"""Unit tests for memory domain mappers."""

from datetime import UTC, datetime
from uuid import uuid4

from app.database.models.memory import UserFactORM
from app.database.repositories.mappers import fact_to_domain, fact_to_orm
from app.domain.memory import UserFact


def test_fact_mapper_roundtrip():
    fact = UserFact(
        id=uuid4(),
        user_id="user-1",
        content="Works as a software engineer",
        category="professional",
        confidence=0.95,
    )
    orm = fact_to_orm(fact)
    restored = fact_to_domain(orm)

    assert restored.id == fact.id
    assert restored.user_id == fact.user_id
    assert restored.content == fact.content
    assert restored.category == fact.category
    assert restored.confidence == fact.confidence


def test_fact_to_domain_from_orm():
    fact_id = uuid4()
    orm = UserFactORM(
        id=fact_id,
        user_id="user-2",
        content="Prefers direct feedback",
        category="preference",
        confidence=0.8,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    domain = fact_to_domain(orm)

    assert domain.id == fact_id
    assert domain.content == "Prefers direct feedback"
    assert domain.is_active is True
