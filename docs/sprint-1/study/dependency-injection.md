# 의존성 주입으로 Service와 Repository 연결하기

## 왜 이 문서를 보는가?

기존 Sprint 1 코드에서는 `PostService`가 생성자 안에서 `PostRepository`를 직접 만들었습니다.

```python
class PostService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.posts = PostRepository(db)
```

이 방식은 단순해서 처음 흐름을 이해하기 좋습니다. 하지만 팀원들과 이야기한 것처럼, service가 repository 구현체를 직접 만들면 service가 너무 많은 것을 알게 됩니다.

```text
Service가 아는 것
- 게시글 기능 처리 순서
- transaction commit 위치
- 없는 게시글일 때 어떤 에러를 낼지
- repository 구현체가 PostRepository라는 것
- repository를 만들 때 db가 필요하다는 것
```

마지막 두 가지는 비즈니스 규칙이라기보다 객체 조립 방식입니다. 그래서 이 책임을 service 밖으로 빼는 것이 의존성 주입의 출발점입니다.

## 의존성 주입이란?

의존성 주입은 객체가 필요한 부품을 직접 만들지 않고, 바깥에서 받아서 쓰는 방식입니다.

```text
직접 생성 방식
Service가 Repository를 직접 만든다.

의존성 주입 방식
Service는 Repository를 받아서 쓴다.
Repository를 누가 어떻게 만들지는 조립 전용 코드가 담당한다.
```

여기서 의존성은 `PostService`가 일을 하기 위해 필요한 `PostRepository`입니다.

## 바꾼 구조

현재 구조는 아래처럼 나눕니다.

```text
Router
-> get_post_service dependency
-> PostService
-> PostRepository
-> PostgreSQL
```

각 책임은 다음과 같습니다.

| 위치 | 책임 |
| --- | --- |
| `api/v1/posts.py` | HTTP 요청을 받고 service를 호출한다. |
| `api/dependencies.py` | DB session, repository, service를 조립한다. |
| `services/post_service.py` | 게시글 기능 흐름과 transaction을 담당한다. |
| `repositories/post_repository.py` | DB 저장과 조회를 담당한다. |

## 코드 흐름

라우터는 이제 DB session이나 repository 생성 방법을 알지 않습니다.

```python
@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload)
```

라우터가 아는 것은 `PostService`를 받아서 `create()`를 호출한다는 것뿐입니다.

객체 조립은 dependency provider가 담당합니다.

```python
def get_post_service(db: Session = Depends(get_db)) -> PostService:
    posts = PostRepository(db)
    return PostService(db=db, posts=posts)
```

`PostService`는 repository를 직접 만들지 않고 생성자로 받습니다.

```python
class PostService:
    def __init__(self, db: Session, posts: PostRepository) -> None:
        self.db = db
        self.posts = posts
```

여기서 `self.posts = posts`는 `PostRepository`를 새로 만드는 코드가 아닙니다. 이미 바깥에서 만들어서 넘겨준 repository 객체를 `PostService` 내부 필드에 저장하는 코드입니다.

직접 생성은 아래처럼 `PostRepository(db)`를 호출하는 경우입니다.

```python
self.posts = PostRepository(db)
```

현재 `PostService` 안에는 이 코드가 없습니다. `PostRepository(db)`는 조립 전용 함수인 `get_post_service()` 안에만 있습니다.

## 라우터로 책임이 넘어간 것 아닌가?

라우터 함수 안에서 직접 조립하면 책임이 라우터로 넘어간 것이 맞습니다.

피해야 할 방식:

```python
def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> PostRead:
    posts = PostRepository(db)
    service = PostService(db=db, posts=posts)
    return service.create(payload)
```

이렇게 하면 라우터가 너무 많은 것을 알게 됩니다.

```text
Router가 알게 되는 것
- PostRepository가 필요하다.
- PostRepository는 db로 만든다.
- PostService는 db와 posts가 필요하다.
- 객체를 어떤 순서로 만들어야 한다.
```

이건 service 내부 결합을 라우터 결합으로 옮긴 것에 가깝습니다.

그래서 조립 전용 함수인 `get_post_service()`를 둡니다.

```text
Router는 service를 받는다.
Dependency provider는 객체를 조립한다.
Service는 기능 흐름을 처리한다.
Repository는 DB 작업을 처리한다.
```

핵심은 객체 생성 코드를 아무 곳으로 옮기는 것이 아니라, 객체 조립 책임을 한 곳에 모으는 것입니다.

## Depends가 라우터에 남아 있어도 되는가?

FastAPI에서는 라우터 함수가 필요한 의존성을 `Depends(...)`로 선언합니다. 따라서 라우터에 아래 코드가 남아 있는 것은 정상입니다.

```python
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload)
```

여기서 라우터가 아는 것은 `PostService`가 필요하다는 사실뿐입니다. 라우터는 `PostRepository`를 어떻게 만들지, DB session을 어떻게 가져올지, service 생성자에 무엇을 넣을지는 모릅니다.

반대로 아래처럼 라우터 안에서 repository와 service를 직접 만들면 좋지 않습니다.

```python
def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> PostRead:
    posts = PostRepository(db)
    service = PostService(db=db, posts=posts)
    return service.create(payload)
```

