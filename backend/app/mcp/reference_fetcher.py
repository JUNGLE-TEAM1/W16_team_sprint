from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from html import unescape
from typing import Any
from urllib.parse import urlparse

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
        source="공공데이터포털",
        title="경기도 수원시 청년지원사업 상세설명 API",
        url="https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1",
        excerpt="수원시 청년지원사업의 사업명, 사업내용, 기간, 주소, 전화번호, 데이터기준일자를 제공하는 OpenAPI입니다.",
        keywords=("수원", "수원시", "청년", "청년정책", "청년지원사업", "월세", "취업", "창업"),
    ),
    OfficialReferenceCandidate(
        source="수원청년포털",
        title="수원 청년지원사업 안내",
        url="http://www.swyouth.kr",
        excerpt="수원시 청년 관련 정책, 지원사업, 공간과 프로그램을 확인할 수 있는 수원청년포털입니다.",
        keywords=("수원", "수원시", "청년", "수원청년", "지원사업", "청년월세"),
    ),
    OfficialReferenceCandidate(
        source="수원시청",
        title="수원시청 청년정책",
        url="https://www.suwon.go.kr/",
        excerpt="수원시청 공식 사이트에서 청년정책과 시정 공고를 확인할 수 있습니다.",
        keywords=("수원", "수원시청", "청년정책", "공고", "정책"),
    ),
)


def fetch_reference_payloads(
    *,
    query_text: str,
    matches: list[dict[str, Any]],
    reference_urls: list[str] | None = None,
    enabled: bool,
    api_url: str,
    max_items: int,
    timeout_seconds: float,
) -> list[ReferencePayload]:
    if not enabled:
        return []

    limit = _bounded_int(max_items, minimum=1, maximum=5)
    timeout = _bounded_float(timeout_seconds, minimum=0.5, maximum=10.0)

    custom_urls_requested = any(_clean(url) for url in reference_urls or [])
    if custom_urls_requested:
        return _dedupe_references(
            _fetch_url_references(
                urls=reference_urls or [],
                source="custom-url",
                limit=limit,
                timeout_seconds=timeout,
            )
        )[:limit]

    references = _fetch_external_api_references(
        query_text=query_text,
        api_url=api_url,
        limit=limit,
        timeout_seconds=timeout,
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


def _fetch_url_references(
    *,
    urls: list[str],
    source: str,
    limit: int,
    timeout_seconds: float,
) -> list[ReferencePayload]:
    safe_urls = _reference_urls(urls)[:limit]
    if not safe_urls:
        return []

    references: list[ReferencePayload] = []
    with httpx.Client(timeout=timeout_seconds) as client:
        for url in safe_urls:
            reference = _fetch_url_preview(client=client, url=url, source=source)
            if reference is not None:
                references.append(reference)

    return references


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
        if candidate.source == "공공데이터포털":
            score += 2
        if score > 0:
            scored_candidates.append((score, candidate))

    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    if scored_candidates:
        return [candidate for _, candidate in scored_candidates]
    return list(OFFICIAL_REFERENCE_CATALOG)


def _fetch_official_doc_preview(
    *,
    client: httpx.Client,
    candidate: OfficialReferenceCandidate,
) -> ReferencePayload | None:
    return _fetch_url_preview(
        client=client,
        url=candidate.url,
        source=candidate.source,
        fallback_title=candidate.title,
        fallback_excerpt=candidate.excerpt,
    )


def _fetch_url_preview(
    *,
    client: httpx.Client,
    url: str,
    source: str,
    fallback_title: str = "",
    fallback_excerpt: str = "",
) -> ReferencePayload | None:
    current_url = url
    try:
        for _ in range(4):
            if not _is_allowed_reference_url(current_url):
                return None
            response = client.get(current_url, follow_redirects=False)
            if response.is_redirect:
                next_request = response.next_request
                if next_request is None:
                    return None
                current_url = str(next_request.url)
                continue
            response.raise_for_status()
            break
        else:
            return None
    except httpx.HTTPError:
        if fallback_title:
            return {
                "title": fallback_title[:120],
                "url": url,
                "source": source,
                "excerpt": (fallback_excerpt or fallback_title)[:260],
            }
        return None

    parsed_url = urlparse(str(response.url))
    host = parsed_url.hostname or "Reference URL"
    title = _extract_title(response.text) or fallback_title or host
    excerpt = _extract_description(response.text) or fallback_excerpt or title
    return {
        "title": title[:120],
        "url": str(response.url),
        "source": source,
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


def _reference_urls(values: list[str]) -> list[str]:
    seen_urls: set[str] = set()
    safe_urls: list[str] = []
    for value in values:
        url = _clean(value)
        if not url or not _is_allowed_reference_url(url):
            continue
        dedupe_key = url.rstrip("/")
        if dedupe_key in seen_urls:
            continue
        seen_urls.add(dedupe_key)
        safe_urls.append(url)
    return safe_urls


def _is_allowed_reference_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False

    host = (parsed.hostname or "").strip().lower()
    if not host or host in {"localhost", "0.0.0.0"} or host.endswith(".localhost"):
        return False
    if host.endswith(".local") or "." not in host:
        return False

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True

    return ip.is_global


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
