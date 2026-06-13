# D-006. 게시글에 `user_id`를 추가할 것인가?

Date: 2026-06-13
Sprint: 1
Level: 3
Status: Accepted
Implementation: Planned
Owner: User
Chosen: A. `posts.user_id`를 추가한다.

## Evaluation Status

Current Evaluation: Pass

Reason:
- 선택 A와 권한 기준은 명확하다.
- DB 변경 비용도 Sprint 1 이후 유지할 구조로 이해하고 있다.
- 후속 후보를 미루는 것이 아니라 바로 이어서 순차 처리한다는 점을 확인했다.
- `posts.user_id`는 권한 판단용이고, `author_name`은 표시용 책임으로 별도 결정할 수 있음을 확인했다.

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-1/ROADMAP.md`

현재 Decision:
- D-006. 게시글에 `user_id`를 추가할 것인가?

후속 후보:
- `author_name`을 유지할 것인가?
- `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?
- 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
- 게시글 응답에 `user_id`를 노출할 것인가?
- 회원가입 API 계약은 어떻게 둘 것인가?
- 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가?

이번 선택으로 자동 확정하지 않는 것:
- 위 후속 후보 전체

구현 가능 조건:
- 필수 Level 3 후보가 모두 Pass되거나 Level 1/2로 낮아진 뒤에만 구현한다.

## 2. 한 줄 요약

이번 결정은 게시글 row가 로그인 사용자의 `users.id`를 참조해야 하는지 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- 게시글에 `posts.user_id`를 추가할 것인가?

## 4. 왜 먼저 결정해야 하나?

Sprint 1 완료 기준에는 다음 항목이 있다.

- 게시글 작성 API 요청 시 token이 함께 전달된다.
- 백엔드에서 현재 사용자를 확인할 수 있다.
- 로그인하지 않은 사용자는 401 응답을 받는다.
- 다른 사용자의 글을 수정/삭제하려 하면 403 응답을 받는다.

403을 구현하려면 "현재 사용자"와 "게시글 소유자"를 비교해야 한다.

현재 게시글은 `author_name` 문자열만 저장한다. 문자열 작성자만 있으면 사용자가 이름을 임의로 보내거나 이름이 중복되는 경우 권한 검사가 흔들린다.

`posts.user_id`가 있으면 다음처럼 비교할 수 있다.

```python
if post.user_id != current_user.id:
    raise Forbidden
```

## 5. 선택지

### A. `posts.user_id`를 추가한다.

게시글이 `users.id`를 참조하게 만든다. 권한 검사는 `post.user_id == current_user.id`로 처리한다.

### B. `posts.user_id`를 추가하지 않고 기존 작성자 문자열만 사용한다.

게시글 스키마를 바꾸지 않고 `author_name` 같은 문자열로 작성자를 표현한다.

## 6. 선택지 비교

| 기준 | A. user_id 추가 | B. 문자열만 사용 |
| --- | --- | --- |
| 권한 검사 안정성 | 높음 | 낮음 |
| DB 변경 | 있음 | 없음 |
| API 영향 | 중간 | 낮음 |
| Sprint 1 완료 기준 적합도 | 높음 | 낮음 |
| 후속 Sprint 확장성 | 좋음 | 나쁨 |
| 되돌리기 비용 | 중간 | 낮음 |

## 7. Codex 추천

추천: A

이유:
- JWT access token의 `sub`와 게시글의 `user_id`를 비교할 수 있다.
- 401과 403을 명확히 분리할 수 있다.
- 작성자 표시값과 권한 기준을 분리할 수 있다.
- Sprint 1의 인증/인가 학습 목표에 맞다.

## 8. Pass 기준

사용자 답변이 Pass 되려면 다음을 포함해야 한다.

- A 또는 B 중 하나를 명확히 선택한다.
- 수정/삭제 권한 검사를 어떤 값으로 할지 설명한다.
- DB 스키마 변경 비용을 이해한다.
- 이번 결정으로 `author_name` 유지/생성 방식, 응답 노출, 권한 검사 계층은 아직 확정되지 않는다는 점을 인정한다.

## 9. 사용자 답변 템플릿

