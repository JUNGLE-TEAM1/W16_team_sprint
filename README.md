# AI 지식 공유 게시판 Sprint Repo

AI 지식 공유 게시판 개인 과제를 위한 Sprint 레포입니다.

이 레포는 팀 프로젝트가 아니라 개인 구현 과제의 기준 레포입니다. 팀은 같은 MVP 시나리오와 같은 기술 스택을 기준으로 각자 구현하고, 싱크 시간에는 구현 방식, 설계 판단, 막힌 부분, 발표 가능한 설명을 비교합니다.

## 서비스 컨셉

AI 지식 공유 게시판은 개발자와 학습자가 질문, 트러블슈팅, 학습 노트, 참고 자료를 게시글로 공유하고, 이후 AI가 유사 글 탐색, 외부 자료 수집, 글쓰기 보조를 돕는 게시판 서비스입니다.

기본 사용자 흐름은 다음을 기준으로 합니다.

```text
회원가입
-> 로그인
-> 게시글 작성
-> 댓글/태그/검색/페이징
-> RAG 기반 유사 글 추천
-> MCP 기반 외부 자료 조회
-> Agent 기반 글쓰기 보조
```

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Frontend | React + Vite |
| Backend/API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| AI/RAG DB | pgvector 예정 |
| Auth | Session 인증을 main auth로 선택 |

OAuth/OIDC는 현재 필수 구현 범위가 아니며, 필요 시 추후 확장 학습 주제로 다룹니다.

## 현재 Sprint 목표

오늘 목표는 Sprint 1과 Sprint 2를 구현 가능한 기준으로 정리하고 완료하는 것입니다.

### Sprint 1. Foundation

목표는 이후 게시판 기능과 Session 인증을 붙일 수 있는 기반을 만드는 것입니다.

현재 확정된 방향:

- FastAPI 앱 구조는 `router / schema / service / repository / model` 계층을 사용합니다.
- PostgreSQL을 기본 DB로 사용합니다.
- `Post`는 문자열 작성자(`author_name`)가 아니라 `User` FK 기반으로 변경합니다.
- `Post`에는 `updated_at`을 포함합니다.
- 게시글 응답에는 작성자 표시명(`author_display_name`)을 포함합니다.
- `Comment`, `Tag`는 다음 Sprint에서 구현합니다.
- Alembic 도입은 보류하고, 오늘은 로컬 DB reset 방식으로 진행합니다.

Sprint 1 완료 기준:

```text
1. FastAPI 서버가 실행된다.
2. React + Vite 앱이 실행된다.
3. PostgreSQL 연결이 된다.
4. User 모델이 있다.
5. Post 모델이 User와 FK로 연결된다.
6. Post 생성 또는 조회 API가 동작한다.
7. 요청 흐름을 router -> schema -> service -> repository -> DB -> response로 설명할 수 있다.
8. Sprint note에 구조 선택 이유를 남긴다.
```

### Sprint 2. Session Auth

목표는 Session 기반 회원가입, 로그인, 현재 사용자 확인, 보호 API 연결을 구현하는 것입니다.

현재 확정된 방향:

- Session 인증을 main auth 방식으로 사용합니다.
- 세션은 서버 DB에 저장하고, 클라이언트에는 `HttpOnly` cookie를 내려주는 구조를 기준으로 합니다.
- CSRF 대응은 `SameSite=Lax`, 명시적 CORS origin 제한을 최소 안전장치로 두고, CSRF token은 후속 검토합니다.
- Session 만료 시간은 4시간입니다.
- JWT/token pair 코드는 구현 범위에서 제거합니다.
- 게시글 작성은 로그인 사용자와 연결합니다.
- 게시글 수정/삭제 권한은 내일 CRUD Sprint에서 본격 처리합니다.

Sprint 2 완료 기준:

```text
1. 회원가입이 된다.
2. Session 로그인이 된다.
3. 현재 로그인 사용자를 확인할 수 있다.
4. 로그아웃이 된다.
5. 인증 없이 보호 API를 호출하면 401이 발생한다.
6. 로그인 사용자가 게시글 작성 시 author_id와 연결된다.
7. Session 인증 방식의 장점과 한계를 설명할 수 있다.
8. Sprint note에 인증 흐름과 선택 이유를 남긴다.
```

## 실행 방법

### Backend

```bash
cp .env.example .env
docker compose up -d db
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/uvicorn backend.app.main:app --reload --env-file .env
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

프론트엔드 개발 서버:

```text
http://127.0.0.1:5173
```

## 테스트 방법

```bash
docker compose up -d db
.venv/bin/python -m pytest backend/tests
```

테스트도 PostgreSQL을 사용합니다. 로컬 DB schema를 크게 바꾼 뒤 테스트가 꼬이면 학습용 데이터 reset이 필요할 수 있습니다.

## 주요 코드 위치

| 영역 | 파일 |
| --- | --- |
| FastAPI app | `backend/app/main.py` |
| DB 설정 | `backend/app/db/session.py` |
| 공통 설정 | `backend/app/core/config.py` |
| 공통 에러 | `backend/app/core/errors.py` |
| 보안 유틸 | `backend/app/core/security.py` |
| 인증 API | `backend/app/api/v1/auth.py` |
| 게시글 API | `backend/app/api/v1/posts.py` |
| 인증 서비스 | `backend/app/services/auth_service.py` |
| 게시글 서비스 | `backend/app/services/post_service.py` |
| DB 모델 | `backend/app/models/` |
| React UI | `frontend/src/App.jsx` |

## 문서

- [스프린트 운영 문서](docs/ai_knowledge_board_sprint_plan.md)
- [레포지토리 전체 흐름](docs/repository-overall-flow.md)
- [Sprint 1 Foundation 설계 의사결정 가이드](docs/sprint-notes/sprint-01-foundation-decisions.md)
- [Sprint 1 구현 기록](docs2/sprint-1/implementation-record.md)
- [Sprint 2 Session 인증 의사결정과 전체 흐름](docs2/sprint-2/session-auth-decision-and-flow.md)
- [Sprint 2 구현 기록](docs2/sprint-2/implementation-record.md)
- [스프린트 1 파일 구조](docs/sprint-1-file-structure.md)
- [스프린트 1 API 데이터 흐름](docs/sprint-1-api-data-flow.md)
- [스프린트 2 인증/인가 흐름](docs/sprint-2-auth-flow.md)
- [스프린트 2 실행 흐름 가이드](docs/sprint-2-execution-flow-guide.md)
- [Sprint 2 인증/인가 개념 가이드](docs/sprint-2/auth-security-concepts.md)

## 다음 Sprint로 넘긴 결정

- 게시글 수정/삭제 권한을 `403 Forbidden`으로 처리합니다.
- CSRF token 또는 Origin 검증 추가 여부를 상태 변경 API가 늘어나는 시점에 다시 결정합니다.
- 만료된 session cleanup 전략을 추후 결정합니다.
