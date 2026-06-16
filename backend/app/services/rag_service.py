from __future__ import annotations

import json
import re
from typing import Any, Protocol

import httpx
from fastapi import status

from backend.app.core.config import settings
from backend.app.core.embedding import (
    EmbeddingError,
    active_embedding_model,
    active_embedding_provider,
    cosine_similarity,
    embed_text,
    embedding_dimensions,
    embedding_signature,
)
from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.schemas.rag import RagAssistRequest, RagAssistResponse, RagMatch, RagMvpHighlight, RagReference
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
            self._upsert_post_embedding(post)
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
                message="AI 매칭에는 상담 제목이나 현재 상황이 필요합니다.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        try:
            self._ensure_indexed()
            query_vector = embed_text(query_text)
        except EmbeddingError as exc:
            raise AppError(
                code="QUERY_EMBEDDING_FAILED",
                message="검색 문장 임베딩 생성에 실패했습니다. OPENAI_API_KEY와 임베딩 설정을 확인하세요.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from exc

        current_embeddings = self._support_card_embeddings()
        expected_dimensions = embedding_dimensions()
        scored_matches = []
        for embedding, post in current_embeddings:
            stored_vector = self._vector_from_json(embedding.vector_json)
            score = max(0.0, min(1.0, cosine_similarity(query_vector, stored_vector)))
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
        should_fetch_references = payload.include_references or bool(payload.reference_urls)
        references = (
            fetch_reference_materials(
                query_text=query_text,
                matches=matches,
                reference_urls=payload.reference_urls,
            )
            if should_fetch_references
            else []
        )
        recommendation, enriched_matches, llm_used = self._assist_with_llm(
            query_text=query_text,
            matches=matches,
            references=references,
            duplicate_warning=duplicate_warning,
        )

        return RagAssistResponse(
            embedding_dimensions=expected_dimensions,
            embedding_provider=active_embedding_provider(),
            embedding_model=active_embedding_model(),
            llm_provider="openai" if llm_used else "none",
            llm_model=settings.openai_llm_model if llm_used else "rule-fallback",
            llm_used=llm_used,
            stored_vectors=len(scored_matches),
            duplicate_warning=duplicate_warning,
            mvp_highlight=self._mvp_highlight(query_text=query_text, matches=enriched_matches),
            recommendation=recommendation,
            matches=enriched_matches,
            references=references,
        )

    def _ensure_indexed(self) -> None:
        current_embeddings = self._support_card_embeddings()
        expected_dimensions = embedding_dimensions()
        indexed_post_ids = {embedding.post_id for embedding, _ in current_embeddings}
        embedding_by_post_id = {embedding.post_id: embedding for embedding, _ in current_embeddings}
        posts, _ = self.posts.list(page=1, size=500)
        support_posts = [post for post in posts if self._is_support_card(post)]
        try:
            for post in support_posts:
                embedding = embedding_by_post_id.get(post.id)
                if (
                    post.id not in indexed_post_ids
                    or embedding is None
                    or self._vector_dimensions(embedding.vector_json) != expected_dimensions
                    or embedding.source_text != self._indexed_source_text(post)
                ):
                    self._upsert_post_embedding(post)
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            raise

    def _support_card_embeddings(self) -> list[tuple[PostEmbedding, Post]]:
        return [
            (embedding, post)
            for embedding, post in self.embeddings.list_with_posts()
            if self._is_support_card(post)
        ]

    def _is_support_card(self, post: Post) -> bool:
        return post.author_name == "data-bot"

    def _upsert_post_embedding(self, post: Post) -> None:
        source_text = self._source_text(post)
        self.embeddings.upsert(
            post_id=post.id,
            source_text=self._indexed_source_text(post),
            vector=embed_text(source_text),
        )

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
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return self._recommendation(matches, duplicate_warning), matches, False

        recommendation = self._string_from_llm_value(llm_payload.get("recommendation"))
        if not recommendation:
            return self._recommendation(matches, duplicate_warning), matches, False

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
                        "너는 경기도 수원시 청년지원사업 API 기반 RAG 상담 어시스턴트다. "
                        "사용자의 상담 상황, 제공된 수원시 청년정책 카드 후보, 참고자료만 근거로 한국어 추천을 작성한다. "
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
                    "수원시 청년정책 추천 문구 1개와 후보별 요약을 JSON으로 작성하세요. "
                    "recommendation은 260자 이내로 받을 수 있는 수원시 지원사업 후보, 조건 충족/부족 사유, "
                    "신청 체크리스트, 문의처/상담 경로를 포함하세요. summary는 후보당 120자 이내. "
                    "recommendation과 summary 값은 객체가 아니라 반드시 문자열로만 작성하세요. "
                    "조건이 불확실하면 추가 확인이 필요하다고 명확히 말하세요."
                ),
                "output_schema": {
                    "recommendation": "string",
                    "match_summaries": [{"post_id": "number", "summary": "string"}],
                },
                "duplicate_warning": duplicate_warning,
                "case": query_text,
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
            summary_text = self._string_from_llm_value(summary)
            if isinstance(post_id, int) and summary_text:
                summaries[post_id] = summary_text
        return summaries

    def _string_from_llm_value(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return ", ".join(
                text for item in value if (text := self._string_from_llm_value(item))
            ).strip()
        if not isinstance(value, dict):
            return ""

        parts: list[str] = []
        for key in (
            "text",
            "summary",
            "conditions_met",
            "conditions_not_met",
            "application_checklist",
            "checklist",
            "contact_info",
            "contact",
        ):
            text = self._string_from_llm_value(value.get(key))
            if text:
                parts.append(text)
        if parts:
            return " ".join(parts).strip()

        return " ".join(
            text for item in value.values() if (text := self._string_from_llm_value(item))
        ).strip()

    def _vector_dimensions(self, vector_json: str) -> int:
        try:
            vector = json.loads(vector_json)
        except json.JSONDecodeError:
            return 0
        return len(vector) if isinstance(vector, list) else 0

    def _source_text(self, post: Post) -> str:
        tag_text = " ".join(tag.name for tag in post.tags)
        return f"{post.title}\n{post.content}\n{tag_text}".strip()

    def _match_normalize(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.lower()).strip()

    def _indexed_source_text(self, post: Post) -> str:
        return f"__embedding_index__:{embedding_signature()}\n{self._source_text(post)}"

    def _vector_from_json(self, vector_json: str) -> list[float]:
        try:
            vector = json.loads(vector_json)
        except json.JSONDecodeError:
            return []
        if not isinstance(vector, list):
            return []
        return [float(component) for component in vector if isinstance(component, int | float)]

    def _mvp_highlight(self, *, query_text: str, matches: list[RagMatch]) -> RagMvpHighlight | None:
        if not matches:
            return None

        top_match = matches[0]
        query_norm = self._match_normalize(query_text)
        title = self._clean_policy_title(top_match.title)
        tag_text = " ".join(tag.name for tag in top_match.tags)
        matched_signal = self._highlight_signal(query_norm=query_norm, title=title, tag_text=tag_text)
        score_percent = round(top_match.score * 100)

        return RagMvpHighlight(
            post_id=top_match.post_id,
            title=f"{title} 먼저 확인",
            why_it_fits=(
                f"입력한 상황에서 {matched_signal} 신호가 잡혔고, "
                f"이 카드가 그 조건과 가장 가까운 수원시 청년정책 후보입니다."
            ),
            why_highlight=(
                f"현재 RAG 상위 매칭률이 {score_percent}%라 먼저 눌러서 대상 조건, 사업기간, 문의처를 확인할 가치가 큽니다."
            ),
        )

    def _highlight_signal(self, *, query_norm: str, title: str, tag_text: str) -> str:
        combined = self._match_normalize(f"{title} {tag_text}")
        if any(keyword in query_norm or keyword in combined for keyword in ("월세", "주거", "임차", "전세", "보증금")):
            return "월세/주거비 부담"
        if any(keyword in query_norm or keyword in combined for keyword in ("경제", "어려움", "소득", "생활비", "기본소득", "금융")):
            return "경제적 부담"
        if any(keyword in query_norm or keyword in combined for keyword in ("취업", "구직", "면접", "일자리", "직장", "교통비")):
            return "취업 준비 비용"
        if any(keyword in query_norm or keyword in combined for keyword in ("창업", "사업", "스타트업", "컨설팅")):
            return "창업/사업화"
        if any(keyword in query_norm or keyword in combined for keyword in ("교육", "강의", "강좌", "학습", "훈련")):
            return "교육/역량 강화"
        return "수원시 청년 조건"

    def _clean_policy_title(self, value: str) -> str:
        return re.sub(r"^\[[^\]]+\]\s*", "", value).strip() or value

    def _excerpt(self, value: str) -> str:
        normalized = value.strip().replace("\n", " ")
        return normalized[:140] + ("..." if len(normalized) > 140 else "")

    def _summary(self, post: Post, score: float) -> str:
        tag_text = ", ".join(tag.name for tag in post.tags) or "no tags"
        return f"{post.title} 카드는 {tag_text} 조건과 연결되며 현재 상담과 관련도 {score:.2f}로 매칭됩니다."

    def _duplicate_risk(self, score: float) -> str:
        if score >= 0.58:
            return "high"
        if score >= 0.35:
            return "medium"
        return "low"

    def _recommendation(self, matches: list[RagMatch], duplicate_warning: bool) -> str:
        if not matches:
            return "가까운 수원시 청년정책 카드를 찾지 못했습니다. 수원시 거주 여부, 나이, 소득, 필요한 지원 분야를 더 구체적으로 적어 다시 매칭해 보세요."
        if duplicate_warning:
            return "관련도가 높은 수원시 청년정책 카드가 있습니다. 대상 조건과 사업기간을 먼저 확인하고, 담당 부서나 문의처로 자격을 확정하세요."
        return "연결 가능한 수원시 청년정책 카드가 있습니다. 상위 후보의 사업내용, 기간, 문의처를 비교하고 부족한 조건은 상담 메모로 보강해 보세요."
