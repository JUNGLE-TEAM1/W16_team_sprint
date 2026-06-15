# Sprint 2 Summary

Date: 2026-06-15

## 1. 목표와 완료 기준

목표:
- 게시글 CRUD + 댓글 기능을 완성한다.

완료 기준:
- 로그인한 사용자가 게시글을 작성할 수 있다.
- 게시글 목록을 조회할 수 있다.
- 게시글 상세 화면을 조회할 수 있다.
- 작성자만 게시글을 수정/삭제할 수 있다.
- 댓글을 작성할 수 있다.
- 게시글 상세 화면에서 댓글을 조회할 수 있다.
- 이번 repository에서 최소 화면을 동작 확인 가능한 수준으로 제공한다.

## 2. 완료된 Decision

| ID | 제목 | 결과 |
| --- | --- | --- |
| D-009 | 댓글 모델은 어떤 필드를 가질 것인가? | C. `updated_at` 포함 확장 모델 |
| D-010 | 댓글 API 계약은 어떻게 둘 것인가? | A. 게시글 하위 nested API |
| D-011 | 최소 화면 구현을 이번 repository에서 다룰 것인가? | B. 프론트엔드 앱 추가 |
| D-012 | 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가? | A. Vite + React + TypeScript |

## 3. 구현 결과

Backend:
- `Comment` 모델을 추가했다.
- 댓글 schema/repository/service를 추가했다.
- nested 댓글 API를 추가했다.
- 댓글 생성/조회/수정/삭제를 구현했다.
- 댓글 수정/삭제 권한은 `comments.user_id == current_user.id` 기준으로 service 계층에서 검사한다.

Frontend:
- `frontend/`에 Vite + React + TypeScript 앱을 추가했다.
- 로그인 화면, 게시글 목록, 게시글 작성/수정/삭제, 게시글 상세, 댓글 작성/수정/삭제/조회 UI를 구현했다.
- token은 `localStorage`에 저장하고 `Authorization: Bearer <token>`으로 API에 전달한다.

## 4. 테스트와 검증 결과

Backend:

```bash
DATABASE_URL=sqlite+pysqlite:////tmp/sprint2-implementation-test.db python3 -m pytest backend/tests
```

결과:
- `21 passed`

기본 PostgreSQL 설정:

```bash
python3 -m pytest backend/tests
```

결과:
- 실패
- 원인: `localhost:5433` PostgreSQL 연결 거부
- 코드 실패가 아니라 로컬 DB 미실행 상태다.

Frontend:

```bash
cd frontend && npm test
cd frontend && npm run build
cd frontend && npm audit --json
```

결과:
- Vitest `1 passed`
- build 성공
- npm audit `0 vulnerabilities`

Browser:
- `http://127.0.0.1:3000`에서 로그인, 게시글 작성, 댓글 작성/수정/삭제 흐름을 확인했다.

## 5. 낮아진 후보

| 후보 | 낮아진 Level | 처리 |
| --- | --- | --- |
| C4. 댓글 수정/삭제 권한 검사 계층 | Level 2 | 기존 게시글 패턴과 동일하게 service 계층 |
| C5. 게시글 CRUD 보강 | Level 2 | 기존 구현을 유지하고 프론트 화면에서 작성/수정/삭제 연결 |

## 6. 다음 스프린트로 넘길 항목

- Sprint 3 태그
- Sprint 3 페이징
- Sprint 3 검색
- Sprint 3 프론트엔드 검색/페이징/태그 UI
- HttpOnly Cookie + CSRF 전환은 별도 보안 개선 Decision으로 남긴다.

## 7. 알려진 제약

- 마이그레이션 도구가 없으므로 로컬 DB는 `Base.metadata.create_all()` 기반이다.
- 기본 PostgreSQL 테스트는 DB 컨테이너가 켜져 있어야 통과한다.
- 댓글 응답에는 작성자 식별/표시 정보를 노출하지 않는다.
