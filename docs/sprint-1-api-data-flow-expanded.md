# Sprint 1: API + 데이터 흐름

## 주제

게시글 작성 또는 AI 요청 하나가 프론트 -> 백엔드 -> DB -> 응답까지 어떻게 흐르는가?

## 전체 흐름

```text
사용자 입력
-> 프론트 validation
-> HTTP request
-> FastAPI router
-> Pydantic request schema validation
-> Service business rule
-> Repository database access
-> SQLAlchemy model / DB table
-> commit
-> response schema
-> 프론트 loading/error/success 반영
```

## 공부할 것과 이 저장소의 구현

| 개념 | 이 저장소에서 보는 위치 | 확인할 점 |
| --- | --- | --- |
| REST API | `backend/app/api/v1/posts.py` | `/posts`, method, status code가 리소스 행동을 표현하는가 |
| request/response | `backend/app/schemas/post.py` | `PostCreate`, `PostRead`가 계약을 고정하는가 |
| HTTP status | router decorator, tests | 생성은 `201`, 조회는 `200`, 없음은 `404` |
| error response | `backend/app/core/errors.py` | 실패 응답이 `{ error: { code, message, details } }`로 통일되는가 |
| ERD | `Post`, `User`, `AiRequest` model | 어떤 테이블과 관계가 필요한가 |
| PK/FK | `id`, `requester_id`, `user_id` | 각 row의 식별자와 관계가 명확한가 |
| transaction | service의 `db.commit()` | 여러 DB 변경을 하나의 성공/실패 단위로 묶는가 |
| validation | Pydantic `Field` | 빈 title, 너무 긴 prompt 같은 입력을 막는가 |

## 게시글 작성 예시

```http
POST /api/v1/posts
Content-Type: application/json

{
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1"
}
```

성공 응답:

```json
{
  "id": 1,
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1",
  "created_at": "2026-06-13T00:00:00"
}
```

## AI 요청 예시

AI 요청은 스프린트 2 인증 흐름과 연결되어 로그인 사용자가 필요합니다.

```http
POST /api/v1/ai/requests
Authorization: Bearer <access-token>
Content-Type: application/json

{
  "prompt": "스프린트 내용을 요약해줘"
}
```

이 요청은 `AiRequest` 테이블에 `requester_id`, `prompt`, `result`, `status`를 저장합니다.

## 싱크 때 확인할 질문

1. 이 기능의 resource는 무엇인가?
2. endpoint는 어떻게 잡을 것인가?
3. request body에는 무엇이 들어가는가?
4. response는 어떤 형태인가?
5. 실패하면 어떤 status code를 줄 것인가?
6. DB에는 어떤 테이블이 필요한가?
7. 1:N, N:M 관계가 있는가?
8. transaction이 필요한가?
9. 프론트는 loading/error/success를 어떻게 처리하는가?

## 구현 판단 기준

- API는 함수 이름이 아니라 리소스와 method로 표현한다.
- 실패 응답 모양은 프론트가 안정적으로 처리할 수 있게 통일한다.
- DB 저장 전 validation과 권한 검사를 먼저 한다.
- 성공과 실패 status code를 프론트 상태 처리와 연결한다.
- AI 요청처럼 비용이 큰 기능은 인증, rate limit, 사용량 기록과 연결한다.
