# D-008. 회원가입 API 계약을 어떻게 둘 것인가?

Date: 2026-06-14
Sprint: 1
Level: 3
Status: Accepted
Implementation: Completed
Owner: User
Chosen: A. 최소 회원가입 API를 추가한다.

## Evaluation Status

Current Evaluation: Pass

Reason:
- 선택 A가 명확하다.
- 회원가입 성공 응답에는 토큰을 포함하지 않고, 토큰 발급 책임은 로그인 API로 분리한다는 기준이 명확하다.
- 중복 이메일은 `409 Conflict`로 처리하기로 했다.
- A는 `POST /api/v1/auth/register`로 사용자를 생성하므로 Sprint 1 완료 기준의 "회원가입이 가능하다"를 충족한다.

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-1/ROADMAP.md`

선행 결정:
- D-006: 게시글에 `posts.user_id`를 추가한다.
- D-007: `author_name`은 제거한다.

현재 Decision:
- D-008. 회원가입 API 계약을 어떻게 둘 것인가?

후속 후보:
- 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가?

이번 선택으로 자동 확정하지 않는 것:
- 로그인 성공 후 토큰 저장 위치
- 프론트엔드 전체 인증 상태 관리 방식

이번 선택과 별도로 Level 2로 처리 가능한 것:
- 게시글 응답에 `user_id`를 노출하지 않는다.
- 게시글 수정/삭제 권한 검사는 service 계층에서 처리한다.

## 2. 한 줄 요약

이번 결정은 Sprint 1의 "회원가입이 가능하다" 완료 기준을 어떤 API 계약으로 구현할지 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- 회원가입 엔드포인트, 요청 필드, 응답 필드, 중복 이메일 처리 방식

## 4. 왜 먼저 결정해야 하나?

Sprint 1 완료 기준에는 회원가입과 로그인이 모두 포함된다.

현재 로그인은 이미 `email`과 `password` 기반이다. 회원가입 API도 이 흐름과 맞아야 로그인 테스트와 프론트엔드 인증 흐름이 자연스럽게 연결된다.

회원가입 API 계약은 다음에 영향을 준다.

- 사용자 생성 schema
- auth router
- user service
- 중복 이메일 에러 응답
- 프론트엔드 회원가입 폼
- 테스트 시나리오

## 5. 선택지

### A. 최소 회원가입 API를 추가한다.

계약:
- `POST /api/v1/auth/register`
- Request: `email`, `password`
- Response: 생성된 사용자 기본 정보
- 중복 이메일: `409 Conflict`
- 회원가입 성공 후 자동 로그인은 하지 않는다.

의미:
- 회원가입과 로그인 책임을 분리한다.
- 사용자는 회원가입 후 로그인 API로 토큰을 받는다.

### B. 회원가입 성공 시 토큰까지 발급한다.

계약:
- `POST /api/v1/auth/register`
- Request: `email`, `password`
- Response: access token, refresh token, 사용자 기본 정보
- 중복 이메일: `409 Conflict`

의미:
- 회원가입 직후 로그인 상태가 된다.
- register가 사용자 생성과 로그인 책임을 함께 가진다.

### C. 회원가입 API는 만들지 않고 seed/test user로 Sprint 1을 진행한다.

계약:
- 회원가입 엔드포인트 없음
- 기존 사용자 또는 테스트 fixture로 로그인만 검증

의미:
- 구현량은 가장 적다.
- Sprint 1 완료 기준인 "회원가입이 가능하다"를 충족하지 못한다.

## 6. 선택지 비교

| 기준 | A. 최소 register | B. register + token | C. 생략 |
| --- | --- | --- | --- |
| Sprint 1 완료 기준 | 충족 | 충족 | 미충족 |
| 책임 분리 | 좋음 | 중간 |
| 프론트엔드 흐름 | 회원가입 후 로그인 | 회원가입 즉시 로그인 |
| 테스트 명확성 | 높음 | 중간 |
| 구현 복잡도 | 중간 | 높음 | 낮음 |
| 기존 로그인 API와의 일관성 | 좋음 | 중간 | 낮음 |

## 7. Codex 추천

추천: A

이유:
- Sprint 1 완료 기준을 충족한다.
- 로그인과 토큰 발급 책임을 기존 login API에 남길 수 있다.
- API 계약이 단순해서 테스트와 프론트엔드 흐름을 설명하기 쉽다.
- 중복 이메일 같은 실패 케이스를 명확히 다룰 수 있다.

## 8. Pass 기준

사용자 답변이 Pass 되려면 다음을 포함해야 한다.

- A, B, C 중 하나를 명확히 선택한다.
- 회원가입 성공 응답에 토큰을 포함할지 설명한다.
- 중복 이메일을 어떤 상태 코드로 처리할지 설명한다.
- 선택한 방식이 Sprint 1 완료 기준을 충족하는지 설명한다.

## 9. 사용자 답변 템플릿

```md
선택:

