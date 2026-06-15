import pytest

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.schemas.post import PostCreate, PostUpdate
from backend.app.services.post_service import PostService


class FakeDb:
    def __init__(self) -> None:
        self.committed = False
        self.refreshed = False

    def commit(self) -> None:
        self.committed = True

    def refresh(self, _: Post) -> None:
        self.refreshed = True


class FakePostRepository:
    def __init__(self, found_post: Post | None = None) -> None:
        self.found_post = found_post
        self.saved_post: Post | None = None
        self.deleted_post: Post | None = None

    def create(self, post: Post) -> Post:
        self.saved_post = post
        return post

    def list(self) -> list[Post]:
        return []

    def get(self, post_id: int) -> Post | None:
        return self.found_post

    def delete(self, post: Post) -> None:
        self.deleted_post = post


class FakeTagRepository:
    def __init__(self) -> None:
        self.names: list[str] = []

    def get_or_create_many(self, names: list[str]) -> list:
        self.names = names
        return []


def test_create_post_commits_after_repository_create() -> None:
    db = FakeDb()
    posts = FakePostRepository()
    tags = FakeTagRepository()
    service = PostService(db=db, posts=posts, tags=tags)  # type: ignore[arg-type]

    post = service.create(
        PostCreate(title="Service test", content="No real DB", tags=["fastapi", "auth"]),
        author_id=7,
    )

    assert post.title == "Service test"
    assert post.author_id == 7
    assert db.committed is True
    assert isinstance(posts.saved_post, Post)
    assert tags.names == ["fastapi", "auth"]


def test_get_missing_post_raises_app_error() -> None:
    service = PostService(
        db=FakeDb(),
        posts=FakePostRepository(),
    )  # type: ignore[arg-type]

    with pytest.raises(AppError) as exc_info:
        service.get(999)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.details == {"post_id": 999}


def test_update_post_requires_author() -> None:
    post = Post(id=1, title="old", content="old", author_id=7)
    service = PostService(
        db=FakeDb(),
        posts=FakePostRepository(found_post=post),
    )  # type: ignore[arg-type]

    with pytest.raises(AppError) as exc_info:
        service.update(1, PostUpdate(title="new", content="new"), author_id=9)

    assert exc_info.value.code == "POST_FORBIDDEN"


def test_delete_post_commits_after_author_check() -> None:
    db = FakeDb()
    post = Post(id=1, title="old", content="old", author_id=7)
    posts = FakePostRepository(found_post=post)
    service = PostService(db=db, posts=posts)  # type: ignore[arg-type]

    service.delete(1, author_id=7)

    assert posts.deleted_post is post
    assert db.committed is True
