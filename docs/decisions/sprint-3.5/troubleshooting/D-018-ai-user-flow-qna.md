# D-018 Q&A: AI 사용자 흐름

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-018-ai-user-flow.md`

## 진행 기록

사용자는 Sprint 3.5가 팀 차원에서 정해진 내용이며, RAG는 유사 게시글 추천과 중복 게시글 방지, MCP는 GitHub/외부 URL 참고자료 가져오기, Agent는 RAG/MCP를 사용하는 글쓰기 도우미로 구성하는 방향을 공유했다.

Codex는 이를 Sprint 3.5 첫 Level 3 분기인 AI 사용자 흐름 Decision으로 승격했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: A

이유: 팀 결정에 맞춰야함

RAG/MCP/Agent 연결 방식:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 연결 방식, 영향 범위, 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 Codex가 제시한 예시 3개가 모두 맞으니 적용해 달라고 답했다.

## Final Accepted Prompt

통과된 Decision:
- D-018. AI 사용자 흐름을 무엇으로 고정할 것인가?

사용자 최종 답변:

```md
선택: A

이유:
팀 결정에 맞춰야 하며, 글 작성 시 유사 게시글 추천과 중복 게시글 방지는 게시판 사용 경험과 가장 자연스럽게 연결된다. 중복 글을 줄이고 기존 지식을 재사용할 수 있어 Sprint 4 RAG 구현 목표와도 맞다.

RAG/MCP/Agent 연결 방식:
RAG로 유사 글을 찾고, MCP로 GitHub Issue 참고자료를 가져오며, Agent가 RAG/MCP 결과를 반영해 초안과 추천 태그를 제안한다.

DB/API/테스트 영향:
embedding 테이블, 유사 글 추천 API, MCP tool API, Agent 응답 테스트가 후속으로 바뀔 수 있다.

아직 다음 분기로 남겨둘 것:
RAG 데이터 범위, embedding 저장 위치, 생성 시점, MCP tool 계약, Agent 저장 정책은 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- 팀 싱크와 Sprint 4 구현 목표에 맞춘 이유가 보완되었다.
- RAG/MCP/Agent 연결 방식이 하나의 작성 흐름으로 설명되었다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- RAG 데이터 범위
- embedding 저장 위치
- embedding 생성 시점
- LLM Provider와 Embedding Model
- MCP 외부 서비스와 tool 계약
- Agent 역할과 tool 경계
- AI 결과 저장 정책

최종 결론:
- AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정한다.
