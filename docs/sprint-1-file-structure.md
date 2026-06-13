# 스프린트 1 파일 구조

## 목표

스프린트 1은 아래 흐름을 학습하기 위한 작은 기준 구현입니다.

```text
클라이언트 요청 -> API 라우터 -> 검증/스키마 -> 서비스 -> 레포지토리 -> DB -> 응답/에러
```

예제 도메인은 `posts`입니다. 특정 프로젝트 주제가 아직 정해지지 않은 상태에서도 쓸 수 있도록 일부러 일반적인 리소스를 골랐습니다. 이후 실제 프로젝트 주제가 정해지면 같은 패턴으로 `reviews`, `todos`, `ai_requests` 같은 리소스로 바꿔 확장할 수 있습니다.

## 계획한 구조

```text
W16_team_sprint/
├── README.md
├── requirements.txt
├── learning-priorities.md
├── docs/
│   ├── sprint-1-file-structure.md
│   └── sprint-1-api-data-flow.md
└── backend/
    ├── app/
    │   ├── main.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── v1/
    │   │       ├── __init__.py
    │   │       └── posts.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   └── errors.py
    │   ├── db/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── session.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── post.py
    │   ├── repositories/
    │   │   ├── __init__.py
    │   │   └── post_repository.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   └── post.py
    │   └── services/
    │       ├── __init__.py
    │       └── post_service.py
    └── tests/
        └── test_posts_flow.py
```

## 계층별 책임

| 계층 | 파일 | 책임 |
| --- | --- | --- |
| API 라우터 | `api/v1/posts.py` | HTTP method, URL, status code, 의존성 연결 |
| 스키마 | `schemas/post.py` | 요청/응답 형태와 검증 규칙 |
| 서비스 | `services/post_service.py` | 비즈니스 규칙과 트랜잭션 경계 |
| 레포지토리 | `repositories/post_repository.py` | DB 읽기/쓰기 세부 구현 |
| 모델 | `models/post.py` | 테이블 컬럼, PK, 인덱스 |
| DB | `db/session.py`, `db/base.py` | DB 엔진, 세션, 테이블 생성 |
| 에러 | `core/errors.py` | 공통 에러 응답 형식 |

## 스프린트 1 API 계약

| 메서드 | 경로 | 성공 응답 | 목적 |
| --- | --- | --- | --- |
| `POST` | `/api/v1/posts` | `201 Created` | 게시글 1개 생성 및 저장 |
| `GET` | `/api/v1/posts` | `200 OK` | 저장된 게시글 목록 조회 |
| `GET` | `/api/v1/posts/{post_id}` | `200 OK` | 게시글 1개 조회 |

### 생성 요청

```json
{
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1"
}
```

### 성공 응답

```json
{
  "id": 1,
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1",
  "created_at": "2026-06-13T00:00:00"
}
```

### 에러 응답

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

## 확장 계획

스프린트 1의 구조를 유지한 채 이후 스프린트를 붙일 수 있습니다.

| 이후 스프린트 | 확장 예시 |
| --- | --- |
| 스프린트 2 인증/보안 | `users`, `auth` 라우터, 인증 의존성, 로그인한 사용자만 글 작성 |
| 스프린트 3 아키텍처/로깅/설정 | 설정 관리, 로거, ADR 문서, 구조화된 에러 로그 |
| 스프린트 4 프론트 연결/상태 | 이 API를 호출하고 loading/error/success 상태를 보여주는 작은 프론트엔드 |
| 스프린트 5 AI 흐름 | 같은 라우터/서비스/레포지토리 패턴으로 `ai_requests` 또는 `summaries` 리소스 추가 |
| 스프린트 6 비동기/캐시/신뢰성 | 느린 AI 작업을 작업 테이블이나 큐 형태의 워커로 분리 |
