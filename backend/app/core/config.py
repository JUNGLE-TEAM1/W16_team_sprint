import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/w16_sprint",
    )
    auth_secret: str = os.getenv("AUTH_SECRET", "dev-only-change-me")
    access_token_seconds: int = int(os.getenv("ACCESS_TOKEN_SECONDS", "900"))
    refresh_token_seconds: int = int(os.getenv("REFRESH_TOKEN_SECONDS", "604800"))
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )


settings = Settings()
