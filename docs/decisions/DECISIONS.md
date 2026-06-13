# Decision Index

이 파일은 전역 Decision 인덱스다.

실제 Decision 작업 문서는 스프린트별 폴더에 둔다.

```text
docs/decisions/
  sprint-1/
    ROADMAP.md
    decisions/
    troubleshooting/
    rollbacks/
  sprint-2/
    ROADMAP.md
    decisions/
    troubleshooting/
    rollbacks/
```

## Numbering Rule

Decision ID는 스프린트 전체에서 재사용하지 않는다.

새 결정은 이 파일과 각 `sprint-*/rollbacks/` 기록을 확인한 뒤 다음 번호를 사용한다. 롤백된 ID도 재사용하지 않는다.

롤백된 주제를 다시 진행하더라도 이전 ID를 재사용하지 않는다. 예를 들어 D-001~D-005가 롤백된 뒤 같은 Sprint 1 인증/게시글 권한 구현을 다시 진행하면 새 Decision은 D-006부터 예약한다.

Decision ID는 스프린트별 Decision 문서를 만들기 전에 이 파일에 `Status: Proposed`로 먼저 예약한다.

---

## Sprint 1

Active:

| ID | 제목 | Level | Status | Implementation | 문서 |
| --- | --- | --- | --- | --- | --- |
| D-006 | 게시글에 `user_id`를 추가할 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-1/decisions/D-006-post-user-id.md |
| D-007 | `author_name`을 유지할 것인가? | 3 | Proposed | Not Started | docs/decisions/sprint-1/decisions/D-007-author-name-retention.md |

Rolled Back:

| Related ID | 제목 | 상태 | 상세 기록 |
| --- | --- | --- | --- |
| D-001~D-005 | Sprint 1 인증/게시글 권한 구현 | Rolled Back | docs/decisions/sprint-1/rollbacks/R-001-sprint1-auth-posts-rollback.md |

---

## Sprint 2

Active: 없음

Rolled Back: 없음

---

## Template

```md
## D-000: 결정 제목

Sprint:
Date:
Level: 1 / 2 / 3
Status: Proposed / Accepted / Rejected / Revisit
Implementation: Not Started / Planned / Completed / Failed / Rolled Back
Chosen:
Owner:

Documents:
- Decision:
- Troubleshooting:
- Rollback:
```
