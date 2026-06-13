import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/w16_sprint",
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-only-change-me")
    access_token_seconds: int = int(os.getenv("ACCESS_TOKEN_SECONDS", "900"))
    refresh_token_seconds: int = int(os.getenv("REFRESH_TOKEN_SECONDS", "604800"))
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:8000",
        ).split(",")
        if origin.strip()
    )
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


settings = Settings()
