# Request Body와 Response Schema 이해하기

Sprint 1에서 API 계약을 볼 때 가장 먼저 확인해야 하는 것은 요청과 응답의 모양입니다.

```text
Request body = 클라이언트가 서버에 보내는 데이터
Response body = 서버가 클라이언트에 돌려주는 데이터
```

현재 프로젝트에서는 요청과 응답의 모양을 `backend/app/schemas/post.py`에서 확인합니다.

## Request Body는 어디서 확인하는가?

게시글 생성 요청 body는 `PostCreate`를 보면 됩니다.

```python
class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    author_name: str = Field(default="anonymous", min_length=1, max_length=40)
```

이 schema가 의미하는 request body는 다음과 같습니다.

```json
{
  "title": "Sprint 1",
  "content": "API and DB flow",
  "author_name": "team1"
}
```

각 필드는 다음 의미를 가집니다.

| 필드 | 의미 | 검증 규칙 |
| --- | --- | --- |
| `title` | 게시글 제목 | 최소 1글자, 최대 120글자 |
| `content` | 게시글 내용 | 최소 1글자 |
| `author_name` | 작성자 표시 이름 | 없으면 `anonymous`, 최소 1글자, 최대 40글자 |

## Endpoint는 Request Body를 어떻게 받는가?

`backend/app/api/v1/posts.py`에서 아래 코드를 보면 됩니다.

```python
@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload)
```

핵심은 이 부분입니다.

```python
payload: PostCreate
```

이 말은 다음 뜻입니다.

```text
POST 요청 body를 PostCreate 형식으로 검증해서 payload로 넣어줘.
```

즉, request body의 구조는 `PostCreate`가 정의하고, 실제 endpoint에서는 `payload: PostCreate`로 그 body를 받습니다.

## 검증은 누가 하는가?

검증 자체는 Pydantic이 합니다.

조금 더 정확히는 다음 흐름입니다.

```text
1. 클라이언트가 JSON body를 보낸다.
2. FastAPI가 요청 body를 읽는다.
3. FastAPI가 Pydantic 모델인 PostCreate에 body를 넣어 검증한다.
4. 검증에 성공하면 payload 객체로 endpoint 함수에 전달한다.
5. 검증에 실패하면 endpoint 함수는 실행되지 않고 422 에러를 반환한다.
```

예를 들어 title이 비어 있으면 아래 요청은 실패합니다.

```json
{
  "title": "",
  "content": "내용",
  "author_name": "team1"
}
```

왜냐하면 `PostCreate`에 아래 조건이 있기 때문입니다.

```python
title: str = Field(min_length=1, max_length=120)
```

따라서 정리하면 다음과 같습니다.

```text
검증 규칙 정의 = Pydantic 모델
검증 실행 연결 = FastAPI
검증 실패 응답 = FastAPI exception handler
```

현재 프로젝트에서는 validation error를 `backend/app/core/errors.py`에서 공통 형식으로 바꿔줍니다.

```python
@app.exception_handler(RequestValidationError)
def handle_validation_error(...):
    ...
```

## Response는 어디서 확인하는가?

응답 body의 모양은 `PostRead`를 보면 됩니다.

```python
class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author_name: str
    created_at: datetime
```

이 schema가 의미하는 response body는 다음과 같습니다.

```json
{
  "id": 1,
  "title": "Sprint 1",
  "content": "API and DB flow",
  "author_name": "team1",
  "created_at": "2026-06-13T00:00:00"
}
```

## Request Schema와 Response Schema를 왜 나누는가?

요청에는 없지만 응답에는 있는 값이 있기 때문입니다.

예를 들어 클라이언트는 게시글을 생성할 때 `id`와 `created_at`을 보내지 않습니다.

```json
{
  "title": "Sprint 1",
  "content": "API and DB flow",
  "author_name": "team1"
}
```

하지만 서버는 DB에 저장한 뒤 `id`와 `created_at`을 포함해서 응답합니다.

```json
{
  "id": 1,
  "title": "Sprint 1",
  "content": "API and DB flow",
  "author_name": "team1",
  "created_at": "2026-06-13T00:00:00"
}
```

그래서 역할을 나눕니다.

```text
PostCreate = 클라이언트가 서버에 보내는 생성 요청 모양
PostRead = 서버가 클라이언트에 돌려주는 게시글 응답 모양
```

## Endpoint는 Response Schema를 어떻게 쓰는가?

게시글 생성 endpoint에는 아래 옵션이 있습니다.

```python
response_model=PostRead
```

전체 코드는 다음과 같습니다.

```python
@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload)
```

`response_model=PostRead`는 다음 뜻입니다.

```text
이 endpoint의 응답은 PostRead 모양으로 정리해서 반환해줘.
```

목록 조회는 `PostRead` 하나가 아니라 여러 개를 반환합니다.

```python
@router.get("", response_model=list[PostRead])
def list_posts(service: PostService = Depends(get_post_service)) -> list[PostRead]:
    return service.list()
```

따라서 응답은 배열입니다.

```json
[
  {
    "id": 1,
    "title": "Sprint 1",
    "content": "API and DB flow",
    "author_name": "team1",
    "created_at": "2026-06-13T00:00:00"
  }
]
```

## Request와 Response 확인 순서

API 계약을 확인할 때는 아래 순서로 보면 됩니다.

```text
1. api/v1/posts.py에서 endpoint를 확인한다.
2. endpoint 함수의 parameter에서 request schema를 확인한다.
3. response_model에서 response schema를 확인한다.
4. schemas/post.py에서 각 schema의 필드와 검증 규칙을 확인한다.
```

Sprint 1의 게시글 생성 endpoint를 예로 들면 다음과 같습니다.

```text
Endpoint = POST /api/v1/posts
Request schema = PostCreate
Response schema = PostRead
Success status = 201 Created
```

## 최종 요약

```text
Request body의 구조 = PostCreate
Request body 검증 = Pydantic
FastAPI 연결 지점 = payload: PostCreate
Response body의 구조 = PostRead
FastAPI 응답 변환 지점 = response_model=PostRead
```

짧게 기억하면 다음과 같습니다.

```text
요청은 PostCreate를 보고,
응답은 PostRead를 본다.
```
