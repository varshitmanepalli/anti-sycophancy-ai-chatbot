"""Health and readiness endpoints.

Used by Docker, Kubernetes, and load balancers to verify the API process
is alive and its dependencies (database, model server) are reachable.
"""

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness probe — returns 200 when the process is running."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Readiness probe — extend to check DB and vLLM connectivity."""
    # TODO: verify database and model server connections
    return HealthResponse(status="ok")