```md
선택:

이유:

권한 검사는 어떤 값으로 할 것인가:

DB 변경 비용에 대한 생각:

아직 다음 분기로 남겨둘 것:
```

## 10. Lowered Decisions

아직 없음.

## 11. Q&A

### Q1. 사용자 1차 답변 평가

사용자 답변:

```md
선택: A

이유: 애초에 추가를 안하면 게시글 api에 대한 권한 확인을 못함, author_name은 이메일이라던데 애초에 토큰에 이메일이 안들어있어서 책임 분리도 명확하지 않음

권한 검사는 어떤 값으로 할 것인가: posts.user_id로 해야지

DB 변경 비용에 대한 생각: 어짜피 앞으로 만들어나가야 하는 틀 미리 만드는거 아닌가?

아직 다음 분기로 남겨둘 것: 다음 분기로 뭘 남겨놔 그냥 지금 해결하고 가야지
```

Codex 평가:
- Hold

좋은 점:
- A 선택이 명확하다.
- 권한 검사를 `posts.user_id` 기준으로 해야 한다는 점을 이해했다.
- `author_name`/이메일/token payload 사이의 책임 혼란을 문제로 봤다.

보완이 필요한 점:
- D-006은 `posts.user_id` 추가 여부만 결정한다.
- `author_name` 유지 여부, 생성 위치, 응답 노출, 권한 검사 계층, 회원가입 API 계약은 이 결정으로 자동 확정하지 않는다.
- 다음 분기로 넘긴다는 것은 미루자는 뜻이 아니라, 한 번에 뭉뚱그리지 않고 바로 이어서 순서대로 확정한다는 뜻이다.

### Q2. 사용자 보완 답변 평가

Codex 질문:

```md
1. D-006에서는 `posts.user_id` 추가만 확정하고, `author_name` 유지/생성 방식은 다음 후보에서 바로 이어서 결정해도 괜찮나요?
2. `posts.user_id`는 권한 판단용이고, `author_name`은 표시용인지 여부는 별도 결정으로 다루는 것에 동의하나요?
```

사용자 답변:

```md
1. 좋아
2. 음 그 부분은 나중에 만들어 가야 하는 상황이고 지금 고민하는 책임이랑은 다른 부분이니 오케이
```

Codex 평가:
- Pass

통과 이유:
- D-006의 책임 범위가 `posts.user_id` 추가 여부임을 수락했다.
- `posts.user_id`를 권한 판단용으로 보고, 표시용 작성자 책임은 별도 분기로 다룰 수 있음을 인정했다.

Final Accepted Prompt:

```md
선택: A

이유: 게시글 API의 권한 확인에는 사용자를 안정적으로 식별할 값이 필요하다. 문자열 작성자 값이나 표시용 이메일은 권한 기준으로 쓰기 어렵다.

권한 검사는 어떤 값으로 할 것인가: `posts.user_id`와 현재 인증 사용자 `current_user.id`를 비교한다.

DB 변경 비용에 대한 생각: Sprint 1 이후에도 유지할 기본 구조이므로 `posts.user_id` 컬럼 추가 비용을 감수한다.

아직 다음 분기로 남겨둘 것: `author_name` 유지 여부, 생성 위치, 응답 노출, 권한 검사 계층은 D-006에서 자동 확정하지 않고 바로 이어지는 별도 분기에서 순차 결정한다.
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

- A 선택 시 `posts.user_id` 컬럼이 추가된다.
- 현재 마이그레이션 도구가 없으므로 로컬 개발 DB 재생성이 필요할 수 있다.

롤백 방법:

- `posts.user_id` 컬럼과 저장 로직을 제거한다.
- 관련 테스트를 기존 `author_name` 문자열 작성 방식으로 되돌린다.

롤백 확인:

```bash
./.venv/bin/python -m pytest backend/tests
```

## 13. 다음 분기

D-006이 Pass되었으므로 ROADMAP의 후속 후보를 재분류한다. 다음 실제 사용자 선택 후보는 D-007 `author_name` 유지 여부다.

관련 Q&A 기록:
- `docs/decisions/sprint-1/troubleshooting/D-006-post-user-id-qna.md`
