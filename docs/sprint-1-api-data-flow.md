# 스프린트 1 API 데이터 흐름

## 학습 목표

팀원들이 기능 하나를 요청부터 응답까지 설명할 수 있어야 합니다.

```text
POST /api/v1/posts
-> 요청 본문 검증
-> 서비스 호출
-> posts 테이블에 행 저장
-> 트랜잭션 커밋
-> 201 응답 반환
```

## 리소스

예제 리소스는 `post`입니다.

```text
post
- id: 기본키
- title: 필수 텍스트
- content: 필수 텍스트
- author_name: 선택 가능한 작성자 표시 이름
- created_at: 서버에서 생성하는 작성 시각
```

## API 계약

### 게시글 생성

```text
POST /api/v1/posts
Status: 201 Created
```

요청:

```json
{
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1"
}
```

응답:

```json
{
  "id": 1,
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1",
  "created_at": "2026-06-13T00:00:00"
}
```

### 게시글 목록 조회

```text
GET /api/v1/posts
Status: 200 OK
```

응답:

```json
[
  {
    "id": 1,
    "title": "스프린트 1",
    "content": "API와 DB 흐름",
    "author_name": "team1",
    "created_at": "2026-06-13T00:00:00"
  }
]
```

### 게시글 단건 조회

```text
GET /api/v1/posts/{post_id}
Status: 200 OK
```

찾을 수 없을 때의 응답:

```json
{
  "error": {
    "code": "POST_NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다.",
    "details": {
      "post_id": 999
    }
  }
}
```

## 파일별 흐름

```text
api/v1/posts.py
  HTTP 요청을 받고 상태 코드를 결정한다.

api/dependencies.py
  DB session으로 repository와 service를 조립한다.

schemas/post.py
  요청/응답 형태와 검증 규칙을 정의한다.

services/post_service.py
  비즈니스 규칙과 트랜잭션 경계를 담당한다.

repositories/post_repository.py
  SQLAlchemy 쿼리 세부 내용을 감춘다.

models/post.py
  DB 테이블 컬럼과 인덱스를 정의한다.

core/errors.py
  도메인 에러를 공통 에러 응답으로 변환한다.
```

## 스프린트 싱크 질문

이 구현을 보면서 아래 질문에 답할 수 있어야 합니다.

```text
리소스는 무엇인가?
어떤 endpoint가 리소스를 생성하는가?
request body에는 무엇이 들어가는가?
response에는 무엇이 들어가는가?
어떤 validation error가 발생할 수 있는가?
데이터는 어떤 table에 저장되는가?
transaction은 어디에서 commit되는가?
404 error는 어디에서 만들어지는가?
response schema가 바뀌면 어떤 파일을 수정해야 하는가?
DB column이 바뀌면 어떤 파일을 수정해야 하는가?
```

## 현재 구현으로 확인한 흐름

### 1. 게시글 생성

```text
클라이언트
-> POST /api/v1/posts
-> PostCreate schema가 title/content/author_name 검증
-> get_post_service()가 PostRepository와 PostService 조립
-> PostService.create()
-> PostRepository.create()
-> posts 테이블에 insert
-> service layer에서 commit
-> PostRead schema로 201 응답 반환
```

이 흐름에서 팀이 확인해야 하는 핵심은 `commit` 위치입니다. 현재 예제에서는 repository가 DB 세부 쿼리만 담당하고, transaction 경계는 service가 담당합니다. 이후 기능이 커져도 "하나의 사용자 요청에서 여러 DB 변경이 함께 성공하거나 함께 실패해야 하는가?"를 service layer에서 판단하는 구조로 확장할 수 있습니다.

### 2. 게시글 목록 조회

```text
클라이언트
-> GET /api/v1/posts
-> get_post_service()가 PostRepository와 PostService 조립
-> PostService.list()
-> PostRepository.list()
-> created_at desc 정렬로 posts 조회
-> list[PostRead]로 200 응답 반환
```

목록 조회는 아직 pagination, 검색, 권한 처리가 없습니다. Sprint 1에서는 단순 목록 조회로 요청/응답 흐름을 확인하고, 실제 프로젝트에서는 `page`, `limit`, `q`, `tag` 같은 query parameter를 추가할 수 있습니다.

### 3. 게시글 단건 조회 실패

