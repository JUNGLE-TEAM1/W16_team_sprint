import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


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
    session_expire_hours: int = _int_env("SESSION_EXPIRE_HOURS", 4)
    session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "session_id")
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_summary_model: str = os.getenv("OPENAI_SUMMARY_MODEL", "gpt-5.4-nano")
    openai_summary_max_output_tokens: int = _int_env("OPENAI_SUMMARY_MAX_OUTPUT_TOKENS", 700)
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
