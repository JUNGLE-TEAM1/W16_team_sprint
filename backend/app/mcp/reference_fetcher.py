from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from typing import Any

import httpx


ReferencePayload = dict[str, str]


@dataclass(frozen=True)
class OfficialReferenceCandidate:
    source: str
    title: str
    url: str
    excerpt: str
    keywords: tuple[str, ...]


OFFICIAL_REFERENCE_CATALOG: tuple[OfficialReferenceCandidate, ...] = (
    OfficialReferenceCandidate(
        source="FastAPI docs",
        title="FastAPI security tutorial",
        url="https://fastapi.tiangolo.com/tutorial/security/",
        excerpt="Authentication and authorization patterns for FastAPI applications.",
        keywords=("fastapi", "api", "jwt", "auth", "authorization", "bearer", "401", "인증", "권한"),
    ),
    OfficialReferenceCandidate(
        source="React docs",
        title="React docs: Learn React",
        url="https://react.dev/learn",
        excerpt="Official React guidance for components, state, events, and rendering.",
        keywords=("react", "frontend", "component", "state", "ui", "프론트", "상태", "컴포넌트"),
    ),
    OfficialReferenceCandidate(
        source="OpenAI docs",
        title="OpenAI embeddings guide",
        url="https://platform.openai.com/docs/guides/embeddings",
        excerpt="Official guidance for turning text into vectors for search and recommendation.",
        keywords=("openai", "embedding", "embeddings", "vector", "rag", "llm", "임베딩", "벡터"),
    ),
    OfficialReferenceCandidate(
        source="PostgreSQL docs",
        title="PostgreSQL documentation",
        url="https://www.postgresql.org/docs/current/",
        excerpt="Official PostgreSQL reference for database features, SQL, and operations.",
        keywords=("postgres", "postgresql", "database", "db", "sql", "데이터베이스"),
    ),
    OfficialReferenceCandidate(
        source="SQLAlchemy docs",
        title="SQLAlchemy ORM documentation",
        url="https://docs.sqlalchemy.org/en/20/orm/",
        excerpt="Official SQLAlchemy ORM guidance for sessions, models, and persistence.",
        keywords=("sqlalchemy", "orm", "repository", "session", "model", "모델", "레포지토리"),
    ),
    OfficialReferenceCandidate(
        source="Vite docs",
        title="Vite guide",
        url="https://vite.dev/guide/",
        excerpt="Official Vite guide for local development, builds, and frontend tooling.",
        keywords=("vite", "build", "dev server", "frontend", "번들", "빌드"),
    ),
)


def fetch_reference_payloads(
    *,
    query_text: str,
    matches: list[dict[str, Any]],
    enabled: bool,
    api_url: str,
    max_items: int,
    timeout_seconds: float,
) -> list[ReferencePayload]:
    if not enabled:
        return []

    limit = _bounded_int(max_items, minimum=1, maximum=5)
    timeout = _bounded_float(timeout_seconds, minimum=0.5, maximum=10.0)
    references: list[ReferencePayload] = []

    references.extend(
        _fetch_external_api_references(
            query_text=query_text,
            api_url=api_url,
            limit=limit,
            timeout_seconds=timeout,
        )
    )
    if len(references) < limit:
        references.extend(
            _fetch_official_doc_references(
                query_text=query_text,
                matches=matches,
                limit=limit - len(references),
                timeout_seconds=timeout,
            )
        )

    return _dedupe_references(references)[:limit]


def _fetch_external_api_references(
    *,
    query_text: str,
    api_url: str,
    limit: int,
    timeout_seconds: float,
) -> list[ReferencePayload]:
    if not api_url:
        return []

    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            response = client.get(api_url, params={"q": query_text, "limit": limit})
            response.raise_for_status()
        return _parse_external_api_payload(response.json())[:limit]
    except (httpx.HTTPError, ValueError, TypeError):
        return []


def _fetch_official_doc_references(
    *,
    query_text: str,
    matches: list[dict[str, Any]],
    limit: int,
    timeout_seconds: float,
) -> list[ReferencePayload]:
    candidates = _rank_official_candidates(query_text=query_text, matches=matches)
    references: list[ReferencePayload] = []

    with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
        for candidate in candidates[:limit]:
            reference = _fetch_official_doc_preview(client=client, candidate=candidate)
            if reference is not None:
                references.append(reference)

    return references


def _rank_official_candidates(
    *,
    query_text: str,
    matches: list[dict[str, Any]],
) -> list[OfficialReferenceCandidate]:
    haystack_parts = [query_text]
    for match in matches:
        haystack_parts.extend(
            [
                _clean(match.get("title")),
                _clean(match.get("excerpt")),
                _clean(match.get("summary")),
            ]
        )
        haystack_parts.extend(_tag_names(match.get("tags")))
    haystack = _normalize(" ".join(haystack_parts))

    scored_candidates: list[tuple[int, OfficialReferenceCandidate]] = []
    for candidate in OFFICIAL_REFERENCE_CATALOG:
        score = sum(1 for keyword in candidate.keywords if _normalize(keyword) in haystack)
        if score > 0:
            scored_candidates.append((score, candidate))

    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    return [candidate for _, candidate in scored_candidates]


def _fetch_official_doc_preview(
    *,
    client: httpx.Client,
    candidate: OfficialReferenceCandidate,
) -> ReferencePayload | None:
    try:
        response = client.get(candidate.url)
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    title = _extract_title(response.text) or candidate.title
    excerpt = _extract_description(response.text) or candidate.excerpt
    return {
        "title": title[:120],
        "url": str(response.url),
        "source": candidate.source,
        "excerpt": excerpt[:260],
    }


def _parse_external_api_payload(payload: Any) -> list[ReferencePayload]:
    if isinstance(payload, dict):
        raw_items = (
            payload.get("references")
            or payload.get("items")
            or payload.get("results")
            or payload.get("data")
            or []
        )
    else:
        raw_items = payload

    if not isinstance(raw_items, list):
        return []

    references: list[ReferencePayload] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue

        title = _clean(item.get("title") or item.get("name"))
        url = _clean(item.get("url") or item.get("link"))
        excerpt = _clean(item.get("excerpt") or item.get("summary") or item.get("description"))
        source = _clean(item.get("source") or item.get("provider")) or "external-api"
        if title and url:
            references.append(
                {
                    "title": title[:120],
                    "url": url,
                    "source": source[:80],
                    "excerpt": (excerpt or title)[:260],
                }
            )

    return references


def _extract_title(value: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", value, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return _clean(_strip_tags(match.group(1)))


def _extract_description(value: str) -> str:
    patterns = (
        r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
        r'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']',
        r'<meta\s+[^>]*property=["\']og:description["\'][^>]*content=["\'](.*?)["\']',
        r'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:description["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, value, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return _clean(match.group(1))
    return ""


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value)


def _clean(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _normalize(value: str) -> str:
    return _clean(value).lower()


def _tag_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    names: list[str] = []
    for tag in value:
        if isinstance(tag, str):
            names.append(tag)
        elif isinstance(tag, dict):
            names.append(_clean(tag.get("name")))
    return [name for name in names if name]


def _dedupe_references(references: list[ReferencePayload]) -> list[ReferencePayload]:
    seen_urls: set[str] = set()
    unique_references: list[ReferencePayload] = []
    for reference in references:
        url = reference.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        unique_references.append(reference)
    return unique_references


def _bounded_int(value: Any, *, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return minimum
    return max(minimum, min(maximum, parsed))


def _bounded_float(value: Any, *, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return minimum
    return max(minimum, min(maximum, parsed))
