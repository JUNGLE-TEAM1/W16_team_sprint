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
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    rag_default_limit: int = int(os.getenv("RAG_DEFAULT_LIMIT", "3"))
    rag_max_limit: int = int(os.getenv("RAG_MAX_LIMIT", "5"))
    rag_high_similarity: float = float(os.getenv("RAG_HIGH_SIMILARITY", "0.8"))
    rag_medium_similarity: float = float(os.getenv("RAG_MEDIUM_SIMILARITY", "0.6"))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    ollama_timeout_seconds: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "20"))


settings = Settings()
