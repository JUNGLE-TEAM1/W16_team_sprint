from __future__ import annotations

import pytest

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.models.tag import Tag
from backend.app.schemas.post import PostCreate, PostUpdate
from backend.app.services.post_service import PostService


class FakePostRepository:
    def __init__(self) -> None:
        self.posts: list[Post] = []

    def create(self, post: Post) -> Post:
        post.id = 1
        self.posts.append(post)
        return post

    def list(
        self,
        *,
        tag: str | None = None,
        q: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Post], int]:
        return self.posts, len(self.posts)

    def get(self, post_id: int) -> Post | None:
        return next((post for post in self.posts if post.id == post_id), None)

    def delete(self, post: Post) -> None:
        self.posts.remove(post)

    def resolve_tags(self, names: list[str]) -> list[Tag]:
        return [Tag(name=name) for name in names]


class FailingPostRepository(FakePostRepository):
    def create(self, post: Post) -> Post:
        raise RuntimeError("insert failed")


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_post_service_uses_injected_repository_and_unit_of_work() -> None:
    repository = FakePostRepository()
    unit_of_work = FakeUnitOfWork()
    service = PostService(posts=repository, unit_of_work=unit_of_work)

    post = service.create(
        PostCreate(title="DI test", content="No database dependency", tags=["FastAPI", "fastapi", ""]),
        user_id=7,
    )

    assert post.id == 1
    assert post.user_id == 7
    assert [tag.name for tag in post.tags] == ["fastapi"]
    assert repository.posts == [post]
    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False


def test_post_service_rolls_back_injected_unit_of_work_on_error() -> None:
    unit_of_work = FakeUnitOfWork()
    service = PostService(posts=FailingPostRepository(), unit_of_work=unit_of_work)

    with pytest.raises(RuntimeError):
        service.create(PostCreate(title="DI test", content="Failure path"), user_id=7)

    assert unit_of_work.committed is False
    assert unit_of_work.rolled_back is True


def test_post_service_rejects_update_from_non_owner() -> None:
    repository = FakePostRepository()
    unit_of_work = FakeUnitOfWork()
    service = PostService(posts=repository, unit_of_work=unit_of_work)
    post = service.create(PostCreate(title="Owner", content="Only owner"), user_id=1)

    with pytest.raises(AppError) as exc_info:
        service.update(post.id, PostUpdate(title="Other", content="Denied"), user_id=2)

    assert exc_info.value.status_code == 403
    assert unit_of_work.rolled_back is False
