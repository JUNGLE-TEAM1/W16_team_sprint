import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.embedding import EmbeddingError, embed_text
from backend.app.core.security import hash_password
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.models.tag import Tag
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


def seed_demo_users(database_engine) -> None:
    with Session(database_engine) as db:
        users = UserRepository(db)
        demo_users = [
            {
                "email": "member@sprint.local",
                "password": "password123",
                "role": "member",
            },
            {
                "email": "admin@sprint.local",
                "password": "admin123",
                "role": "admin",
            },
        ]

        for demo_user in demo_users:
            if users.get_by_email(demo_user["email"]) is None:
                users.create(
                    User(
                        email=demo_user["email"],
                        password_hash=hash_password(demo_user["password"]),
                        role=demo_user["role"],
                    )
                )

        db.commit()


SPRINT_POSTS = [
    {
        "number": 1,
        "title": "Sprint 1. API 계약과 데이터 흐름",
        "content": """요청 하나가 프론트엔드에서 백엔드, 데이터베이스, 응답까지 어떤 흐름으로 지나가는지 확인하는 기준 스프린트입니다.

핵심 흐름은 `클라이언트 요청 -> API 라우터 -> 검증 스키마 -> 서비스 -> 레포지토리 -> DB -> 응답/에러`입니다. 게시글 생성 요청을 기준으로 리소스 endpoint, request body, response schema, transaction, 404 error 위치를 설명할 수 있어야 합니다.

완료 기준은 팀원 모두가 게시글 생성 요청 하나를 `프론트 -> 라우터 -> 서비스 -> 레포지토리 -> DB -> 응답` 흐름으로 말할 수 있는 것입니다.""",
        "tags": ["sprint", "api", "data-flow", "backend"],
    },
    {
        "number": 2,
        "title": "Sprint 2. 회원가입과 로그인, 인증/인가",
        "content": """로그인과 인증이 필요한 API를 호출할 때 서버와 클라이언트가 어떤 책임을 나눠 가지는지 구현으로 확인합니다.

회원가입과 로그인은 token pair를 발급하고, 보호 API는 `Authorization: Bearer <access_token>`으로 호출합니다. 서버는 JWT 서명, 만료, token type, session 상태, role을 검증합니다. 인증 실패는 401, 권한 부족은 403으로 구분합니다.

완료 기준은 회원가입과 로그인이 되고, 로그인 사용자만 글 작성/수정/삭제가 가능하며 프론트엔드에서 로그인 상태를 실제 기능에 사용할 수 있는 것입니다.""",
        "tags": ["sprint", "auth", "security", "jwt"],
    },
    {
        "number": 3,
        "title": "Sprint 3. 게시글 CRUD, 댓글, 태그",
        "content": """게시판의 기본 리소스 관계를 실제 기능으로 붙이는 스프린트입니다.

게시글 CRUD, 댓글 작성/조회/삭제, 태그 생성/연결/조회가 동작해야 합니다. 학습 포인트는 `User -> Post`, `Post -> Comment`, `Post -> Tag`, `Tag -> Post` 관계입니다. 특히 태그는 N:M 관계가 가능하므로 join table, index, PK/FK 개념을 함께 확인합니다.

구현은 router, service, repository, schema, model 책임을 기능별로 나눠 유지합니다.""",
        "tags": ["sprint", "crud", "comments", "tags"],
    },
    {
        "number": 4,
        "title": "Sprint 4. 페이지 검색과 목록 UX",
        "content": """게시판 데이터를 사용자가 탐색할 수 있게 만드는 스프린트입니다.

게시글 목록은 페이지 단위로 조회하고, 검색어로 제목/내용을 찾을 수 있어야 하며, 태그 기반 필터링도 가능해야 합니다. 프론트엔드에서는 페이지 이동, 검색, 태그 필터, 검색 결과 없음, 로딩, 에러 상태가 모두 화면에 보여야 합니다.

이 스프린트는 RAG와도 연결됩니다. 기본 검색 구조를 이해해야 일반 검색과 AI 기반 관련 글 탐색의 차이를 설명할 수 있습니다.""",
        "tags": ["sprint", "frontend", "search", "paging"],
    },
    {
        "number": 6,
        "title": "Sprint 6. RAG 중복 검색과 관련 글 추천",
        "content": """게시판 내부 데이터만 사용해서 글 작성 중 비슷한 기존 글을 찾는 RAG 흐름을 구현합니다.

글 작성/수정 시 title, content, tag 텍스트를 embedding하고 `post_embeddings` 테이블에 vector_json으로 저장합니다. 작성 폼의 RAG duplicate check 버튼은 `POST /api/v1/rag/assist`를 호출하고, 현재 초안과 기존 글 embedding의 유사도를 계산해 후보 게시글과 중복 위험도를 찾습니다.

후보를 찾은 뒤에는 OpenAI Responses API의 LLM을 사용해 추천 문구와 후보별 요약을 생성합니다. `OPENAI_API_KEY`가 없는 로컬 테스트 환경에서만 규칙 기반 fallback을 사용하고, 키가 있는데 LLM 호출이 실패하면 실패를 명확히 반환합니다.""",
        "tags": ["sprint", "rag", "embedding", "llm"],
    },
]


