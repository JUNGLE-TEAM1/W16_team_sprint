# Request Body와 Path Parameter 차이

API 요청에서 클라이언트가 서버에 값을 보내는 방법은 여러 가지가 있습니다. Sprint 1에서 먼저 구분해야 할 것은 `request body`와 `path parameter`입니다.

둘 다 클라이언트가 서버에 보내는 값이지만, 담기는 위치와 목적이 다릅니다.

```text
Path parameter = URL 경로 안에 들어가서 특정 리소스를 가리키는 값
Request body = 요청 본문 안에 들어가서 생성/수정할 데이터 내용을 담는 값
```

## Path Parameter

Path parameter는 URL 경로 안에 들어가는 값입니다.

예를 들어 아래 요청을 봅니다.

```text
GET /api/v1/posts/1
```

여기서 `1`이 path parameter입니다.

Sprint 1 코드에서는 이렇게 받습니다.

```python
@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.get(post_id)
```

여기서 아래 두 부분이 연결됩니다.

```python
@router.get("/{post_id}")
```

```python
post_id: int
```

즉, 클라이언트가 아래 요청을 보내면:

```text
GET /api/v1/posts/1
```

FastAPI는 URL의 `1`을 꺼내서 함수 인자인 `post_id`에 넣습니다.

```text
post_id = 1
```

Path parameter는 보통 특정 리소스 하나를 가리킬 때 씁니다.

예시:

```text
GET /posts/1        1번 게시글 조회
PATCH /posts/1      1번 게시글 수정
DELETE /posts/1     1번 게시글 삭제
```

## Request Body

Request body는 HTTP 요청의 본문에 들어가는 데이터입니다.

예를 들어 게시글을 생성할 때는 제목, 내용, 작성자 이름 같은 데이터를 서버에 보내야 합니다.

```http
POST /api/v1/posts
Content-Type: application/json

{
  "title": "Sprint 1",
  "content": "API and DB flow",
  "author_name": "team1"
}
```

여기서 JSON 부분이 request body입니다.

Sprint 1 코드에서는 이렇게 받습니다.

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

이 말은 다음 의미입니다.

```text
요청 본문에 들어온 JSON을 PostCreate schema로 검증해서 payload에 넣어줘.
```

Request body는 보통 새로 만들거나 수정할 데이터의 내용을 담습니다.

예시:

```text
POST /posts
body: 새 게시글 제목, 내용, 작성자
```

```text
PATCH /posts/1
body: 수정할 제목 또는 내용
```

## 차이 요약

| 구분 | Path Parameter | Request Body |
| --- | --- | --- |
| 위치 | URL 경로 안 | 요청 본문 안 |
| 역할 | 어떤 리소스인지 식별 | 생성/수정할 데이터 전달 |
| 예시 | `/posts/1`의 `1` | `{ "title": "...", "content": "..." }` |
| 코드 위치 | `post_id: int` | `payload: PostCreate` |
| 자주 쓰는 상황 | 단건 조회, 수정, 삭제 | 생성, 수정 |

## Sprint 1 예시

### 게시글 단건 조회

```text
GET /api/v1/posts/1
```

여기서 `1`은 path parameter입니다.

```python
def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
) -> PostRead:
```

서버는 `post_id`를 사용해서 DB에서 1번 게시글을 찾습니다.

```text
post_id = 1
```

### 게시글 생성

```text
POST /api/v1/posts
```

request body:

```json
{
  "title": "Sprint 1",
  "content": "API and DB flow",
  "author_name": "team1"
}
```

서버는 이 body를 `PostCreate`로 검증한 뒤 `payload`로 받습니다.

```python
def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
) -> PostRead:
```

## 언제 무엇을 써야 하나?

특정 대상을 가리켜야 하면 path parameter를 씁니다.

```text
1번 게시글을 조회한다 -> GET /posts/1
1번 게시글을 수정한다 -> PATCH /posts/1
1번 게시글을 삭제한다 -> DELETE /posts/1
```

새 데이터나 변경할 내용을 보내야 하면 request body를 씁니다.

```text
새 게시글을 만든다 -> POST /posts + request body
1번 게시글 내용을 수정한다 -> PATCH /posts/1 + request body
```

## 최종 요약

```text
Path parameter는 "어떤 대상인가?"를 URL에서 알려준다.
Request body는 "어떤 내용인가?"를 요청 본문에서 알려준다.
```

Sprint 1 기준으로 짧게 말하면:

```text
GET /api/v1/posts/{post_id}
-> post_id는 path parameter

POST /api/v1/posts
-> title, content, author_name은 request body
```
