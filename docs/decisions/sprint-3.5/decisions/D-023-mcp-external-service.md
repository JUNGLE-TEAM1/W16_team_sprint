# D-023: MCP 외부 서비스와 MVP tool을 어떻게 둘 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: A. GitHub Issue 조회를 MVP tool로 둔다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-023-mcp-external-service.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정했다.

D-022까지 RAG 데이터, embedding 저장, 생성 시점, 로컬 model 우선 기준을 확정했다.

이제 글 작성 흐름에서 MCP가 어떤 외부 서비스를 가져올지 정해야 한다.

팀 싱크 입력에서는 GitHub Issue/Repo 또는 외부 URL 참고자료 가져오기를 제안했고, MVP는 `fetch_github_issue` 하나를 추천했다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 MCP 외부 서비스와 MVP tool 경계만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- MCP 서버 구현 방식의 세부 JSON-RPC envelope
- GitHub token 필수 여부
- rate limit 처리 방식
- issue comments 몇 개까지 가져올지
- body/comments 요약 provider
- Agent가 MCP tool을 호출하는 loop 상세

## 3. 선택지

### A. GitHub Issue 조회를 MVP tool로 둔다

MVP tool은 `fetch_github_issue`로 둔다.

입력:
- `owner`
- `repo`
- `issue_number`

출력:
- `title`
- `state`
- `labels`
- `body_summary`
- `url`

장점:
- 개발 지식 공유 게시판 맥락과 잘 맞는다.
- 외부 서비스 1개 이상 연동 요구를 명확히 만족한다.
- JSON-RPC 요청/응답 예시를 설명하기 쉽다.
- API key/권한 관리 전략을 GitHub token 기준으로 설명할 수 있다.

단점:
- GitHub rate limit과 private repository 접근 권한을 고려해야 한다.
- issue comments 요약까지 포함하면 범위가 커질 수 있다.

### B. 외부 URL metadata 조회를 MVP tool로 둔다

사용자가 붙여넣은 공식문서, 블로그, StackOverflow URL의 title, description, canonical URL 같은 metadata를 가져온다.

장점:
- GitHub 외 자료까지 넓게 처리할 수 있다.
- API token 없이도 일부 구현 가능하다.

단점:
- 사이트별 HTML 구조가 달라 실패 처리가 늘어난다.
- 과제 요구사항에서 외부 서비스/API 연동을 설명하기 GitHub보다 약할 수 있다.
- 본문 요약까지 가면 크롤링/저작권/robots 정책을 더 신경 써야 한다.

### C. GitHub Issue와 외부 URL metadata를 모두 MVP에 포함한다

두 tool을 동시에 제공한다.

장점:
- 참고자료 범위가 넓다.
- 발표 데모가 풍부해진다.

단점:
- Sprint 4 이전 설계와 구현 범위가 커진다.
- 실패 처리와 테스트가 늘어난다.
- Agent tool 선택 로직이 복잡해진다.

## 4. Codex 추천

추천은 A다.

팀 싱크에서도 MVP는 `fetch_github_issue` 하나를 추천했고, 개발 지식 공유 게시판에서 GitHub Issue는 가장 자연스러운 외부 참고자료다.

외부 URL metadata는 시간이 남으면 후속 tool로 추가하는 편이 안전하다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- MVP tool 이름과 입력/출력 범위가 설명되어야 한다.
- API key/권한 관리와 테스트 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

MVP tool 입출력:

API key/권한/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- MCP server 또는 tool adapter
- GitHub API client
- 참고자료 카드 API/schema
- Agent tool registry
- 관련 테스트

되돌릴 때 확인할 범위:
- `fetch_github_issue` tool 구현
- GitHub 환경변수 사용 위치
- Agent에서 MCP tool 호출 경로
- 프론트엔드 참고자료 카드 UI

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- 후속 구현에서 외부 참고자료를 DB에 저장하지 않으면 데이터 손실 이슈는 작다.

원래 상태 보장:
- GitHub token이 없어도 기존 게시글 CRUD와 RAG 테스트는 깨지지 않아야 한다.
- MCP 관련 테스트는 fake GitHub client로 실행 가능해야 한다.

재검토 조건:
- 팀 요구가 GitHub가 아니라 공식문서 URL metadata 중심으로 바뀌는 경우
- GitHub API 사용이 환경상 불가능한 경우
- MCP 구현 범위를 더 작은 metadata tool로 줄여야 하는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: 학습 목적에 있어 타당한 선탱이라 생각함. 추가 툴은 추후 확장으로 해도 늦지않음

MVP tool 입출력:

API key/권한/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 학습 목적과 확장 순서를 근거로 하므로 충분하다.
- MVP tool 입출력, API key/권한/테스트 영향, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 예시를 진행하되, 공개 GitHub Issue token 없는 조회는 실제 환경에서 확인해야 하는 부분임을 지적했다.

정리된 최종 답변:

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
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- MCP MVP tool은 `fetch_github_issue`로 둔다.
- 입력은 `owner`, `repo`, `issue_number`로 둔다.
- 출력은 `title`, `state`, `labels`, `body_summary`, `url`로 둔다.
- 테스트는 fake GitHub client를 사용한다.

아직 구현 전 확정되지 않은 범위:
- GitHub token 필수 여부
- comments 조회 범위
- body/comments 요약 방식
- JSON-RPC envelope 상세
- Agent tool 호출 방식
- 외부 URL metadata tool 추가 여부
