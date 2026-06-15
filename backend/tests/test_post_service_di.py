import pytest

from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.models.tag import Tag
from backend.app.schemas.post import PostCreate
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
        page: int,
        size: int,
        query: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[Post], int]:
        return self.posts, len(self.posts)

    def get(self, post_id: int) -> Post | None:
        return next((post for post in self.posts if post.id == post_id), None)

    def delete(self, post: Post) -> None:
        self.posts.remove(post)


class FailingPostRepository(FakePostRepository):
    def create(self, post: Post) -> Post:
        raise RuntimeError("insert failed")


class FakeTagRepository:
    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        return [Tag(id=index + 1, name=name) for index, name in enumerate(names)]


class FakePostEmbeddingRepository:
    def __init__(self) -> None:
        self.embeddings: list[PostEmbedding] = []

    def upsert(self, *, post_id: int, source_text: str, vector: list[float]) -> PostEmbedding:
        embedding = PostEmbedding(post_id=post_id, source_text=source_text, vector_json="[]")
        self.embeddings.append(embedding)
        return embedding


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def fake_user():
    return type("User", (), {"id": 1, "email": "unit@sprint.local", "role": "member"})()


def test_post_service_uses_injected_repository_and_unit_of_work() -> None:
    repository = FakePostRepository()
    embeddings = FakePostEmbeddingRepository()
    unit_of_work = FakeUnitOfWork()
    service = PostService(
        posts=repository,
        tags=FakeTagRepository(),
        embeddings=embeddings,
        unit_of_work=unit_of_work,
    )

    post = service.create(
        PostCreate(title="DI test", content="No database dependency", tag_names=["di"]),
        fake_user(),
    )

    assert post.id == 1
    assert post.user_id == 1
    assert post.author_name == "unit@sprint.local"
    assert repository.posts == [post]
    assert embeddings.embeddings[0].post_id == 1
    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False


def test_post_service_rolls_back_injected_unit_of_work_on_error() -> None:
    unit_of_work = FakeUnitOfWork()
    service = PostService(
        posts=FailingPostRepository(),
        tags=FakeTagRepository(),
        embeddings=FakePostEmbeddingRepository(),
        unit_of_work=unit_of_work,
    )

    with pytest.raises(RuntimeError):
        service.create(
            PostCreate(title="DI test", content="Failure path"),
            fake_user(),
        )

    assert unit_of_work.committed is False
    assert unit_of_work.rolled_back is True
