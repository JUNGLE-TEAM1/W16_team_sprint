import json
import asyncio
from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import get_settings


def _excerpt(text: str, max_length: int = 180) -> str:
    return text[:max_length] + ("..." if len(text) > max_length else "")


def fallback_draft(question: str, evidence: list[dict]) -> dict:
    if not evidence:
        return {
            "summary": "관련 실록 기사를 아직 찾지 못했습니다.",
            "interpretation": "검색어를 더 구체적으로 바꾸면 원문 근거를 찾기 쉬워집니다.",
            "tags": ["검색필요", "실록"],
        }

    first = evidence[0]
    summary = f"{first['title']} 기사를 중심으로 질문과 관련된 원문 근거를 찾았습니다."
    interpretation = (
        f"첫 근거는 {first.get('date') or first.get('reign_date') or '날짜 미상'}의 기사입니다. "
        f"원문 일부: {_excerpt(first['content'])}"
    )
    tags = list(dict.fromkeys(["실록", first.get("king") or "조선", *(first.get("subject_classes") or [])]))[:5]
    return {"summary": summary, "interpretation": interpretation, "tags": tags}


def fallback_rerank_evidence(evidence: list[dict], max_items: int = 3) -> dict:
    selected = evidence[:max_items]
    selected_ids = [item["article_id"] for item in selected]
    return {
        "selected_evidence": selected,
        "selected_ids": selected_ids,
        "rejected_ids": [item["article_id"] for item in evidence if item["article_id"] not in selected_ids],
        "reason": "LLM reranking을 사용할 수 없어 검색 순서대로 근거 후보를 선택했습니다.",
    }


async def _stream_fallback_text(text: str) -> AsyncIterator[str]:
    words = text.split(" ")
    for index, word in enumerate(words):
        yield word + (" " if index < len(words) - 1 else "")
        await asyncio.sleep(0.01)


def _discussion_context_text(post_context: dict, evidence: list[dict], comments: list[dict]) -> str:
    evidence_text = "\n\n".join(
        [
            (
                f"[{idx}] {item['title']} ({item.get('date') or item.get('reign_date') or '날짜 미상'})\n"
                f"기사 ID: {item['article_id']}\n"
                f"URL: {item['official_url']}\n"
                f"원문: {item['content'][:900]}"
            )
            for idx, item in enumerate(evidence, start=1)
        ]
    )
    comment_text = "\n".join(
        [f"- {item['username']}: {item['content']}" for item in comments[-8:]]
    )
    return (
        f"게시글 제목:\n{post_context['title']}\n\n"
        f"게시글 질문:\n{post_context['question']}\n\n"
        f"기존 AI 요약:\n{post_context['ai_summary']}\n\n"
        f"기존 AI 해석:\n{post_context['ai_interpretation']}\n\n"
        f"실록 원문 근거:\n{evidence_text or '연결된 원문 근거 없음'}\n\n"
        f"최근 댓글:\n{comment_text or '아직 댓글 없음'}"
    )


async def stream_discussion_reply(
    message: str,
    post_context: dict,
    evidence: list[dict],
    comments: list[dict],
) -> AsyncIterator[str]:
    settings = get_settings()
    context_text = _discussion_context_text(post_context, evidence, comments)

    if not settings.openai_api_key:
        fallback = (
            "OpenAI API 키가 없어 임시 토론 답변을 제공합니다. "
            "이 질문은 기존 게시글의 실록 근거와 댓글 맥락을 바탕으로 검토해야 합니다. "
            "먼저 근거 기사에 직접 드러난 표현과, 사용자의 해석이 덧붙인 부분을 구분해 보세요."
        )
        async for chunk in _stream_fallback_text(fallback):
            yield chunk
        return

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    stream = await client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.3,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 조선왕조실록 원문 기반 역사 토론 게시판의 AI 토론 도우미다. "
                    "반드시 제공된 게시글, 실록 원문 근거, 댓글 맥락 안에서만 답한다. "
                    "근거에 없는 내용을 단정하지 말고, 토론자가 다음에 확인할 쟁점을 제안한다. "
                    "답변은 한국어로 4-7문장 정도로 작성한다."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"게시글과 근거 맥락:\n{context_text}\n\n"
                    f"사용자의 후속 토론 질문:\n{message}"
                ),
            },
        ],
    )

    async for event in stream:
        delta = event.choices[0].delta.content if event.choices else None
        if delta:
            yield delta


