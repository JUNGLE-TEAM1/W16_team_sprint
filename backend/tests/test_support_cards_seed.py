from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.seeds import SUPPORT_CARDS, seed_demo_users, seed_support_cards
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

    card_titles = [card["title"] for card in SUPPORT_CARDS]
    with Session(engine) as db:
        seeded_total = db.scalar(select(func.count(Post.id)).where(Post.title.in_(card_titles)))
        support_cards = list(db.scalars(select(Post).where(Post.title.in_(card_titles))))
        youth_tag_total = db.scalar(select(func.count(Tag.id)).where(Tag.name == "청년"))
        embedding_total = db.scalar(
            select(func.count(PostEmbedding.post_id)).where(
                PostEmbedding.post_id.in_([post.id for post in support_cards])
            )
        )

    assert len(SUPPORT_CARDS) == 50
    assert seeded_total == 50
    assert youth_tag_total == 1
    assert embedding_total == 50


def test_seed_support_cards_are_available_to_rag_assist() -> None:
    seed_support_cards(engine)

    response = client.post(
        "/api/v1/rag/assist",
        json={
            "title": "서울 거주 24세 취준생 월세 상담",
            "content": "서울 거주 24세 취준생이고 월세 60만 원을 내고 있습니다. 소득은 없고 받을 수 있는 지원이 궁금합니다.",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    match_titles = {match["title"] for match in body["matches"]}
    assert body["stored_vectors"] >= 50
    assert any("청년월세" in title or "청년수당" in title for title in match_titles)
