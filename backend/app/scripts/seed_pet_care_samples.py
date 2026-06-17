from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.db.session import engine
from backend.app.models.post import Post
from backend.app.models.tag import Tag
from backend.app.models.user import User

SAMPLE_AUTHOR_USERNAME = "data-bot"
SAMPLE_AUTHOR_DISPLAY_NAME = "케어 데이터봇"
SAMPLE_SOURCE_NAME = "pet-care-sample"


@dataclass(frozen=True)
class SamplePost:
    title: str
    content: str
    tags: list[str]
    location_region: str
    like_count: int


SYMPTOM_CASES = [
    (
        "강아지가 켁켁 기침을 반복해요",
        "5개월 강아지가 흥분하거나 물을 마신 뒤 켁켁거리는 기침을 반복합니다. 식욕은 괜찮지만 밤에도 한두 번 기침을 해서 보호자가 관찰할 포인트를 정리하고 싶습니다.",
        ["기침", "호흡기", "자견"],
        "자견",
    ),
    (
        "노령견이 산책 후 다리를 절어요",
        "12살 강아지가 짧은 산책 뒤 오른쪽 뒷다리를 들고 걷습니다. 만지면 크게 아파하지는 않지만 계단을 피하려고 해서 관절 관리와 병원 방문 기준이 궁금합니다.",
        ["관절", "통증", "노령견"],
        "노령견",
    ),
    (
        "사료를 바꾼 뒤 묽은 변을 봐요",
        "최근 새 사료로 바꾼 뒤 변이 묽어졌습니다. 구토는 없고 활력은 평소와 비슷하지만 배변 횟수가 늘어 식이 변경을 어떻게 해야 할지 알고 싶습니다.",
        ["소화기", "설사", "사료"],
        "성견",
    ),
    (
        "눈곱이 많고 눈을 자주 비벼요",
        "아침마다 노란 눈곱이 끼고 강아지가 앞발로 눈 주변을 자주 비빕니다. 충혈도 조금 보여서 집에서 관찰할 점과 병원에 가야 하는 신호를 알고 싶습니다.",
        ["안과", "눈곱", "충혈"],
        "성견",
    ),
    (
        "피부를 긁고 귀에서 냄새가 나요",
        "귀 주변을 자주 긁고 냄새가 납니다. 목욕 후에도 금방 냄새가 돌아오고 귀지가 늘어서 피부/귀 관리와 진료과 선택이 고민됩니다.",
        ["피부", "귀", "가려움"],
        "성견",
    ),
    (
        "예방접종 후 축 처져 보여요",
        "오늘 예방접종을 맞고 돌아온 뒤 평소보다 잠을 많이 자고 밥을 조금 남겼습니다. 열이나 부기 여부를 어떻게 확인해야 하는지 궁금합니다.",
        ["예방접종", "활력저하", "자견"],
        "자견",
    ),
    (
        "물 마시는 양이 갑자기 늘었어요",
        "최근 일주일 사이 물을 많이 마시고 소변도 자주 봅니다. 더운 날씨 때문인지 질병 신호인지 구분하기 어려워 기록해야 할 항목을 알고 싶습니다.",
        ["음수량", "소변", "내과"],
        "성견",
    ),
    (
        "구토를 한 번 했는데 지켜봐도 될까요",
        "아침에 노란 거품 섞인 구토를 한 번 했습니다. 이후 물은 마시고 산책도 했지만 보호자가 바로 병원에 가야 하는 상황인지 판단하고 싶습니다.",
        ["구토", "소화기", "관찰"],
        "성견",
    ),
    (
        "발바닥을 계속 핥아요",
        "산책 후 발바닥을 계속 핥고 붉어 보입니다. 상처인지 알레르기인지 모르겠고, 집에서 씻기거나 소독해도 되는지 궁금합니다.",
        ["피부", "발바닥", "알레르기"],
        "성견",
    ),
    (
        "새끼 강아지 배변 훈련이 잘 안돼요",
        "입양한 지 2주 된 자견이 패드 근처까지 가지만 자주 실수합니다. 건강 문제와 훈련 문제를 어떻게 구분하면 좋을지 알고 싶습니다.",
        ["자견", "배변", "행동"],
        "자견",
    ),
]

SAMPLE_REGIONS = [
    "서울 마포구",
    "서울 강남구",
    "서울 송파구",
    "부산 해운대구",
    "대구 수성구",
]


def build_sample_posts() -> list[SamplePost]:
    posts: list[SamplePost] = []
    for index in range(50):
        title, content, tags, _life_cycle = SYMPTOM_CASES[index % len(SYMPTOM_CASES)]
        round_no = index // len(SYMPTOM_CASES) + 1
        suffix = f" #{round_no}" if round_no > 1 else ""
        posts.append(
            SamplePost(
                title=f"{title}{suffix}",
                content=content,
                tags=tags,
                location_region=SAMPLE_REGIONS[index % len(SAMPLE_REGIONS)],
                like_count=(index * 7) % 31,
            )
        )
    return posts


def get_or_create_author(db: Session) -> User:
    user = db.execute(select(User).where(User.username == SAMPLE_AUTHOR_USERNAME)).scalar_one_or_none()
    if user is not None:
        return user
    user = User(
        username=SAMPLE_AUTHOR_USERNAME,
        password_hash=hash_password("sample-password-not-for-login"),
        display_name=SAMPLE_AUTHOR_DISPLAY_NAME,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = db.execute(select(Tag).where(Tag.name == name)).scalar_one_or_none()
    if tag is not None:
        return tag
    tag = Tag(name=name)
    db.add(tag)
    db.flush()
    return tag


def upsert_sample_posts(db: Session) -> int:
    author = get_or_create_author(db)
    samples = build_sample_posts()
    for index, sample in enumerate(samples, start=1):
        external_id = f"pet-care-sample-{index:03d}"
        post = db.execute(select(Post).where(Post.source_external_id == external_id)).scalar_one_or_none()
        if post is None:
            post = Post(author_id=author.id, source_external_id=external_id)
            db.add(post)

        post.title = sample.title
        post.content = sample.content
        post.author_id = author.id
        post.post_type = "case"
        post.visibility = "public"
        post.comment_policy = "public"
        post.rag_scope = "excluded"
        post.region = sample.location_region
        post.source_name = SAMPLE_SOURCE_NAME
        post.source_url = None
        post.like_count = sample.like_count
        post.tag_entities = [get_or_create_tag(db, tag_name) for tag_name in sample.tags]

    db.commit()
    return len(samples)


def main() -> None:
    with Session(engine) as db:
        count = upsert_sample_posts(db)
    print(f"seeded {count} pet-care sample posts")


if __name__ == "__main__":
    main()
