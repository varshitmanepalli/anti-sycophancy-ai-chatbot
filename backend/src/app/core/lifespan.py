"""Application lifespan management.

Startup: initialize DB engine, warm up model connections.
Shutdown: gracefully close pools and clients.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import get_settings
from app.logging.setup import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager."""
    settings = get_settings()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    # TODO: initialize database connection pool
    # TODO: verify vLLM / model server reachability

    yield

    logger.info("Shutting down %s", settings.app_name)
    # TODO: dispose database engine and close HTTP clients
