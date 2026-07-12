"""FastAPI application entry point.

Creates and configures the ASGI application: middleware, routers, lifespan
hooks, and exception handlers. Keep this file thin — route handlers belong
in ``api/`` and orchestration in ``services/``.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import register_middleware
from app.logging.setup import configure_logging


def create_app() -> FastAPI:
    """Application factory used by uvicorn and tests."""
    settings = get_settings()
    configure_logging(settings)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_middleware(application)
    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = create_app()
