from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://annals:annals@localhost:5432/annals_board"
    annals_xml_dir: str = "data/xml"
    annals_private_bundle_zip: str = "data/annals_private_bundle.zip"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_realtime_model: str = "gpt-realtime-2"
    openai_realtime_voice: str = "marin"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def xml_dir_path(self) -> Path:
        return Path(self.annals_xml_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
