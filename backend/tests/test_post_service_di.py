import pytest

from backend.app.models.post import Post
from backend.app.schemas.post import PostCreate
from backend.app.services.post_service import PostService


class FakePostRepository:
    def __init__(self) -> None:
        self.posts: list[Post] = []

    def create(self, post: Post) -> Post:
        post.id = 1
        self.posts.append(post)
        return post

    def list(self) -> list[Post]:
        return self.posts

    def get(self, post_id: int) -> Post | None:
        return next((post for post in self.posts if post.id == post_id), None)


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
        PostCreate(title="DI test", content="No database dependency", author_name="unit")
    )

    assert post.id == 1
    assert repository.posts == [post]
    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False


def test_post_service_rolls_back_injected_unit_of_work_on_error() -> None:
    unit_of_work = FakeUnitOfWork()
    service = PostService(posts=FailingPostRepository(), unit_of_work=unit_of_work)

    with pytest.raises(RuntimeError):
        service.create(
            PostCreate(title="DI test", content="Failure path", author_name="unit")
        )

    assert unit_of_work.committed is False
    assert unit_of_work.rolled_back is True
