# Sprint 1 Summary

Date: 2026-06-14
Status: Completed

## 1. 목표

Sprint 1은 인증 구현을 목표로 한다.

기준 문서:
- `docs/taejung/development-order.md`

완료 기준:
- 회원가입이 가능하다.
- 로그인이 가능하다.
- 로그인 성공 시 JWT가 발급된다.
- 보호된 API 요청 시 token이 함께 전달된다.
- 백엔드에서 현재 사용자를 확인할 수 있다.
- 로그인하지 않은 사용자는 401 응답을 받는다.
- 다른 사용자의 글을 수정/삭제하려 하면 403 응답을 받는다.

## 2. 완료된 Decisions

| ID | 제목 | 결과 |
| --- | --- | --- |
| D-006 | 게시글에 `user_id`를 추가할 것인가? | `posts.user_id` 추가 |
| D-007 | `author_name`을 유지할 것인가? | 제거 |
| D-008 | 회원가입 API 계약을 어떻게 둘 것인가? | 최소 register API 추가 |

## 3. 구현 결과

Auth:
- `POST /api/v1/auth/register` 추가
- 회원가입 성공 응답에는 token 미포함
- 중복 이메일은 `409 Conflict`
- 기존 login/refresh/me/logout 흐름 유지

Posts:
- 게시글 생성 시 인증 필요
- 게시글 row에 `user_id` 저장
- 게시글 응답에 `user_id`와 `author_name` 노출하지 않음
- 게시글 수정/삭제 API 추가
- 소유자가 아니면 `403 POST_FORBIDDEN`

## 4. 낮아진 후보

| 후보 | 처리 |
| --- | --- |
| `author_name` 생성 위치 | D-007에 의해 제거 |
| 게시글 응답 `user_id` 노출 | Level 2, 노출하지 않음 |
| 수정/삭제 권한 검사 계층 | Level 2, service 계층 |
| 프론트엔드 token 저장 확인 범위 | Level 2, 현재 repository에 frontend 없음 |

## 5. 검증

SQLite 검증:

```bash
DATABASE_URL=sqlite+pysqlite:////tmp/sprint1-implementation-test.db python3 -m pytest backend/tests
```

결과:

```text
14 passed
```

기본 PostgreSQL 검증:

```bash
python3 -m pytest backend/tests
```

결과:
- `localhost:5433` PostgreSQL 연결 거부로 setup 실패
- 코드 실패가 아니라 로컬 DB 미실행 상태

## 6. Sprint 2로 넘기는 것

Sprint 2의 중심은 게시글 CRUD + 댓글이다.

이미 Sprint 1에서 게시글 작성/목록/상세/수정/삭제의 백엔드 기반은 일부 구현됐다.

Sprint 2에서 이어서 확인할 것:
- 댓글 모델/API 계약
- 댓글 권한 삭제 기준
- 게시글 CRUD가 Sprint 2 완료 기준에 맞는지 재검수
- 프론트엔드 최소 화면이 필요한지 여부
