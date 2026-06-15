# D-007. `author_name`을 유지할 것인가?

Date: 2026-06-14
Sprint: 1
Level: 3
Status: Accepted
Implementation: Completed
Owner: User
Chosen: B. `author_name`을 제거한다.

## Evaluation Status

Current Evaluation: Pass

Reason:
- 최종 선택이 B로 명확하다.
- 게시글에는 권한 판단용 `user_id`만 있으면 되고, 이메일/`author_name`을 게시글에 표시할 필요가 낮다는 기준이 명확하다.
- 게시글에서 이메일을 표시하지 않으므로 이메일 변경 시 과거 게시글 표시값 최신화 문제가 사라진다.

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-1/ROADMAP.md`

선행 결정:
- D-006: 게시글에 `posts.user_id`를 추가한다.

현재 Decision:
- D-007. `author_name`을 유지할 것인가?

후속 후보:
- 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
- 게시글 응답에 `user_id`를 노출할 것인가?
- 회원가입 API 계약은 어떻게 둘 것인가?
- 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가?

이번 선택으로 자동 확정하지 않는 것:
- 게시글 응답에 `user_id`를 노출할지 여부
- 수정/삭제 권한 검사 계층

이번 선택으로 낮아진 것:
- `author_name` 생성 위치는 더 이상 결정하지 않는다. `author_name` 자체를 제거하기 때문이다.

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

### B. `author_name`을 제거한다.

게시글은 `user_id`만 저장한다. 게시글 목록/상세 응답에는 작성자 이메일을 굳이 포함하지 않는다.

의미:
- `user_id`: 권한 판단용
- 표시용 작성자: Sprint 1 범위에서는 없음
- 작성자 프로필 표시/이동: 후속 화면 설계에서 별도 결정

## 6. 선택지 비교

| 기준 | A. 유지 | B. 제거 |
| --- | --- | --- |
| 현재 코드 변경량 | 낮음 | 중간 |
| 표시값 스냅샷 보존 | 가능 | 어려움 |
| 데이터 중복 | 있음 | 적음 |
| 사용자 이메일 변경 시 과거 글 표시 | 기존 값 유지 | 게시글에서 이메일을 표시하지 않음 |
| Sprint 1 학습 다양성 | 좋음 | 단순함 |
| 책임 분리 | 권한/표시 분리 가능 | 게시글은 권한 기준만 보유 |

## 7. Codex 추천

추천: 보류

이유:
- 이전 대화 기준으로는 A가 자연스러웠다.
- 하지만 "게시글에 이메일을 굳이 표시할 이유가 없다"는 기준을 적용하면 B가 더 단순하고 Sprint 1 완료 기준에도 충분하다.
- B를 선택하면 C3 `author_name` 생성 위치 후보는 사라지거나 Level 1로 낮아진다.

주의:
- A를 선택하면 `author_name` 생성 위치는 다음 Decision에서 결정한다.
- B를 선택하면 `author_name` 생성 위치 결정은 필요 없어질 수 있다.

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

### C3. `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?

결론:
- 제거됨

이유:
- D-007에서 `author_name`을 제거하기로 했으므로 생성 위치를 결정할 대상이 사라졌다.
- 게시글 작성 요청은 `author_name`을 받지 않는다.
- 게시글 응답도 Sprint 1 범위에서는 작성자 이메일/표시명을 포함하지 않는다.

## 11. Q&A

### Q1. 사용자 1차 답변 평가

사용자 답변:

```md
선택: A

이유: user_id는 권한 판단용이고 author_name은 UX표시용으로 분리하면 깔끔할듯?

author_name의 책임: 책임까지는 없고 그냥 객체의 속성인데 ux표시용으로 사용하고 다른 용도는 없음

사용자 이메일 변경 시 과거 게시글 표시값에 대한 생각: 사용자가 이메일을 변경할시에는 자동으로 변경되게 테이블들을 foreign 연결해두면 문제 없을것 같다.

아직 다음 분기로 남겨둘 것: 이거 제외한 남은것들
```

Codex 평가:
- Hold

좋은 점:
- A 선택이 명확하다.
- `user_id`는 권한 판단용, `author_name`은 UX 표시용이라는 분리가 명확하다.
- `author_name`을 권한이나 인증 책임으로 쓰지 않겠다는 방향이 맞다.

