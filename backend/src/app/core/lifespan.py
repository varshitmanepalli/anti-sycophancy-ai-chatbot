"""Application lifespan management.

Startup: initialize DB engine, warm up model connections.
Shutdown: gracefully close pools and clients.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import get_settings
from app.logging.setup import get_logger
from app.models.model_manager import ModelManager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager."""
    settings = get_settings()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    # TODO: initialize database connection pool

    if settings.model_auto_load:
        manager = await ModelManager.get_instance()
        info = await manager.load()
        logger.info("Model warmed up: %s", info)

    yield

    logger.info("Shutting down %s", settings.app_name)

    manager = await ModelManager.get_instance()
    if manager.is_loaded:
        await manager.unload()

    # TODO: dispose database engine
