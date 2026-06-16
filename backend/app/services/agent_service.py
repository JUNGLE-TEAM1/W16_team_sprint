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
    ("청년", ("청년", "24세", "취준생", "대학생", "사회초년생")),
    ("주거", ("주거", "월세", "전세", "보증금", "임대차", "원룸")),
    ("취업", ("취업", "구직", "면접", "일자리", "훈련", "내일배움")),
    ("복지", ("복지", "지원", "급여", "수당", "바우처", "긴급")),
    ("복지시설", ("복지관", "시설", "센터", "주민센터", "상담센터")),
    ("서울", ("서울", "서울시")),
    ("마포구", ("마포", "마포구", "홍대")),
    ("저소득", ("소득 없음", "저소득", "기초생활", "생계", "실직")),
    ("장애", ("장애", "발달장애", "활동지원")),
    ("노인", ("노인", "어르신", "돌봄", "요양")),
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
                    "상담 내용을 읽었습니다.",
                    "생활지원 매칭에 필요한 조건을 정리했습니다.",
                    "태그와 추가 확인 질문을 추천했습니다.",
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
                        "너는 생활지원 상담 케이스 작성 Agent다. 사용자의 상황을 바탕으로 "
                        "상담 제목, 정리된 상황 본문, 태그, 확인할 항목, 다음 질문을 JSON으로만 추천한다."
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
            "현재 상황과 거주 지역 정리하기",
            "소득, 나이, 가구 형태, 주거 조건 확인하기",
            "원하는 지원과 긴급도를 다음 액션으로 정리하기",
        ]
        next_questions = [
            "현재 주민등록상 거주 지역과 실제 거주지는 어디인가요?",
            "최근 3개월 소득, 고용 상태, 가구원 수는 어떻게 되나요?",
            "가장 급한 문제가 주거비, 취업, 의료, 돌봄 중 무엇인가요?",
        ]

        return AgentWritingAssistResponse(
            provider="none",
            model="rule-life-support-agent",
            suggested_title=title,
            suggested_content=self._draft_content(title=title, content=content, outline=outline),
            suggested_tag_names=tags,
            outline=outline,
            next_questions=next_questions,
            agent_steps=[
                "입력된 상담 상황을 읽었습니다.",
                "핵심 조건으로 태그 후보를 골랐습니다.",
                "지원 매칭에 필요한 형식으로 초안을 정리했습니다.",
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
            suggested_tags.extend(["상담", "복지", "생활지원"])

        return suggested_tags[:5]

    def _fallback_title(self, payload: AgentWritingAssistRequest) -> str:
        text = payload.content.strip()
        if not text:
            return "생활지원 상담 케이스"

        first_line = re.sub(r"\s+", " ", text.splitlines()[0]).strip()
        if len(first_line) <= 60:
            return first_line
        return f"{first_line[:57]}..."

    def _draft_content(self, *, title: str, content: str, outline: list[str]) -> str:
        if content:
            return (
                f"{content}\n\n"
                "상담 정리\n"
                f"1. {outline[0]}\n"
                f"2. {outline[1]}\n"
                f"3. {outline[2]}"
            )

        return (
            f"{title}\n\n"
            "현재 상황\n"
            "거주 지역, 나이, 고용 상태, 소득, 가구 형태를 적습니다.\n\n"
            "필요한 지원\n"
            "주거비, 취업, 의료, 돌봄, 긴급생계 중 우선순위를 적습니다.\n\n"
            "다음 액션\n"
            "AI 매칭으로 지원 카드와 신청 체크리스트를 확인합니다."
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
            return ["상담", "복지"]
        tags = [self._normalize_tag(item) for item in value if isinstance(item, str)]
        return [tag for tag in tags if tag][:5] or ["상담", "복지"]

    def _normalize_tag(self, value: str) -> str:
        return value.strip().lower().lstrip("#")

    def _confidence(self, value: Any) -> float:
        if not isinstance(value, int | float):
            return 0.7
        return max(0.0, min(1.0, float(value)))
