from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.seeds import SPRINT_POSTS, seed_demo_users, seed_sprint_posts
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_demo_users(engine)


def test_seed_sprint_posts_is_idempotent_and_indexes_posts() -> None:
    seed_sprint_posts(engine)
    seed_sprint_posts(engine)

    sprint_titles = [post["title"] for post in SPRINT_POSTS]
    with Session(engine) as db:
        seeded_total = db.scalar(select(func.count(Post.id)).where(Post.title.in_(sprint_titles)))
        sprint_posts = list(db.scalars(select(Post).where(Post.title.in_(sprint_titles))))
        embedding_total = db.scalar(
            select(func.count(PostEmbedding.post_id)).where(
                PostEmbedding.post_id.in_([post.id for post in sprint_posts])
            )
        )

    assert seeded_total == 5
    assert embedding_total == 5


def test_seed_sprint_posts_are_available_to_rag_assist() -> None:
    seed_sprint_posts(engine)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "RAG 중복 검색과 관련 글 추천",
            "content": "게시글 embedding을 저장하고 유사 게시글을 찾아 중복 위험도를 보고 싶습니다.",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    sprint6_title = next(post["title"] for post in SPRINT_POSTS if post["number"] == 6)
    assert body["stored_vectors"] >= 5
    assert any(match["title"] == sprint6_title for match in body["matches"])
