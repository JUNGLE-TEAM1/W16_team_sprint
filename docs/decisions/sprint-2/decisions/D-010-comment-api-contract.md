# D-010. 댓글 API 계약은 어떻게 둘 것인가?

Date: 2026-06-15
Sprint: 2
Level: 3
Status: Accepted
Implementation: Completed
Owner: User
Chosen: A. 게시글 하위 nested 댓글 API로 통일한다.

## Evaluation Status

Current Evaluation: Pass

Reason:
- 사용자는 A를 명확히 선택했다.
- 댓글 생성/조회/수정/삭제를 모두 nested URL로 통일한다.
- 응답에는 작성자 식별/표시 정보는 노출하지 않고, `id`, `post_id`, `content`, `created_at`, `updated_at`은 반환한다.
- 테스트에는 정상 처리, 404, 비로그인 401, 타인 수정/삭제 403을 포함한다.

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-2/ROADMAP.md`

선행 결정:
- D-009: 댓글 모델은 `id`, `post_id`, `user_id`, `content`, `created_at`, `updated_at`을 가진다.

현재 Decision:
- D-010. 댓글 API 계약은 어떻게 둘 것인가?

후속 후보:
- 댓글 수정/삭제 권한 검사를 어느 계층에서 할 것인가?
- 게시글 상세 응답에 댓글을 포함할 것인가?
- 최소 화면 구현을 이번 repository에서 다룰 것인가?

이번 선택으로 자동 확정하지 않는 것:
- 권한 검사를 router/service 중 어느 계층에서 수행할지
- 게시글 상세 `GET /posts/{post_id}` 응답에 댓글을 포함할지 여부
- 프론트엔드 화면 구현 범위

## 2. 한 줄 요약

이번 결정은 댓글 생성/목록/수정/삭제 API의 URL 구조와 기본 요청/응답 계약을 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- 댓글 API URL 구조
- 댓글 생성/목록/수정/삭제 endpoint 포함 여부
- 댓글 조회를 게시글 하위 리소스로 둘지, 댓글 자체 리소스로 둘지

## 4. 왜 먼저 결정해야 하나?

댓글 model만 있어서는 Sprint 2 완료 기준을 만족할 수 없다.

API 계약이 정해져야 다음 구현 범위가 결정된다.

- router 위치
- service 메서드
- repository 조회 조건
- 401/403/404 테스트
- 게시글 상세 화면에서 댓글을 가져오는 방식

## 5. 선택지

### A. 게시글 하위 nested 댓글 API로 통일한다.

계약:
- `POST /api/v1/posts/{post_id}/comments`
- `GET /api/v1/posts/{post_id}/comments`
- `PUT /api/v1/posts/{post_id}/comments/{comment_id}`
- `DELETE /api/v1/posts/{post_id}/comments/{comment_id}`

요청:
- Create: `content`
- Update: `content`

응답:
- CommentRead: `id`, `post_id`, `content`, `created_at`, `updated_at`
- `user_id`와 작성자 표시명은 노출하지 않는다.

의미:
- 댓글은 항상 게시글 맥락 안에서 다룬다.
- `post_id`와 `comment_id`가 맞지 않으면 404로 처리할 수 있다.
- 게시글 상세 화면에서 댓글 목록을 별도 호출로 가져온다.

### B. 생성/목록은 nested, 수정/삭제는 댓글 단독 API로 둔다.

계약:
- `POST /api/v1/posts/{post_id}/comments`
- `GET /api/v1/posts/{post_id}/comments`
- `PUT /api/v1/comments/{comment_id}`
- `DELETE /api/v1/comments/{comment_id}`

요청:
- Create: `content`
- Update: `content`

응답:
- CommentRead: `id`, `post_id`, `content`, `created_at`, `updated_at`

의미:
- 생성/목록은 게시글 맥락을 사용한다.
- 수정/삭제는 comment id만 알면 호출할 수 있어 URL이 짧다.
- 수정/삭제 시 댓글이 어느 게시글에 속하는지 URL만으로는 드러나지 않는다.

### C. 게시글 상세 응답에 댓글 목록을 포함한다.

계약:
- `POST /api/v1/posts/{post_id}/comments`
- `GET /api/v1/posts/{post_id}` 응답에 `comments` 포함
- `PUT /api/v1/posts/{post_id}/comments/{comment_id}`
- `DELETE /api/v1/posts/{post_id}/comments/{comment_id}`

요청:
- Create: `content`
- Update: `content`

응답:
- PostDetailRead: 게시글 필드 + `comments`
- CommentRead: `id`, `post_id`, `content`, `created_at`, `updated_at`

의미:
- 게시글 상세 화면은 한 번의 API 호출로 댓글을 받을 수 있다.
- 기존 `PostRead`와 상세 응답 schema가 갈라진다.
- 게시글 상세 API의 응답 계약이 커진다.

## 6. 선택지 비교

| 기준 | A. nested 통일 | B. mixed | C. 상세 포함 |
| --- | --- | --- | --- |
| 게시글-댓글 관계 표현 | 높음 | 중간 | 높음 |
| URL 단순성 | 중간 | 높음 | 중간 |
| 기존 PostRead 영향 | 낮음 | 낮음 | 높음 |
| 상세 화면 편의 | 중간 | 중간 | 높음 |
| 테스트 명확성 | 높음 | 중간 | 중간 |
| 되돌리기 비용 | 중간 | 중간 | 높음 |

## 7. Codex 추천

추천: A

이유:
- 댓글은 게시글 하위 리소스이므로 URL에서 관계가 명확하다.
- 기존 `GET /posts/{post_id}` 응답 계약을 바로 키우지 않아도 된다.
- `post_id`와 `comment_id` 불일치 테스트를 만들 수 있어 스코프가 명확하다.
- Sprint 2 완료 기준의 "게시글 상세 화면에서 댓글 조회"는 프론트엔드가 상세 진입 후 댓글 목록 API를 호출하는 방식으로 충족할 수 있다.

## 8. Pass 기준

사용자 답변이 Pass 되려면 다음을 포함해야 한다.

- A, B, C 중 하나를 명확히 선택한다.
- 댓글 수정 API를 포함할지 확인한다.
- 게시글 상세 응답에 댓글을 포함할지, 별도 조회로 둘지 설명한다.
- `user_id` 또는 작성자 표시명을 응답에 노출할지 설명한다.
- 401/403/404 테스트에서 무엇을 확인할지 대략 구분한다.

## 9. 사용자 답변 템플릿

```md
선택:

