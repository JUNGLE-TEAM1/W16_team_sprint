import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.app.core.config import settings
from backend.app.core.errors import error_body


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable):
        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"
        now = time.monotonic()
        window_start = now - settings.rate_limit_window_seconds
        bucket = self.requests[key]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= settings.rate_limit_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_body(
                    "RATE_LIMIT_EXCEEDED",
                    "요청이 너무 많습니다. 잠시 후 다시 시도하세요.",
                    {
                        "limit": settings.rate_limit_requests,
                        "window_seconds": settings.rate_limit_window_seconds,
                    },
                ),
            )

        bucket.append(now)
        return await call_next(request)