```text
클라이언트
-> GET /api/v1/posts/999
-> get_post_service()가 PostRepository와 PostService 조립
-> PostService.get()
-> PostRepository.get() 결과 없음
-> AppError 발생
-> 공통 exception handler가 error response 생성
-> 404 응답 반환
```

에러 응답은 아래 공통 형식을 사용합니다.

```json
{
  "error": {
    "code": "POST_NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다.",
    "details": {
      "post_id": 999
    }
  }
}
```

## Sprint 1 기본값 후보

팀 싱크에서 별도 반대가 없다면 아래를 초기 기본값으로 둘 수 있습니다.

| 항목 | 기본값 후보 | 이유 |
| --- | --- | --- |
| API 스타일 | REST | 프론트엔드와 백엔드가 가장 빠르게 공통 언어를 맞출 수 있다. |
| API prefix | `/api/v1` | 이후 breaking change가 생겼을 때 버전을 나눌 수 있다. |
| 요청 검증 | Pydantic schema | FastAPI와 자연스럽게 연결되고 validation error를 자동으로 만들 수 있다. |
| 응답 schema | request schema와 분리 | 생성 요청에는 없지만 응답에는 있는 `id`, `created_at` 같은 필드를 명확히 구분한다. |
| 의존성 조립 | `api/dependencies.py` | 라우터와 service가 객체 생성 책임을 직접 떠안지 않게 한다. |
| transaction 경계 | service layer | 여러 repository 호출을 하나의 비즈니스 흐름으로 묶기 쉽다. |
| DB 접근 | repository layer | SQLAlchemy 쿼리 세부 구현이 API/router로 새지 않게 한다. |
| DB 종류 | PostgreSQL | 실제 팀 프로젝트 환경에 가까운 RDBMS 기준으로 요청/저장 흐름을 학습한다. |
| 에러 응답 | `{ "error": { "code", "message", "details" } }` | 프론트엔드가 실패 처리를 일관되게 할 수 있다. |
| 조회 실패 | `404 Not Found` | 리소스가 존재하지 않는 상황을 HTTP 의미에 맞게 표현한다. |
| validation 실패 | `422 Unprocessable Entity` | FastAPI/Pydantic 기본 흐름과 맞고 필드 단위 오류를 전달하기 쉽다. |

## 아직 결정하지 않은 질문

아래 질문은 실제 프로젝트 주제가 정해지거나 Sprint 2 이후 다시 결정해야 합니다.

- 게시글 삭제는 hard delete로 할 것인가, soft delete로 할 것인가?
- 목록 조회는 처음부터 pagination을 필수로 둘 것인가?
- 작성자 정보는 `author_name` 문자열로 둘 것인가, `users` 테이블과 FK로 연결할 것인가?
- API 응답 최상위에 항상 `data`를 둘 것인가, 지금처럼 리소스를 바로 반환할 것인가?
- 에러 `message`는 사용자에게 바로 보여줄 문구인가, 개발자 디버깅용 문구인가?
- validation error의 `details`를 FastAPI 기본 형식으로 둘 것인가, 팀 형식으로 가공할 것인가?
- created_at은 서버 로컬 시간, UTC, timezone-aware datetime 중 무엇으로 관리할 것인가?
- DB table 이름은 복수형으로 통일할 것인가?

## 실행 확인

아래 테스트로 게시글 생성, 목록 조회, 단건 조회, 공통 에러 응답 흐름을 확인했습니다.

```bash
docker compose up -d postgres
.venv/bin/python -m pytest backend/tests/test_posts_flow.py
```

확인 결과:

```text
2 passed
```

## Sprint 1 완료 체크리스트

- [x] 예시 리소스 `post`를 정했다.
- [x] 생성, 목록 조회, 단건 조회 endpoint를 만들었다.
- [x] request schema와 response schema를 분리했다.
- [x] DB table, column, index를 코드로 확인할 수 있다.
- [x] service layer에서 transaction을 commit한다.
- [x] repository layer가 SQLAlchemy 쿼리를 담당한다.
- [x] 공통 error response 형식을 만들었다.
- [x] 테스트로 성공 흐름과 실패 흐름을 확인했다.
- [ ] 실제 프로젝트 도메인에 맞는 리소스로 같은 흐름을 다시 그린다.
- [ ] pagination, 검색, 인증 사용자 연결 여부를 팀에서 결정한다.
