from __future__ import annotations

import json
import re
from typing import Any

import httpx
from fastapi import status

from backend.app.core.config import settings
from backend.app.core.errors import AppError
from backend.app.schemas.agent import AgentWritingAssistRequest, AgentWritingAssistResponse


KEYWORD_TAGS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("fastapi", ("fastapi", "api", "router", "dependency")),
    ("react", ("react", "component", "state", "hook", "frontend")),
    ("rag", ("rag", "embedding", "vector", "similarity", "검색")),
    ("llm", ("llm", "openai", "gpt", "responses", "model")),
    ("mcp", ("mcp", "tool", "external api", "공식 문서", "참고자료")),
    ("agent", ("agent", "assistant", "도우미", "초안", "추천")),
    ("auth", ("auth", "jwt", "login", "token", "401", "인증")),
    ("db", ("db", "database", "postgres", "sqlalchemy", "table")),
    ("backend", ("backend", "service", "repository", "schema", "백엔드")),
    ("frontend", ("frontend", "ui", "ux", "button", "화면")),
)


class AgentService:
    def assist_writing(self, payload: AgentWritingAssistRequest) -> AgentWritingAssistResponse:
        if settings.openai_api_key:
            return self._assist_with_openai(payload)
        return self._assist_with_rules(payload)

    def _assist_with_openai(
        self,
        payload: AgentWritingAssistRequest,
    ) -> AgentWritingAssistResponse:
        try:
            data = self._request_openai(payload)
            return AgentWritingAssistResponse(
                provider="openai",
                model=settings.openai_llm_model,
                suggested_title=self._string_value(data.get("suggested_title"), "작성 초안"),
                suggested_content=self._string_value(data.get("suggested_content"), ""),
                suggested_tag_names=self._tag_values(data.get("suggested_tag_names")),
                outline=self._list_values(data.get("outline"), minimum=3),
                next_questions=self._list_values(data.get("next_questions"), minimum=3),
                agent_steps=[
                    "초안 입력을 읽었습니다.",
                    "게시글 구조를 정했습니다.",
                    "태그와 다음 질문을 추천했습니다.",
                ],
                confidence=self._confidence(data.get("confidence")),
            )
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise AppError(
                code="AGENT_ASSIST_FAILED",
                message="Agent writing assist failed. Check OPENAI_API_KEY and OpenAI LLM settings.",
                status_code=status.HTTP_502_BAD_GATEWAY,
            ) from exc

    def _request_openai(self, payload: AgentWritingAssistRequest) -> dict[str, Any]:
        endpoint = f"{settings.openai_base_url.rstrip('/')}/responses"
        body: dict[str, Any] = {
            "model": settings.openai_llm_model,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "너는 게시판 글쓰기 Agent다. 사용자의 초안을 바탕으로 "
                        "제목, 본문 초안, 태그, 개요, 다음 질문을 JSON으로만 추천한다."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "title": payload.title,
                            "content": payload.content,
                            "tag_names": payload.tag_names,
                            "intent": payload.intent,
                            "output_schema": {
                                "suggested_title": "string",
                                "suggested_content": "string",
                                "suggested_tag_names": ["string"],
                                "outline": ["string"],
                                "next_questions": ["string"],
                                "confidence": "number",
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "max_output_tokens": min(settings.openai_llm_max_output_tokens, 700),
        }
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=settings.openai_timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=body)
            response.raise_for_status()

        text = self._extract_response_text(response.json())
        return self._parse_json_object(text)

    def _assist_with_rules(
        self,
        payload: AgentWritingAssistRequest,
    ) -> AgentWritingAssistResponse:
        title = payload.title.strip() or self._fallback_title(payload)
        content = payload.content.strip()
        tags = self._suggest_tags(payload)
        outline = [
            "문제 상황을 한 문단으로 정리하기",
            "구현 흐름과 선택한 이유 적기",
            "남은 질문이나 다음 액션으로 마무리하기",
        ]
        next_questions = [
            "이 글의 독자가 바로 알아야 할 결론은 무엇인가?",
            "내가 실제로 바꾼 파일이나 API는 무엇인가?",
            "다음에 검증해야 할 위험은 무엇인가?",
        ]

        return AgentWritingAssistResponse(
            provider="none",
            model="rule-writing-agent",
            suggested_title=title,
            suggested_content=self._draft_content(title=title, content=content, outline=outline),
            suggested_tag_names=tags,
            outline=outline,
            next_questions=next_questions,
            agent_steps=[
                "입력된 제목과 본문을 읽었습니다.",
                "핵심 키워드로 태그 후보를 골랐습니다.",
                "게시글 구조에 맞춰 초안을 정리했습니다.",
            ],
            confidence=0.68 if content else 0.52,
        )

    def _suggest_tags(self, payload: AgentWritingAssistRequest) -> list[str]:
        existing_tags = [self._normalize_tag(tag_name) for tag_name in payload.tag_names]
        text = f"{payload.title} {payload.content} {payload.intent}".lower()
        suggested_tags = [tag for tag in existing_tags if tag]

        for tag_name, keywords in KEYWORD_TAGS:
            if tag_name in suggested_tags:
                continue
            if any(keyword in text for keyword in keywords):
                suggested_tags.append(tag_name)

        if not suggested_tags:
            suggested_tags.extend(["sprint", "writing", "agent"])

        return suggested_tags[:5]

    def _fallback_title(self, payload: AgentWritingAssistRequest) -> str:
        text = payload.content.strip()
        if not text:
            return "Sprint Agent 글쓰기 도우미 구현 메모"

        first_line = re.sub(r"\s+", " ", text.splitlines()[0]).strip()
        if len(first_line) <= 60:
            return first_line
        return f"{first_line[:57]}..."

    def _draft_content(self, *, title: str, content: str, outline: list[str]) -> str:
        if content:
            return (
                f"{content}\n\n"
                "정리 방향\n"
                f"1. {outline[0]}\n"
                f"2. {outline[1]}\n"
                f"3. {outline[2]}"
            )

        return (
            f"{title}\n\n"
            "문제 상황\n"
            "지금 구현하려는 기능과 사용자가 얻을 값을 먼저 적습니다.\n\n"
            "구현 흐름\n"
            "프론트 요청, 백엔드 AgentService 처리, 응답 적용 순서로 정리합니다.\n\n"
            "다음 액션\n"
            "초안 저장 전에 RAG 검사와 태그를 한 번 더 확인합니다."
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
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        return "\n".join(parts).strip()

    def _parse_json_object(self, value: str) -> dict[str, Any]:
        normalized = value.strip()
        start = normalized.find("{")
        end = normalized.rfind("}")
        if start != -1 and end != -1:
            normalized = normalized[start : end + 1]

        parsed = json.loads(normalized)
        if not isinstance(parsed, dict):
            raise ValueError("Agent JSON output must be an object")
        return parsed

    def _string_value(self, value: Any, fallback: str) -> str:
        return value.strip() if isinstance(value, str) and value.strip() else fallback

    def _list_values(self, value: Any, *, minimum: int) -> list[str]:
        if not isinstance(value, list):
            return []
        items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return items[: max(minimum, 5)]

    def _tag_values(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return ["agent", "writing"]
        tags = [self._normalize_tag(item) for item in value if isinstance(item, str)]
        return [tag for tag in tags if tag][:5] or ["agent", "writing"]

    def _normalize_tag(self, value: str) -> str:
        return value.strip().lower().lstrip("#")

    def _confidence(self, value: Any) -> float:
        if not isinstance(value, int | float):
            return 0.7
        return max(0.0, min(1.0, float(value)))
