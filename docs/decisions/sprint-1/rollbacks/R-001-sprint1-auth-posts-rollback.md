# R-001. Sprint 1 인증/게시글 권한 구현 롤백

Date: 2026-06-13
Related Decisions: D-001, D-002, D-003, D-004, D-005
Requested By: User

## 1. 롤백 요청

사용자 요청:

```text
그리고 스프린트1은 롤백할게 롤백한 내용은 자동으로 롤백 기록 폴더에 들어가면 좋을것같네
```

## 2. 롤백 범위

Sprint 1 구현 코드와 예시를 롤백했다.

롤백한 항목:

- 회원가입 API 추가분
- 게시글 작성 인증 필수화
- `posts.user_id` 컬럼 추가분
- `author_name=current_user.email` 서버 생성 로직
- 게시글 수정 API
- 게시글 삭제 API
- 게시글 소유자 403 검사
- 정적 프론트엔드 `frontend/index.html`
- README의 Sprint 1 인증/프론트/보호 게시글 요청 예시
- Sprint 1 구현을 검증하던 테스트 변경분

유지한 항목:

- Decision Harness 운영 규칙 보완
- 이 롤백 기록

정리 원칙:

- 롤백된 Sprint 1 구현과 그 과정에서 생긴 분기/학습/트러블슈팅 상세 기록은 이 문서가 책임진다.
- `docs/decisions/sprint-1/decisions/`, `docs/decisions/sprint-1/troubleshooting/`에는 롤백된 기록을 남기지 않는다.
- 해당 폴더들은 앞으로 실제 진행 중이거나 유지되는 Decision 기록용으로 사용한다.

## 3. 변경 파일

코드/테스트:

- `backend/app/models/post.py`
- `backend/app/schemas/post.py`
- `backend/app/repositories/post_repository.py`
- `backend/app/api/v1/posts.py`
- `backend/app/services/post_service.py`
- `backend/app/api/v1/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/tests/test_posts_flow.py`
- `backend/tests/test_auth_security_flow.py`
- `backend/tests/test_post_service_di.py`

문서/프론트:

- `README.md`
- `frontend/index.html`
- `docs/decisions/DECISIONS.md`
- `docs/decisions/sprint-1/rollbacks/R-001-sprint1-auth-posts-rollback.md`

## 4. 롤백 후 상태

- 게시글은 다시 `author_name` 문자열 기반으로 생성된다.
- `POST /api/v1/posts`는 인증 토큰을 요구하지 않는다.
- 게시글 수정/삭제 API는 제거됐다.
- 회원가입 API는 제거됐다.
- 로그인, current_user, refresh, logout, admin role, CSRF 데모 흐름은 기존대로 남아 있다.

## 5. DB 영향

`posts.user_id` 컬럼 추가분을 모델에서 제거했다.

마이그레이션 도구가 없으므로 이미 Sprint 1 구현 상태로 로컬 DB를 생성했다면 개발 DB 재생성이 필요할 수 있다.

## 6. 검증 결과

권장 확인 명령:

```bash
docker compose up -d db
./.venv/bin/python -m pytest backend/tests
```

Docker 데몬이 꺼져 있어 PostgreSQL 통합 테스트는 실행하지 못했다.

보조 확인 명령:

```bash
DATABASE_URL=sqlite+pysqlite:////tmp/sprint1-rollback-test.db python3 -m pytest backend/tests
```

보조 확인 결과:

```text
9 passed
```

## 7. 다음 재진입 조건

Sprint 1 구현을 다시 진행할 때는 보완된 Decision Harness에 따라 다음 순서로 진행한다.

주의:

- D-001~D-005는 롤백된 ID이므로 재사용하지 않는다.
- 같은 주제를 다시 진행하면 새 Decision ID를 D-006부터 예약한다.

예상 재진입 순서:

