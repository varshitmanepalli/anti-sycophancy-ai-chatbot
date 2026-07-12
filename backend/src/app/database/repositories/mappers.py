"""ORM ↔ domain mappers for memory entities."""

from app.database.models.conversation import ConversationORM, MessageORM
from app.database.models.memory import (
    MemoryContradictionORM,
    UserFactORM,
    UserGoalORM,
    UserOpinionORM,
)
from app.domain.entities import Conversation, Message, MessageRole
from app.domain.memory import (
    ContradictionSeverity,
    GoalStatus,
    MemoryContradiction,
    MemorySourceType,
    OpinionStance,
    UserFact,
    UserGoal,
    UserOpinion,
)


def message_to_domain(orm: MessageORM) -> Message:
    return Message(
        id=orm.id,
        role=MessageRole(orm.role),
        content=orm.content,
        created_at=orm.created_at,
    )


def message_to_orm(message: Message, conversation_id) -> MessageORM:
    return MessageORM(
        id=message.id,
        conversation_id=conversation_id,
        role=message.role.value,
        content=message.content,
        created_at=message.created_at,
    )


def conversation_to_domain(orm: ConversationORM) -> Conversation:
    return Conversation(
        id=orm.id,
        messages=[message_to_domain(m) for m in orm.messages],
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def fact_to_domain(orm: UserFactORM) -> UserFact:
    return UserFact(
        id=orm.id,
        user_id=orm.user_id,
        conversation_id=orm.conversation_id,
        message_id=orm.message_id,
        content=orm.content,
        category=orm.category,
        confidence=orm.confidence,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def fact_to_orm(fact: UserFact) -> UserFactORM:
    return UserFactORM(
        id=fact.id,
        user_id=fact.user_id,
        conversation_id=fact.conversation_id,
        message_id=fact.message_id,
        content=fact.content,
        category=fact.category,
        confidence=fact.confidence,
        is_active=fact.is_active,
        created_at=fact.created_at,
        updated_at=fact.updated_at,
    )


def opinion_to_domain(orm: UserOpinionORM) -> UserOpinion:
    return UserOpinion(
        id=orm.id,
        user_id=orm.user_id,
        conversation_id=orm.conversation_id,
        message_id=orm.message_id,
        topic=orm.topic,
        opinion=orm.opinion,
        stance=OpinionStance(orm.stance),
        confidence=orm.confidence,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def opinion_to_orm(opinion: UserOpinion) -> UserOpinionORM:
    return UserOpinionORM(
        id=opinion.id,
        user_id=opinion.user_id,
        conversation_id=opinion.conversation_id,
        message_id=opinion.message_id,
        topic=opinion.topic,
        opinion=opinion.opinion,
        stance=opinion.stance.value,
        confidence=opinion.confidence,
        is_active=opinion.is_active,
        created_at=opinion.created_at,
        updated_at=opinion.updated_at,
    )


def goal_to_domain(orm: UserGoalORM) -> UserGoal:
    return UserGoal(
        id=orm.id,
        user_id=orm.user_id,
        conversation_id=orm.conversation_id,
        content=orm.content,
        status=GoalStatus(orm.status),
        priority=orm.priority,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def goal_to_orm(goal: UserGoal) -> UserGoalORM:
    return UserGoalORM(
        id=goal.id,
        user_id=goal.user_id,
        conversation_id=goal.conversation_id,
        content=goal.content,
        status=goal.status.value,
        priority=goal.priority,
        is_active=goal.is_active,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def contradiction_to_domain(orm: MemoryContradictionORM) -> MemoryContradiction:
    return MemoryContradiction(
        id=orm.id,
        user_id=orm.user_id,
        conversation_id=orm.conversation_id,
        statement_a=orm.statement_a,
        statement_b=orm.statement_b,
        statement_a_source_type=(
            MemorySourceType(orm.statement_a_source_type)
            if orm.statement_a_source_type
            else None
        ),
        statement_a_source_id=orm.statement_a_source_id,
        statement_b_source_type=(
            MemorySourceType(orm.statement_b_source_type)
            if orm.statement_b_source_type
            else None
        ),
        statement_b_source_id=orm.statement_b_source_id,
        description=orm.description,
        severity=ContradictionSeverity(orm.severity),
        resolved=orm.resolved,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def contradiction_to_orm(contradiction: MemoryContradiction) -> MemoryContradictionORM:
    return MemoryContradictionORM(
        id=contradiction.id,
        user_id=contradiction.user_id,
        conversation_id=contradiction.conversation_id,
        statement_a=contradiction.statement_a,
        statement_b=contradiction.statement_b,
        statement_a_source_type=(
            contradiction.statement_a_source_type.value
            if contradiction.statement_a_source_type
            else None
        ),
        statement_a_source_id=contradiction.statement_a_source_id,
        statement_b_source_type=(
            contradiction.statement_b_source_type.value
            if contradiction.statement_b_source_type
            else None
        ),
        statement_b_source_id=contradiction.statement_b_source_id,
        description=contradiction.description,
        severity=contradiction.severity.value,
        resolved=contradiction.resolved,
        created_at=contradiction.created_at,
        updated_at=contradiction.updated_at,
    )
