from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.seeds import seed_demo_users, seed_support_cards
from backend.app.db.session import engine
from backend.app.main import app
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.models.tag import Tag

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_demo_users(engine)


def test_seed_support_cards_is_idempotent_and_indexes_posts() -> None:
    with Session(engine) as db:
        db.add(Tag(name="청년"))
        db.commit()

    seed_support_cards(engine)
    seed_support_cards(engine)

    with Session(engine) as db:
        support_cards = list(db.scalars(select(Post).where(Post.author_name == "data-bot")))
        seeded_total = len(support_cards)
        youth_tag_total = db.scalar(select(func.count(Tag.id)).where(Tag.name == "청년"))
        embedding_total = db.scalar(
            select(func.count(PostEmbedding.post_id)).where(
                PostEmbedding.post_id.in_([post.id for post in support_cards])
            )
        )

    assert seeded_total == 3
    assert youth_tag_total == 1
    assert embedding_total == 3


def test_seed_support_cards_are_available_to_rag_assist() -> None:
    seed_support_cards(engine)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "수원시 거주 24세 청년 월세 상담",
            "content": "경기도 수원시 거주 24세 청년이고 월세 60만 원을 내고 있습니다. 받을 수 있는 지원이 궁금합니다.",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    match_titles = {match["title"] for match in body["matches"]}
    assert body["stored_vectors"] >= 3
    assert any("청년월세" in title for title in match_titles)
