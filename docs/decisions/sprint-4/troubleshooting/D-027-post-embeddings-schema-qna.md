# D-027 Q&A: `post_embeddings` schema

Date: 2026-06-15
Decision: `docs/decisions/sprint-4/decisions/D-027-post-embeddings-schema.md`
Status: Accepted

## 1. 진행 중 질문

### Q1. `post_embeddings`의 schema가 무엇인가?

Codex 답변:
- schema는 embedding을 저장하는 테이블의 설계도다.
- `posts`는 게시글 원본을 저장하고, `post_embeddings`는 게시글 내용을 embedding한 vector와 관련 metadata를 저장한다.
- 예상 필드는 `id`, `post_id`, `embedding`, `content_snapshot`, `metadata`, `model_name`, `created_at`, `updated_at`이다.

### Q2. 모델 하나를 쓰니까 row도 하나만 있는 게 맞지 않은가?

Codex 답변:
- 맞다. Sprint 4에서는 embedding model 하나만 사용하므로 게시글당 embedding row 하나가 자연스럽다.
- `model_name`은 지금 model이 하나여도 나중에 재색인과 model 변경을 설명하기 위해 저장한다.

### Q3. 최신 embedding row란 매번 embedding을 업데이트한다는 뜻인가?

Codex 답변:
- 맞다. 게시글 하나에 대해 embedding row를 하나만 두고, 게시글 내용이 바뀌면 같은 row의 embedding을 새 값으로 업데이트한다.
- 과거 embedding 이력은 저장하지 않는다.

## 2. Final Accepted Prompt

통과된 Decision:
- D-027. `post_embeddings` schema를 어떻게 정의할 것인가?

사용자 최종 답변:

```md
선택: A

이유:
Sprint 4에서는 embedding model을 하나만 쓰므로 게시글당 최신 embedding row 하나만 두는 게 적당함

row 저장 기준:
게시글 하나당 `post_embeddings` row 하나를 둔다. 게시글 수정 시 기존 row를 갱신하고, 삭제 시 함께 삭제한다. `model_name`은 현재 하나의 model만 쓰더라도 추후 재색인 설명을 위해 저장함.

DB/API/테스트 영향:
DB에는 `post_id` unique 제약을 둔다. API는 최신 embedding 기준으로 유사 게시글을 검색한다. 테스트는 게시글 생성/수정 후 embedding row가 1개로 유지되는지 확인한다.

trade-off:
구조는 단순하지만 model별 비교나 chunk 단위 검색은 바로 지원하지 않는다. 다만 Sprint 4 범위에서는 단순성이 더 중요하다.

아직 다음 분기로 남겨둘 것:
embedding 실패 처리, 추천 API 계약, similarity threshold/top-N, LLM 요약 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택, 이유, row 저장 기준, DB/API/테스트 영향, trade-off, 후속 분기가 모두 충족되었다.

Pass 이유:
- Sprint 4의 게시글 기반 RAG 구현에 필요한 embedding 저장 단위가 확정되었다.

보완 질문 여부:
- 개념 확인 질문은 있었지만, 최종 답변은 Pass 기준을 충족해 추가 보완 질문은 하지 않았다.

아직 남은 후속 분기:
- embedding 실패 처리
- 추천 API 계약
- similarity threshold/top-N
- LLM 요약 방식

최종 결론:
- `post_embeddings`는 게시글당 최신 embedding row 하나를 유지한다.
- 게시글 수정 시 embedding row를 갱신하고, 게시글 삭제 시 함께 삭제한다.
- model별 여러 row와 chunk 단위 row는 Sprint 4 범위에서 제외한다.
