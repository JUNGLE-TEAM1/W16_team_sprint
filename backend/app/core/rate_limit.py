from collections import defaultdict, deque
from time import monotonic

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.errors import error_body

login_rate_limit: dict[str, deque[float]] = defaultdict(deque)


class LoginRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 5, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/v1/auth/login" and request.method == "POST":
            client = request.client.host if request.client else "unknown"
            key = f"{client}:{request.url.path}"
            now = monotonic()
            bucket = login_rate_limit[key]
            while bucket and now - bucket[0] > self.window_seconds:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=error_body(
                        "RATE_LIMITED",
                        "Too many login attempts",
                        {"retry_after_seconds": self.window_seconds},
                    ),
                )
            bucket.append(now)
        return await call_next(request)
