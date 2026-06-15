# Decision Index

이 파일은 전역 Decision 인덱스다.

실제 Decision 작업 문서는 스프린트별 폴더에 둔다.

```text
docs/decisions/
  sprint-1/
    ROADMAP.md
    SUMMARY.md
    decisions/
    troubleshooting/
    rollbacks/
  sprint-2/
    ROADMAP.md
    SUMMARY.md
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
| D-006 | 게시글에 `user_id`를 추가할 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-1/decisions/D-006-post-user-id.md |
| D-007 | `author_name`을 유지할 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-1/decisions/D-007-author-name-retention.md |
| D-008 | 회원가입 API 계약을 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-1/decisions/D-008-registration-api-contract.md |

Rolled Back:

| Related ID | 제목 | 상태 | 상세 기록 |
| --- | --- | --- | --- |
| D-001~D-005 | Sprint 1 인증/게시글 권한 구현 | Rolled Back | docs/decisions/sprint-1/rollbacks/R-001-sprint1-auth-posts-rollback.md |

---

## Sprint 2

Roadmap:
- docs/decisions/sprint-2/ROADMAP.md

Active:

| ID | 제목 | Level | Status | Implementation | 문서 |
| --- | --- | --- | --- | --- | --- |
| D-009 | 댓글 모델은 어떤 필드를 가질 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-2/decisions/D-009-comment-model-fields.md |
| D-010 | 댓글 API 계약은 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-2/decisions/D-010-comment-api-contract.md |
| D-011 | 최소 화면 구현을 이번 repository에서 다룰 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-2/decisions/D-011-frontend-scope.md |
| D-012 | 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-2/decisions/D-012-frontend-stack.md |

Rolled Back: 없음

---

## Sprint 3

Roadmap:
- docs/decisions/sprint-3/ROADMAP.md

Active:

| ID | 제목 | Level | Status | Implementation | 문서 |
| --- | --- | --- | --- | --- | --- |
| D-013 | 태그 모델을 어떤 구조로 저장할 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-3/decisions/D-013-tag-model-structure.md |
| D-014 | 게시글 작성/수정 API에서 태그 입력 계약을 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-3/decisions/D-014-post-tag-api-contract.md |
| D-015 | 태그로 게시글을 조회하는 API 계약을 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-3/decisions/D-015-tag-filter-api-contract.md |
| D-016 | 게시글 목록 페이징 계약을 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-3/decisions/D-016-post-pagination-contract.md |
| D-017 | 게시글 목록 응답 shape를 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-3/decisions/D-017-post-list-response-shape.md |

Rolled Back: 없음

---

## Sprint 3.5

Roadmap:
- docs/decisions/sprint-3.5/ROADMAP.md

Active:

| ID | 제목 | Level | Status | Implementation | 문서 |
| --- | --- | --- | --- | --- | --- |
| D-018 | AI 사용자 흐름을 무엇으로 고정할 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-018-ai-user-flow.md |
| D-019 | RAG 데이터 범위를 어디까지 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-019-rag-data-scope.md |
| D-020 | Embedding 저장 위치를 어떻게 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-020-embedding-storage.md |
| D-021 | Embedding 생성 시점을 어떻게 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-021-embedding-generation-timing.md |
| D-022 | LLM Provider와 Embedding Model 후보를 어떻게 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-022-llm-provider-embedding-model.md |
| D-023 | MCP 외부 서비스와 MVP tool을 어떻게 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-023-mcp-external-service.md |
| D-024 | Agent 역할과 tool 경계를 어떻게 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-024-agent-role-tool-boundary.md |
| D-025 | AI 결과 저장 정책을 어떻게 둘 것인가? | 3 | Accepted | Planned | docs/decisions/sprint-3.5/decisions/D-025-ai-result-save-policy.md |

Rolled Back: 없음

---

## Sprint 4

Roadmap:
- docs/decisions/sprint-4/ROADMAP.md

Active:
| ID | 제목 | Level | Status | Implementation | 문서 |
| --- | --- | --- | --- | --- | --- |
| D-026 | 로컬 embedding model과 vector dimension을 무엇으로 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-4/decisions/D-026-local-embedding-model-dimension.md |
| D-027 | `post_embeddings` schema를 어떻게 정의할 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-4/decisions/D-027-post-embeddings-schema.md |
| D-028 | embedding 실패 시 게시글 작성/수정 API는 어떻게 응답할 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-4/decisions/D-028-embedding-failure-policy.md |
| D-029 | 유사 게시글 추천 API 계약을 어떻게 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-4/decisions/D-029-similar-posts-api-contract.md |
| D-030 | RAG 검색 결과 요약을 어떤 방식으로 생성할 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-4/decisions/D-030-rag-summary-generation.md |
| D-031 | 로컬 LLM provider와 기본 model을 무엇으로 둘 것인가? | 3 | Accepted | Completed | docs/decisions/sprint-4/decisions/D-031-local-llm-provider-model.md |

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
