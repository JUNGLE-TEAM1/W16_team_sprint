# Sprint 1 Decision Roadmap

Date: 2026-06-13

## 1. 목적

Sprint 1 인증 구현 중 보이는 설계 후보를 한 곳에서 관리한다.

이 문서는 후보와 순서를 관리한다. 실제 사용자 선택이 필요한 후보만 Decision으로 승격하고, 그때 `D-###` ID와 개별 Decision 문서를 만든다.

## 2. 전체 후보 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 게시글에 `user_id`를 추가할 것인가? | Level 3 | Accepted as D-006 | 없음 |
| 2 | C2 | `author_name`을 유지할 것인가? | Level 3 | Promoted to D-007 | C1 |
| 3 | C3 | `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가? | Level 3 또는 2 | Blocked | C1, C2 |
| 4 | C4 | 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가? | Level 2 | Blocked | C1 |
| 5 | C5 | 게시글 응답에 `user_id`를 노출할 것인가? | Level 2 또는 3 | Blocked | C1 |
| 6 | C6 | 회원가입 API 계약은 어떻게 둘 것인가? | Level 3 또는 2 | Pending | 없음 |
| 7 | C7 | 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가? | Level 2 또는 3 | Pending | C6 |

## 3. 현재 진행 중인 Decision

- D-007: `author_name`을 유지할 것인가?
- 문서: `docs/decisions/sprint-1/decisions/D-007-author-name-retention.md`

## 4. 아직 Decision ID를 받지 않은 후보

- C3: `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?
- C4: 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
- C5: 게시글 응답에 `user_id`를 노출할 것인가?
- C6: 회원가입 API 계약은 어떻게 둘 것인가?
- C7: 프론트엔드 토큰 저장 확인 범위는 어디까지 둘 것인가?

## 5. 구현 가능 조건

필수 Level 3 후보가 모두 Pass되거나 Level 1/2로 낮아진 뒤에만 구현한다.

## 6. 롤백 이력

이 주제는 한 번 D-001~D-005로 진행되었다가 롤백됐다.

롤백 기록:
- `docs/decisions/sprint-1/rollbacks/R-001-sprint1-auth-posts-rollback.md`

롤백된 ID는 재사용하지 않는다. 같은 주제로 다시 진행하는 첫 Decision은 D-006부터 시작한다.
