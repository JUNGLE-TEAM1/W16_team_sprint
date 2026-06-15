# D-019 Q&A: RAG 데이터 범위

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-019-rag-data-scope.md`

## 진행 기록

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정되었다.

D-019에서는 RAG의 1차 embedding 입력과 similarity search 대상 범위를 정했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: A

이유: post_embeddings 테이블과 pgvector 검색으로 바로 이어가기 쉬움, 그리고 지금 미리 분리 해놓아야 스프린트4에서 구현이 편할것 같음
embedding 입력 범위:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 embedding 입력 범위, DB/API/테스트 영향, 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 Codex가 제시한 예시대로 진행하라고 답했다.

## Final Accepted Prompt

통과된 Decision:
- D-019. RAG 데이터 범위를 어디까지 둘 것인가?

사용자 최종 답변:

```md
선택: A

이유:
`post_embeddings` 테이블과 pgvector 검색으로 바로 이어가기 쉽고, 지금 미리 분리해 놓아야 Sprint 4에서 구현이 편하다.

embedding 입력 범위:
게시글의 `title`, `content`, `tags`만 embedding 입력에 포함한다. 댓글은 Sprint 4 MVP의 1차 embedding 입력에서는 제외한다.

DB/API/테스트 영향:
DB는 후속 Decision에서 `post_embeddings` 테이블을 검토하고, API는 유사 게시글 추천 API가 필요해질 수 있다. 테스트는 `title`/`content`/`tags` 기반으로 유사 게시글이 검색되는지 확인해야 한다.

아직 다음 분기로 남겨둘 것:
embedding 저장 위치, embedding 생성 시점, embedding model, 유사도 threshold, top-3/top-5 개수, 댓글 요약 포함 여부는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- embedding 입력 범위가 게시글 `title`, `content`, `tags`로 구분되었다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- embedding 저장 위치
- embedding 생성 시점
- LLM Provider와 Embedding Model
- MCP 외부 서비스와 tool 계약
- Agent 역할과 tool 경계
- AI 결과 저장 정책

최종 결론:
- RAG의 1차 embedding 입력은 게시글의 `title`, `content`, `tags`로 확정한다.
- 댓글은 Sprint 4 MVP의 1차 embedding 입력에서 제외한다.