def seed_sprint_posts(database_engine) -> None:
    with Session(database_engine) as db:
        admin_user = db.scalar(select(User).where(User.email == "admin@sprint.local"))
        if admin_user is None:
            seed_demo_users(database_engine)
            admin_user = db.scalar(select(User).where(User.email == "admin@sprint.local"))

        if admin_user is None:
            return

        for sprint_post in SPRINT_POSTS:
            tags = [_get_or_create_tag(db, tag_name) for tag_name in sprint_post["tags"]]
            existing_post = _find_existing_sprint_post(db, sprint_post)
            if existing_post is not None:
                existing_post.title = sprint_post["title"]
                existing_post.content = sprint_post["content"]
                existing_post.author_name = "Sprint Team"
                existing_post.user_id = admin_user.id
                existing_post.tags = tags
                _ensure_post_embedding(db, existing_post)
                continue

            post = Post(
                title=sprint_post["title"],
                content=sprint_post["content"],
                author_name="Sprint Team",
                user_id=admin_user.id,
                tags=tags,
            )
            db.add(post)
            db.flush()
            _ensure_post_embedding(db, post)

        db.commit()


def _find_existing_sprint_post(db: Session, sprint_post: dict[str, object]) -> Post | None:
    title = str(sprint_post["title"])
    existing_post = db.scalar(select(Post).where(Post.title == title))
    if existing_post is not None:
        return existing_post

    number = int(sprint_post["number"])
    return db.scalar(
        select(Post).where(
            Post.author_name == "Sprint Team",
            Post.title.like(f"Sprint {number}.%"),
        )
    )


def _get_or_create_tag(db: Session, tag_name: str) -> Tag:
    normalized_name = tag_name.strip().lower().lstrip("#")
    tag = db.scalar(select(Tag).where(Tag.name == normalized_name))
    if tag is not None:
        return tag

    tag = Tag(name=normalized_name)
    db.add(tag)
    db.flush()
    return tag


def _ensure_post_embedding(db: Session, post: Post) -> None:
    source_text = f"{post.title}\n{post.content}\n{' '.join(tag.name for tag in post.tags)}".strip()
    try:
        vector = embed_text(source_text)
    except EmbeddingError:
        return

    embedding = db.get(PostEmbedding, post.id)
    if embedding is None:
        db.add(
            PostEmbedding(
                post_id=post.id,
                source_text=source_text,
                vector_json=json.dumps(vector),
            )
        )
        db.flush()
        return

    embedding.source_text = source_text
    embedding.vector_json = json.dumps(vector)
