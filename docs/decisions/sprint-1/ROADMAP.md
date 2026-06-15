# Sprint 1 Decision Roadmap

Date: 2026-06-13

## 1. 목적

Sprint 1 인증 구현 중 보이는 설계 후보를 한 곳에서 관리한다.

이 문서는 후보와 순서를 관리한다. 실제 사용자 선택이 필요한 후보만 Decision으로 승격하고, 그때 `D-###` ID와 개별 Decision 문서를 만든다.

## 2. 전체 후보 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 게시글에 `user_id`를 추가할 것인가? | Level 3 | Accepted as D-006 | 없음 |
| 2 | C2 | `author_name`을 유지할 것인가? | Level 3 | Accepted as D-007 | C1 |
| 3 | C3 | `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가? | Level 1 | Removed by D-007 | C1, C2 |
| 4 | C4 | 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가? | Level 2 | Lowered: service layer | C1 |
| 5 | C5 | 게시글 응답에 `user_id`를 노출할 것인가? | Level 2 | Lowered: do not expose | C1 |
| 6 | C6 | 회원가입 API 계약은 어떻게 둘 것인가? | Level 3 | Accepted as D-008 | 없음 |
| 7 | C7 | 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가? | Level 2 | Lowered: backend token flow only | C6 |

## 3. 현재 진행 중인 Decision

없음

## 4. 아직 Decision ID를 받지 않은 후보

없음

## 5. 구현 가능 조건

필수 Level 3 후보가 모두 Pass되거나 Level 1/2로 낮아진 뒤에만 구현한다.

현재 상태:
- 충족

## 6. Level 2 처리 요약

### C4. 게시글 수정/삭제 권한 검사 계층

결정:
- service 계층에서 검사한다.

이유:
- router는 인증 사용자 주입과 HTTP 요청/응답 조립을 맡는다.
- service는 게시글 조회 후 `post.user_id == current_user.id`를 비교할 수 있다.
- 권한 실패는 service 단위 테스트와 API 테스트 모두에서 확인하기 쉽다.

### C5. 게시글 응답의 `user_id` 노출

결정:
- 노출하지 않는다.

이유:
- D-006에서 `user_id`는 내부 권한 판단용으로 확정됐다.
- D-007에서 게시글 작성자 표시값을 제거했다.
- 따라서 게시글 목록/상세 응답에는 `id`, `title`, `content`, `created_at`만 포함한다.

### C7. 프론트엔드 토큰 저장 확인 범위

결정:
- 이번 구현에서는 백엔드 토큰 발급/검증 흐름만 검증한다.

이유:
- 현재 repository에는 별도 프론트엔드 앱 파일이 없다.
- Sprint 1의 프론트엔드 token 저장 완료 기준은 이후 프론트엔드 파일이 생기면 별도 구현한다.
- 현재 작업에서는 login response, protected posts request, 401/403 흐름을 백엔드 테스트로 확인한다.

## 7. Implementation Batch Snapshot

Date: 2026-06-14

Git status before code edits:

```text
 M docs/decisions/DECISIONS.md
 M docs/decisions/sprint-1/ROADMAP.md
 M docs/decisions/sprint-1/decisions/D-007-author-name-retention.md
?? docs/decisions/sprint-1/decisions/D-008-registration-api-contract.md
```

Existing user changes:
- `.gitignore`, `AGENTS.md`, `DECISION_HARNESS.md`, `docs/decisions/`, `docs/taejung/` were already project/process files in this thread and are not rollback targets unless explicitly requested.

Planned code files:
- `backend/app/models/post.py`
- `backend/app/schemas/post.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/post_service.py`
- `backend/app/api/v1/auth.py`
- `backend/app/api/v1/posts.py`
- `backend/tests/test_auth_security_flow.py`
- `backend/tests/test_posts_flow.py`
- `backend/tests/test_post_service_di.py`

Codex change scope:
- Add `posts.user_id`.
- Remove `author_name` from post create/read contract.
- Add minimal register API.
- Require authentication for post create/update/delete.
- Add update/delete post APIs with 403 owner checks.
- Keep `user_id` out of post responses.

Rollback scope:
- Remove register endpoint and related schema/service tests.
- Remove post auth requirement, `user_id`, update/delete APIs, and ownership tests.
- Restore public post create with `author_name` only if the Sprint 1 decision set is rolled back.

Rollback verification:

```bash
./.venv/bin/python -m pytest backend/tests
```

Implementation result:
- Completed: 2026-06-14
- SQLite verification: `DATABASE_URL=sqlite+pysqlite:////tmp/sprint1-implementation-test.db python3 -m pytest backend/tests` -> `14 passed`
- Default PostgreSQL verification: `python3 -m pytest backend/tests` -> failed at setup because `localhost:5433` refused connection

## 8. 롤백 이력

이 주제는 한 번 D-001~D-005로 진행되었다가 롤백됐다.

롤백 기록:
- `docs/decisions/sprint-1/rollbacks/R-001-sprint1-auth-posts-rollback.md`

롤백된 ID는 재사용하지 않는다. 같은 주제로 다시 진행하는 첫 Decision은 D-006부터 시작한다.
