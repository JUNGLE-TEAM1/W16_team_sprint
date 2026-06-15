# D-024 Q&A: Agent 역할과 tool 경계

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-024-agent-role-tool-boundary.md`

## 진행 기록

D-023에서 MCP MVP tool은 `fetch_github_issue`로 확정되었다.

D-024에서는 Agent가 RAG/MCP를 사용하는 글쓰기 도우미 역할을 맡을지 정했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: A

이유: 지금까지의 방향과 잘 맞음

Agent tool과 결과:

loop/실패/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 Agent tool과 결과, loop/실패/테스트 영향, 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 진행하라고 답했고, Codex가 제시한 예시를 최종 답변으로 적용했다.

## Final Accepted Prompt

통과된 Decision:
- D-024. Agent 역할과 tool 경계를 어떻게 둘 것인가?

사용자 최종 답변:

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

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- AI 결과 저장 정책

최종 결론:
- Agent는 RAG/MCP를 사용하는 글쓰기 도우미로 둔다.
- Agent는 RAG search tool과 MCP `fetch_github_issue` tool을 사용한다.
- 결과는 초안/태그/관련 글/외부 참고자료 미리보기로 반환한다.
