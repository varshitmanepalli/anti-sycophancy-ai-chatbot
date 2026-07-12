"""Root API router.

Aggregates versioned sub-routers into a single router mounted by
``main.py`` under the configured API prefix.
"""

from fastapi import APIRouter

from app.api import chat
from app.api.v1.router import v1_router

api_router = APIRouter()
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(v1_router)

# Backward-compatible top-level health routes (no /v1 prefix)
from app.api.v1 import health  # noqa: E402

api_router.include_router(health.router, tags=["health"])
