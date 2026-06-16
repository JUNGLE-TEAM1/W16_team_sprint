from __future__ import annotations

from html import unescape
import re
from typing import Any, Protocol

import httpx

from backend.app.core.config import settings
from backend.app.schemas.mcp import ExternalReferenceItem, ExternalReferenceSearchArguments

TECH_KEYWORD_STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "backend",
    "browser",
    "but",
    "can",
    "client",
    "frontend",
    "from",
    "have",
    "how",
    "implementing",
    "into",
    "returns",
    "sends",
    "server",
    "that",
    "the",
    "this",
    "using",
    "with",
}


class ExternalReferenceError(Exception):
    pass


class ExternalReferenceProvider(Protocol):
    def search(self, payload: ExternalReferenceSearchArguments) -> list[ExternalReferenceItem]:
        raise NotImplementedError


class StackExchangeReferenceProvider:
    def __init__(
        self,
        api_url: str = settings.stack_exchange_api_url,
        site: str = settings.stack_exchange_site,
        api_key: str | None = settings.stack_exchange_api_key,
        timeout_seconds: float = settings.external_reference_timeout_seconds,
    ) -> None:
        self.api_url = api_url
        self.site = site
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def search(self, payload: ExternalReferenceSearchArguments) -> list[ExternalReferenceItem]:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for query in self._build_queries(payload):
            items = self._search_query(query=query, limit=payload.limit, headers=headers)
            if items:
                return items
        return []

    def _search_query(
        self,
        query: str,
        limit: int,
        headers: dict[str, str],
    ) -> list[ExternalReferenceItem]:
        params: dict[str, Any] = {
            "site": self.site,
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "pagesize": limit,
        }

        try:
            response = httpx.get(
                self.api_url,
                params=params,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalReferenceError("external reference search failed") from exc

        data = response.json()
        items = data.get("items", [])
        if not isinstance(items, list):
            return []

        return [self._to_reference_item(item) for item in items if isinstance(item, dict)]

    def _build_queries(self, payload: ExternalReferenceSearchArguments) -> list[str]:
        tag_text = " ".join(payload.tags)
        content_keywords = " ".join(self._extract_content_keywords(payload.content))
        candidates = [
            self._compact_query([payload.title, tag_text, content_keywords]),
            self._compact_query([payload.title, tag_text]),
            self._compact_query([tag_text, content_keywords]),
            self._compact_query([payload.title]),
        ]

        queries: list[str] = []
        seen: set[str] = set()
        for query in candidates:
            normalized = query.lower()
            if not query or normalized in seen:
                continue
            queries.append(query)
            seen.add(normalized)
        return queries

    def _extract_content_keywords(self, content: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_.+-]{1,}", content)
        keywords: list[str] = []
        seen: set[str] = set()
        for word in words:
            normalized = word.lower()
            if normalized in TECH_KEYWORD_STOPWORDS or normalized in seen:
                continue
            keywords.append(word)
            seen.add(normalized)
            if len(keywords) >= 8:
                break
        return keywords

    def _compact_query(self, parts: list[str], max_length: int = 180) -> str:
        query = " ".join(" ".join(part.split()) for part in parts if part.strip()).strip()
        if len(query) <= max_length:
            return query
        return query[:max_length].rsplit(" ", 1)[0].strip()

    def _to_reference_item(self, item: dict[str, Any]) -> ExternalReferenceItem:
        title = unescape(str(item.get("title") or "Untitled Stack Overflow question")).strip()
        url = str(item.get("link") or "")
        tags = [str(tag) for tag in item.get("tags", []) if isinstance(tag, str)]
        score = self._optional_int(item.get("score"))
        answer_count = self._optional_int(item.get("answer_count"))
        is_answered = item.get("is_answered")
        if not isinstance(is_answered, bool):
            is_answered = None

        summary_parts = ["Stack Overflow에서 찾은 관련 질문입니다."]
        if answer_count is not None:
            summary_parts.append(f"답변 {answer_count}개")
        if score is not None:
            summary_parts.append(f"점수 {score}")
        if is_answered is True:
            summary_parts.append("채택된 답변이 있습니다.")
        elif is_answered is False:
            summary_parts.append("아직 채택된 답변은 없습니다.")

        return ExternalReferenceItem(
            title=title,
            url=url,
            source="Stack Overflow",
            summary=" · ".join(summary_parts),
            tags=tags[:5],
            score=score,
            answer_count=answer_count,
            is_answered=is_answered,
        )

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        return None
