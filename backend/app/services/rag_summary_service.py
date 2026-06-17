from __future__ import annotations

import json
from typing import Protocol

from backend.app.core.config import settings
from backend.app.repositories.embedding_repository import RelatedPostRow
from backend.app.schemas.ai import RelatedPostsRequest


class RagSummaryProvider(Protocol):
    def summarize(
        self,
        payload: RelatedPostsRequest,
        related_posts: list[RelatedPostRow],
    ) -> dict[int, str]:
        raise NotImplementedError


class OpenAIRagSummaryProvider:
    def __init__(
        self,
        api_key: str | None = settings.openai_api_key,
        model: str = settings.openai_summary_model,
        max_output_tokens: int = settings.openai_summary_max_output_tokens,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.max_output_tokens = max_output_tokens

    def summarize(
        self,
        payload: RelatedPostsRequest,
        related_posts: list[RelatedPostRow],
    ) -> dict[int, str]:
        if not related_posts:
            return {}
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=self._build_prompt(payload, related_posts),
            max_output_tokens=self.max_output_tokens,
        )
        return self._parse_output(self._extract_output_text(response), related_posts)

    def _build_prompt(self, payload: RelatedPostsRequest, related_posts: list[RelatedPostRow]) -> str:
        related_post_blocks = []
        for row in related_posts:
            related_post_blocks.append(
                "\n".join(
                    [
                        f"post_id: {row.post_id}",
                        f"title: {row.title}",
                        f"tags: {', '.join(row.tags)}",
                        f"similarity: {row.similarity}",
                        f"content: {row.content_for_summary}",
                    ]
                )
            )

        return "\n\n".join(
            [
                "너는 게시판 RAG 추천 요약 도우미다.",
                "사용자 입력과 관련 있는 공개 참고 게시글을 보고 각 항목마다 한국어 summary를 작성한다.",
                "각 summary는 2-3문장으로 작성하고, 왜 관련 있는지와 사용자가 추가로 확인해야 할 조건을 함께 담는다.",
                "확정 판정을 하지 말고, 제공된 내용에 근거한 참고 정보로만 작성한다.",
                '반드시 JSON 배열만 반환한다. 예: [{"post_id":1,"summary":"..."}]',
                "사용자가 작성 중인 개인 상담 요청:",
                f"type: {payload.post_type}",
                f"title: {payload.title}",
                f"content: {payload.content}",
                f"region: {payload.region or ''}",
                f"tags: {', '.join(payload.tags)}",
                "관련 공개 참고 글 목록:",
                "\n\n---\n\n".join(related_post_blocks),
            ]
        )

    def _extract_output_text(self, response: object) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str):
            return output_text

        chunks: list[str] = []
        for output_item in getattr(response, "output", []) or []:
            for content_item in getattr(output_item, "content", []) or []:
                text = getattr(content_item, "text", None)
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks)

    def _parse_output(
        self,
        output_text: str,
        related_posts: list[RelatedPostRow],
    ) -> dict[int, str]:
        allowed_post_ids = {row.post_id for row in related_posts}
        data = json.loads(self._strip_code_fence(output_text))
        if not isinstance(data, list):
            return {}

        summaries: dict[int, str] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            post_id = item.get("post_id")
            summary = item.get("summary")
            if not isinstance(post_id, int) or post_id not in allowed_post_ids:
                continue
            if not isinstance(summary, str) or not summary.strip():
                continue
            summaries[post_id] = summary.strip()[:1000]
        return summaries

    @staticmethod
    def _strip_code_fence(value: str) -> str:
        stripped = value.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return stripped
