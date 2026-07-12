"""Generic async repository base class."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Shared CRUD helpers for SQLAlchemy ORM models."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def _get_orm(self, entity_id: UUID) -> ModelT | None:
        return await self._session.get(self._model, entity_id)

    async def _delete_orm(self, entity_id: UUID) -> bool:
        instance = await self._get_orm(entity_id)
        if instance is None:
            return False
        await self._session.delete(instance)
        await self._session.flush()
        return True

    async def _list(
        self,
        *filters,
        limit: int = 100,
        offset: int = 0,
        order_by=None,
    ) -> list[ModelT]:
        stmt = select(self._model).where(*filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
