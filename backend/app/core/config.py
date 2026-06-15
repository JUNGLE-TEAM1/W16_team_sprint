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
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_embedding_dimensions: int = int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1536"))
    openai_llm_model: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
    openai_llm_max_output_tokens: int = int(os.getenv("OPENAI_LLM_MAX_OUTPUT_TOKENS", "700"))
    openai_timeout_seconds: float = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))


settings = Settings()
