from __future__ import annotations

import json
import re
from typing import Any

import httpx
from fastapi import status

from backend.app.core.config import settings
from backend.app.core.errors import AppError
from backend.app.schemas.agent import AgentMvpHighlight, AgentWritingAssistRequest, AgentWritingAssistResponse


KEYWORD_TAGS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("수원시", ("수원", "수원시", "팔달구", "영통구", "권선구", "장안구")),
    ("경기도", ("경기도", "경기")),
    ("청년", ("청년", "대학생", "취준생", "구직자", "사회초년생", "24세")),
    ("주거", ("주거", "월세", "임차", "전세", "보증금", "원룸")),
    ("월세", ("월세", "임차료")),
    ("취업", ("취업", "구직", "면접", "일자리", "직장")),
    ("창업", ("창업", "사업화", "스타트업")),
    ("교육", ("교육", "강의", "강좌", "학습", "훈련")),
    ("금융", ("금융", "저축", "통장", "자산", "대출")),
    ("문화", ("문화", "예술", "활동", "축제")),
    ("상담", ("상담", "멘토링", "컨설팅", "코칭")),
    ("교통", ("교통", "버스", "통학")),
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
            suggested_tags = self._tag_values(data.get("suggested_tag_names"))
            return AgentWritingAssistResponse(
                provider="openai",
                model=settings.openai_llm_model,
                mvp_highlight=self._highlight_value(data.get("mvp_highlight"), payload=payload, tags=suggested_tags),
                suggested_title=self._string_value(data.get("suggested_title"), "수원시 청년정책 상담"),
                suggested_content=self._string_value(data.get("suggested_content"), ""),
                suggested_tag_names=suggested_tags,
                outline=self._list_values(data.get("outline"), minimum=3),
                next_questions=self._list_values(data.get("next_questions"), minimum=3),
                agent_steps=[
                    "상담 내용을 읽었습니다.",
                    "수원시 청년지원사업 API 카드와 매칭하기 좋은 조건을 정리했습니다.",
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
                        "너는 수원시 청년정책 상담 케이스 작성 Agent다. "
                        "사용자의 상황을 바탕으로 상담 제목, 정리된 본문, 수원시 청년정책 태그, "
                        "MVP 하이라이트, 추가 확인 질문을 JSON으로만 추천한다. "
                        "mvp_highlight에는 이 사용자의 상황에 가장 먼저 보여줄 핵심 지원 방향 1개와 "
                        "왜 맞는지, 왜 MVP 하이라이트인지 설명한다."
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
                                "mvp_highlight": {
                                    "title": "string",
                                    "why_it_fits": "string",
                                    "why_highlight": "string",
                                },
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
            "수원시 거주 여부와 나이 조건 정리",
            "소득, 고용 상태, 주거/취업/창업 등 필요한 지원 분야 확인",
            "수원시 청년지원사업 카드와 매칭할 신청 조건 정리",
        ]
        next_questions = [
            "현재 주민등록상 거주지가 수원시인가요?",
            "만 나이, 고용 상태, 최근 소득 수준은 어떻게 되나요?",
            "가장 급한 문제가 월세, 취업, 창업, 교육, 문화 활동 중 무엇인가요?",
        ]

        return AgentWritingAssistResponse(
            provider="none",
            model="rule-suwon-youth-agent",
            mvp_highlight=self._mvp_highlight(payload=payload, tags=tags),
            suggested_title=title,
            suggested_content=self._draft_content(title=title, content=content, outline=outline),
            suggested_tag_names=tags,
            outline=outline,
            next_questions=next_questions,
            agent_steps=[
                "입력한 상담 상황을 읽었습니다.",
                "수원시 청년정책 기준 태그 후보를 골랐습니다.",
                "AI 매칭에 필요한 형식으로 상담 초안을 정리했습니다.",
            ],
            confidence=0.7 if content else 0.52,
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
            suggested_tags.extend(["수원시", "청년", "청년정책"])

        return suggested_tags[:5]

    def _fallback_title(self, payload: AgentWritingAssistRequest) -> str:
        text = payload.content.strip()
        if not text:
            return "수원시 청년정책 상담"

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
            "수원시 거주 여부, 나이, 고용 상태, 소득, 필요한 지원 분야를 적습니다.\n\n"
            "필요한 지원\n"
            "월세, 취업, 창업, 교육, 문화 활동 중 우선순위를 적습니다.\n\n"
            "다음 액션\n"
            "AI 매칭으로 수원시 청년지원사업 카드와 신청 체크리스트를 확인합니다."
        )

    def _mvp_highlight(self, *, payload: AgentWritingAssistRequest, tags: list[str]) -> AgentMvpHighlight:
        text = f"{payload.title} {payload.content} {payload.intent} {' '.join(tags)}".lower()

        if any(keyword in text for keyword in ("월세", "주거", "임차", "전세", "보증금")):
            return AgentMvpHighlight(
                title="월세 부담 완화가 1순위",
                why_it_fits="상담 내용에 수원시 청년, 주거비, 월세 부담 신호가 함께 들어 있어 주거 지원 후보와 가장 직접적으로 연결됩니다.",
                why_highlight="MVP에서는 사용자가 바로 체감하는 현금성/주거 지원을 먼저 보여줄 때 매칭 가치가 가장 빨리 전달됩니다.",
            )

        if any(keyword in text for keyword in ("경제", "어려움", "소득", "생활비", "금융", "지원금")):
            return AgentMvpHighlight(
                title="생활비성 지원 확인이 우선",
                why_it_fits="경제적 어려움과 소득 조건이 핵심이라 기본소득, 교통비, 월세처럼 부담을 줄이는 지원부터 확인하는 흐름이 맞습니다.",
                why_highlight="MVP에서 조건 확인 질문과 지원 후보를 한 번에 보여주기 좋아 상담 보드의 핵심 효용을 가장 빨리 보여줍니다.",
            )

        if any(keyword in text for keyword in ("취업", "구직", "면접", "일자리", "직장")):
            return AgentMvpHighlight(
                title="취업 준비 비용 절감이 핵심",
                why_it_fits="구직, 면접, 취업 준비 신호가 있어 교통비나 취업 지원 프로그램과 먼저 매칭하는 게 자연스럽습니다.",
                why_highlight="MVP에서 신청 조건, 준비서류, 문의처를 짧게 정리해 사용자가 다음 행동으로 바로 넘어갈 수 있습니다.",
            )

        if any(keyword in text for keyword in ("창업", "사업", "스타트업", "컨설팅", "교육")):
            return AgentMvpHighlight(
                title="창업/교육 지원 매칭이 우선",
                why_it_fits="창업이나 교육 수요가 드러나 있어 사업화 교육, 컨설팅, 청년 활동 지원 후보를 먼저 보는 게 맞습니다.",
                why_highlight="MVP에서 정책 카드의 프로그램 성격과 사용자의 목표가 명확히 연결되어 데모 설득력이 좋습니다.",
            )

        return AgentMvpHighlight(
            title="수원시 청년정책 기본 매칭",
            why_it_fits="수원시와 청년 조건이 확인되어 지역 기반 청년지원사업 카드와 먼저 비교할 수 있습니다.",
            why_highlight="MVP에서는 지역, 나이, 필요 지원 분야만으로도 후보 카드와 추가 질문을 바로 제시하는 흐름이 핵심입니다.",
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
            return ["수원시", "청년"]
        tags = [self._normalize_tag(item) for item in value if isinstance(item, str)]
        return [tag for tag in tags if tag][:5] or ["수원시", "청년"]

    def _highlight_value(
        self,
        value: Any,
        *,
        payload: AgentWritingAssistRequest,
        tags: list[str],
    ) -> AgentMvpHighlight:
        fallback = self._mvp_highlight(payload=payload, tags=tags)
        if not isinstance(value, dict):
            return fallback

        title = self._string_value(value.get("title"), fallback.title)
        why_it_fits = self._string_value(value.get("why_it_fits"), fallback.why_it_fits)
        why_highlight = self._string_value(value.get("why_highlight"), fallback.why_highlight)
        return AgentMvpHighlight(
            title=title[:80],
            why_it_fits=why_it_fits[:220],
            why_highlight=why_highlight[:220],
        )

    def _normalize_tag(self, value: str) -> str:
        return value.strip().lower().lstrip("#")

    def _confidence(self, value: Any) -> float:
        if not isinstance(value, int | float):
            return 0.7
        return max(0.0, min(1.0, float(value)))
