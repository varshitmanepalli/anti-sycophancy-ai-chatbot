"""User goal repository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import UserGoalORM
from app.database.repositories.base import BaseRepository
from app.database.repositories.mappers import goal_to_domain, goal_to_orm
from app.domain.memory import UserGoal


class SQLUserGoalRepository(BaseRepository[UserGoalORM]):
    """CRUD operations for user goals."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserGoalORM)

    async def create(self, goal: UserGoal) -> UserGoal:
        orm = goal_to_orm(goal)
        self._session.add(orm)
        await self._session.flush()
        return goal_to_domain(orm)

    async def get_by_id(self, goal_id: UUID) -> UserGoal | None:
        orm = await self._get_orm(goal_id)
        return goal_to_domain(orm) if orm else None

    async def update(self, goal: UserGoal) -> UserGoal:
        orm = await self._get_orm(goal.id)
        if orm is None:
            raise ValueError(f"Goal {goal.id} not found")

        orm.content = goal.content
        orm.status = goal.status.value
        orm.priority = goal.priority
        orm.is_active = goal.is_active
        orm.conversation_id = goal.conversation_id
        await self._session.flush()
        return goal_to_domain(orm)

    async def delete(self, goal_id: UUID, *, soft: bool = True) -> bool:
        orm = await self._get_orm(goal_id)
        if orm is None:
            return False
        if soft:
            orm.is_active = False
            await self._session.flush()
            return True
        return await self._delete_orm(goal_id)

    async def list_by_user(
        self,
        user_id: str,
        *,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UserGoal]:
        filters = [UserGoalORM.user_id == user_id]
        if active_only:
            filters.append(UserGoalORM.is_active.is_(True))
        rows = await self._list(
            *filters,
            limit=limit,
            offset=offset,
            order_by=UserGoalORM.priority.desc(),
        )
        return [goal_to_domain(r) for r in rows]

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        active_only: bool = True,
    ) -> list[UserGoal]:
        filters = [UserGoalORM.conversation_id == conversation_id]
        if active_only:
            filters.append(UserGoalORM.is_active.is_(True))
        rows = await self._list(*filters, order_by=UserGoalORM.priority.desc())
        return [goal_to_domain(r) for r in rows]
