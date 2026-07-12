"""Shared API response schemas."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: str
    version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CheckResult(BaseModel):
    """Result of a single dependency health check."""

    status: str
    detail: str | None = None


class ReadinessResponse(BaseModel):
    """Readiness probe with per-dependency checks."""

    status: str
    version: str
    checks: dict[str, CheckResult]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str
    error_code: str | None = None
    request_id: str | None = None
