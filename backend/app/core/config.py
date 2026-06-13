import os
from dataclasses import dataclass


def _int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _list_env(name: str, default: list[str]) -> list[str]:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/w16_sprint",
    )
    auth_secret_key: str = os.getenv(
        "AUTH_SECRET_KEY",
        "dev-only-change-me",
    )
    access_token_expire_minutes: int = _int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    refresh_token_expire_days: int = _int_env("REFRESH_TOKEN_EXPIRE_DAYS", 14)
    session_expire_hours: int = _int_env("SESSION_EXPIRE_HOURS", 8)
    session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "session_id")
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    cors_origins: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.cors_origins is None:
            object.__setattr__(
                self,
                "cors_origins",
                _list_env(
                    "CORS_ORIGINS",
                    ["http://127.0.0.1:5173", "http://localhost:5173"],
                ),
            )


settings = Settings()
