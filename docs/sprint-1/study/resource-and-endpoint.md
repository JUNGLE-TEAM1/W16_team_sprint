# 리소스와 Endpoint 이해하기

Sprint 1에서 자주 나오는 단어 중 하나가 `resource`와 `endpoint`입니다.

처음에는 둘 다 API 주소와 관련된 말처럼 보여서 헷갈릴 수 있습니다. 쉽게 나누면 다음과 같습니다.

```text
Resource = API가 다루는 대상
Endpoint = 그 대상을 다루기 위해 클라이언트가 호출하는 API 지점
```

## 리소스란 무엇인가?

리소스는 API가 관리하는 핵심 데이터 대상입니다.

Sprint 1 예제에서는 `post`가 리소스입니다.

```text
post = 게시글
```

즉, 이 API는 게시글이라는 데이터를 만들고, 조회하고, 나중에는 수정하거나 삭제할 수 있습니다.

다른 예시는 다음과 같습니다.

| 리소스 | 의미 | API 주소 예시 |
| --- | --- | --- |
| `user` | 사용자 | `/users` |
| `post` | 게시글 | `/posts` |
| `comment` | 댓글 | `/comments` |
| `tag` | 태그 | `/tags` |
| `ai_request` | AI 요청 기록 | `/ai-requests` |

리소스를 고른다는 것은 아래 질문에 답하는 것과 같습니다.

```text
우리 API가 무엇을 만들고, 조회하고, 수정하고, 삭제할 것인가?
```

## REST API에서 리소스는 URL로 표현한다

REST API에서는 보통 리소스를 URL에 명사로 표현합니다.

좋은 예:

```text
/posts
/users
/comments
```

덜 좋은 예:

```text
/createPost
/getPost
/deletePost
```

왜냐하면 REST API에서는 URL이 대상을 나타내고, 행동은 HTTP method가 나타내기 때문입니다.

```text
POST /posts      게시글 생성
GET /posts       게시글 목록 조회
GET /posts/1     1번 게시글 조회
PATCH /posts/1   1번 게시글 수정
DELETE /posts/1  1번 게시글 삭제
```

## REST API란 무엇인가?

REST API는 서버가 가진 데이터를 URL과 HTTP method로 다루는 API 설계 방식입니다.

핵심 규칙은 두 가지입니다.

```text
URL = 무엇을 다룰 것인가
HTTP method = 어떤 행동을 할 것인가
```

예를 들어 게시글을 생성하려면 다음처럼 표현합니다.

```text
POST /posts
```

의미:

```text
posts 리소스에 새 게시글을 생성한다.
```

Sprint 1에서는 API prefix와 version이 붙어서 실제 endpoint가 아래처럼 됩니다.

```text
POST /api/v1/posts
GET /api/v1/posts
GET /api/v1/posts/{post_id}
```

## Endpoint란 무엇인가?

Endpoint는 클라이언트가 호출할 수 있는 API 지점입니다.

보통 endpoint는 아래 요소를 함께 봅니다.

```text
HTTP method + URL path + 처리 함수
```

Sprint 1의 게시글 생성 endpoint는 다음입니다.

```text
POST /api/v1/posts
```

뜻을 풀면 다음과 같습니다.

```text
POST    = 생성한다
/api/v1 = API version 1
/posts  = 게시글 리소스
```

즉, 전체 의미는 다음과 같습니다.

```text
게시글 리소스를 새로 하나 생성한다.
```

## Endpoint와 Router의 관계

Endpoint는 실제 API 약속이고, router는 그 endpoint들을 코드에서 등록하고 묶어두는 곳입니다.

```text
Endpoint = 실제 API 주소와 method
Router = endpoint를 코드로 정의해둔 FastAPI 객체
Handler function = endpoint가 호출됐을 때 API Router 계층에서 실행되는 함수
```

Sprint 1 코드에서는 `backend/app/api/v1/posts.py`가 posts 리소스의 router 역할을 합니다.

```python
router = APIRouter(prefix="/posts", tags=["posts"])
```

그리고 `main.py`에서 이 router를 `/api/v1` prefix와 함께 등록합니다.

```python
app.include_router(posts_router, prefix="/api/v1")
```

따라서 두 prefix가 합쳐집니다.

```text
/api/v1 + /posts = /api/v1/posts
```

## 게시글 생성 Endpoint 코드

```python
@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload)
```

이 코드가 만드는 endpoint는 다음입니다.

```text
POST /api/v1/posts
```

여기서 `@router.post("")`의 빈 문자열은 `/posts` 뒤에 더 붙는 경로가 없다는 뜻입니다.

`create_post()`는 생성 handler function입니다. 이 함수는 API Router 계층에 있으며, 직접 DB 저장 규칙을 처리하지 않고 요청을 `PostService`로 넘기는 역할을 합니다.

## 게시글 단건 조회 Endpoint 코드

```python
@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.get(post_id)
```

이 코드가 만드는 endpoint는 다음입니다.

```text
GET /api/v1/posts/{post_id}
```

예를 들어 `post_id`가 1이면 클라이언트는 다음 주소를 호출합니다.

```text
GET /api/v1/posts/1
```

## 최종 요약

```text
Resource = API가 다루는 대상
Endpoint = 그 대상을 다루기 위해 호출하는 API 지점
Router = endpoint들을 코드에서 모아둔 객체
Handler function = endpoint 호출 시 실제 실행되는 함수
```

Sprint 1 기준으로 정리하면 다음과 같습니다.

| 개념 | Sprint 1 예시 |
| --- | --- |
| Resource | `post` |
| Resource URL | `/posts` |
| 생성 Endpoint | `POST /api/v1/posts` |
| 목록 조회 Endpoint | `GET /api/v1/posts` |
| 단건 조회 Endpoint | `GET /api/v1/posts/{post_id}` |
| Router 파일 | `backend/app/api/v1/posts.py` |
| 생성 Handler | `create_post()` |
| Handler가 속한 계층 | API Router 계층 |
