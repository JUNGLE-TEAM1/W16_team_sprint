# Sprint 1 개인 학습 가이드

목표 시간은 1시간입니다.

이 학습의 목표는 코드를 많이 외우는 것이 아니라, 게시글 생성 요청 하나가 API, 서비스 로직, DB 저장, 응답까지 어떻게 흐르는지 말로 설명할 수 있게 되는 것입니다.

## 0-10분: 전체 그림 잡기

먼저 아래 문서를 읽습니다.

- `README.md`
- `docs/sprint-1-file-structure.md`
- `docs/sprint-1-api-data-flow.md`

확인할 질문:

- Sprint 1의 예제 리소스는 무엇인가?
- 왜 `post`를 예제로 골랐는가?
- 요청 흐름은 어떤 순서로 지나가는가?

이 단계에서 외워야 할 흐름은 하나입니다.

```text
클라이언트 요청
-> API 라우터
-> 요청 schema 검증
-> service
-> repository
-> DB table
-> response schema
-> 응답
```

## 10-25분: API 계약 보기

볼 파일:

- `backend/app/api/v1/posts.py`
- `backend/app/schemas/post.py`
- `backend/app/core/errors.py`

확인할 내용:

- `POST /api/v1/posts`는 어떤 함수로 연결되는가?
- `GET /api/v1/posts`는 어떤 응답 형태를 가지는가?
- `GET /api/v1/posts/{post_id}`에서 없는 글을 조회하면 어디서 에러가 만들어지는가?
- `PostCreate`와 `PostRead`는 왜 분리되어 있는가?
- validation error와 domain error는 응답 형식이 어떻게 다른가?

추가 학습할 개념:

- REST API에서 resource가 무엇인지
- HTTP method: `GET`, `POST`
- HTTP status code: `200`, `201`, `404`, `422`
- request body와 path parameter 차이
- Pydantic schema의 역할

말로 설명해볼 문장:

```text
게시글 생성 요청은 POST /api/v1/posts로 들어오고,
FastAPI가 request body를 PostCreate schema로 검증한 뒤,
PostService.create()를 호출한다.
응답은 DB에 저장된 Post 객체를 PostRead schema 형태로 반환한다.
```

## 25-40분: DB 저장 흐름 보기

볼 파일:

- `backend/app/services/post_service.py`
- `backend/app/repositories/post_repository.py`
- `backend/app/models/post.py`
- `backend/app/db/session.py`

확인할 내용:

- `commit`은 어느 계층에서 호출되는가?
- repository는 왜 `add`, `flush`, `refresh`를 사용하는가?
- `posts` 테이블에는 어떤 column이 있는가?
- `created_at`은 클라이언트가 보내는 값인가, 서버가 만드는 값인가?
- `DATABASE_URL`은 어디서 가져오는가?

추가 학습할 개념:

- ORM model과 DB table의 관계
- primary key
- index
- transaction
- `commit`, `flush`, `refresh`의 차이
- service layer와 repository layer를 나누는 이유

PostgreSQL 관련 확인:

- 이 프로젝트는 기본 DB로 PostgreSQL을 사용한다.
- 로컬 학습용 DB는 Docker Compose로 실행한다.
- 기본 연결 문자열은 아래와 같다.

```text
postgresql+psycopg://postgres:postgres@localhost:5433/w16_sprint
```

SQLite와 PostgreSQL 차이에서 지금 알아야 할 것:

- SQLite는 파일 하나로 동작하는 가벼운 DB다.
- PostgreSQL은 실제 서버 프로세스로 동작하는 RDBMS다.
- PostgreSQL을 쓰면 연결 URL, 계정, 비밀번호, DB 이름, 포트를 명확히 관리해야 한다.
- 실제 팀 프로젝트에 가까운 환경은 PostgreSQL이다.

## 40-50분: 직접 실행하고 요청 보내기

PostgreSQL 실행:

```bash
docker compose up -d db
```

의존성 설치:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

테스트 실행:

```bash
.venv/bin/python -m pytest backend/tests/test_posts_flow.py
```

서버 실행:

```bash
.venv/bin/uvicorn backend.app.main:app --reload
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

요청 예시:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title":"Sprint 1","content":"API and DB flow"}'
```

게시글 생성은 세션 인증이 필요합니다. 위 요청을 보내기 전에 회원가입과 세션 로그인을 먼저 수행해 `cookies.txt`에 `session_id`를 저장해야 합니다.

```bash
curl http://127.0.0.1:8000/api/v1/posts
```

```bash
curl http://127.0.0.1:8000/api/v1/posts/999
```

확인할 내용:

- 생성 요청은 `201`을 반환하는가?
- 로그인하지 않고 생성 요청을 보내면 `401`을 반환하는가?
- 목록 조회는 배열을 반환하는가?
- 응답에 `author_id`, `author_display_name`, `updated_at`이 포함되는가?
- 없는 글 조회는 공통 error response를 반환하는가?
- 테스트는 PostgreSQL에 연결해서 통과하는가?

## 50-60분: 팀 싱크용 정리

마지막 10분은 아래 질문에 답을 적습니다.

```md
## 내가 이해한 흐름

- 게시글 생성 요청은 어떤 파일들을 지나가는가?

## 기본값 후보

- API prefix는 `/api/v1`로 둬도 되는가?
- 에러 응답은 `{ error: { code, message, details } }`로 통일해도 되는가?
- transaction commit은 service layer에서 하는 것이 맞는가?

## 아직 헷갈리는 질문

- response schema와 DB model은 왜 따로 있는가?
- flush와 commit은 정확히 무엇이 다른가?
- PostgreSQL을 쓰면 SQLite와 비교해서 개발 방식이 무엇이 달라지는가?
```

## 이번 스프린트에서 더 학습하면 좋은 것

우선순위가 높은 것:

- HTTP method와 status code
- request/response schema
- Pydantic validation
- SQLAlchemy model
- transaction과 commit
- PostgreSQL 연결 문자열

지금은 깊게 안 파도 되는 것:

- Alembic migration
- PostgreSQL index 튜닝
- connection pool 세부 설정
- SQLAlchemy relationship 심화
- Clean Architecture 심화

이 주제들은 Sprint 1의 흐름을 이해한 뒤, 실제 프로젝트 구조가 잡히면 다시 다룹니다.
