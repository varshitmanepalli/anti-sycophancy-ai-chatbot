"""Contradiction check API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.memory import ContradictionSeverity, MemorySourceType


class DetectedContradictionSchema(BaseModel):
    """A detected contradiction in API responses."""

    memory_statement: str
    new_statement: str
    description: str
    clarification_question: str
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    memory_source: MemorySourceType | None = None
    memory_source_id: str | None = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ContradictionCheckRequest(BaseModel):
    """Check a message against stored user memory."""

    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=32_000)


class ContradictionCheckResponse(BaseModel):
    """Contradiction check result."""

    contradictions: list[DetectedContradictionSchema] = Field(default_factory=list)
    clarification_question: str | None = None
    summary: str = ""

    @classmethod
    def from_domain(cls, result) -> "ContradictionCheckResponse":
        return cls(
            contradictions=[
                DetectedContradictionSchema(
                    memory_statement=c.memory_statement,
                    new_statement=c.new_statement,
                    description=c.description,
                    clarification_question=c.clarification_question,
                    severity=c.severity,
                    memory_source=c.memory_source,
                    memory_source_id=c.memory_source_id,
                    confidence=c.confidence,
                )
                for c in result.contradictions
            ],
            clarification_question=result.clarification_question,
            summary=result.summary,
        )


class ContradictionStoreRequest(BaseModel):
    """Check and persist detected contradictions."""

    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=32_000)
    conversation_id: UUID | None = None


class ContradictionStoreResponse(BaseModel):
    """Result of check-and-store operation."""

    check: ContradictionCheckResponse
    stored_count: int = 0

    @classmethod
    def from_result(cls, result, stored_count: int) -> "ContradictionStoreResponse":
        return cls(
            check=ContradictionCheckResponse.from_domain(result),
            stored_count=stored_count,
        )
