"""Authentication-related Pydantic schemas."""

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """Authenticated (or anonymous) caller identity."""

    user_id: str = Field(..., description="Unique user identifier")
    is_authenticated: bool = False
    roles: list[str] = Field(default_factory=list)
