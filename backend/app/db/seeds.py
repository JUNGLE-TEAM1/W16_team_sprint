from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.embedding import embed_text, embedding_dimensions, embedding_signature
from backend.app.core.security import hash_password
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.models.tag import Tag
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class SuwonYouthPolicyDataset:
    year: str
    uddi: str

    @property
    def endpoint(self) -> str:
        base_url = settings.suwon_youth_policy_api_base_url.rstrip("/")
        return f"{base_url}/15089956/v1/uddi:{self.uddi}"

    @property
    def swagger_url(self) -> str:
        return "https://infuser.odcloud.kr/oas/docs?namespace=15089956/v1"


SUWON_YOUTH_POLICY_DATASETS = (
    SuwonYouthPolicyDataset("2021", "d2b6d077-8272-4219-b965-ac3dca6d0d8b"),
    SuwonYouthPolicyDataset("2022", "b99faab3-3489-48c5-b846-f751aed59a2a"),
    SuwonYouthPolicyDataset("2023", "69880ec1-eaa7-4267-8f1e-9d6bc210c493"),
    SuwonYouthPolicyDataset("2024", "a44dd5bb-4f85-41d0-a75c-bf32b49e412a"),
    SuwonYouthPolicyDataset("2025", "088153f3-7fd0-4c44-a6d4-dcc8ac26cbc8"),
)


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


def seed_support_cards(database_engine) -> None:
    cards = fetch_suwon_youth_policy_cards()
    if not cards:
        return

    with Session(database_engine) as db:
        admin_user = db.scalar(select(User).where(User.email == "admin@sprint.local"))
        if admin_user is None:
            seed_demo_users(database_engine)
            admin_user = db.scalar(select(User).where(User.email == "admin@sprint.local"))

        if admin_user is None:
            return

        card_titles = {str(card["title"]) for card in cards}
        _delete_replaced_support_cards(db, card_titles)
        _delete_legacy_sprint_cards(db)

        for card in cards:
            tags = [_get_or_create_tag(db, tag_name) for tag_name in card["tags"]]
            existing_post = _find_existing_support_card(db, card)
            if existing_post is not None:
                existing_post.title = str(card["title"])
                existing_post.content = str(card["content"])
                existing_post.author_name = "data-bot"
                existing_post.user_id = admin_user.id
                existing_post.tags = tags
                _ensure_post_embedding(db, existing_post)
                continue

            post = Post(
                title=str(card["title"]),
                content=str(card["content"]),
                author_name="data-bot",
                user_id=admin_user.id,
                tags=tags,
            )
            db.add(post)
            db.flush()
            _ensure_post_embedding(db, post)

        db.commit()


def fetch_suwon_youth_policy_cards() -> list[dict[str, object]]:
    rows: list[tuple[SuwonYouthPolicyDataset, dict[str, Any]]] = []
    for dataset in SUWON_YOUTH_POLICY_DATASETS:
        rows.extend((dataset, row) for row in _fetch_suwon_dataset_rows(dataset))
    return normalize_suwon_youth_policy_rows(rows)


def normalize_suwon_youth_policy_rows(
    rows: list[tuple[SuwonYouthPolicyDataset, dict[str, Any]]],
) -> list[dict[str, object]]:
    cards: list[dict[str, object]] = []
    title_counts: Counter[str] = Counter()

    for dataset, row in rows:
        base_title = _card_title(dataset, row)
        title_counts[base_title] += 1
        title = base_title
        if title_counts[base_title] > 1:
            suffix = f" #{title_counts[base_title]}"
            title = f"{base_title[: 120 - len(suffix)]}{suffix}"

        cards.append(
            {
                "title": title,
                "content": _card_content(dataset, row),
                "tags": _card_tags(dataset, row),
            }
        )

    return cards


def normalize_support_card_record(
    *,
    title: str,
    target: str = "",
    support: str = "",
    period: str = "",
    region: str = "",
    contact: str = "",
    source_url: str = "",
    tags: list[str] | None = None,
) -> dict[str, object]:
    return {
        "title": title.strip(),
        "content": "\n".join(
            line
            for line in [
                f"지원대상: {target}",
                f"지원내용: {support}",
                f"신청기간: {period}",
                f"지역: {region}",
                f"문의처: {contact}",
                f"출처 URL: {source_url}",
            ]
            if line.split(": ", 1)[-1]
        ),
        "tags": tags or [],
    }


def _fetch_suwon_dataset_rows(dataset: SuwonYouthPolicyDataset) -> list[dict[str, Any]]:
    api_key = settings.suwon_youth_policy_api_key.strip()
    if not api_key:
        return []

    rows: list[dict[str, Any]] = []
    page = 1
    per_page = settings.suwon_youth_policy_api_per_page

    with httpx.Client(timeout=settings.suwon_youth_policy_api_timeout_seconds) as client:
        while True:
            response = client.get(_dataset_url(dataset, page=page, per_page=per_page, api_key=api_key))
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", [])
            if not isinstance(data, list):
                return rows

            rows.extend(row for row in data if isinstance(row, dict))

            total_count = int(payload.get("totalCount") or len(rows))
            current_count = int(payload.get("currentCount") or len(data))
            if not data or current_count == 0 or len(rows) >= total_count:
                return rows
            page += 1


def _dataset_url(
    dataset: SuwonYouthPolicyDataset,
    *,
    page: int,
    per_page: int,
    api_key: str,
) -> str:
    return (
        f"{dataset.endpoint}"
        f"?page={page}"
        f"&perPage={per_page}"
        f"&returnType=JSON"
        f"&serviceKey={api_key}"
    )


