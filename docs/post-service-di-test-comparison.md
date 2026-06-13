# PostService DI 테스트 비교

## 왜 기존에는 서비스 테스트가 없었나

기존 테스트는 `backend/tests/test_posts_flow.py`에서 HTTP API부터 DB까지 한 번에 확인한다.
그래서 `PostService`만 따로 검증하는 단위 테스트는 없었다.

이 구조에서는 `PostService`가 `PostRepository`를 내부에서 직접 생성한다.

```python
class PostService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.posts = PostRepository(db)
```

서비스가 repository 생성 방법까지 알고 있으므로, 테스트에서 fake repository를 생성자에 바로 넣을 수 없다.

## DI 적용 전 서비스 테스트

DI 적용 전에는 `PostService` 내부의 `PostRepository` 심볼을 바꿔치기해야 한다.
테스트가 서비스의 공개 API만 다루지 못하고, 서비스 내부 구현에 기대게 된다.

```python
import pytest

from backend.app.core.errors import AppError
from backend.app.models.post import Post
from backend.app.schemas.post import PostCreate
from backend.app.services import post_service
from backend.app.services.post_service import PostService


class FakeDb:
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True


class FakePostRepository:
    saved_post: Post | None = None

    def __init__(self, db: FakeDb) -> None:
        self.db = db

    def create(self, post: Post) -> Post:
        self.saved_post = post
        return post

    def list(self) -> list[Post]:
        return []

    def get(self, post_id: int) -> Post | None:
        return None


def test_create_post_commits_after_repository_create(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(post_service, "PostRepository", FakePostRepository)
    db = FakeDb()
    service = PostService(db)

    post = service.create(
        PostCreate(title="Service test", content="No real DB", author_name="team1")
    )

    assert post.title == "Service test"
    assert db.committed is True
    assert isinstance(service.posts.saved_post, Post)


def test_get_missing_post_raises_app_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(post_service, "PostRepository", FakePostRepository)
    service = PostService(FakeDb())

    with pytest.raises(AppError) as exc_info:
        service.get(999)

    assert exc_info.value.code == "POST_NOT_FOUND"
    assert exc_info.value.details == {"post_id": 999}
```

## DI 적용 후 서비스 테스트

DI 적용 후에는 `PostService`가 이미 만들어진 repository를 받는다.

```python
class PostService:
    def __init__(self, db: Session, posts: PostRepository) -> None:
        self.db = db
        self.posts = posts
```

라우터의 dependency provider가 실제 객체 조립을 담당한다.

```python
def get_post_service(db: Session = Depends(get_db)) -> PostService:
    posts = PostRepository(db)
    return PostService(db=db, posts=posts)
```

서비스 테스트는 fake repository를 생성자에 바로 넣으면 된다.
monkeypatch가 필요 없고, 테스트가 서비스 내부 구현보다 생성자 계약에만 의존한다.

```python
def test_create_post_commits_after_repository_create() -> None:
    db = FakeDb()
    posts = FakePostRepository()
    service = PostService(db=db, posts=posts)

    post = service.create(
        PostCreate(title="Service test", content="No real DB", author_name="team1")
    )

    assert post.title == "Service test"
    assert db.committed is True
    assert isinstance(posts.saved_post, Post)
```

## 비교 포인트

- DI 전: 테스트가 `PostService` 내부의 `PostRepository` 이름을 monkeypatch해야 한다.
- DI 후: 테스트가 `PostService(db, posts)` 생성자에 fake 객체를 바로 넣는다.
- DI 전: service가 repository 생성 책임과 비즈니스 로직 책임을 함께 가진다.
- DI 후: 객체 조립은 FastAPI dependency가 맡고, service는 게시글 규칙에 집중한다.

실제 리팩터링 이력을 남길 때는 커밋을 둘로 나누는 편이 가장 명확하다.

1. `test: add post service tests before di refactor`
2. `refactor: inject post repository into post service`
