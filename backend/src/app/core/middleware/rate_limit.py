"""Rate limiting middleware (placeholder).

In-memory sliding-window counter keyed by client IP. Replace with Redis
or an API gateway (Cloudflare, Kong, etc.) for distributed production use.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config.settings import get_settings
from app.logging.setup import get_logger

logger = get_logger(__name__)

# {client_ip: [timestamp, ...]}
_request_log: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests that exceed the configured rate limit."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        settings = get_settings()

        # Skip rate limiting for health probes
        if request.url.path.endswith(("/health", "/ready")):
            return await call_next(request)

        if not settings.rate_limit_enabled:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = settings.rate_limit_window_seconds
        limit = settings.rate_limit_requests

        # Prune expired timestamps
        cutoff = now - window
        timestamps = [ts for ts in _request_log[client_ip] if ts > cutoff]

        if len(timestamps) >= limit:
            logger.warning("Rate limit exceeded for %s", client_ip)
            request_id = getattr(request.state, "request_id", None)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "error_code": "rate_limit_exceeded",
                    "request_id": request_id,
                },
                headers={"Retry-After": str(window)},
            )

        timestamps.append(now)
        _request_log[client_ip] = timestamps

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - len(timestamps)))
        return response


def reset_rate_limit_store() -> None:
    """Clear the in-memory rate limit store — for tests only."""
    _request_log.clear()