def _card_title(dataset: SuwonYouthPolicyDataset, row: dict[str, Any]) -> str:
    name = _text(row.get("사업명")) or "청년지원사업"
    return f"[수원청년/{dataset.year}] {name}"[:120]


def _card_content(dataset: SuwonYouthPolicyDataset, row: dict[str, Any]) -> str:
    start_month = _text(row.get("사업시작월"))
    end_month = _text(row.get("사업종료월"))
    period = " ~ ".join(value for value in [start_month, end_month] if value)
    source_url = _source_url(dataset, row)

    lines = [
        f"사업명: {_text(row.get('사업명'))}",
        f"사업내용: {_text(row.get('사업내용'))}",
        f"사업기간: {period}",
        "지역: 경기도 수원시",
        f"관리부서: {_text(row.get('관리부서명'))}",
        f"전화번호: {_text(row.get('전화번호'))}",
        f"도로명주소: {_text(row.get('소재지도로명주소'))}",
        f"지번주소: {_text(row.get('소재지지번주소'))}",
        f"위도/경도: {_text(row.get('위도'))}, {_text(row.get('경도'))}",
        f"데이터기준일자: {_text(row.get('데이터기준일자')) or dataset.year}",
        f"상세 URL: {source_url}",
        f"원본 API: {dataset.endpoint}",
    ]
    return "\n".join(line for line in lines if line.split(": ", 1)[-1].strip(" ,"))


def _card_tags(dataset: SuwonYouthPolicyDataset, row: dict[str, Any]) -> list[str]:
    text = f"{_text(row.get('사업명'))} {_text(row.get('사업내용'))}".lower()
    tags = ["수원시", "경기도", "청년", "청년정책", dataset.year]
    keyword_tags = (
        ("주거", ("월세", "임차", "주거", "전월세")),
        ("월세", ("월세", "임차료")),
        ("취업", ("취업", "구직", "일자리", "면접", "직장")),
        ("창업", ("창업", "스타트업", "기업")),
        ("교육", ("교육", "강의", "강좌", "학습", "어학", "훈련")),
        ("금융", ("금융", "저축", "통장", "자산", "대출")),
        ("문화", ("문화", "예술", "축제", "활동")),
        ("상담", ("상담", "멘토", "컨설팅", "코칭")),
        ("복지", ("지원", "복지", "수당", "급여")),
        ("교통", ("교통", "버스", "통학")),
        ("공간", ("공간", "센터", "시설")),
    )
    for tag, keywords in keyword_tags:
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    return list(dict.fromkeys(tags))


def _source_url(dataset: SuwonYouthPolicyDataset, row: dict[str, Any]) -> str:
    raw_url = _text(row.get("비고"))
    if raw_url.startswith(("http://", "https://")):
        return raw_url
    return dataset.swagger_url


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _find_existing_support_card(db: Session, card: dict[str, object]) -> Post | None:
    return db.scalar(
        select(Post).where(
            Post.author_name == "data-bot",
            Post.title == str(card["title"]),
        )
    )


def _delete_replaced_support_cards(db: Session, keep_titles: set[str]) -> None:
    if not keep_titles:
        return

    stale_posts = db.scalars(
        select(Post).where(
            Post.author_name == "data-bot",
            Post.title.not_in(keep_titles),
        )
    ).all()
    for post in stale_posts:
        db.delete(post)
    if stale_posts:
        db.flush()


def _delete_legacy_sprint_cards(db: Session) -> None:
    legacy_posts = db.scalars(
        select(Post).where(
            Post.author_name == "Sprint Team",
            Post.title.like("Sprint %.%"),
        )
    ).all()
    for post in legacy_posts:
        db.delete(post)
    if legacy_posts:
        db.flush()


def _get_or_create_tag(db: Session, tag_name: str) -> Tag:
    normalized_name = tag_name.strip().lower().lstrip("#")
    with db.no_autoflush:
        tag = db.scalar(select(Tag).where(Tag.name == normalized_name))
    if tag is not None:
        return tag

    dialect_name = db.get_bind().dialect.name
    if dialect_name == "postgresql":
        statement = (
            postgresql_insert(Tag)
            .values(name=normalized_name)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        db.execute(statement)
    elif dialect_name == "sqlite":
        statement = (
            sqlite_insert(Tag)
            .values(name=normalized_name)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        db.execute(statement)
    else:
        db.add(Tag(name=normalized_name))

    db.flush()
    with db.no_autoflush:
        tag = db.scalar(select(Tag).where(Tag.name == normalized_name))
    if tag is None:
        raise RuntimeError(f"Failed to create or load tag: {normalized_name}")
    return tag


def _ensure_post_embedding(db: Session, post: Post) -> None:
    source_text = f"{post.title}\n{post.content}\n{' '.join(tag.name for tag in post.tags)}".strip()
    indexed_source_text = _indexed_source_text(source_text)

    embedding = db.get(PostEmbedding, post.id)
    if (
        embedding is not None
        and embedding.source_text == indexed_source_text
        and _vector_dimensions(embedding.vector_json) == embedding_dimensions()
    ):
        return

    vector = embed_text(source_text)
    if embedding is None:
        db.add(
            PostEmbedding(
                post_id=post.id,
                source_text=indexed_source_text,
                vector_json=json.dumps(vector),
            )
        )
        db.flush()
        return

    embedding.source_text = indexed_source_text
    embedding.vector_json = json.dumps(vector)


def _indexed_source_text(source_text: str) -> str:
    return f"__embedding_index__:{embedding_signature()}\n{source_text}"


def _vector_dimensions(vector_json: str) -> int:
    try:
        vector = json.loads(vector_json)
    except json.JSONDecodeError:
        return 0
    return len(vector) if isinstance(vector, list) else 0
