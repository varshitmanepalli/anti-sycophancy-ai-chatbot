"""Authentication placeholder.

Provides optional API-key / Bearer-token validation. When ``auth_enabled``
is False (default), all requests receive an anonymous ``UserContext``.
Replace with JWT, OAuth2, or API-gateway integration in production.
"""

from typing import Annotated

from fastapi import Depends, Header

from app.config.settings import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.schemas.auth import UserContext


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    settings: Settings = Depends(get_settings),
) -> UserContext:
    """Resolve the caller identity from request headers.

    Placeholder behaviour:
      - ``auth_enabled=false`` → anonymous user (default for local dev)
      - ``auth_enabled=true``  → requires matching ``Authorization: Bearer <key>``
        or ``X-API-Key: <key>`` header
    """
    if not settings.auth_enabled:
        return UserContext(user_id="anonymous", is_authenticated=False)

    token = _extract_token(authorization, x_api_key)
    if not token or not settings.api_key or token != settings.api_key:
        raise UnauthorizedError("Invalid or missing API key")

    return UserContext(
        user_id="api-user",
        is_authenticated=True,
        roles=["user"],
    )


async def get_optional_user(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    settings: Settings = Depends(get_settings),
) -> UserContext:
    """Like ``get_current_user`` but never raises — returns anonymous on failure."""
    if not settings.auth_enabled:
        return UserContext(user_id="anonymous", is_authenticated=False)

    token = _extract_token(authorization, x_api_key)
    if token and settings.api_key and token == settings.api_key:
        return UserContext(user_id="api-user", is_authenticated=True, roles=["user"])

    return UserContext(user_id="anonymous", is_authenticated=False)


def _extract_token(authorization: str | None, x_api_key: str | None) -> str | None:
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None
