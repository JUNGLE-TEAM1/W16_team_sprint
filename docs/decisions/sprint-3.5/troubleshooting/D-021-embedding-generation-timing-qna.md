# D-021 Q&A: Embedding 생성 시점

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-021-embedding-generation-timing.md`

## 진행 기록

D-020에서 embedding 저장 위치는 `post_embeddings` 별도 테이블로 확정되었다.

D-021에서는 게시글 작성/수정 흐름과 embedding 생성/갱신 시점의 관계를 정했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: A

이유: 미리 생성해놔야 나중에 가져다 쓰기 편해보임 유사 게시글 검색 같은 기능 등에

게시글 작성/수정과 embedding 생성 관계: 작성 또는 수정시에 임베딩 생성

DB/API/테스트 영향: 작성 수정시에 db에 생성/수정이 필요하고, 관련api가 필요함, 테스트는 기본 임베딩 생성 확인

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 Codex가 제시한 예시를 적용하라고 답했다.

## Final Accepted Prompt

통과된 Decision:
- D-021. Embedding 생성 시점을 어떻게 둘 것인가?

사용자 최종 답변:

```md
선택: A

이유:
미리 생성해놔야 유사 게시글 검색 같은 기능에서 나중에 가져다 쓰기 편하다.

게시글 작성/수정과 embedding 생성 관계:
게시글 작성 또는 수정 성공 후 embedding을 생성하거나 갱신한다.

DB/API/테스트 영향:
작성/수정 시 DB에 embedding row 생성/수정이 필요하고, 관련 API 흐름이 필요하다. 테스트는 기본 embedding 생성과 갱신을 확인한다.

아직 다음 분기로 남겨둘 것:
embedding model과 vector dimension, provider 실패 시 처리, 재시도/재색인 방식, 유사도 threshold, top-3/top-5 개수는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- 게시글 작성/수정과 embedding 생성 관계가 설명되었다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- LLM Provider와 Embedding Model
- MCP 외부 서비스와 tool 계약
- Agent 역할과 tool 경계
- AI 결과 저장 정책

최종 결론:
- 게시글 작성 또는 수정 성공 후 embedding을 생성하거나 갱신한다.
