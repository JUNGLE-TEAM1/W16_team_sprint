from __future__ import annotations

import hashlib
from typing import Protocol

from backend.app.core.config import settings
from backend.app.models.post import Post
from backend.app.models.post_embedding import EMBEDDING_DIMENSIONS


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        api_key: str | None = settings.openai_api_key,
        model: str = settings.openai_embedding_model,
    ) -> None:
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(model=self.model, input=text)
        return [float(value) for value in response.data[0].embedding]


class MockEmbeddingProvider:
    def __init__(self, dimensions: int = EMBEDDING_DIMENSIONS) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        values: list[float] = []
        seed = text.encode("utf-8")
        block_index = 0
        while len(values) < self.dimensions:
            digest = hashlib.sha256(seed + str(block_index).encode("utf-8")).digest()
            values.extend((byte / 127.5) - 1.0 for byte in digest)
            block_index += 1
        return values[: self.dimensions]


class PostEmbeddingService:
    def __init__(
        self,
        provider: EmbeddingProvider,
        dimensions: int = EMBEDDING_DIMENSIONS,
    ) -> None:
        self.provider = provider
        self.dimensions = dimensions

    def build_post_text(self, post: Post) -> str:
        tags = ", ".join(post.tags)
        return "\n".join(
            [
                f"title: {post.title.strip()}",
                f"content: {post.content.strip()}",
                f"tags: {tags}",
            ]
        )

    def build_content_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def build_metadata(self, post: Post) -> dict:
        return {
            "title": post.title,
            "tags": post.tags,
            "author_id": post.author_id,
        }

    def embed(self, text: str) -> list[float]:
        embedding = self.provider.embed(text)
        if len(embedding) != self.dimensions:
            raise ValueError(
                f"embedding dimension mismatch: expected {self.dimensions}, got {len(embedding)}"
            )
        return embedding
