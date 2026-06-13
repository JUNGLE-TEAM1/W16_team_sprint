import pytest

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.schemas.post import PostCreate
from backend.app.services.post_service import PostService


class FakeDb:
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True


class FakePostRepository:
    def __init__(self, found_post: Post | None = None) -> None:
        self.found_post = found_post
        self.saved_post: Post | None = None

    def create(self, post: Post) -> Post:
        self.saved_post = post
        return post

    def list(self) -> list[Post]:
        return []

    def get(self, post_id: int) -> Post | None:
        return self.found_post


def test_create_post_commits_after_repository_create() -> None:
    db = FakeDb()
    posts = FakePostRepository()
    service = PostService(db=db, posts=posts)  # type: ignore[arg-type]

    post = service.create(
        PostCreate(title="Service test", content="No real DB", author_name="team1")
    )

    assert post.title == "Service test"
    assert db.committed is True
    assert isinstance(posts.saved_post, Post)


def test_get_missing_post_raises_app_error() -> None:
    service = PostService(
        db=FakeDb(),
        posts=FakePostRepository(),
    )  # type: ignore[arg-type]

    with pytest.raises(AppError) as exc_info:
        service.get(999)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.details == {"post_id": 999}
