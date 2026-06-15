# D-020 Q&A: Embedding 저장 위치

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-020-embedding-storage.md`

## 진행 기록

D-019에서 RAG의 1차 embedding 입력은 게시글의 `title`, `content`, `tags`로 확정되었다.

D-020에서는 embedding을 `posts` 테이블에 직접 둘지, `post_embeddings` 별도 테이블로 분리할지 정했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: A
 
이유: 주후 확장이 용이해서 분리해놓는게 훨씬 나음, 이전 분기와 일관성이 이어짐

posts와 embedding 분리 기준:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 `posts`와 embedding 분리 기준, DB/API/테스트 영향, 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 Codex가 제시한 예시대로 적용하라고 답했다.

## Final Accepted Prompt

통과된 Decision:
- D-020. Embedding 저장 위치를 어떻게 둘 것인가?

사용자 최종 답변:

```md
선택: A

이유:
추후 확장이 용이해서 분리해놓는 게 훨씬 낫고, 이전 분기와 일관성이 이어진다.

posts와 embedding 분리 기준:
`posts`는 게시글 원본 데이터와 사용자-facing 필드를 책임지고, `post_embeddings`는 AI 검색 인덱스인 `embedding`, `content_snapshot`, `metadata`, `created_at`을 책임진다.

DB/API/테스트 영향:
DB에는 `post_embeddings` 테이블과 `post_id` 관계가 필요해진다. API는 유사 게시글 추천 API에서 `post_embeddings`를 조회하게 되고, 테스트는 게시글 원본과 embedding row가 연결되어 검색되는지 확인해야 한다.

아직 다음 분기로 남겨둘 것:
embedding 생성 시점, embedding model과 vector dimension, metadata JSON 구조, content_snapshot 구성, 유사도 threshold, top-3/top-5 개수는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- `posts`와 `post_embeddings`의 책임 분리가 명확하다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- embedding 생성 시점
- LLM Provider와 Embedding Model
- MCP 외부 서비스와 tool 계약
- Agent 역할과 tool 경계
- AI 결과 저장 정책

최종 결론:
- embedding은 `post_embeddings` 별도 테이블에 저장한다.
- `posts`는 게시글 원본 데이터와 사용자-facing 필드를 책임지고, `post_embeddings`는 AI 검색 인덱스를 책임진다.
