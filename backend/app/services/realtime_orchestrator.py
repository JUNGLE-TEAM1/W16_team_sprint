import json
import re
from typing import Literal, TypedDict

from openai import AsyncOpenAI

from app.config import get_settings

RealtimeRouteAction = Literal["current_context", "retrieve", "out_of_scope", "clarify"]


class RealtimeRouteDecision(TypedDict):
    action: RealtimeRouteAction
    search_query: str
    reason: str


JOSEON_TERMS = {
    "조선",
    "실록",
    "왕",
    "왕조",
    "태조",
    "정종",
    "태종",
    "세종",
    "문종",
    "단종",
    "세조",
    "예종",
    "성종",
    "연산군",
    "중종",
    "인종",
    "명종",
    "선조",
    "광해군",
    "인조",
    "효종",
    "현종",
    "숙종",
    "경종",
    "영조",
    "정조",
    "순조",
    "헌종",
    "철종",
    "고종",
    "순종",
    "정도전",
    "이성계",
    "이방원",
    "사화",
    "환국",
    "붕당",
    "훈구",
    "사림",
    "궁궐",
    "왕자의",
}
EXPANSION_TERMS = {"다른", "비슷", "또", "추가", "더", "비교", "태종", "세종", "정조", "영조", "선조", "인조", "숙종"}
OUT_OF_SCOPE_TERMS = {"삼겹살", "목살", "날씨", "주식", "코인", "축구", "게임", "나폴레옹", "로마", "고구려", "백제", "신라"}


def fallback_realtime_route(transcript: str, evidence: list[dict]) -> RealtimeRouteDecision:
    normalized = transcript.strip()
    compact = re.sub(r"\s+", "", normalized)

    if not normalized:
        return {
            "action": "clarify",
            "search_query": "",
            "reason": "전사된 사용자 발화가 비어 있습니다.",
        }

    if any(term in compact for term in OUT_OF_SCOPE_TERMS) and not any(term in compact for term in JOSEON_TERMS):
        return {
            "action": "out_of_scope",
            "search_query": "",
            "reason": "조선왕조실록 근거로 답하기 어려운 범위 밖 질문입니다.",
        }

    is_joseon_related = any(term in compact for term in JOSEON_TERMS)
    asks_for_expansion = any(term in compact for term in EXPANSION_TERMS)

    if is_joseon_related and asks_for_expansion and not evidence:
        return {
            "action": "clarify",
            "search_query": "",
            "reason": "현재 게시글 근거가 없어 무엇과 비교할지 불명확합니다.",
        }

    if is_joseon_related and (asks_for_expansion or not evidence):
        return {
            "action": "retrieve",
            "search_query": normalized,
            "reason": "조선사 관련 확장 질문이어서 추가 실록 검색이 필요합니다.",
        }

    return {
        "action": "current_context",
        "search_query": "",
        "reason": "현재 게시글 근거로 우선 답변할 수 있습니다.",
    }


async def route_realtime_turn(
    transcript: str,
    post_context: dict,
    evidence: list[dict],
) -> RealtimeRouteDecision:
    settings = get_settings()
    fallback = fallback_realtime_route(transcript, evidence)
    if not settings.openai_api_key:
        return fallback

    evidence_titles = "\n".join(
        [
            f"- {item['article_id']}: {item['title']} ({item.get('date') or item.get('reign_date') or '날짜 미상'})"
            for item in evidence[:4]
        ]
    )
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 조선왕조실록 음성 토론의 RAG 라우팅 에이전트다. "
                        "사용자 발화를 보고 추가 검색이 필요한지 판단한다. "
                        "반드시 JSON만 반환한다. action은 current_context, retrieve, out_of_scope, clarify 중 하나다. "
                        "retrieve는 조선왕조실록/조선사와 관련 있고 현재 게시글 근거만으로 부족한 확장 질문일 때만 선택한다. "
                        "범위 밖 질문은 out_of_scope다. 애매하지만 현재 근거로 답할 수 있으면 current_context를 선택한다."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"게시글 제목: {post_context['title']}\n"
                        f"게시글 질문: {post_context['question']}\n\n"
                        f"현재 근거 기사:\n{evidence_titles or '없음'}\n\n"
                        f"사용자 음성 발화:\n{transcript}\n\n"
                        "JSON 필드: action, search_query, reason. "
                        "retrieve가 아니면 search_query는 빈 문자열로 둔다."
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.choices[0].message.content or "{}")
    except Exception:
        return fallback

    action = parsed.get("action")
    if action not in {"current_context", "retrieve", "out_of_scope", "clarify"}:
        return fallback
    if fallback["action"] == "retrieve" and action == "out_of_scope":
        return fallback

    search_query = str(parsed.get("search_query") or "")
    if action == "retrieve" and not search_query.strip():
        search_query = transcript.strip()

    return {
        "action": action,
        "search_query": search_query[:200],
        "reason": str(parsed.get("reason") or fallback["reason"])[:300],
    }
