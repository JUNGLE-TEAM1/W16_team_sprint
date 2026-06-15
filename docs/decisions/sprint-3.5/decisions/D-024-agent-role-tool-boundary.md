# D-024: Agent 역할과 tool 경계를 어떻게 둘 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: A. RAG/MCP를 사용하는 글쓰기 도우미 Agent로 둔다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-024-agent-role-tool-boundary.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정했다.

D-023에서 MCP MVP tool은 `fetch_github_issue`로 확정했다.

이제 Agent가 어떤 역할을 맡고 어떤 tool을 호출할지 정해야 한다.

팀 싱크 입력에서는 RAG/MCP를 사용하는 글쓰기 도우미 Agent를 제안했다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 Agent의 역할과 tool 경계만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- Agent API endpoint 상세
- max_iterations, max_tool_calls 값
- Agent state schema 상세
- tool 실패 시 사용자 메시지 문구
- AI 결과 저장 정책
- 프론트엔드 미리보기 UI 상세

## 3. 선택지

### A. RAG/MCP를 사용하는 글쓰기 도우미 Agent로 둔다

사용자 요청을 분석하고, RAG search tool과 MCP `fetch_github_issue` tool을 호출한 뒤 초안, 추천 태그, 관련 글, 외부 참고자료를 미리보기로 반환한다.

장점:
- RAG/MCP/Agent가 하나의 작성 경험으로 연결된다.
- tool 선택과 호출, state 저장, loop 제한을 설명하기 좋다.
- 팀 싱크 입력과 가장 잘 맞다.

단점:
- Agent API와 state schema가 필요하다.
- tool 실패와 부분 결과 반환을 설계해야 한다.

### B. 태그 추천 Agent로 둔다

게시글 초안을 보고 추천 태그만 생성한다.

장점:
- 구현이 쉽다.
- UI 반영이 작다.

단점:
- RAG/MCP tool 사용이 약하다.
- Agent 요구사항인 tool 사용 추론 루프를 보여주기 어렵다.

### C. 자료 조사 Agent로 둔다

사용자가 입력한 키워드나 URL을 바탕으로 외부 자료를 모아 요약한다.

장점:
- MCP와 잘 연결된다.
- 외부 자료 기반 요약을 보여주기 쉽다.

단점:
- 게시글 작성과 유사 게시글 추천 흐름에서 분리될 수 있다.
- RAG 중복 방지 기능과의 연결이 약해질 수 있다.

## 4. Codex 추천

추천은 A다.

D-018의 AI 사용자 흐름과 가장 직접적으로 이어지고, RAG search와 MCP `fetch_github_issue`를 모두 tool로 사용한다.

Agent는 게시글을 직접 저장하지 않고, 사용자 확인 전 미리보기 결과만 반환하는 방향이 안전하다. 실제 저장 정책은 D-025에서 별도로 다룬다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- Agent가 사용할 tool 목록과 결과 형태가 설명되어야 한다.
- loop 제한, tool 실패, 테스트 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

Agent tool과 결과:

loop/실패/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- Agent service
- tool registry
- RAG search tool adapter
- MCP tool adapter
- Agent API schema
- 관련 테스트

되돌릴 때 확인할 범위:
- Agent service와 API endpoint
- tool 호출 경로
- 프론트엔드 Agent 미리보기 UI
- fake tool 기반 테스트

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- Agent가 직접 게시글을 저장하지 않는다면 데이터 손실 가능성은 낮다.

원래 상태 보장:
- Agent tool 실패가 기존 게시글 작성/수정 흐름을 깨뜨리지 않아야 한다.
- Agent 테스트는 fake RAG/MCP/LLM provider로 실행 가능해야 한다.

재검토 조건:
- 팀 요구가 Agent 없이 RAG/MCP 단독 기능으로 축소되는 경우
- 로컬 LLM 성능이 초안 생성에 부족한 경우
- Agent loop 구현이 Sprint 4 범위를 과도하게 늘리는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: 지금까지의 방향과 잘 맞음

Agent tool과 결과:

loop/실패/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 D-018~D-023의 흐름과 일관성을 근거로 하므로 충분하다.
- Agent tool과 결과, loop/실패/테스트 영향, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 예시대로 진행한다.

정리된 최종 답변:

```md
선택: A

이유:
지금까지의 방향과 잘 맞다.

Agent tool과 결과:
Agent는 RAG search tool과 MCP `fetch_github_issue` tool을 사용한다. 결과는 `draft_title`, `draft_content`, `recommended_tags`, `related_posts`, `external_sources`를 미리보기로 반환한다.

loop/실패/테스트 영향:
Agent는 `max_iterations`와 `max_tool_calls`를 제한한다. RAG나 MCP tool이 실패해도 가능한 부분 결과를 반환한다. 테스트는 fake RAG tool, fake MCP tool, fake LLM provider로 tool 호출 순서와 실패 처리 결과를 확인한다.

아직 다음 분기로 남겨둘 것:
Agent API endpoint, `max_iterations`/`max_tool_calls` 구체값, Agent state schema, tool 실패 문구, AI 결과 저장 정책, 프론트엔드 미리보기 UI 상세는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- Agent tool과 결과가 설명되었다.
- loop/실패/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- Agent는 RAG/MCP를 사용하는 글쓰기 도우미로 둔다.
- Agent는 RAG search tool과 MCP `fetch_github_issue` tool을 사용한다.
- Agent 결과는 `draft_title`, `draft_content`, `recommended_tags`, `related_posts`, `external_sources` 미리보기로 반환한다.
- Agent는 loop/tool call 제한과 부분 실패 반환을 가진다.

아직 구현 전 확정되지 않은 범위:
- Agent API endpoint
- `max_iterations`/`max_tool_calls` 구체값
- Agent state schema
- tool 실패 문구
- AI 결과 저장 정책
- 프론트엔드 미리보기 UI 상세