1. D-006: 게시글에 `user_id`를 추가할 것인가?
2. D-007: `author_name`을 유지할 것인가?
3. D-008: `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?
4. D-009: 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
5. D-010: 게시글 응답에 `user_id`를 노출할 것인가?

## 8. 롤백된 Decision 기록 아카이브

아래 기록은 원래 `DECISIONS.md`, `decisions/`, `troubleshooting/`에 흩어졌을 Sprint 1 구현 관련 기록을 롤백 문서로 모은 것이다.

### D-001. 게시글에 `user_id`를 추가할 것인가?

결과: Rolled Back

선택:
- A. `posts.user_id`를 추가한다.

선택 이유:
- 수정/삭제 API의 권한 확인을 위해 게시글에 `user_id`를 추가하는 것이 필요하다고 판단했다.
- 표시용 데이터와 권한용 식별자를 분리하는 틀이 앞으로도 유지할 만하다고 보았다.

Pass 평가:
- 사용자가 `user_id`의 목적을 권한 검사로 이해했다.
- 표시용 작성자와 권한용 식별자를 구분했다.

롤백:
- `posts.user_id` 모델 변경과 게시글 작성자 연결 로직을 제거했다.

### D-002. `author_name`을 유지할 것인가?

결과: Rolled Back

선택:
- A. `author_name`을 표시용 필드로 유지한다.

선택 이유:
- 이메일은 UX 표시용으로 괜찮고, 학습 목적상 표시용 데이터와 권한용 식별자를 분리하는 다양성이 있다고 보았다.

Pass 평가:
- `author_name`을 권한 기준이 아니라 UX 표시용으로 한정했다.

롤백:
- `author_name=current_user.email` 구현을 제거하고 기존 클라이언트 입력 방식으로 되돌렸다.

### D-003. `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?

결과: Rolled Back

선택:
- A. 서버가 현재 사용자 정보에서 생성한다.

선택 이유:
- 이메일 표시용이라면 유지해도 되지만, 권한 기준은 `user_id`로 두는 것이 맞다고 판단했다.

Pass 평가:
- 표시용 값은 서버가 현재 사용자에서 만들면 클라이언트가 다른 사람 이름을 보내는 문제를 피할 수 있다.

롤백:
- 서버 생성 방식을 제거하고 기존 요청 body 입력 방식으로 되돌렸다.

### D-004. 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?

결과: Rolled Back

선택:
- 서비스 계층에서 검사한다.

평가:
- 게시글 도메인 규칙이 서비스에 모이면 테스트하기 쉽고 라우터는 HTTP 입출력에 집중할 수 있다.

롤백:
- `PostService._ensure_owner()`와 수정/삭제 권한 검사 API를 제거했다.

### D-005. 게시글 응답에 `user_id`를 노출할 것인가?

결과: Rolled Back

선택:
- Sprint 1 학습/테스트 확인을 위해 응답에 `user_id`를 노출한다.

평가:
- Sprint 1 학습용으로는 `user_id` 노출이 흐름 확인에 도움이 된다.
- 실제 제품에서는 공개 식별자 정책을 별도로 검토할 수 있다.

롤백:
- `PostRead.user_id`를 제거했다.

## 9. 롤백된 Q&A 아카이브

### Q1. `author_name`은 어디서 생성되나?

답변 요약:
- 롤백 전 구현안에서는 클라이언트가 `author_name`을 보내지 않고, 백엔드가 JWT access token으로 현재 사용자를 확인한 뒤 `current_user.email`에서 생성하기로 했다.
- 롤백 후에는 기존처럼 클라이언트 요청 body의 `author_name`을 저장한다.

### Q2. 게시글에 이메일만 표시하는 거라면 `author_name`을 유지해도 괜찮지 않나?

답변 요약:
- `author_name`을 권한 판단 기준으로 쓰지 않고 표시용 이메일 스냅샷으로만 쓰면 유지할 수 있다.
- 롤백 후에는 이 결정이 구현에 남아 있지 않다.

### Q3. 인증 토큰에는 어떤 정보들이 들어가나?

답변 요약:
- 현재 JWT payload에는 `sub`, `role`, `type`, `sid`, `jti`, `iat`, `exp`가 들어간다.
- `sub`는 사용자 ID 문자열이며, 롤백 전 구현안에서는 게시글의 `user_id`와 비교할 핵심 값이었다.
- 이메일은 토큰에 들어 있지 않다.

## 10. 실패 원인 메모

이번 Sprint 1 구현 자체보다 Decision Harness 운영이 먼저 미숙했다.

문제:
- 여러 분기를 D-001 하나로 뭉뚱그려 제시했다.
- 사용자의 답변을 너무 쉽게 Pass 처리했다.
- 롤백된 상세 기록을 활성 Decision 문서와 troubleshooting에 남겨 문서 책임이 흐려졌다.

보완:
- Decision Harness를 순차 분기 방식으로 고쳤다.
- Pass 전 보완 질문 규칙을 추가했다.
- 롤백된 기록은 `rollbacks/` 폴더가 책임지도록 정리했다.
