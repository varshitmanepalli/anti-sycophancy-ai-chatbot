"""Health and readiness endpoints.

Used by Docker, Kubernetes, and load balancers to verify the API process
is alive and its dependencies (database, model server) are reachable.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.api.deps import DbSession, HealthServiceDep, SettingsDep
from app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Return 200 when the API process is running."""
    return HealthResponse(status="ok", version=settings.app_version)


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    responses={503: {"description": "One or more dependencies unavailable"}},
)
async def readiness_check(
    settings: SettingsDep,
    health_service: HealthServiceDep,
    session: DbSession,
) -> JSONResponse | ReadinessResponse:
    """Verify database and model dependencies are reachable."""
    checks = await health_service.readiness_checks(session)

    has_error = any(c.status == "error" for c in checks.values())
    has_degraded = any(c.status == "degraded" for c in checks.values())
    overall = "error" if has_error else ("degraded" if has_degraded else "ok")

    body = ReadinessResponse(
        status=overall,
        version=settings.app_version,
        checks=checks,
    )

    if has_error:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=body.model_dump(mode="json"),
        )

    return body
