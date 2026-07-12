"""Application-wide exception hierarchy and FastAPI handlers."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging.setup import get_logger
from app.schemas.common import ErrorResponse

logger = get_logger(__name__)


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404, error_code="not_found")


class UnauthorizedError(AppError):
    """Authentication failed."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401, error_code="unauthorized")


class ForbiddenError(AppError):
    """Authorization failed."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403, error_code="forbidden")


class RateLimitError(AppError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429, error_code="rate_limit_exceeded")


class ModelInferenceError(AppError):
    """LLM inference failure."""

    def __init__(self, message: str = "Model inference failed") -> None:
        super().__init__(message, status_code=502, error_code="model_inference_error")


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _error_response(
    request: Request,
    *,
    status_code: int,
    detail: str,
    error_code: str | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        detail=detail,
        error_code=error_code,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_exception_handlers(application: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI app."""

    @application.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error("AppError [%s]: %s", exc.error_code, exc.message)
        return _error_response(
            request,
            status_code=exc.status_code,
            detail=exc.message,
            error_code=exc.error_code,
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _error_response(
            request,
            status_code=exc.status_code,
            detail=str(exc.detail),
            error_code="http_error",
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Validation error: %s", exc.errors())
        return _error_response(
            request,
            status_code=422,
            detail="Request validation failed",
            error_code="validation_error",
        )

    @application.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return _error_response(
            request,
            status_code=500,
            detail="Internal server error",
            error_code="internal_error",
        )
