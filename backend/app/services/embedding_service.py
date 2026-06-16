from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any, Protocol

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from backend.app.core.config import settings
from backend.app.models.post import Post
from backend.app.models.post_embedding import EMBEDDING_DIMENSIONS


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(Embeddings):
    def __init__(
        self,
        api_key: str | None = settings.openai_api_key,
        model: str = settings.openai_embedding_model,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._embeddings: OpenAIEmbeddings | None = None

    def embed(self, text: str) -> list[float]:
        return self.embed_query(text)

    def embed_query(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        return [float(value) for value in self._client().embed_query(text)]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        return [[float(value) for value in embedding] for embedding in self._client().embed_documents(texts)]

    def _client(self) -> OpenAIEmbeddings:
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model=self.model, api_key=self.api_key)
        return self._embeddings


class MockEmbeddingProvider(Embeddings):
    def __init__(self, dimensions: int = EMBEDDING_DIMENSIONS) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        return self.embed_query(text)

    def embed_query(self, text: str) -> list[float]:
        values: list[float] = []
        seed = text.encode("utf-8")
        block_index = 0
        while len(values) < self.dimensions:
            digest = hashlib.sha256(seed + str(block_index).encode("utf-8")).digest()
            values.extend((byte / 127.5) - 1.0 for byte in digest)
            block_index += 1
        return values[: self.dimensions]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


class LangChainEmbeddingAdapter(Embeddings):
    def __init__(self, provider: EmbeddingProvider | Embeddings | Any) -> None:
        self.provider = provider

    def embed_query(self, text: str) -> list[float]:
        if hasattr(self.provider, "embed_query"):
            return [float(value) for value in self.provider.embed_query(text)]
        return [float(value) for value in self.provider.embed(text)]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if hasattr(self.provider, "embed_documents"):
            return [
                [float(value) for value in embedding]
                for embedding in self.provider.embed_documents(texts)
            ]
        return [self.embed_query(text) for text in texts]


def as_langchain_embeddings(provider: EmbeddingProvider | Embeddings | Any) -> Embeddings:
    if isinstance(provider, Embeddings):
        return provider
    return LangChainEmbeddingAdapter(provider)


class PostEmbeddingService:
    def __init__(
        self,
        provider: EmbeddingProvider,
        dimensions: int = EMBEDDING_DIMENSIONS,
    ) -> None:
        self.provider = provider
        self.dimensions = dimensions

    def build_post_text(self, post: Post) -> str:
        return self.build_text(title=post.title, content=post.content, tags=post.tags)

    def build_text(self, title: str, content: str, tags: Sequence[str]) -> str:
        tag_text = ", ".join(sorted(tag.strip().lower() for tag in tags if tag.strip()))
        return "\n".join(
            [
                f"title: {title.strip()}",
                f"content: {content.strip()}",
                f"tags: {tag_text}",
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
        embedding = as_langchain_embeddings(self.provider).embed_query(text)
        if len(embedding) != self.dimensions:
            raise ValueError(
                f"embedding dimension mismatch: expected {self.dimensions}, got {len(embedding)}"
            )
        return embedding
