from __future__ import annotations

import hashlib
import math
from typing import Protocol

from backend.app.core.config import settings


class EmbeddingProvider(Protocol):
    model_name: str

    def embed(self, text: str) -> list[float]:
        pass


class LocalSentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str = settings.embedding_model_name) -> None:
        self.model_name = model_name
        self._model = None

    def embed(self, text: str) -> list[float]:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        vector = self._model.encode(text, normalize_embeddings=True)
        return [float(value) for value in vector.tolist()]


class HashEmbeddingProvider:
    def __init__(
        self,
        model_name: str = "fake-hash-embedding",
        dimension: int = settings.embedding_dimension,
    ) -> None:
        self.model_name = model_name
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
