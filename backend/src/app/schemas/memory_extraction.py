"""Memory extraction API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.memory_extraction import MemoryCategory


class ExtractedMemoryItemSchema(BaseModel):
    """A single extracted long-term memory item."""

    content: str
    category: MemoryCategory
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    topic: str | None = None


class MemoryExtractionRequest(BaseModel):
    """Request to extract long-term memory from a message."""

    message: str = Field(..., min_length=1, max_length=32_000)
    context: str = ""


class MemoryExtractionResponse(BaseModel):
    """Extracted long-term memory grouped by category."""

    career: list[ExtractedMemoryItemSchema] = Field(default_factory=list)
    programming_language: list[ExtractedMemoryItemSchema] = Field(default_factory=list)
    goals: list[ExtractedMemoryItemSchema] = Field(default_factory=list)
    preferences: list[ExtractedMemoryItemSchema] = Field(default_factory=list)
    projects: list[ExtractedMemoryItemSchema] = Field(default_factory=list)
    summary: str = ""

    @classmethod
    def from_domain(cls, result) -> "MemoryExtractionResponse":
        def _items(category: MemoryCategory):
            return [
                ExtractedMemoryItemSchema(
                    content=item.content,
                    category=item.category,
                    confidence=item.confidence,
                    topic=item.topic,
                )
                for item in result.items_for_category(category)
            ]

        return cls(
            career=_items(MemoryCategory.CAREER),
            programming_language=_items(MemoryCategory.PROGRAMMING_LANGUAGE),
            goals=_items(MemoryCategory.GOALS),
            preferences=_items(MemoryCategory.PREFERENCES),
            projects=_items(MemoryCategory.PROJECTS),
            summary=result.summary,
        )


class MemoryStoreRequest(BaseModel):
    """Extract and persist long-term memory for a user."""

    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=32_000)
    context: str = ""
    conversation_id: UUID | None = None
    message_id: UUID | None = None


class StoredMemoryCountsSchema(BaseModel):
    """Counts of persisted items per storage table."""

    facts: int = 0
    goals: int = 0
    opinions: int = 0


class MemoryStoreResponse(BaseModel):
    """Result of extraction and persistence."""

    extracted: MemoryExtractionResponse
    stored: StoredMemoryCountsSchema

    @classmethod
    def from_domain(cls, result) -> "MemoryStoreResponse":
        return cls(
            extracted=MemoryExtractionResponse.from_domain(result.extracted),
            stored=StoredMemoryCountsSchema(
                facts=result.stored.facts,
                goals=result.stored.goals,
                opinions=result.stored.opinions,
            ),
        )
