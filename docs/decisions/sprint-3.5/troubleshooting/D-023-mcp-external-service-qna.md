# D-023 Q&A: MCP 외부 서비스와 MVP tool

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-023-mcp-external-service.md`

## 진행 기록

D-022에서 로컬 또는 오픈소스 model 우선 기준과 fake provider 테스트 전략이 확정되었다.

D-023에서는 MCP가 연결할 외부 서비스와 MVP tool을 정했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: A

이유: 학습 목적에 있어 타당한 선탱이라 생각함. 추가 툴은 추후 확장으로 해도 늦지않음

MVP tool 입출력:

API key/권한/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 MVP tool 입출력, API key/권한/테스트 영향, 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 공개 issue token 없는 조회는 실제 환경에서 확인해야 하는 것인지 질문했고, Codex는 구현 시 확인할 항목과 설계 방향을 분리해 정리했다.

## Final Accepted Prompt

통과된 Decision:
- D-023. MCP 외부 서비스와 MVP tool을 어떻게 둘 것인가?

사용자 최종 답변:

```md
선택: A

이유:
학습 목적에 있어 타당한 선택이다. 추가 tool은 추후 확장으로 해도 늦지 않다.

MVP tool 입출력:
MVP tool은 `fetch_github_issue`로 둔다. 입력은 `owner`, `repo`, `issue_number`이고, 출력은 `title`, `state`, `labels`, `body_summary`, `url`로 둔다.

API key/권한/테스트 영향:
MVP는 공개 GitHub Issue 조회를 우선 대상으로 한다. 공개 issue는 token 없이 조회 가능한 방향을 우선 검토하되, 실제 GitHub API 동작, rate limit, 서버 호출 방식은 구현 시 확인한다. rate limit 완화나 private repo 확장을 위해 `GITHUB_TOKEN` 환경변수 기반 인증을 지원할 수 있게 설계한다. 테스트는 실제 GitHub API를 호출하지 않고 fake GitHub client로 대체한다.

아직 다음 분기로 남겨둘 것:
GitHub token 필수 여부, comments 조회 범위, body/comments 요약 방식, JSON-RPC envelope 상세, Agent tool 호출 방식, 외부 URL metadata tool 추가 여부는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- MVP tool 이름과 입출력 범위가 설명되었다.
- API key/권한/테스트 영향이 언급되었다.
- 실제 환경에서 확인해야 하는 부분과 설계 방향이 구분되었다.
- 후속 분기가 구분되었다.

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- Agent 역할과 tool 경계
- AI 결과 저장 정책

최종 결론:
- MCP MVP tool은 `fetch_github_issue`로 둔다.
- 공개 GitHub Issue 조회를 우선 대상으로 하되, token/rate limit 세부 동작은 구현 시 확인한다.