이유:

댓글 수정 API 포함 여부:

댓글 조회 방식:

응답에 작성자 식별/표시 정보 노출 여부:

테스트에서 확인할 것:
```

## 10. Lowered Decisions

### C4. 댓글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?

임시 판단:
- Level 2로 낮출 수 있다.

추천:
- service 계층에서 검사한다.

이유:
- Sprint 1 게시글 수정/삭제 권한 검사가 `PostService`에 있다.
- 댓글도 조회 후 `comments.user_id == current_user.id`를 비교해야 하므로 service 계층이 기존 패턴과 맞다.
- router는 인증 사용자 주입과 path/body validation에 집중할 수 있다.

## 11. Q&A

### Q1. 사용자 1차 답변 평가

사용자 답변:

```md
선택: A

이유: 형식 통일로 인한 유지 보수 편의성, 개발 편의성

댓글 수정 API 포함 여부: 댓글 수정도 일단 포함하는걸로

댓글 조회 방식: nested로 통일

응답에 작성자 식별/표시 정보 노출 여부: 불필요해 보임 그냥 코멘트id 만 있어도 가능

테스트에서 확인할 것: 404 처리 응답, 정상 처리 응답
```

Codex 평가:
- Hold

좋은 점:
- A 선택이 명확하다.
- 댓글 생성/조회/수정/삭제를 모두 nested URL로 통일한다는 방향이 명확하다.
- 댓글 수정 API 포함 여부가 명확하다.
- 작성자 식별/표시 정보를 응답에 노출하지 않는 방향은 D-009와 일관된다.
- 404와 정상 처리 테스트 필요성을 언급했다.

보완이 필요한 점:
- "그냥 코멘트id 만 있어도 가능"이 문자 그대로 응답에 `id`만 둔다는 뜻인지, 작성자 정보 없이 `id`, `post_id`, `content`, `created_at`, `updated_at`은 반환한다는 뜻인지 확인이 필요하다.
- 테스트 기준에서 비로그인 `401`, 타인 수정/삭제 `403`을 포함할지 확인이 필요하다.

### Q2. 사용자 보완 답변 평가

Codex 질문:

```md
1. "그냥 코멘트id만 있어도 가능"은 작성자 식별/표시 정보만 빼고 `id`, `post_id`, `content`, `created_at`, `updated_at`은 반환한다는 뜻인가요?
2. 테스트는 정상/404에 더해서 비로그인 401, 타인 수정/삭제 403도 포함해도 되나요?
```

사용자 답변:

```md
1. A안 그대로를 말하는거야 작성자 식별/ 표시 정보는 불필요하다는 뜻이고
2. 포함시켜
```

Codex 평가:
- Pass

통과 이유:
- A 선택과 nested URL 통일 방향이 명확하다.
- 댓글 수정 API 포함이 명확하다.
- 댓글 조회는 별도 nested 목록 API로 둔다.
- 응답에는 작성자 식별/표시 정보를 노출하지 않고 댓글 본문/시간 필드는 반환한다.
- 테스트 범위에 정상, 404, 401, 403이 포함됐다.

## 12. 롤백 계획

예상 변경 파일:

- `backend/app/schemas/comment.py`
- `backend/app/repositories/comment_repository.py`
- `backend/app/services/comment_service.py`
- `backend/app/api/dependencies.py`
- `backend/app/api/v1/posts.py` 또는 `backend/app/api/v1/comments.py`
- `backend/tests/test_comments_flow.py`
- `backend/tests/test_comment_service_di.py`

DB 영향:

- D-009의 `comments` 테이블 설계 안에서 동작한다.
- 이 Decision 자체는 추가 컬럼을 만들지 않는다.

롤백 방법:

- 선택한 댓글 endpoint와 schema/service/repository/test 변경분을 제거한다.
- D-009 모델만 남겨야 하는지, 댓글 기능 전체를 되돌릴지 사용자가 판단한다.

롤백 확인:

```bash
python3 -m pytest backend/tests
```

재검토 조건:
- 사용자가 API 계약 선택이 잘못됐다고 판단한다.
- 프론트엔드 상세 화면 요구가 한 번의 API 호출을 강제한다.
- 댓글 작성자 표시 또는 사용자 프로필 정책이 확정된다.

## 12.1 Pre-Implementation Notes

Recorded: 2026-06-15

선택:
- A. 게시글 하위 nested 댓글 API로 통일한다.

구현 전 상태:
- 아직 댓글 API 구현을 시작하지 않았다.
- D-009 모델 결정은 Accepted/Planned 상태다.
- 최소 화면 구현 범위는 아직 확정되지 않았다.

확정 계약:
- `POST /api/v1/posts/{post_id}/comments`
- `GET /api/v1/posts/{post_id}/comments`
- `PUT /api/v1/posts/{post_id}/comments/{comment_id}`
- `DELETE /api/v1/posts/{post_id}/comments/{comment_id}`

응답:
- `id`, `post_id`, `content`, `created_at`, `updated_at`
- `user_id`와 작성자 표시 정보는 노출하지 않는다.

테스트:
- 정상 생성/조회/수정/삭제
- 없는 게시글 또는 게시글-댓글 불일치 404
- 비로그인 작성/수정/삭제 401
- 타인 댓글 수정/삭제 403

## 13. 다음 분기

D-010이 Pass되면 권한 검사 계층과 테스트 범위를 Level 2로 낮출 수 있는지 재분류한다.

## 14. 구현 결과

Completed: 2026-06-15

구현 내용:
- nested 댓글 API를 추가했다.
- `POST /api/v1/posts/{post_id}/comments`
- `GET /api/v1/posts/{post_id}/comments`
- `PUT /api/v1/posts/{post_id}/comments/{comment_id}`
- `DELETE /api/v1/posts/{post_id}/comments/{comment_id}`
- 응답에는 `id`, `post_id`, `content`, `created_at`, `updated_at`을 반환하고 작성자 식별/표시 정보는 노출하지 않는다.

검증:
- 정상 생성/조회/수정/삭제
- 없는 게시글 또는 게시글-댓글 불일치 404
- 비로그인 401
- 타인 댓글 수정/삭제 403
- `DATABASE_URL=sqlite+pysqlite:////tmp/sprint2-implementation-test.db python3 -m pytest backend/tests` -> `21 passed`
