"""Root API router.

Aggregates versioned sub-routers (``v1/``) into a single router mounted by
``main.py`` under the configured API prefix.
"""

from fastapi import APIRouter

from app.api.v1 import chat, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