이유:

회원가입 성공 응답에 토큰을 포함할 것인가:

중복 이메일 처리:

Sprint 1 완료 기준 충족 여부:
```

## 10. Lowered Decisions

### C5. 게시글 응답에 `user_id`를 노출할 것인가?

임시 판단:
- Level 2로 낮출 수 있다.

추천:
- 노출하지 않는다.

이유:
- D-006에서 `user_id`는 내부 권한 판단용으로 확정됐다.
- D-007에서 게시글 작성자 표시값도 제거했다.
- 따라서 게시글 목록/상세 응답에 `user_id`를 노출할 필수 이유가 낮다.

### C4. 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?

임시 판단:
- Level 2로 낮출 수 있다.

추천:
- service 계층에서 검사한다.

이유:
- router는 인증 사용자 주입과 요청/응답 처리를 맡는다.
- service는 게시글 조회 후 소유자 검사를 할 수 있다.
- 테스트에서 403 권한 실패를 service 단위와 API 흐름 모두에서 확인하기 쉽다.

## 11. Q&A

### Q1. 사용자 1차 답변 평가

사용자 답변:

```md
선택: A

이유: 토큰 발급은 뭘로할지 확인하는 하나의 분기니까 좀있다 분리해서 정하고 일단은 기본 회원가입 기능만 만들자

회원가입 성공 응답에 토큰을 포함할 것인가: 아니

중복 이메일 처리: 중복 이메일의 경우 409 에러 반환

Sprint 1 완료 기준 충족 여부:? 이게 무슨 뜻이지
```

Codex 평가:
- Pass

통과 이유:
- A 선택이 명확하다.
- 회원가입 성공 응답에 토큰을 포함하지 않는다고 명확히 답했다.
- 중복 이메일을 `409 Conflict`로 처리한다고 명확히 답했다.
- "Sprint 1 완료 기준 충족 여부"는 `docs/taejung/development-order.md`의 완료 기준 중 "회원가입이 가능하다"를 만족하는지 묻는 항목이다. A는 register endpoint로 사용자 생성을 제공하므로 이 기준을 충족한다.

Final Accepted Prompt:

```md
선택: A

이유: 토큰 발급은 로그인 API의 책임으로 분리하고, 회원가입은 기본 사용자 생성 기능만 담당하게 한다.

회원가입 성공 응답에 토큰을 포함할 것인가: 아니오. 회원가입 성공 후 별도 로그인 API로 토큰을 발급받는다.

중복 이메일 처리: 중복 이메일은 `409 Conflict`를 반환한다.

Sprint 1 완료 기준 충족 여부: 충족한다. `POST /api/v1/auth/register`로 회원가입이 가능해지기 때문이다.
```

## 12. 롤백 계획

예상 변경 파일:

- `backend/app/schemas/user.py`
- `backend/app/services/user_service.py`
- `backend/app/api/v1/auth.py`
- `backend/tests/test_auth_flow.py`
- 프론트엔드 회원가입 화면 또는 인증 API 호출 파일

DB 영향:

- 새 테이블 생성은 없다.
- 기존 `users` 테이블을 사용한다.

롤백 방법:

- register endpoint와 관련 schema/service/test를 제거한다.
- 로그인 API와 기존 user model은 유지한다.

롤백 확인:

```bash
./.venv/bin/python -m pytest backend/tests
```

## 13. 다음 분기

D-008이 Pass되어 프론트엔드 토큰 저장 확인 범위를 재분류했다.

결론:
- 현재 repository에는 별도 프론트엔드 앱 파일이 없으므로 C7은 Level 2로 낮춘다.
- 이번 Sprint 1 구현에서는 백엔드 token 발급/검증, 보호 API 요청, 401/403 응답을 테스트로 확인한다.

## 14. 구현 결과

Completed: 2026-06-14

구현 내용:
- `POST /api/v1/auth/register`를 추가했다.
- Request는 `email`, `password`를 받는다.
- Response는 생성된 사용자 기본 정보만 반환한다.
- 회원가입 성공 응답에는 토큰을 포함하지 않는다.
- 중복 이메일은 `409 Conflict`로 반환한다.

검증:
- `DATABASE_URL=sqlite+pysqlite:////tmp/sprint1-implementation-test.db python3 -m pytest backend/tests` -> `14 passed`
- `python3 -m pytest backend/tests` -> PostgreSQL `localhost:5433` 연결 거부로 setup 실패
