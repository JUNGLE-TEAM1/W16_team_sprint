from __future__ import annotations

import json
import re
from typing import Any, Protocol

import httpx
from fastapi import status

from backend.app.core.config import settings
from backend.app.core.embedding import (
    EmbeddingError,
    active_embedding_provider,
    cosine_similarity,
    embed_text,
    embedding_dimensions,
    token_overlap,
)
from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.schemas.rag import RagAssistRequest, RagAssistResponse, RagMatch, RagReference
from backend.app.services.reference_service import fetch_reference_materials


class PostRepositoryPort(Protocol):
    def list(
        self,
        *,
        page: int,
        size: int,
        query: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[Post], int]:
        pass


class PostEmbeddingRepositoryPort(Protocol):
    def upsert(self, *, post_id: int, source_text: str, vector: list[float]) -> PostEmbedding:
        pass

    def list_with_posts(self) -> list[tuple[PostEmbedding, Post]]:
        pass

    def post_ids(self) -> set[int]:
        pass


class UnitOfWork(Protocol):
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class RagService:
    def __init__(
        self,
        posts: PostRepositoryPort,
        embeddings: PostEmbeddingRepositoryPort,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.posts = posts
        self.embeddings = embeddings
        self.unit_of_work = unit_of_work

    def index_post(self, post: Post) -> None:
        try:
            source_text = self._source_text(post)
            self.embeddings.upsert(
                post_id=post.id,
                source_text=source_text,
                vector=embed_text(source_text),
            )
        except EmbeddingError as exc:
            raise AppError(
                code="EMBEDDING_FAILED",
                message="Embedding generation failed. Check OPENAI_API_KEY and embedding settings.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from exc

    def assist(self, payload: RagAssistRequest) -> RagAssistResponse:
        query_text = f"{payload.title}\n{payload.content}".strip()
        if not query_text:
            raise AppError(
                code="RAG_INPUT_REQUIRED",
                message="RAG 검색에는 제목이나 초안이 필요합니다.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        self._ensure_indexed()
        try:
            query_vector = embed_text(query_text)
        except EmbeddingError as exc:
            raise AppError(
                code="EMBEDDING_FAILED",
                message="Embedding generation failed. Check OPENAI_API_KEY and embedding settings.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from exc

        scored_matches = []
        for embedding, post in self.embeddings.list_with_posts():
            stored_vector = json.loads(embedding.vector_json)
            vector_score = cosine_similarity(query_vector, stored_vector)
            overlap_score = token_overlap(query_text, embedding.source_text)
            score = max(0.0, min(1.0, (vector_score * 0.7) + (overlap_score * 0.3)))
            scored_matches.append((score, post, embedding.source_text))

        scored_matches.sort(key=lambda match: match[0], reverse=True)
        matches = [
            RagMatch(
                post_id=post.id,
                title=post.title,
                excerpt=self._excerpt(post.content),
                score=round(score, 3),
                duplicate_risk=self._duplicate_risk(score),
                summary=self._summary(post, score),
                tags=post.tags,
            )
            for score, post, _ in scored_matches[: payload.top_k]
            if score > 0
        ]

        duplicate_warning = any(match.score >= 0.58 for match in matches)
        references = (
            fetch_reference_materials(
                query_text=query_text,
                matches=matches,
                reference_urls=payload.reference_urls,
            )
            if payload.include_references
            else []
        )
        recommendation, enriched_matches, llm_used = self._assist_with_llm(
            query_text=query_text,
            matches=matches,
            references=references,
            duplicate_warning=duplicate_warning,
        )

        return RagAssistResponse(
            embedding_dimensions=len(query_vector),
            embedding_provider=active_embedding_provider(),
            embedding_model=settings.openai_embedding_model
            if active_embedding_provider() == "openai"
            else "local-hash",
            llm_provider="openai" if llm_used else "none",
            llm_model=settings.openai_llm_model if llm_used else "rule-fallback",
            llm_used=llm_used,
            stored_vectors=len(scored_matches),
            duplicate_warning=duplicate_warning,
            recommendation=recommendation,
            matches=enriched_matches,
            references=references,
        )

    def _ensure_indexed(self) -> None:
        expected_dimensions = embedding_dimensions()
        current_embeddings = self.embeddings.list_with_posts()
        indexed_post_ids = {embedding.post_id for embedding, _ in current_embeddings}
        stale_post_ids = {
            embedding.post_id
            for embedding, _ in current_embeddings
            if self._vector_dimensions(embedding.vector_json) != expected_dimensions
        }
        posts, _ = self.posts.list(page=1, size=500)
        try:
            for post in posts:
                if post.id not in indexed_post_ids or post.id in stale_post_ids:
                    self.index_post(post)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def _assist_with_llm(
        self,
        *,
        query_text: str,
        matches: list[RagMatch],
        references: list[RagReference],
        duplicate_warning: bool,
    ) -> tuple[str, list[RagMatch], bool]:
        if not settings.openai_api_key:
            return self._recommendation(matches, duplicate_warning), matches, False

        try:
            llm_payload = self._request_llm_assist(
                query_text=query_text,
                matches=matches,
                references=references,
                duplicate_warning=duplicate_warning,
            )
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AppError(
                code="LLM_ASSIST_FAILED",
                message="LLM assist failed. Check OPENAI_API_KEY and OpenAI LLM settings.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from exc

        recommendation = llm_payload.get("recommendation")
        if not isinstance(recommendation, str) or not recommendation.strip():
            raise AppError(
                code="LLM_ASSIST_INVALID_RESPONSE",
                message="LLM assist returned an invalid recommendation.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            )

        summaries = self._summary_map_from_llm(llm_payload.get("match_summaries"))
        enriched_matches = [
            match.model_copy(update={"summary": summaries.get(match.post_id, match.summary)})
            for match in matches
        ]
        return recommendation.strip(), enriched_matches, True

    def _request_llm_assist(
        self,
        *,
        query_text: str,
        matches: list[RagMatch],
        references: list[RagReference],
        duplicate_warning: bool,
    ) -> dict[str, Any]:
        endpoint = f"{settings.openai_base_url.rstrip('/')}/responses"
        payload: dict[str, Any] = {
            "model": settings.openai_llm_model,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "너는 게시판 작성 보조 RAG 어시스턴트다. "
                        "사용자의 초안, 제공된 유사 게시글 후보, 참고자료만 근거로 한국어 추천을 작성한다. "
                        "새 사실을 지어내지 말고 JSON만 반환한다."
                    ),
                },
                {
                    "role": "user",
                    "content": self._llm_prompt(
                        query_text=query_text,
                        matches=matches,
                        references=references,
                        duplicate_warning=duplicate_warning,
                    ),
                },
            ],
            "max_output_tokens": settings.openai_llm_max_output_tokens,
        }
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=settings.openai_timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()

        text = self._extract_response_text(response.json())
        if not text:
            raise ValueError("OpenAI response did not include text output")
        return self._parse_json_object(text)

    def _llm_prompt(
        self,
        *,
        query_text: str,
        matches: list[RagMatch],
        references: list[RagReference],
        duplicate_warning: bool,
    ) -> str:
        match_lines = []
        for match in matches:
            tag_text = ", ".join(tag.name for tag in match.tags) or "none"
            match_lines.append(
                {
                    "post_id": match.post_id,
                    "title": match.title,
                    "score": match.score,
                    "duplicate_risk": match.duplicate_risk,
                    "tags": tag_text,
                    "excerpt": match.excerpt,
                }
            )

        return json.dumps(
            {
                "task": (
                    "추천 문구 1개와 후보별 요약을 JSON으로 작성하세요. "
                    "recommendation은 220자 이내, summary는 후보당 120자 이내. "
                    "중복 위험이 높으면 기존 글에 댓글/보완으로 이어갈지, 새 글이면 어떤 관점을 달리할지 제안하세요."
                ),
                "output_schema": {
                    "recommendation": "string",
                    "match_summaries": [{"post_id": "number", "summary": "string"}],
                },
                "duplicate_warning": duplicate_warning,
                "draft": query_text,
                "matches": match_lines,
                "references": [
                    {
                        "title": reference.title,
                        "url": reference.url,
                        "source": reference.source,
                        "excerpt": reference.excerpt,
                    }
                    for reference in references
                ],
            },
            ensure_ascii=False,
        )

    def _extract_response_text(self, data: dict[str, Any]) -> str:
        output_text = data.get("output_text")
        if isinstance(output_text, str):
            return output_text.strip()

        parts: list[str] = []
        for item in data.get("output", []):
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()

    def _parse_json_object(self, value: str) -> dict[str, Any]:
        normalized = value.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", normalized, flags=re.DOTALL)
        if fenced:
            normalized = fenced.group(1).strip()
        else:
            start = normalized.find("{")
            end = normalized.rfind("}")
            if start != -1 and end != -1:
                normalized = normalized[start : end + 1]

        parsed = json.loads(normalized)
        if not isinstance(parsed, dict):
            raise ValueError("LLM JSON output must be an object")
        return parsed

    def _summary_map_from_llm(self, value: Any) -> dict[int, str]:
        if not isinstance(value, list):
            return {}

        summaries: dict[int, str] = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            post_id = item.get("post_id")
            summary = item.get("summary")
            if isinstance(post_id, int) and isinstance(summary, str) and summary.strip():
                summaries[post_id] = summary.strip()
        return summaries

    def _vector_dimensions(self, vector_json: str) -> int:
        try:
            vector = json.loads(vector_json)
        except json.JSONDecodeError:
            return 0
        return len(vector) if isinstance(vector, list) else 0

    def _source_text(self, post: Post) -> str:
        tag_text = " ".join(tag.name for tag in post.tags)
        return f"{post.title}\n{post.content}\n{tag_text}".strip()

    def _excerpt(self, value: str) -> str:
        normalized = value.strip().replace("\n", " ")
        return normalized[:140] + ("..." if len(normalized) > 140 else "")

    def _summary(self, post: Post, score: float) -> str:
        tag_text = ", ".join(tag.name for tag in post.tags) or "no tags"
        return f"{post.title} 글은 {tag_text} 주제를 다루며 현재 초안과 유사도 {score:.2f}로 연결됩니다."

    def _duplicate_risk(self, score: float) -> str:
        if score >= 0.58:
            return "high"
        if score >= 0.35:
            return "medium"
        return "low"

    def _recommendation(self, matches: list[RagMatch], duplicate_warning: bool) -> str:
        if not matches:
            return "비슷한 기존 글을 찾지 못했습니다. 새 글로 작성해도 좋아 보입니다."
        if duplicate_warning:
            return "유사도가 높은 기존 글이 있습니다. 제목과 문제 상황을 더 구체화하거나 기존 글의 댓글로 보완하는 방식을 검토하세요."
        return "완전한 중복은 낮아 보입니다. 관련 글을 참고해 배경 링크와 태그를 보강해 보세요."
