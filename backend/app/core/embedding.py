import hashlib
import math
import re

import httpx

from backend.app.core.config import settings

LOCAL_EMBEDDING_DIMENSIONS = 1536


class EmbeddingError(RuntimeError):
    pass


def active_embedding_provider() -> str:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return "openai"
    return "local-hash"


def embedding_dimensions() -> int:
    if active_embedding_provider() == "openai":
        return settings.openai_embedding_dimensions
    return LOCAL_EMBEDDING_DIMENSIONS


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def tokens(value: str) -> list[str]:
    normalized = normalize_text(value)
    words = re.findall(r"[a-z0-9_#.+-]+|[가-힣]{2,}", normalized)
    chunks = [normalized[index : index + 3] for index in range(max(len(normalized) - 2, 0))]
    return [*words, *chunks]


def embed_text(value: str) -> list[float]:
    if active_embedding_provider() == "openai":
        return _embed_with_openai(value)
    return _embed_with_local_hash(value)


def embed_text_local(value: str) -> list[float]:
    return _embed_with_local_hash(value)


def _embed_with_local_hash(value: str) -> list[float]:
    vector = [0.0] * LOCAL_EMBEDDING_DIMENSIONS
    for token in tokens(value):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % LOCAL_EMBEDDING_DIMENSIONS
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(component * component for component in vector))
    if norm == 0:
        return vector
    return [component / norm for component in vector]


def _embed_with_openai(value: str) -> list[float]:
    endpoint = f"{settings.openai_base_url.rstrip('/')}/embeddings"
    payload: dict[str, object] = {
        "model": settings.openai_embedding_model,
        "input": value or " ",
        "dimensions": settings.openai_embedding_dimensions,
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=settings.openai_timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
        data = response.json()
        vector = data["data"][0]["embedding"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise EmbeddingError("OpenAI embedding request failed") from exc

    return [float(component) for component in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(left_component * right_component for left_component, right_component in zip(left, right))


def token_overlap(left: str, right: str) -> float:
    left_tokens = set(tokens(left))
    right_tokens = set(tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
