# D-007. `author_name`을 유지할 것인가?

Date: 2026-06-14
Sprint: 1
Level: 3
Status: Proposed
Implementation: Not Started
Owner: User

## Evaluation Status

Current Evaluation: Pending

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-1/ROADMAP.md`

선행 결정:
- D-006: 게시글에 `posts.user_id`를 추가한다.

현재 Decision:
- D-007. `author_name`을 유지할 것인가?

후속 후보:
- `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?
- 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
- 게시글 응답에 `user_id`를 노출할 것인가?
- 회원가입 API 계약은 어떻게 둘 것인가?
- 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가?

이번 선택으로 자동 확정하지 않는 것:
- `author_name`의 생성 위치
- 게시글 응답에 `user_id`를 노출할지 여부
- 수정/삭제 권한 검사 계층

## 2. 한 줄 요약

이번 결정은 게시글에 표시용 작성자 필드인 `author_name`을 계속 둘지 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- `posts.user_id`가 추가된 이후에도 `posts.author_name`을 유지할 것인가?

## 4. 왜 따로 결정해야 하나?

D-006에서 `posts.user_id`는 권한 판단용으로 확정됐다.

하지만 화면에 보여줄 작성자 값은 별도 책임이다. 표시용 이름이나 이메일을 게시글 row에 저장할 수도 있고, 게시글 응답을 만들 때 `users.email`에서 계산할 수도 있다.

이 결정은 데이터 모델과 API 응답 모양에 영향을 준다.

## 5. 선택지

### A. `author_name`을 유지한다.

게시글은 권한 판단용 `user_id`와 표시용 `author_name`을 함께 가진다.

의미:
- `user_id`: 권한 판단용
- `author_name`: UX 표시용

### B. `author_name`을 제거하고 사용자 정보에서 계산한다.

게시글은 `user_id`만 저장한다. 화면 표시용 작성자 값은 응답 생성 시 사용자 테이블에서 가져온다.

의미:
- `user_id`: 권한 판단용
- 표시용 작성자: `users.email` 또는 추후 프로필 정보에서 계산

## 6. 선택지 비교

| 기준 | A. 유지 | B. 제거 |
| --- | --- | --- |
| 현재 코드 변경량 | 낮음 | 중간 |
| 표시값 스냅샷 보존 | 가능 | 어려움 |
| 데이터 중복 | 있음 | 적음 |
| 사용자 이메일 변경 시 과거 글 표시 | 기존 값 유지 | 최신 값 반영 |
| Sprint 1 학습 다양성 | 좋음 | 단순함 |
| 책임 분리 | 권한/표시 분리 가능 | 권한/표시 모두 사용자 참조 |

## 7. Codex 추천

추천: A

이유:
- D-006에서 권한 기준을 `user_id`로 분리했기 때문에 `author_name`은 표시용으로 유지해도 책임이 섞이지 않는다.
- 현재 코드 변경량이 낮아 Sprint 1 범위를 안정적으로 관리할 수 있다.
- 학습 관점에서 "권한 판단용 식별자"와 "화면 표시용 값"을 분리해 볼 수 있다.

주의:
- A를 선택해도 `author_name`을 누가 생성하는지는 아직 확정하지 않는다. 그 부분은 다음 Decision에서 결정한다.

## 8. Pass 기준

사용자 답변이 Pass 되려면 다음을 포함해야 한다.

- A 또는 B 중 하나를 명확히 선택한다.
- `author_name`이 권한 기준이 아니라 표시용인지 이해한다.
- 사용자 이메일이 바뀔 때 과거 게시글 표시값을 어떻게 볼지 설명한다.
- `author_name` 생성 위치는 아직 별도 결정으로 남는다는 점을 인정한다.

## 9. 사용자 답변 템플릿

```md
선택:

이유:

author_name의 책임:

사용자 이메일 변경 시 과거 게시글 표시값에 대한 생각:

아직 다음 분기로 남겨둘 것:
```

## 10. Lowered Decisions

아직 없음.

## 11. Q&A

아직 없음.

## 12. 롤백 계획

예상 변경 파일:

- `backend/app/models/post.py`
- `backend/app/schemas/post.py`
- `backend/app/services/post_service.py`
- `backend/app/api/v1/posts.py`
- `backend/tests/test_posts_flow.py`
- `backend/tests/test_post_service_di.py`

DB 영향:

- A 선택 시 기존 `author_name` 컬럼을 유지한다.
- B 선택 시 `author_name` 컬럼 제거 또는 미사용 처리가 필요하다.

롤백 방법:

- A에서 문제가 생기면 표시용 작성자 값을 사용자 테이블에서 계산하는 방식으로 전환한다.
- B에서 문제가 생기면 `author_name` 컬럼과 응답 필드를 복구한다.

롤백 확인:

```bash
./.venv/bin/python -m pytest backend/tests
```

## 13. 다음 분기

D-007이 Pass되면 `author_name` 생성 위치를 다음 후보로 재분류한다.
