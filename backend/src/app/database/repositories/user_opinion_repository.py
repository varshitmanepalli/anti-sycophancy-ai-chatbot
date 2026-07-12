"""User opinion repository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import UserOpinionORM
from app.database.repositories.base import BaseRepository
from app.database.repositories.mappers import opinion_to_domain, opinion_to_orm
from app.domain.memory import UserOpinion


class SQLUserOpinionRepository(BaseRepository[UserOpinionORM]):
    """CRUD operations for user opinions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserOpinionORM)

    async def create(self, opinion: UserOpinion) -> UserOpinion:
        orm = opinion_to_orm(opinion)
        self._session.add(orm)
        await self._session.flush()
        return opinion_to_domain(orm)

    async def get_by_id(self, opinion_id: UUID) -> UserOpinion | None:
        orm = await self._get_orm(opinion_id)
        return opinion_to_domain(orm) if orm else None

    async def update(self, opinion: UserOpinion) -> UserOpinion:
        orm = await self._get_orm(opinion.id)
        if orm is None:
            raise ValueError(f"Opinion {opinion.id} not found")

        orm.topic = opinion.topic
        orm.opinion = opinion.opinion
        orm.stance = opinion.stance.value
        orm.confidence = opinion.confidence
        orm.is_active = opinion.is_active
        orm.conversation_id = opinion.conversation_id
        orm.message_id = opinion.message_id
        await self._session.flush()
        return opinion_to_domain(orm)

    async def delete(self, opinion_id: UUID, *, soft: bool = True) -> bool:
        orm = await self._get_orm(opinion_id)
        if orm is None:
            return False
        if soft:
            orm.is_active = False
            await self._session.flush()
            return True
        return await self._delete_orm(opinion_id)

    async def list_by_user(
        self,
        user_id: str,
        *,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UserOpinion]:
        filters = [UserOpinionORM.user_id == user_id]
        if active_only:
            filters.append(UserOpinionORM.is_active.is_(True))
        rows = await self._list(
            *filters,
            limit=limit,
            offset=offset,
            order_by=UserOpinionORM.created_at.desc(),
        )
        return [opinion_to_domain(r) for r in rows]

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        active_only: bool = True,
    ) -> list[UserOpinion]:
        filters = [UserOpinionORM.conversation_id == conversation_id]
        if active_only:
            filters.append(UserOpinionORM.is_active.is_(True))
        rows = await self._list(*filters, order_by=UserOpinionORM.created_at.desc())
        return [opinion_to_domain(r) for r in rows]
