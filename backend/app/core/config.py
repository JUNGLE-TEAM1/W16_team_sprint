import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv_if_present() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue

        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


load_dotenv_if_present()


def env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


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
            (
                "http://localhost:3000,http://127.0.0.1:3000,"
                "http://localhost:3001,http://127.0.0.1:3001,"
                "http://127.0.0.1:8000,http://127.0.0.1:8001"
            ),
        ).split(",")
        if origin.strip()
    )
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_embedding_dimensions: int = int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1536"))
    openai_llm_model: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
    openai_llm_max_output_tokens: int = int(os.getenv("OPENAI_LLM_MAX_OUTPUT_TOKENS", "700"))
    openai_timeout_seconds: float = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))
    reference_fetch_enabled: bool = env_bool("REFERENCE_FETCH_ENABLED", True)
    reference_api_url: str = os.getenv("REFERENCE_API_URL", "").strip()
    reference_max_items: int = int(os.getenv("REFERENCE_MAX_ITEMS", "3"))
    reference_timeout_seconds: float = float(os.getenv("REFERENCE_TIMEOUT_SECONDS", "2.5"))


settings = Settings()
