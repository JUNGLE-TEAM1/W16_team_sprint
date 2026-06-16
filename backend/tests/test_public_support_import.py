from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.post import PostSearchType, PostSortType
from backend.app.services.post_service import PostService
from backend.app.services.public_support_import_service import (
    DATA_BOT_USERNAME,
    PublicSupportImportService,
    PublicSupportRecord,
)


def setup_function() -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def build_import_service(db: Session) -> PublicSupportImportService:
    posts = PostRepository(db)
    tags = TagRepository(db)
    users = UserRepository(db)
    post_service = PostService(db=db, posts=posts, tags=tags)
    return PublicSupportImportService(users=users, posts=posts, post_service=post_service)


def test_import_records_creates_data_bot_and_public_support_cards() -> None:
    record = PublicSupportRecord(
        source_external_id="seed-policy-test",
        post_type="policy",
        title="[청년/주거] 테스트 지원",
        content="서울 청년 주거 지원 테스트 데이터입니다.",
        tags=["청년", "주거", "서울"],
        region="서울",
        source_name="테스트 공공데이터",
        source_url="https://www.data.go.kr",
    )

    with Session(engine) as db:
        result = build_import_service(db).import_records([record])
        db.commit()

        data_bot = UserRepository(db).get_by_username(DATA_BOT_USERNAME)
        post = PostRepository(db).get_by_source_external_id("seed-policy-test")

        assert result.created == 1
        assert result.updated == 0
        assert result.skipped == 0
        assert data_bot is not None
        assert post is not None
        assert post.author_id == data_bot.id
        assert post.post_type == "policy"
        assert post.visibility == "public"
        assert post.comment_policy == "none"
        assert post.rag_scope == "public"
        assert post.region == "서울"
        assert post.source_name == "테스트 공공데이터"
        assert post.tags == ["서울", "주거", "청년"]

        public_posts, total = PostRepository(db).list(
            q=None,
            search_type=PostSearchType.title_content,
            tag=None,
            sort=PostSortType.latest,
            page=1,
            size=9,
        )
        assert total == 1
        assert public_posts[0].source_external_id == "seed-policy-test"


def test_import_records_upserts_by_source_external_id() -> None:
    first_record = PublicSupportRecord(
        source_external_id="seed-facility-test",
        post_type="facility",
        title="초기 시설 카드",
        content="초기 시설 설명입니다.",
        tags=["시설", "상담"],
        region="서울",
        source_name="테스트 공공데이터",
        source_url="https://www.data.go.kr",
    )
    updated_record = PublicSupportRecord(
        source_external_id="seed-facility-test",
        post_type="facility",
        title="수정된 시설 카드",
        content="수정된 시설 설명입니다.",
        tags=["시설", "상담", "복지"],
        region="마포구",
        source_name="테스트 공공데이터",
        source_url="https://www.data.go.kr",
    )

    with Session(engine) as db:
        import_service = build_import_service(db)
        first_result = import_service.import_records([first_record])
        second_result = import_service.import_records([updated_record])
        third_result = import_service.import_records([updated_record])
        db.commit()

        post = PostRepository(db).get_by_source_external_id("seed-facility-test")

        assert first_result.created == 1
        assert second_result.updated == 1
        assert third_result.skipped == 1
        assert post is not None
        assert post.title == "수정된 시설 카드"
        assert post.region == "마포구"
        assert post.tags == ["복지", "상담", "시설"]
