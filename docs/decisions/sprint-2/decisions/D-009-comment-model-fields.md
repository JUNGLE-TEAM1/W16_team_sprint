# D-009. 댓글 모델은 어떤 필드를 가질 것인가?

Date: 2026-06-14
Sprint: 2
Level: 3
Status: Accepted
Implementation: Completed
Owner: User
Chosen: C. 수정 추적까지 포함한 확장 모델

## Evaluation Status

Current Evaluation: Pass

Reason:
- 사용자는 댓글 수정 기능까지 Sprint 2 범위에 포함한다고 명확히 밝혔다.
- 댓글 권한 판단은 `comments.user_id == current_user.id`로 정리했다.
- 댓글 작성자 표시 정보는 프로필 정책이 없으므로 현재 row에 중복 저장하지 않는다.
- 댓글 수정을 포함하므로 `updated_at`을 함께 저장하는 C가 선택 의도와 맞다.
- 롤백/재검토는 사용자가 완전히 잘못된 선택이라고 판단하거나 재학습 필요가 생긴 경우 수행한다는 기준으로 기록했다.

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-2/ROADMAP.md`

선행 기반:
- Sprint 1에서 `posts.user_id`를 권한 판단용으로 추가했다.
- Sprint 1에서 게시글 작성/수정/삭제는 로그인 사용자 기준으로 동작한다.

현재 Decision:
- D-009. 댓글 모델은 어떤 필드를 가질 것인가?

후속 후보:
- 댓글 작성 API 계약은 어떻게 둘 것인가?
- 댓글 조회 API는 게시글 상세에 포함할 것인가, 별도 endpoint로 둘 것인가?
- 댓글 삭제 권한은 작성자만 허용할 것인가?
- 게시글 CRUD 기존 구현은 Sprint 2 범위에서 보강이 필요한가?
- 최소 화면 구현을 이번 repository에서 다룰 것인가?

이번 선택으로 자동 확정하지 않는 것:
- 댓글 생성 요청/응답의 정확한 API 계약
- 댓글 목록을 `GET /posts/{id}` 응답에 포함할지 여부
- 댓글 조회 전용 endpoint 형태
- 댓글 삭제 endpoint 형태
- 프론트엔드 화면 구현 범위

## 2. 한 줄 요약

이번 결정은 댓글 row가 어떤 최소 필드로 게시글과 로그인 사용자를 참조할지 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- 댓글 DB 모델의 핵심 필드
- 댓글이 `posts.id`와 `users.id`를 참조할지 여부
- 표시용 작성자 정보를 댓글 row에 중복 저장할지 여부
- 수정 추적용 `updated_at`을 Sprint 2에서 포함할지 여부

## 4. 왜 먼저 결정해야 하나?

Sprint 2 완료 기준에는 다음 항목이 있다.

- 댓글을 작성할 수 있다.
- 게시글 상세 화면에서 댓글을 조회할 수 있다.
- 작성자만 게시글을 수정/삭제할 수 있다.

댓글 작성과 조회를 구현하려면 댓글이 어떤 게시글에 속하는지 알아야 한다.
댓글 삭제 권한까지 구현하려면 댓글 작성자를 안정적으로 식별할 값이 필요하다.

게시글에서 이미 `posts.user_id`를 권한 판단용으로 쓰기로 했으므로, 댓글도 같은 기준을 따를지 먼저 정해야 한다.

## 5. 선택지

### A. 최소 정규화 모델

필드:
- `id`
- `post_id`
- `user_id`
- `content`
- `created_at`

의미:
- 댓글은 게시글과 사용자 row를 참조한다.
- 권한 판단은 `comments.user_id == current_user.id`로 처리할 수 있다.
- 표시용 작성자 값은 댓글 row에 중복 저장하지 않는다.
- `updated_at`은 댓글 수정 기능이 생길 때 추가한다.

### B. 작성자 표시값까지 중복 저장

필드:
- `id`
- `post_id`
- `user_id`
- `author_name`
- `content`
- `created_at`

의미:
- 권한 판단은 `user_id`로 하고, 표시값은 `author_name`으로 빠르게 응답할 수 있다.
- 사용자 표시 정책이 바뀌면 댓글 row의 중복 데이터가 낡을 수 있다.
- Sprint 1에서 `Post.author_name`을 제거한 방향과 다소 달라진다.

### C. 수정 추적까지 포함한 확장 모델

필드:
- `id`
- `post_id`
- `user_id`
- `content`
- `created_at`
- `updated_at`

의미:
- 댓글 수정 기능을 나중에 추가하기 쉽다.
- Sprint 2 완료 기준에는 댓글 수정이 없으므로 현재 범위보다 조금 넓다.
- `updated_at` 갱신 규칙과 테스트가 추가된다.

## 6. 선택지 비교

| 기준 | A. 최소 정규화 | B. 표시값 중복 | C. 수정 추적 포함 |
| --- | --- | --- | --- |
| Sprint 2 완료 기준 | 충족 | 충족 | 충족 |
| 권한 검사 안정성 | 높음 | 높음 | 높음 |
| Sprint 1 게시글 모델과 일관성 | 높음 | 낮음 | 높음 |
| API 응답 확장성 | 중간 | 높음 | 중간 |
| DB 중복 | 낮음 | 중간 | 낮음 |
| 구현 복잡도 | 낮음 | 중간 | 중간 |
| 되돌리기 비용 | 중간 | 중간 | 중간 |

## 7. Codex 추천

초기 추천: A

이유:
- Sprint 2 완료 기준을 만족하는 최소 모델이다.
- Sprint 1에서 `Post.author_name`을 제거하고 `user_id`를 권한 기준으로 둔 흐름과 일관된다.
- 댓글 삭제 권한을 `comments.user_id` 기준으로 명확히 구현할 수 있다.
- 댓글 수정 기능이 아직 완료 기준에 없으므로 `updated_at`은 후속 스프린트에서 필요해질 때 추가해도 된다.

최종 선택: C

변경 이유:
- 사용자가 댓글 수정 기능도 Sprint 2 범위에 포함한다고 명확히 밝혔다.
- 댓글 수정이 포함되면 수정 시각 추적용 `updated_at`을 모델에 포함하는 편이 테스트와 API 응답 설명에 더 적합하다.

## 8. Pass 기준

사용자 답변이 Pass 되려면 다음을 포함해야 한다.

- A, B, C 중 하나를 명확히 선택한다.
- 댓글 권한 판단을 어떤 값으로 할지 설명한다.
- 댓글 표시용 작성자 정보를 이번 모델에 저장할지 말지 설명한다.
- DB/API/테스트 중 무엇이 바뀌는지 언급한다.
- 댓글 작성 API, 조회 방식, 삭제 endpoint는 후속 분기로 남는다는 점을 인정한다.
- 롤백 또는 재검토 조건을 설명한다.

## 9. 사용자 답변 템플릿

```md
선택:

