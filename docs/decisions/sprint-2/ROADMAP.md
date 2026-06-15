# Sprint 2 Decision Roadmap

Date: 2026-06-14

## 1. 목적

Sprint 2는 게시글 CRUD + 댓글을 완성한다.

기준 문서:
- `docs/taejung/development-order.md`

Sprint 2 완료 기준:
- 로그인한 사용자가 게시글을 작성할 수 있다.
- 게시글 목록을 조회할 수 있다.
- 게시글 상세 화면을 조회할 수 있다.
- 작성자만 게시글을 수정/삭제할 수 있다.
- 댓글을 작성할 수 있다.
- 게시글 상세 화면에서 댓글을 조회할 수 있다.

## 2. Sprint 1에서 이미 완료된 기반

Posts:
- 게시글 작성
- 게시글 목록 조회
- 게시글 상세 조회
- 게시글 수정
- 게시글 삭제
- 작성자 권한 검사

Auth:
- 회원가입
- 로그인
- JWT 발급/검증
- current_user 확인
- 401/403 응답 흐름

## 3. 전체 후보 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 댓글 모델은 어떤 필드를 가질 것인가? | Level 3 | Accepted | Sprint 1 auth |
| 2 | C2 | 댓글 API 계약은 어떻게 둘 것인가? | Level 3 | Accepted | C1 |
| 3 | C3 | 댓글 조회 API는 게시글 상세에 포함할 것인가, 별도 endpoint로 둘 것인가? | Level 3 또는 2 | Accepted in D-010 | C1 |
| 4 | C4 | 댓글 삭제/수정 권한은 작성자만 허용할 것인가? | Level 2 | Lowered | C1, C2 |
| 5 | C5 | 게시글 CRUD 기존 구현은 Sprint 2 범위에서 보강이 필요한가? | Level 2 | Pending | Sprint 1 posts |
| 6 | C6 | 최소 화면 구현을 이번 repository에서 다룰 것인가? | Level 3 | Accepted | frontend 부재 |
| 7 | C7 | 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가? | Level 3 | Accepted | C6 |

## 4. 현재 진행 중인 Decision

없음

## 5. 아직 Decision ID를 받지 않은 후보

- C4: 댓글 삭제/수정 권한은 작성자만 허용할 것인가? (D-010 이후 Level 2로 낮아짐)
- C5: 게시글 CRUD 기존 구현은 Sprint 2 범위에서 보강이 필요한가?
없음

## 6. 구현 가능 조건

필수 Level 3 후보가 모두 Pass되거나 Level 1/2로 낮아진 뒤에만 구현한다.

필수 Level 3 후보:
- 모두 Accepted

## 7. Sprint 2 Decisions

Accepted:
- D-009. 댓글 모델은 어떤 필드를 가질 것인가?
- D-010. 댓글 API 계약은 어떻게 둘 것인가?
- D-011. 최소 화면 구현을 이번 repository에서 다룰 것인가?
- D-012. 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가?

Proposed:
- 없음

주의:
- 이 문서는 후보 지도다.
- D-009는 Accepted 되었고 구현 전 Planned 상태다.
- D-010은 Accepted 되었고 구현 전 Planned 상태다.
- D-011은 Accepted 되었고 구현 전 Planned 상태다.
- D-012는 Accepted 되었고 구현 전 Planned 상태다.

## 8. Implementation Batch Snapshot

Recorded: 2026-06-15

현재 git status:

```text
 M AGENTS.md
 M DECISION_HARNESS.md
 M backend/app/api/v1/auth.py
 M backend/app/api/v1/posts.py
 M backend/app/models/post.py
 M backend/app/repositories/post_repository.py
 M backend/app/schemas/auth.py
 M backend/app/schemas/post.py
 M backend/app/services/auth_service.py
 M backend/app/services/post_service.py
 M backend/tests/test_auth_security_flow.py
 M backend/tests/test_post_service_di.py
 M backend/tests/test_posts_flow.py
 M docs/decisions/DECISIONS.md
 M docs/decisions/decision-harness-flow.md
 M docs/decisions/sprint-1/ROADMAP.md
 M docs/decisions/sprint-1/decisions/D-006-post-user-id.md
 M docs/decisions/sprint-1/decisions/D-007-author-name-retention.md
 M docs/taejung/development-order.md
?? docs/decisions/sprint-1/SUMMARY.md
?? docs/decisions/sprint-1/decisions/D-008-registration-api-contract.md
?? docs/decisions/sprint-2/ROADMAP.md
?? docs/decisions/sprint-2/decisions/D-009-comment-model-fields.md
?? docs/decisions/sprint-2/decisions/D-010-comment-api-contract.md
?? docs/decisions/sprint-2/decisions/D-011-frontend-scope.md
?? docs/decisions/sprint-2/decisions/D-012-frontend-stack.md
?? docs/decisions/sprint-2/troubleshooting/D-009-comment-model-fields-qna.md
?? docs/decisions/sprint-2/troubleshooting/D-010-comment-api-contract-qna.md
?? docs/decisions/sprint-2/troubleshooting/D-011-frontend-scope-qna.md
?? docs/decisions/sprint-2/troubleshooting/D-012-frontend-stack-qna.md
?? docs/taejung/reference/
```

수정 예정 파일:
- `backend/app/models/comment.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/comment.py`
- `backend/app/repositories/comment_repository.py`
- `backend/app/services/comment_service.py`
- `backend/app/api/dependencies.py`
- `backend/app/api/v1/posts.py`
- `backend/tests/test_comments_flow.py`
- `backend/tests/test_comment_service_di.py`
- `frontend/`
- `docs/decisions/sprint-2/SUMMARY.md`
- `docs/decisions/sprint-3/ROADMAP.md`
- Sprint 2 Decision 문서의 Implementation 상태

기존 사용자 변경 여부:
- 작업 시작 시점에 여러 backend/test/docs 파일이 이미 수정되어 있었다.
- 기존 수정은 사용자 또는 이전 작업 산출물로 간주하고 롤백 대상에 포함하지 않는다.
- `backend/app/api/v1/posts.py`, `backend/app/api/dependencies.py`처럼 구현상 필요한 파일만 기존 패턴을 보존하며 최소 범위로 수정한다.

Codex 변경 범위:
- 댓글 모델/스키마/repository/service/API/test 추가
- 댓글 API를 nested route로 구현
- Vite + React + TypeScript 최소 화면 추가
- Sprint 2 완료 문서와 Sprint 3 Roadmap 작성

롤백 시 되돌릴 범위:
- 댓글 관련 신규 파일과 `posts.py`/dependencies의 댓글 연결부
- `frontend/` 신규 앱
- Sprint 2 구현 결과 문서 업데이트
- 사용자 기존 변경은 되돌리지 않는다.

롤백 확인 명령 또는 테스트:

```bash
python3 -m pytest backend/tests
cd frontend && npm test -- --run
cd frontend && npm run build
```
