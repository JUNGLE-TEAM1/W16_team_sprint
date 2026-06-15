import pytest

from backend.app.core.errors import AppError
from backend.app.models.comment import Comment
from backend.app.models.post import Post
from backend.app.schemas.comment import CommentCreate, CommentUpdate
from backend.app.services.comment_service import CommentService


class FakeCommentRepository:
    def __init__(self) -> None:
        self.comments: list[Comment] = []

    def create(self, comment: Comment) -> Comment:
        comment.id = len(self.comments) + 1
        self.comments.append(comment)
        return comment

    def list_by_post(self, post_id: int) -> list[Comment]:
        return [comment for comment in self.comments if comment.post_id == post_id]

    def get_for_post(self, post_id: int, comment_id: int) -> Comment | None:
        return next(
            (
                comment
                for comment in self.comments
                if comment.post_id == post_id and comment.id == comment_id
            ),
            None,
        )

    def delete(self, comment: Comment) -> None:
        self.comments.remove(comment)


class FailingCommentRepository(FakeCommentRepository):
    def create(self, comment: Comment) -> Comment:
        raise RuntimeError("insert failed")


class FakePostRepository:
    def __init__(self) -> None:
        self.posts = {1: Post(id=1, title="Post", content="Content", user_id=7)}

    def get(self, post_id: int) -> Post | None:
        return self.posts.get(post_id)


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_comment_service_uses_injected_repository_and_unit_of_work() -> None:
    repository = FakeCommentRepository()
    unit_of_work = FakeUnitOfWork()
    service = CommentService(
        comments=repository,
        posts=FakePostRepository(),
        unit_of_work=unit_of_work,
    )

    comment = service.create(1, CommentCreate(content="DI comment"), user_id=7)

    assert comment.id == 1
    assert comment.post_id == 1
    assert comment.user_id == 7
    assert repository.comments == [comment]
    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False


def test_comment_service_rolls_back_injected_unit_of_work_on_error() -> None:
    unit_of_work = FakeUnitOfWork()
    service = CommentService(
        comments=FailingCommentRepository(),
        posts=FakePostRepository(),
        unit_of_work=unit_of_work,
    )

    with pytest.raises(RuntimeError):
        service.create(1, CommentCreate(content="Failure path"), user_id=7)

    assert unit_of_work.committed is False
    assert unit_of_work.rolled_back is True


def test_comment_service_rejects_update_from_non_owner() -> None:
    repository = FakeCommentRepository()
    unit_of_work = FakeUnitOfWork()
    service = CommentService(
        comments=repository,
        posts=FakePostRepository(),
        unit_of_work=unit_of_work,
    )
    comment = service.create(1, CommentCreate(content="Owner"), user_id=1)

    with pytest.raises(AppError) as exc_info:
        service.update(1, comment.id, CommentUpdate(content="Other"), user_id=2)

    assert exc_info.value.status_code == 403
    assert unit_of_work.rolled_back is False