이유:

댓글 권한 판단 기준:

표시용 작성자 정보 저장 여부:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:

롤백 또는 재검토 조건:
```

## 10. Lowered Decisions

아직 없음.

## 11. Q&A

### Q1. 사용자 1차 답변 평가

사용자 답변:

```md
선택: A

이유: 이번에는 댓글 기능 CRUD를 전부 만들어야한다고 생각한다.

댓글 권한 판단 기준: 권한 판단은 user_id랑 post_id를 비교해서 본인인지 확인

표시용 작성자 정보 저장 여부: 댓글에 작성자 정보는 아직 프로필이 없으므로 애매하다고 판단

DB/API/테스트 영향: DB에는 관련 테이블 추가, api는 선택지에 포함된 CRUD API추가, 테스트는 기본 단위 API테스트 추가

아직 다음 분기로 남겨둘 것: 남은 부분들

롤백 또는 재검토 조건: 다음 분기 가서 정함
```

Codex 평가:
- Hold

좋은 점:
- A 선택이 명확하다.
- 댓글 작성자 표시 정보를 지금 저장하지 않는 방향은 A와 맞다.
- DB 테이블 추가, API 추가, 테스트 추가 영향은 이해하고 있다.

보완이 필요한 점:
- D-009의 A는 댓글 모델 필드 결정이며, 댓글 전체 CRUD API 계약은 후속 분기다.
- Sprint 2 완료 기준에는 댓글 작성/조회/삭제가 있고, 댓글 수정은 명시되어 있지 않다. "CRUD 전부"가 댓글 수정까지 포함하는지 확인이 필요하다.
- 권한 판단에서 `post_id`는 댓글이 특정 게시글에 속하는지 확인하는 값이고, 본인 여부는 `comments.user_id == current_user.id`로 판단해야 한다.
- "남은 부분들", "다음 분기 가서 정함"은 후속 분기와 재검토 조건이 너무 넓어 Pass하기 어렵다.

### Q2. 사용자 보완 답변 평가

Codex 질문:

```md
1. "댓글 CRUD 전부"라고 한 게 댓글 수정(Update)까지 포함한다는 뜻인가요?
2. 권한 판단은 본인 여부를 `comments.user_id == current_user.id`로 보고, `post_id`는 게시글 스코프 확인값으로 정리해도 되나요?
3. 롤백/재검토 조건은 작성자 표시명 필요, 댓글 수정 범위 포함, 댓글 관련 변경 제거로 두면 될까요?
```

사용자 답변:

```md
1. 수정 기능도 포함한다는거야
2. 맞아 userid기준으로 가자
3. 롤백 기준은 완전히 잘못된 선택을 했을때, 아니면 재학습 등의 이유로 내가 필요하다고 판단했을때야 이렇게 물어볼 필요는 없는 부분같아
```

Codex 평가:
- Hold

좋은 점:
- 댓글 수정도 Sprint 2 범위에 포함한다는 의도가 명확해졌다.
- 권한 판단 기준은 `comments.user_id == current_user.id`로 정리됐다.
- `post_id`는 본인 판단 값이 아니라 게시글 스코프 확인값으로 분리됐다.
- 롤백/재검토는 사용자가 완전히 잘못된 선택이라고 판단하거나 재학습 필요가 생긴 경우 수행한다는 기준으로 기록한다.

보완이 필요한 점:
- 사용자는 A를 선택했지만, 댓글 수정 기능을 포함한다고 밝혔다.
- A는 `updated_at` 없이 최소 필드로 가는 선택이고, C는 댓글 수정 추적을 위해 `updated_at`을 포함하는 선택이다.
- 따라서 댓글 수정 기능을 포함하되 수정 시각 추적은 하지 않을지, 아니면 C로 바꿔 `updated_at`까지 포함할지 확인이 필요하다.

### Q3. 사용자 최종 답변 평가

Codex 질문:

```md
댓글 수정 기능을 포함하되 `updated_at` 없이 A로 갈까요, 아니면 `updated_at`까지 포함하는 C로 바꿀까요?
```

사용자 답변:

```md
C로 가자
```

Codex 평가:
- Pass

통과 이유:
- 최종 선택이 C로 명확하다.
- 댓글 수정 기능 포함이라는 사용자의 범위 판단과 `updated_at` 포함 모델이 일치한다.
- 권한 판단은 이전 답변에서 `comments.user_id == current_user.id`로 정리됐다.
- 댓글 작성자 표시 정보는 현재 저장하지 않는 것으로 정리됐다.
- API 계약과 조회 방식은 D-010에서 별도 결정한다.

## 12. 롤백 계획

예상 변경 파일:

- `backend/app/models/comment.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/comment.py`
- `backend/app/repositories/comment_repository.py`
- `backend/app/services/comment_service.py`
- `backend/app/api/dependencies.py`
- `backend/app/api/v1/posts.py` 또는 댓글 전용 router
- `backend/tests/test_comments_flow.py`
- `backend/tests/test_comment_service_di.py`

DB 영향:

- 새 `comments` 테이블이 추가된다.
- C 선택에 따라 `comments.updated_at` 컬럼도 추가된다.
- 현재 마이그레이션 도구가 없으므로 로컬 개발 DB 재생성이 필요할 수 있다.
- 새 테이블 추가라 기존 `posts`/`users` 데이터 손실은 의도하지 않는다.

롤백 방법:

- 댓글 model/schema/repository/service/router/test 변경분을 제거한다.
- `Base.metadata.create_all()` 기반 테스트에서는 `comments` 테이블 생성 경로가 사라지는지 확인한다.
- 이미 생성된 로컬 DB는 필요 시 재생성한다.

롤백 확인:

```bash
python3 -m pytest backend/tests
```

재검토 조건:
- 사용자가 선택이 완전히 잘못됐다고 판단한다.
- 재학습 또는 재진입을 위해 사용자가 필요하다고 판단한다.

## 12.1 Pre-Implementation Notes

Recorded: 2026-06-15

선택:
- C. 수정 추적까지 포함한 확장 모델

구현 전 상태:
- 아직 댓글 model/schema/repository/service/router/test는 구현하지 않았다.
- D-010 댓글 API 계약이 아직 Proposed 상태이므로 구현을 시작하지 않는다.

예상 구현 범위:
- `comments` 테이블에는 `id`, `post_id`, `user_id`, `content`, `created_at`, `updated_at`을 둔다.
- `post_id`는 게시글 스코프 확인에 사용한다.
- `user_id`는 댓글 수정/삭제 권한 판단에 사용한다.
- 작성자 표시용 필드는 댓글 row에 저장하지 않는다.

## 13. 다음 분기

D-009가 Pass되면 다음 후보를 재분류한다.

예상 다음 후보:
- D-010. 댓글 API 계약
- 댓글 수정/삭제 권한 적용 범위

## 14. 구현 결과

Completed: 2026-06-15

구현 내용:
- `comments` 테이블 모델을 추가했다.
- 필드는 `id`, `post_id`, `user_id`, `content`, `created_at`, `updated_at`이다.
- 댓글 row에는 작성자 표시 정보를 저장하지 않는다.
- 댓글 권한 판단은 `comments.user_id == current_user.id` 기준으로 구현했다.

검증:
- `DATABASE_URL=sqlite+pysqlite:////tmp/sprint2-implementation-test.db python3 -m pytest backend/tests` -> `21 passed`
