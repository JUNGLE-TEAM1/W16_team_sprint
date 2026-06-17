import hashlib
import json
import re
import secrets
from collections.abc import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import create_tables, get_db
from app.models import AnnalsArticle, Comment, Post, User, VoiceMessage, VoiceSession
from app.schemas import (
    AnnalsArticleOut,
    AuthRequest,
    AuthUserOut,
    CommentCreate,
    CommentOut,
    DeleteResult,
    DiscussionPrompt,
    PostCreate,
    PostDetail,
    PostListPage,
    PostUpdate,
    RealtimeTurnPlan,
    RealtimeTurnRequest,
    SearchResult,
    VoiceMessageCreate,
    VoiceMessageOut,
    VoiceSessionCreate,
    VoiceSessionOut,
)
from app.services.agent import run_post_creation_agent
from app.services.llm import rerank_evidence, stream_discussion_reply
from app.services.query_filters import KING_ALIASES, KING_PREFIX_MAP
from app.services.realtime_orchestrator import route_realtime_turn
from app.services.search import search_annals_articles
from app.services.tools import get_annals_article


app = FastAPI(title="조선왕조실록 AI 게시판 API")

PASSWORD_HASH_SCHEME = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 120_000

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


def get_or_create_user(db: Session, username: str) -> User:
    normalized_username = normalize_username(username)
    user = db.scalar(select(User).where(User.username == normalized_username))
    if user:
        return user
    user = User(username=normalized_username, password_hash=hash_password("demo-password-not-for-production"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_existing_user(db: Session, username: str) -> User:
    normalized_username = normalize_username(username)
    user = db.scalar(select(User).where(User.username == normalized_username))
    if not user:
        raise HTTPException(status_code=401, detail="로그인한 사용자만 작성할 수 있습니다.")
    return user


def normalize_username(username: str) -> str:
    return username.strip()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"{PASSWORD_HASH_SCHEME}${PASSWORD_HASH_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations, salt, expected_digest = stored_hash.split("$", 3)
    except ValueError:
        return False

    if scheme != PASSWORD_HASH_SCHEME:
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return secrets.compare_digest(actual_digest, expected_digest)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/register", response_model=AuthUserOut)
def register(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthUserOut:
    username = normalize_username(payload.username)
    existing_user = db.scalar(select(User).where(User.username == username))
    if existing_user:
        raise HTTPException(status_code=409, detail="이미 사용 중인 사용자 이름입니다.")

    user = User(username=username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthUserOut(username=user.username)


@app.post("/auth/login", response_model=AuthUserOut)
def login(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthUserOut:
    username = normalize_username(payload.username)
    user = db.scalar(select(User).where(User.username == username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="사용자 이름 또는 비밀번호가 올바르지 않습니다.")

    return AuthUserOut(username=user.username)


@app.get("/annals/search", response_model=SearchResult)
def search_annals(
    query: str = Query(min_length=1),
    limit: int = Query(default=3, ge=1, le=10),
    db: Session = Depends(get_db),
) -> SearchResult:
    articles = search_annals_articles(db, query, limit=limit)
    return SearchResult(query=query, articles=articles)


@app.post("/posts", response_model=PostDetail)
async def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> PostDetail:
    author = get_existing_user(db, payload.username)
    agent_result = await run_post_creation_agent(db, payload.question)

    post = Post(
        user_id=author.id,
        title=payload.title,
        question=payload.question,
        ai_summary=agent_result["summary"],
        ai_interpretation=agent_result["interpretation"],
        suggested_tags=agent_result["tags"],
        evidence_article_ids=[item["article_id"] for item in agent_result["evidence"]],
        agent_trace=agent_result["trace"],
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return _post_detail(db, post)


@app.get("/posts", response_model=PostListPage)
def list_posts(
    q: str = Query(default="", max_length=100),
    tag: str = Query(default="", max_length=80),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
) -> PostListPage:
    normalized_q = q.strip()
    normalized_tag = tag.strip()
    count_stmt = select(func.count(Post.id))
    list_stmt = select(Post).order_by(desc(Post.created_at))

    if normalized_q:
        like_q = f"%{normalized_q}%"
        search_filter = or_(
            Post.title.ilike(like_q),
            Post.question.ilike(like_q),
            Post.ai_summary.ilike(like_q),
            Post.ai_interpretation.ilike(like_q),
        )
        count_stmt = count_stmt.where(search_filter)
        list_stmt = list_stmt.where(search_filter)

    if normalized_tag:
        tag_filter = Post.suggested_tags.contains([normalized_tag])
        count_stmt = count_stmt.where(tag_filter)
        list_stmt = list_stmt.where(tag_filter)

    total = db.scalar(count_stmt) or 0
    pages = max(1, (total + size - 1) // size)
    current_page = min(page, pages)
    offset = (current_page - 1) * size
    items = list(db.scalars(list_stmt.offset(offset).limit(size)))

    return PostListPage(items=items, total=total, page=current_page, size=size, pages=pages)


@app.get("/posts/{post_id}", response_model=PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)) -> PostDetail:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_detail(db, post)


@app.put("/posts/{post_id}", response_model=PostDetail)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)) -> PostDetail:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.title = payload.title
    db.commit()
    db.refresh(post)
    return _post_detail(db, post)


@app.delete("/posts/{post_id}", response_model=DeleteResult)
def delete_post(post_id: int, db: Session = Depends(get_db)) -> DeleteResult:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return DeleteResult(deleted_id=post_id)


@app.post("/posts/{post_id}/comments", response_model=CommentOut)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_db)) -> CommentOut:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    author = get_existing_user(db, payload.username)
    comment = Comment(post_id=post.id, user_id=author.id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _comment_out(comment)


@app.post("/posts/{post_id}/voice-sessions", response_model=VoiceSessionOut)
def create_voice_session(
    post_id: int,
    payload: VoiceSessionCreate,
    db: Session = Depends(get_db),
) -> VoiceSessionOut:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    author = get_existing_user(db, payload.username)
    voice_session = VoiceSession(post_id=post.id, user_id=author.id)
    db.add(voice_session)
    db.commit()
    db.refresh(voice_session)
    return _voice_session_out(voice_session)


@app.get("/posts/{post_id}/voice-messages", response_model=list[VoiceMessageOut])
def list_voice_messages(
    post_id: int,
    limit: int = Query(default=80, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[VoiceMessageOut]:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    messages = list(
        db.scalars(
            select(VoiceMessage)
            .where(VoiceMessage.post_id == post.id)
            .order_by(desc(VoiceMessage.created_at), desc(VoiceMessage.id))
            .limit(limit)
        )
    )
    return [_voice_message_out(message) for message in reversed(messages)]


@app.post(
    "/posts/{post_id}/voice-sessions/{session_id}/messages",
    response_model=VoiceMessageOut,
)
def create_voice_message(
    post_id: int,
    session_id: int,
    payload: VoiceMessageCreate,
    db: Session = Depends(get_db),
) -> VoiceMessageOut:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    voice_session = db.get(VoiceSession, session_id)
    if not voice_session or voice_session.post_id != post.id:
        raise HTTPException(status_code=404, detail="Voice session not found")

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="음성 대화 내용이 비어 있습니다.")

    voice_message = VoiceMessage(
        session_id=voice_session.id,
        post_id=post.id,
        user_id=voice_session.user_id,
        role=payload.role,
        content=content,
        route_action=payload.route_action,
        route_reason=payload.route_reason,
        search_query=payload.search_query,
        evidence_article_ids=payload.evidence_article_ids,
    )
    db.add(voice_message)
    db.commit()
    db.refresh(voice_message)
    return _voice_message_out(voice_message)


@app.post("/posts/{post_id}/ai-discussion/stream")
async def stream_ai_discussion(
    post_id: int,
    payload: DiscussionPrompt,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_context = {
        "title": post.title,
        "question": post.question,
        "ai_summary": post.ai_summary,
        "ai_interpretation": post.ai_interpretation,
    }
    evidence = [
        _article_dict(article)
        for article_id in post.evidence_article_ids
        if (article := get_annals_article(db, article_id))
    ]
    comments = [_comment_dict(comment) for comment in post.comments]

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for chunk in stream_discussion_reply(payload.message, post_context, evidence, comments):
                yield _sse_event("token", {"text": chunk})
            yield _sse_event("done", {})
        except Exception:
            yield _sse_event("error", {"message": "AI 토론 답변 생성 중 오류가 발생했습니다."})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/posts/{post_id}/realtime/session")
async def create_realtime_discussion_session(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY가 필요합니다.")

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    offer_sdp = _decode_offer_sdp(await request.body())
    if not offer_sdp.strip():
        raise HTTPException(status_code=400, detail="WebRTC offer SDP가 필요합니다.")
    sdp_debug = {
        "received_sdp_length": len(offer_sdp),
        "sdp_preview": offer_sdp[:40],
        "ends_with_crlf": offer_sdp.endswith("\r\n"),
    }

    evidence = [
        _article_dict(article)
        for article_id in post.evidence_article_ids
        if (article := get_annals_article(db, article_id))
    ]
    comments = [_comment_dict(comment) for comment in post.comments]
    session_config = _realtime_session_config(post, evidence, comments)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/calls",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "OpenAI-Safety-Identifier": _safety_identifier(post_id),
            },
            files={
                "sdp": (None, offer_sdp),
                "session": (None, json.dumps(session_config, ensure_ascii=False)),
            },
        )

    if response.status_code >= 400:
        detail = response.text[:800] or "OpenAI Realtime 세션 생성에 실패했습니다."
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI Realtime 오류 ({response.status_code}): {detail} / debug={sdp_debug}",
        )

    return Response(content=response.text, media_type="application/sdp")


@app.post("/posts/{post_id}/realtime/turn/route", response_model=RealtimeTurnPlan)
async def route_realtime_discussion_turn(
    post_id: int,
    payload: RealtimeTurnRequest,
    db: Session = Depends(get_db),
) -> RealtimeTurnPlan:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    evidence = _post_evidence(db, post)
    decision = await route_realtime_turn(payload.transcript, _post_context(post), evidence)
    return RealtimeTurnPlan(
        action=decision["action"],
        reason=decision["reason"],
        search_query=decision["search_query"],
        events=_route_events(decision["action"]),
    )


@app.post("/posts/{post_id}/realtime/turn/retrieve", response_model=RealtimeTurnPlan)
async def retrieve_realtime_discussion_turn(
    post_id: int,
    payload: RealtimeTurnRequest,
    db: Session = Depends(get_db),
) -> RealtimeTurnPlan:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    search_query = _realtime_search_query(post, payload.transcript, payload.search_query)
    search_results = search_annals_articles(db, search_query, limit=6)
    existing_article_ids = set(post.evidence_article_ids)
    additional_articles = [article for article in search_results if article.article_id not in existing_article_ids]
    candidate_articles = additional_articles or search_results
    candidate_evidence = [_article_dict(article) for article in candidate_articles]
    rerank_result = await rerank_evidence(search_query, candidate_evidence, max_items=3)
    selected_evidence = rerank_result["selected_evidence"]

    return RealtimeTurnPlan(
        action="retrieve",
        reason=rerank_result["reason"],
        search_query=search_query,
        events=_retrieval_events(payload.transcript, selected_evidence),
        evidence_article_ids=[item["article_id"] for item in selected_evidence],
    )


def _decode_offer_sdp(body: bytes) -> str:
    return body.decode("utf-8")


def _post_context(post: Post) -> dict:
    return {
        "title": post.title,
        "question": post.question,
        "ai_summary": post.ai_summary,
        "ai_interpretation": post.ai_interpretation,
    }


def _post_evidence(db: Session, post: Post) -> list[dict]:
    return [
        _article_dict(article)
        for article_id in post.evidence_article_ids
        if (article := get_annals_article(db, article_id))
    ]


def _realtime_search_query(post: Post, transcript: str, search_query: str | None = None) -> str:
    base_query = (search_query or transcript).strip()
    target_king = _first_king(transcript)
    if not target_king:
        return base_query

    post_text = f"{post.title} {post.question} {post.ai_summary} {post.ai_interpretation}"
    post_without_kings = _remove_kings(post_text)
    topic_terms = []
    if any(term in post_text for term in ["위대한", "위대", "업적", "평가"]):
        topic_terms.append("업적 정책 제도 즉위 왕위")
    if "건국" in post_text:
        topic_terms.append("건국 즉위 국가 기틀 제도")
    if "정도전" in post_text or "조선경국전" in post_text:
        topic_terms.append("정도전 법전 조선경국전")
    if "왕자의 난" in post_text:
        topic_terms.append("왕자의 난 권력 다툼 왕위 계승")

    compact_topic = re.sub(r"[?!？!.,，。]", " ", post_without_kings)
    compact_topic = re.sub(r"\s+", " ", compact_topic).strip()
    parts = [target_king, *topic_terms, compact_topic[:120], _remove_kings(base_query)]
    return re.sub(r"\s+", " ", " ".join(part for part in parts if part).strip())


def _first_king(text: str) -> str | None:
    for king in KING_PREFIX_MAP:
        if king in text:
            return king
    return None


def _remove_kings(text: str) -> str:
    without_kings = text
    for king in KING_PREFIX_MAP:
        without_kings = without_kings.replace(king, " ")
    for alias in KING_ALIASES:
        without_kings = without_kings.replace(alias, " ")
    return re.sub(r"\s+", " ", without_kings).strip()


def _post_detail(db: Session, post: Post) -> PostDetail:
    evidence_articles = []
    for article_id in post.evidence_article_ids:
        article = get_annals_article(db, article_id)
        if article:
            evidence_articles.append(AnnalsArticleOut.model_validate(article))

    return PostDetail(
        id=post.id,
        title=post.title,
        question=post.question,
        ai_summary=post.ai_summary,
        ai_interpretation=post.ai_interpretation,
        suggested_tags=post.suggested_tags,
        evidence_article_ids=post.evidence_article_ids,
        agent_trace=post.agent_trace,
        created_at=post.created_at,
        evidence_articles=evidence_articles,
        comments=[_comment_out(comment) for comment in post.comments],
    )


def _comment_out(comment: Comment) -> CommentOut:
    return CommentOut(
        id=comment.id,
        post_id=comment.post_id,
        username=comment.author.username,
        content=comment.content,
        created_at=comment.created_at,
    )


def _voice_session_out(voice_session: VoiceSession) -> VoiceSessionOut:
    return VoiceSessionOut(
        id=voice_session.id,
        post_id=voice_session.post_id,
        username=voice_session.author.username,
        created_at=voice_session.created_at,
    )


def _voice_message_out(message: VoiceMessage) -> VoiceMessageOut:
    return VoiceMessageOut(
        id=message.id,
        session_id=message.session_id,
        post_id=message.post_id,
        username=message.author.username,
        role=message.role,
        content=message.content,
        route_action=message.route_action,
        route_reason=message.route_reason,
        search_query=message.search_query,
        evidence_article_ids=message.evidence_article_ids,
        created_at=message.created_at,
    )


def _comment_dict(comment: Comment) -> dict:
    return {
        "username": comment.author.username,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
    }


def _article_dict(article: AnnalsArticle) -> dict:
    return {
        "article_id": article.article_id,
        "title": article.title,
        "king": article.king,
        "reign_date": article.reign_date,
        "date": article.date,
        "content": article.content,
        "official_url": article.official_url,
        "subject_classes": article.subject_classes,
    }


def _sse_event(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _realtime_response_event(instructions: str) -> dict:
    return {
        "type": "response.create",
        "response": {
            "instructions": instructions,
        },
    }


def _realtime_system_item_event(text: str) -> dict:
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "system",
            "content": [{"type": "input_text", "text": text}],
        },
    }


def _route_events(action: str) -> list[dict]:
    if action == "retrieve":
        return [
            _realtime_response_event(
                "정확히 다음 문장만 한국어 존댓말로 말하세요. 다른 말은 덧붙이지 마세요. "
                "'잠시만요, 기록의 맥락을 보고 말씀드리겠습니다.'"
            )
        ]
    if action == "out_of_scope":
        return [
            _realtime_response_event(
                "한국어 존댓말로 짧고 자연스럽게 답하세요. "
                "질문이 제공된 기록 맥락과 떨어져 있으면 '그건 기록에서 바로 확인되는 내용은 아닙니다만' 정도로 한 번만 짧게 구분하세요. "
                "그 뒤 일반 배경지식으로 답할 수 있는 범위만 답하세요. 최신 정보, 투자, 의료, 법률처럼 확인이 필요한 내용은 단정하지 마세요. "
                "출처 원칙을 설명하는 문구를 반복하지 마세요. "
                "기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 마세요."
            )
        ]
    if action == "clarify":
        return [
            _realtime_response_event(
                "한국어 존댓말로 짧게 다시 물어보세요. "
                "사용자가 조선왕조실록과 관련해 무엇을 더 알고 싶은지 자연스럽게 확인하세요. "
                "기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 마세요."
            )
        ]
    return [
        _realtime_response_event(
            "현재 세션에 제공된 게시글 자료와 최근 사용자 발화를 바탕으로 한국어 존댓말 음성 답변을 하세요. "
            "답변은 대화하듯 바로 시작하고, 출처 원칙을 매번 설명하지 마세요. "
            "기록에 직접 확인되는 내용과 일반 배경 설명은 조용히 구분하되, 필요할 때만 '기록상으로는' 정도로 짧게 말하세요. "
            "출처 원칙을 설명하는 문구를 반복하지 마세요. "
            "기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 마세요."
        )
    ]


def _retrieval_events(transcript: str, evidence: list[dict]) -> list[dict]:
    if not evidence:
        return [
            _realtime_response_event(
                "한국어 존댓말로 짧고 자연스럽게 답하세요. "
                "현재 연결된 기록만으로 답할 수 있는 범위와 답하기 어려운 부분을 부드럽게 구분하세요. "
                "일반 배경지식으로 보충해야 한다면 '기록에서 바로 확인되는 내용은 아닙니다만'처럼 한 번만 짧게 말하세요. "
                "출처 원칙을 설명하는 문구를 반복하지 마세요. "
                "기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 마세요."
            )
        ]

    evidence_text = _realtime_evidence_text(evidence)
    return [
        _realtime_system_item_event(
            "사용자 발화와 관련해 확인된 기록 발췌입니다. "
            "다음 최종 답변은 이 발췌와 기존 게시글 자료를 우선 사용하세요. "
            "자료 밖 일반 배경지식을 덧붙일 때는 필요한 경우에만 짧게 구분하세요. "
            "출처 원칙을 설명하는 문구를 반복하지 마세요.\n\n"
            f"사용자 발화:\n{transcript}\n\n"
            f"추가 기록 발췌:\n{evidence_text}"
        ),
        _realtime_response_event(
            "방금 확인한 기록을 우선 사용해서 한국어 존댓말로 짧고 자연스럽게 답하세요. "
            "답변은 대화하듯 바로 시작하고, 출처 원칙을 매번 설명하지 마세요. "
            "기사 ID를 굳이 말하지 말고, 필요하면 기사 제목이나 날짜만 가볍게 언급하세요. "
            "일반 배경지식을 덧붙일 때는 필요한 경우에만 '기록에서 바로 확인되는 내용은 아닙니다만'처럼 한 번만 짧게 말하세요. "
            "출처 원칙을 설명하는 문구를 반복하지 마세요. "
            "기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 마세요."
        ),
    ]


def _realtime_evidence_text(evidence: list[dict]) -> str:
    return "\n\n".join(
        [
            (
                f"[{index}] {item['title']} ({item.get('date') or item.get('reign_date') or '날짜 미상'})\n"
                f"기사 ID: {item['article_id']}\n"
                f"원문 일부: {item['content'][:450]}"
            )
            for index, item in enumerate(evidence[:3], start=1)
        ]
    )


def _realtime_session_config(post: Post, evidence: list[dict], comments: list[dict]) -> dict:
    settings = get_settings()
    evidence_text = "\n\n".join(
        [
            (
                f"[{index}] {item['title']} ({item.get('date') or item.get('reign_date') or '날짜 미상'})\n"
                f"기사 ID: {item['article_id']}\n"
                f"원문 일부: {item['content'][:700]}"
            )
            for index, item in enumerate(evidence[:4], start=1)
        ]
    )
    comment_text = "\n".join(
        [f"- {item['username']}: {item['content']}" for item in comments[-6:]]
    )
    instructions = (
        "너는 조선왕조실록 원문 기반 역사 토론 게시판의 음성 토론 도우미다. "
        "사용자와 자연스럽게 한국어 음성으로 대화한다. "
        "항상 존댓말만 사용하고 반말은 절대 쓰지 않는다. "
        "우선순위는 제공된 게시글 맥락과 기록 발췌다. "
        "답변은 먼저 대화하듯 자연스럽게 시작하고, 출처 원칙을 매번 앞세우지 않는다. "
        "기록에 직접 확인되는 내용과 일반 배경 설명은 구분하되, 구분 문구는 꼭 필요할 때만 한 번 짧게 쓴다. "
        "출처 원칙을 설명하는 문구를 반복하지 않는다. "
        "기록에 없는 내용을 기록에 있는 것처럼 단정하지 않는다. "
        "기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 않는다. "
        "답변은 20초 안에 들을 수 있게 짧고 또렷하게 말한다.\n\n"
        f"게시글 제목: {post.title}\n"
        f"게시글 질문: {post.question}\n"
        f"기존 AI 요약: {post.ai_summary}\n"
        f"기존 AI 해석: {post.ai_interpretation}\n\n"
        f"제공된 기록 발췌:\n{evidence_text or '연결된 기록 발췌 없음'}\n\n"
        f"최근 댓글:\n{comment_text or '아직 댓글 없음'}"
    )
    return {
        "type": "realtime",
        "model": settings.openai_realtime_model,
        "instructions": instructions,
        "output_modalities": ["audio"],
        "audio": {
            "input": {
                "transcription": {
                    "model": "gpt-4o-mini-transcribe",
                    "language": "ko",
                    "prompt": "조선왕조실록, 한국사, 왕명, 인명, 관직명이 포함된 한국어 발화를 정확히 전사한다.",
                },
                "turn_detection": {
                    "type": "server_vad",
                    "create_response": False,
                },
            },
            "output": {
                "voice": settings.openai_realtime_voice,
            },
        },
    }


def _safety_identifier(post_id: int) -> str:
    digest = hashlib.sha256(f"annals-board-post-{post_id}".encode("utf-8")).hexdigest()
    return digest[:32]
