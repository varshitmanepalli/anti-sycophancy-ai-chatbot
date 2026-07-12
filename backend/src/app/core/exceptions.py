"""Application-wide exception hierarchy and FastAPI handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging.setup import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ModelInferenceError(AppError):
    """LLM inference failure."""

    def __init__(self, message: str = "Model inference failed") -> None:
        super().__init__(message, status_code=502)


def register_exception_handlers(application: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI app."""

    @application.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        logger.error("AppError: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @application.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
