"""Health check service.

Probes database connectivity and model availability for readiness checks.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.models.device import is_vllm_server_reachable
from app.models.model_manager import ModelManager
from app.schemas.common import CheckResult


class HealthService:
    """Aggregates liveness and readiness checks."""

    def __init__(self, settings: Settings, model_manager: ModelManager) -> None:
        self._settings = settings
        self._model_manager = model_manager

    async def check_database(self, session: AsyncSession) -> CheckResult:
        """Verify PostgreSQL is reachable."""
        try:
            await session.execute(text("SELECT 1"))
            return CheckResult(status="ok", detail="connected")
        except Exception as exc:
            return CheckResult(status="error", detail=str(exc))

    async def check_model(self) -> CheckResult:
        """Verify the LLM backend is available."""
        if self._model_manager.is_loaded:
            info = self._model_manager.info
            return CheckResult(
                status="ok",
                detail=f"{info.backend} on {info.device}" if info else "loaded",
            )

        if await is_vllm_server_reachable(self._settings.vllm_base_url):
            return CheckResult(status="ok", detail="vllm_server reachable")

        return CheckResult(status="degraded", detail="model not loaded")

    async def readiness_checks(self, session: AsyncSession) -> dict[str, CheckResult]:
        """Run all dependency checks for the readiness probe."""
        db_check = await self.check_database(session)
        model_check = await self.check_model()

        return {
            "database": db_check,
            "model": model_check,
        }
