"""HTTP middleware for the FastAPI application."""

from app.core.middleware.logging import RequestLoggingMiddleware
from app.core.middleware.rate_limit import RateLimitMiddleware

__all__ = ["RequestLoggingMiddleware", "RateLimitMiddleware", "register_middleware"]


def register_middleware(application) -> None:
    """Attach all middleware to the FastAPI app (order matters)."""
    application.add_middleware(RateLimitMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
