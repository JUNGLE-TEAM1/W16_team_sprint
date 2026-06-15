import pytest

from backend.app.api.dependencies import get_embedding_provider, get_summary_provider
from backend.app.main import app
from backend.app.services.embedding_provider import HashEmbeddingProvider
from backend.app.services.summary_provider import FakeSummaryProvider


@pytest.fixture(autouse=True)
def use_fake_ai_providers():
    app.dependency_overrides[get_embedding_provider] = lambda: HashEmbeddingProvider()
    app.dependency_overrides[get_summary_provider] = lambda: FakeSummaryProvider("테스트 요약입니다.")
    yield
    app.dependency_overrides.pop(get_embedding_provider, None)
    app.dependency_overrides.pop(get_summary_provider, None)