따라서 구분은 이렇게 합니다.

```text
라우터에 Depends(get_post_service)가 있다.
-> 정상. 라우터가 service를 주입받는 선언이다.

라우터 안에서 PostRepository(db)를 직접 호출한다.
-> 피해야 한다. 객체 조립 책임이 라우터로 넘어간 것이다.
```

## 현재 DI 관련 코드 위치

현재 코드에서 의존성 주입과 관련된 위치는 다음과 같습니다.

| 파일 | 역할 |
| --- | --- |
| `backend/app/db/session.py` | DB session을 제공하는 `get_db()`를 정의한다. |
| `backend/app/api/dependencies.py` | DB session으로 repository와 service를 조립한다. |
| `backend/app/api/v1/posts.py` | `Depends(get_post_service)`로 service를 주입받는다. |
| `backend/app/services/post_service.py` | 주입받은 repository를 `self.posts`에 저장하고 사용한다. |

현재 `PostRepository(db)` 직접 생성은 `dependencies.py`에만 있어야 합니다. 다른 파일에서 `PostRepository(db)`가 보이면 객체 조립 책임이 새는지 확인해야 합니다.

## 더 엄격하게 나누는 방식

지금은 `get_post_service()` 안에서 repository를 만들고 service에 넣습니다.

```python
def get_post_service(db: Session = Depends(get_db)) -> PostService:
    posts = PostRepository(db)
    return PostService(db=db, posts=posts)
```

팀 규칙을 더 명확히 하고 싶다면 repository provider도 따로 둘 수 있습니다.

```python
def get_post_repository(db: Session = Depends(get_db)) -> PostRepository:
    return PostRepository(db)


def get_post_service(
    db: Session = Depends(get_db),
    posts: PostRepository = Depends(get_post_repository),
) -> PostService:
    return PostService(db=db, posts=posts)
```

이 방식의 장점은 `repository를 만드는 책임`과 `service를 만드는 책임`이 더 명확히 나뉜다는 점입니다. 단점은 작은 예제에서는 함수가 하나 더 늘어나서 처음 읽을 때 약간 장황할 수 있다는 점입니다.

## 이 방식의 장점

### 1. Service의 책임이 줄어든다

`PostService`는 더 이상 `PostRepository(db)`를 직접 알 필요가 없습니다. service는 게시글 생성, 조회, 에러 처리, commit 같은 기능 흐름에 집중합니다.

### 2. 라우터가 깔끔해진다

라우터는 HTTP endpoint와 service 호출만 담당합니다. DB session이나 repository 생성 순서를 알 필요가 없습니다.

### 3. 테스트가 쉬워진다

나중에 service만 테스트하고 싶다면 fake repository를 넣을 수 있습니다.

```python
service = PostService(db=fake_db, posts=fake_posts)
```

지금은 아직 fake repository를 만들지 않았지만, 구조상 가능해졌습니다.

### 4. 구현체 교체가 쉬워진다

나중에 캐싱 repository, 테스트용 repository, 다른 저장소 구현이 필요하면 `get_post_service()`의 조립 코드만 바꾸면 됩니다.

## 이 방식의 단점

### 1. 파일을 하나 더 봐야 한다

요청 흐름을 처음 보는 사람은 `api/v1/posts.py`에서 바로 `PostService(db)`를 볼 수 없고, `api/dependencies.py`를 한 번 더 봐야 합니다.

### 2. 작은 예제에서는 장황할 수 있다

Sprint 1처럼 리소스가 하나뿐인 예제에서는 직접 생성 방식이 더 짧습니다. DI는 기능이 늘어날수록 이점이 커집니다.

### 3. 과하게 추상화하면 오히려 어렵다

지금 단계에서는 interface, abstract class, protocol까지 만들 필요는 없습니다. 의존성 주입의 핵심은 우선 "직접 만들지 않고 바깥에서 받는다"를 이해하는 것입니다.

## 팀 기본값 후보

Sprint 1 기준으로는 아래 방식을 기본값 후보로 둡니다.

```text
Router는 service를 Depends로 받는다.
Service는 repository를 생성자로 받는다.
Repository와 service 조립은 api/dependencies.py에서 담당한다.
Interface나 abstract class는 아직 만들지 않는다.
Transaction commit은 service layer에 둔다.
```

## 확인 질문

팀 싱크 때 아래 질문에 답해봅니다.

- `PostService`가 `PostRepository`를 직접 만들지 않게 된 이유는 무엇인가?
- `self.posts = posts`는 객체 생성인가, 주입받은 객체 저장인가?
- 라우터에서 직접 `PostRepository(db)`를 만들면 왜 좋지 않은가?
- 라우터에 `Depends(get_post_service)`가 남아 있는 것은 왜 괜찮은가?
- `get_post_service()`는 어떤 책임을 가지는가?
- transaction commit은 왜 여전히 service에 남겨두는가?
- 지금 단계에서 interface까지 만들지 않는 이유는 무엇인가?

## 한 줄 정리

```text
의존성 주입은 책임을 라우터로 밀어내는 것이 아니라,
객체 조립 책임을 별도 위치에 모아서 router, service, repository가 각자 역할에 집중하게 만드는 방식이다.
```
