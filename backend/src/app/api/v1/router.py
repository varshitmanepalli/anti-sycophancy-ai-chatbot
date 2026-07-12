"""API version 1 router.

Aggregates all v1 sub-routers under a single prefix.
"""

from fastapi import APIRouter

from app.api.v1 import assumptions, chat, classify, claims, confidence, contradictions, debate, fallacies, health, memory

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(chat.router, prefix="/chat", tags=["chat"])
v1_router.include_router(classify.router, tags=["classification"])
v1_router.include_router(claims.router, prefix="/claims", tags=["claims"])
v1_router.include_router(assumptions.router, prefix="/assumptions", tags=["assumptions"])
v1_router.include_router(fallacies.router, prefix="/fallacies", tags=["fallacies"])
v1_router.include_router(debate.router, prefix="/debate", tags=["debate"])
v1_router.include_router(confidence.router, prefix="/confidence", tags=["confidence"])
v1_router.include_router(memory.router, prefix="/memory", tags=["memory"])
v1_router.include_router(contradictions.router, prefix="/contradictions", tags=["contradictions"])
