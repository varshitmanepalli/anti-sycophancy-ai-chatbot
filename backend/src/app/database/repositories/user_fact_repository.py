"""User fact repository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import UserFactORM
from app.database.repositories.base import BaseRepository
from app.database.repositories.mappers import fact_to_domain, fact_to_orm
from app.domain.memory import UserFact


class SQLUserFactRepository(BaseRepository[UserFactORM]):
    """CRUD operations for extracted user facts."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserFactORM)

    async def create(self, fact: UserFact) -> UserFact:
        orm = fact_to_orm(fact)
        self._session.add(orm)
        await self._session.flush()
        return fact_to_domain(orm)

    async def get_by_id(self, fact_id: UUID) -> UserFact | None:
        orm = await self._get_orm(fact_id)
        return fact_to_domain(orm) if orm else None

    async def update(self, fact: UserFact) -> UserFact:
        orm = await self._get_orm(fact.id)
        if orm is None:
            raise ValueError(f"Fact {fact.id} not found")

        orm.content = fact.content
        orm.category = fact.category
        orm.confidence = fact.confidence
        orm.is_active = fact.is_active
        orm.conversation_id = fact.conversation_id
        orm.message_id = fact.message_id
        await self._session.flush()
        return fact_to_domain(orm)

    async def delete(self, fact_id: UUID, *, soft: bool = True) -> bool:
        orm = await self._get_orm(fact_id)
        if orm is None:
            return False
        if soft:
            orm.is_active = False
            await self._session.flush()
            return True
        return await self._delete_orm(fact_id)

    async def list_by_user(
        self,
        user_id: str,
        *,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UserFact]:
        filters = [UserFactORM.user_id == user_id]
        if active_only:
            filters.append(UserFactORM.is_active.is_(True))
        rows = await self._list(
            *filters,
            limit=limit,
            offset=offset,
            order_by=UserFactORM.created_at.desc(),
        )
        return [fact_to_domain(r) for r in rows]

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        active_only: bool = True,
    ) -> list[UserFact]:
        filters = [UserFactORM.conversation_id == conversation_id]
        if active_only:
            filters.append(UserFactORM.is_active.is_(True))
        rows = await self._list(*filters, order_by=UserFactORM.created_at.desc())
        return [fact_to_domain(r) for r in rows]