def _select_evidence_by_ids(evidence: list[dict], selected_ids: list[str], max_items: int) -> list[dict]:
    evidence_by_id = {item["article_id"]: item for item in evidence}
    selected = []
    seen = set()
    for article_id in selected_ids:
        if article_id in evidence_by_id and article_id not in seen:
            selected.append(evidence_by_id[article_id])
            seen.add(article_id)
        if len(selected) >= max_items:
            break
    return selected


async def rerank_evidence(question: str, evidence: list[dict], max_items: int = 3) -> dict:
    settings = get_settings()
    if not evidence:
        return {"selected_evidence": [], "selected_ids": [], "rejected_ids": [], "reason": "검색 후보가 없습니다."}
    if not settings.openai_api_key:
        return fallback_rerank_evidence(evidence, max_items)

    candidate_text = "\n\n".join(
        [
            (
                f"[{item['article_id']}]\n"
                f"제목: {item['title']}\n"
                f"왕: {item.get('king') or ''}\n"
                f"날짜: {item.get('date') or item.get('reign_date') or ''}\n"
                f"분류: {', '.join(item.get('subject_classes') or [])}\n"
                f"원문 일부: {item['content'][:900]}"
            )
            for item in evidence
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
                        "너는 조선왕조실록 RAG 검색 후보 검증기다. "
                        "답변을 작성하지 말고, 질문에 대한 근거로 직접 쓸 수 있는 기사만 고른다. "
                        "제목, 분류, 원문 일부가 질문과 직접 연결될 때만 선택하고, 애매하면 제외한다. "
                        "JSON만 반환하라: selected_ids, rejected_ids, reason."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"질문:\n{question}\n\n"
                        f"후보 기사:\n{candidate_text}\n\n"
                        f"selected_ids에는 최대 {max_items}개 article_id만 넣어라. "
                        "질문과 관련 없는 후보는 rejected_ids에 넣어라. "
                        "reason은 한 문장으로 짧게 써라."
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.choices[0].message.content or "{}")
    except Exception:
        return fallback_rerank_evidence(evidence, max_items)

    raw_selected_ids = parsed.get("selected_ids", [])
    if not isinstance(raw_selected_ids, list):
        raw_selected_ids = []
    selected_ids = [str(article_id) for article_id in raw_selected_ids]
    selected_evidence = _select_evidence_by_ids(evidence, selected_ids, max_items)
    selected_ids = [item["article_id"] for item in selected_evidence]

    raw_rejected_ids = parsed.get("rejected_ids", [])
    if not isinstance(raw_rejected_ids, list):
        raw_rejected_ids = []
    rejected_ids = [str(article_id) for article_id in raw_rejected_ids if str(article_id) not in selected_ids]
    known_ids = {item["article_id"] for item in evidence}
    rejected_ids = [article_id for article_id in rejected_ids if article_id in known_ids]
    for item in evidence:
        if item["article_id"] not in selected_ids and item["article_id"] not in rejected_ids:
            rejected_ids.append(item["article_id"])

    return {
        "selected_evidence": selected_evidence,
        "selected_ids": selected_ids,
        "rejected_ids": rejected_ids,
        "reason": str(parsed.get("reason") or "질문과 직접 관련 있는 근거 후보를 다시 선별했습니다."),
    }


async def generate_grounded_draft(question: str, evidence: list[dict]) -> dict:
    settings = get_settings()
    if not settings.openai_api_key:
        return fallback_draft(question, evidence)

    evidence_text = "\n\n".join(
        [
            (
                f"[{idx}] {item['title']} ({item.get('date') or item.get('reign_date')})\n"
                f"URL: {item['official_url']}\n"
                f"원문: {item['content'][:1200]}"
            )
            for idx, item in enumerate(evidence, start=1)
        ]
    )

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 조선왕조실록 원문 기반 역사 토론 게시판의 초벌 해석 도우미다. "
                    "반드시 제공된 원문 근거 안에서만 답하고, 모르는 내용은 추정하지 말라. "
                    "JSON만 반환하라: summary, interpretation, tags."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"질문:\n{question}\n\n"
                    f"실록 원문 근거:\n{evidence_text}\n\n"
                    "summary는 2문장, interpretation은 학습자가 이해하기 쉬운 3-5문장, "
                    "tags는 한국어 태그 3-5개 배열로 작성해."
                ),
            },
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)
    return {
        "summary": parsed.get("summary", ""),
        "interpretation": parsed.get("interpretation", ""),
        "tags": parsed.get("tags", []),
    }
