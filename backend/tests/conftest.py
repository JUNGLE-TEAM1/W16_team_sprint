from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def use_local_ai_settings(monkeypatch) -> None:
    local_settings = SimpleNamespace(
        embedding_provider="local",
        openai_api_key="",
        openai_base_url="https://api.openai.com/v1",
        openai_embedding_model="text-embedding-3-small",
        openai_embedding_dimensions=1536,
        openai_llm_model="gpt-test",
        openai_llm_max_output_tokens=300,
        openai_timeout_seconds=1,
    )

    from backend.app.core import embedding
    from backend.app.services import rag_service

    monkeypatch.setattr(embedding, "settings", local_settings)
    monkeypatch.setattr(rag_service, "settings", local_settings)