보완이 필요한 점:
- `author_name` 컬럼을 유지하는 A는 표시값을 게시글 row에 저장하는 선택이다.
- 사용자 이메일 변경 시 과거 게시글의 `author_name`도 자동 변경되게 하려면, 게시글 row의 `author_name`을 믿기보다 사용자 테이블에서 표시값을 계산하는 B에 가까워진다.
- 따라서 "A를 선택하되 과거 글은 기존 표시값 유지"인지, "최신 이메일 자동 반영이 중요하므로 B로 바꿀지"를 확인해야 한다.

### Q2. 게시글에 이메일을 표시하지 않는 선택 검토

사용자 질문:

```md
과거 글은 기존 표시값을 유지한다? 문제가 없으려나? 데이터 최신화가 안된거잖아 아니면 그냥 애초에 이메일을 표시안하는건 어떤가? 그냥 다른유저 프로필 들어가면 알수있는건데 굳이 게시글에 넣을 이유가 없어보이는데
```

Codex 답변:
- 과거 표시값 유지가 항상 문제는 아니다. 작성 시점의 닉네임/표시명을 보존하는 정책이라면 스냅샷이 맞다.
- 하지만 이메일은 보통 최신 계정 정보에 가깝고, 게시글에 계속 노출할 필요도 낮다.
- Foreign key는 `posts.user_id -> users.id` 연결을 보장하지만, `posts.author_name` 같은 문자열 컬럼을 자동 최신화하지 않는다.
- Sprint 1 완료 기준은 게시글 작성자 이메일 표시가 아니라 인증, current_user 확인, 401/403 구분이다.
- 따라서 게시글에 이메일을 표시하지 않는다면 B가 더 단순하다. `posts.user_id`는 내부 권한 판단용으로 유지하고, 게시글 응답에서 작성자 이메일은 빼면 된다.

현재 필요한 확인:
- D-007 선택을 A에서 B로 바꿀 것인가?

### Q3. 사용자 최종 반영 요청

사용자 답변:

```md
반영해
```

Codex 해석:
- 직전 제안인 B를 최종 선택으로 반영한다.

Final Accepted Prompt:

```md
선택: B

이유: 게시글에는 권한 판단용 user_id만 있으면 되고, 이메일/author_name을 게시글에 표시할 필요가 없다.

author_name의 책임: 제거한다. Sprint 1에서는 게시글 작성자 표시 책임을 두지 않는다.

사용자 이메일 변경 시 과거 게시글 표시값에 대한 생각: 게시글에서 이메일을 표시하지 않으므로 최신화 문제가 생기지 않는다.

아직 다음 분기로 남겨둘 것: 게시글 응답에 user_id를 노출할지, 수정/삭제 권한 계층, 회원가입 API 계약 등 남은 후보
```

## 12. 롤백 계획

예상 변경 파일:

- `backend/app/models/post.py`
- `backend/app/schemas/post.py`
- `backend/app/services/post_service.py`
- `backend/app/api/v1/posts.py`
- `backend/tests/test_posts_flow.py`
- `backend/tests/test_post_service_di.py`

DB 영향:

- `author_name` 컬럼 제거 또는 미사용 처리가 필요하다.
- `posts.user_id` 컬럼은 D-006에 따라 추가한다.

롤백 방법:

- A에서 문제가 생기면 표시용 작성자 값을 사용자 테이블에서 계산하는 방식으로 전환한다.
- B에서 문제가 생기면 `author_name` 컬럼과 응답 필드를 복구한다.

롤백 확인:

```bash
./.venv/bin/python -m pytest backend/tests
```

## 13. 다음 분기

D-007이 Pass되었으므로 `author_name` 생성 위치 후보는 제거한다.

다음 후보:
- 게시글 응답에 `user_id`를 노출할 것인가?
- 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
- 회원가입 API 계약은 어떻게 둘 것인가?

## 14. 구현 결과

Completed: 2026-06-14

구현 내용:
- `Post.author_name` 모델 필드를 제거했다.
- 게시글 생성 요청에서 `author_name`을 제거했다.
- 게시글 응답에서 `author_name`을 제거했다.
- 게시글 응답에 `user_id`도 노출하지 않는다.

검증:
- `DATABASE_URL=sqlite+pysqlite:////tmp/sprint1-implementation-test.db python3 -m pytest backend/tests` -> `14 passed`
- `python3 -m pytest backend/tests` -> PostgreSQL `localhost:5433` 연결 거부로 setup 실패
