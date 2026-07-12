"""Shared API response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health / readiness check response."""

    status: str


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str
