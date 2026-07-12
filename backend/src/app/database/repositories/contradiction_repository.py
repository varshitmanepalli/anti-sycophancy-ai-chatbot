"""Contradiction repository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import MemoryContradictionORM
from app.database.repositories.base import BaseRepository
from app.database.repositories.mappers import contradiction_to_domain, contradiction_to_orm
from app.domain.memory import MemoryContradiction


class SQLContradictionRepository(BaseRepository[MemoryContradictionORM]):
    """CRUD operations for detected contradictions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MemoryContradictionORM)

    async def create(self, contradiction: MemoryContradiction) -> MemoryContradiction:
        orm = contradiction_to_orm(contradiction)
        self._session.add(orm)
        await self._session.flush()
        return contradiction_to_domain(orm)

    async def get_by_id(self, contradiction_id: UUID) -> MemoryContradiction | None:
        orm = await self._get_orm(contradiction_id)
        return contradiction_to_domain(orm) if orm else None

    async def update(self, contradiction: MemoryContradiction) -> MemoryContradiction:
        orm = await self._get_orm(contradiction.id)
        if orm is None:
            raise ValueError(f"Contradiction {contradiction.id} not found")

        orm.statement_a = contradiction.statement_a
        orm.statement_b = contradiction.statement_b
        orm.statement_a_source_type = (
            contradiction.statement_a_source_type.value
            if contradiction.statement_a_source_type
            else None
        )
        orm.statement_a_source_id = contradiction.statement_a_source_id
        orm.statement_b_source_type = (
            contradiction.statement_b_source_type.value
            if contradiction.statement_b_source_type
            else None
        )
        orm.statement_b_source_id = contradiction.statement_b_source_id
        orm.description = contradiction.description
        orm.severity = contradiction.severity.value
        orm.resolved = contradiction.resolved
        await self._session.flush()
        return contradiction_to_domain(orm)

    async def delete(self, contradiction_id: UUID) -> bool:
        return await self._delete_orm(contradiction_id)

    async def list_by_user(
        self,
        user_id: str,
        *,
        unresolved_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MemoryContradiction]:
        filters = [MemoryContradictionORM.user_id == user_id]
        if unresolved_only:
            filters.append(MemoryContradictionORM.resolved.is_(False))
        rows = await self._list(
            *filters,
            limit=limit,
            offset=offset,
            order_by=MemoryContradictionORM.created_at.desc(),
        )
        return [contradiction_to_domain(r) for r in rows]

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        unresolved_only: bool = False,
    ) -> list[MemoryContradiction]:
        filters = [MemoryContradictionORM.conversation_id == conversation_id]
        if unresolved_only:
            filters.append(MemoryContradictionORM.resolved.is_(False))
        rows = await self._list(
            *filters, order_by=MemoryContradictionORM.created_at.desc()
        )
        return [contradiction_to_domain(r) for r in rows]
