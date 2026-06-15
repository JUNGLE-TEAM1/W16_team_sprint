# Sprint 3.5 Decision Roadmap

Date: 2026-06-15

## 1. 목적

Sprint 3.5는 RAG, MCP, Agent가 따로 노는 기능이 아니라 하나의 게시판 경험으로 연결되도록 AI 기능 시나리오를 확정한다.

기준 문서:
- `docs/taejung/development-order.md`

팀 싱크 입력:
- RAG는 글 작성 시 유사 게시글 추천과 중복 게시글 방지를 우선한다.
- MCP는 GitHub Issue/Repo 또는 외부 URL 참고자료 가져오기를 우선하되, MVP는 `fetch_github_issue` 하나로 시작한다.
- Agent는 RAG/MCP tool을 사용하는 글쓰기 도우미로 구성한다.
- embedding 저장 구조는 `post_embeddings` 별도 테이블을 우선 후보로 둔다.

## 2. Sprint 3에서 이미 구현된 기반

Backend:
- 회원가입/로그인/JWT 인증
- 게시글 CRUD와 작성자 권한 검사
- 댓글 CRUD와 댓글 권한 검사
- 정규화된 태그 모델
- `tags: string[]` 게시글 입력/응답
- `GET /posts?tag=...&q=...&page=...&size=...` 목록 query
- metadata 포함 게시글 목록 응답

Frontend:
- 로그인/token 저장
- 게시글 목록/작성/수정/삭제
- 게시글 상세/댓글 흐름
- 태그 입력과 태그 표시
- 검색/태그 필터/페이징 UI

## 3. 전체 후보 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 우선 AI 사용자 흐름은 유사 게시글 추천, 중복 게시글 방지, 지식 Q&A 중 무엇인가? | Level 3 | Accepted | Sprint 3 게시판 흐름 |
| 2 | C2 | RAG 데이터는 게시글만 사용할 것인가, 댓글/태그까지 포함할 것인가? | Level 3 | Accepted | C1 |
| 3 | C3 | Embedding 저장 위치는 posts vector 컬럼인가, 별도 post_embeddings 테이블인가? | Level 3 | Accepted | C1, C2 |
| 4 | C4 | Embedding 생성 시점은 게시글 작성 시점인가, 수동 재색인인가? | Level 3 | Accepted | C3 |
| 5 | C5 | 사용할 LLM Provider와 Embedding Model 후보는 무엇인가? | Level 3 | Accepted | C1 |
| 6 | C6 | MCP 외부 서비스는 무엇을 연결할 것인가? | Level 3 | Accepted | C1 |
| 7 | C7 | Agent 역할은 글쓰기 도우미, 태그 추천, 자료 조사 중 무엇인가? | Level 3 | Accepted | C1, C6 |
| 8 | C8 | AI 결과는 일회성 표시인가, 사용자 확인 후 저장인가? | Level 3 | Accepted | C1, C7 |

## 4. 지금 선택할 Decision

현재 승격된 후보:
- 없음. Sprint 3.5의 구현 전 필수 Level 3 결정은 모두 Accepted 상태다.

Decision:
- 마지막 처리 Decision: `docs/decisions/sprint-3.5/decisions/D-025-ai-result-save-policy.md`

이유:
- D-018에서 글 작성 시 유사 게시글 추천과 중복 게시글 방지 흐름을 선택했다.
- D-019에서 RAG 데이터 범위를 게시글 `title`, `content`, `tags`로 확정했다.
- D-020에서 embedding 저장 위치를 `post_embeddings` 별도 테이블로 확정했다.
- D-021에서 게시글 작성/수정 성공 후 embedding을 생성하거나 갱신하기로 확정했다.
- D-022에서 로컬 또는 오픈소스 model을 우선 사용하되 테스트는 fake provider로 대체하기로 확정했다.
- D-023에서 MCP MVP tool은 `fetch_github_issue`로 확정했다.
- D-024에서 Agent는 RAG/MCP를 사용하는 글쓰기 도우미로 확정했다.
- D-025에서 AI 결과는 미리보기로만 반환하고, 사용자가 확인해야 작성 화면에 반영하기로 확정했다.
- Sprint 4 구현 전 필수 의사결정은 완료되었다.

주의:
- 이 문서는 후보 지도다.
- Sprint 3.5의 구현 전 필수 Level 3 결정은 모두 통과했다.
- 팀 싱크에서 제안한 내용은 강한 추천안으로 반영하되, 실제 DB/API/MCP/Agent 계약은 후속 Decision에서 별도로 확정한다.

## 5. 구현 가능 조건

필수 Level 3 결정이 모두 Pass된 뒤에만 구현을 시작한다.

현재 Sprint 3.5에서 구현 전 필수로 볼 후보:
- C1: AI 사용자 흐름
- C2: RAG 데이터 범위
- C3: Embedding 저장 위치
- C4: Embedding 생성 시점
- C5: LLM Provider와 Embedding Model 후보
- C6: MCP 외부 서비스
- C7: Agent 역할과 tool 경계
- C8: AI 결과 저장 정책

## 6. Implementation Batch Snapshot

작성 시점: 2026-06-15

현재 git status 요약:
- 기존 Sprint 1~3 관련 backend/frontend/docs 변경이 다수 존재한다.
- 이번 Sprint 3.5 진행에서 Codex가 변경한 범위는 `docs/decisions/DECISIONS.md`와 `docs/decisions/sprint-3.5/` 문서다.
- `docs/decisions/sprint-4/ROADMAP.md`는 Sprint Completion Rule에 따라 Sprint 4 진입용으로 생성한다.

수정 예정 또는 수정한 파일:
- `docs/decisions/DECISIONS.md`
- `docs/decisions/sprint-3.5/ROADMAP.md`
- `docs/decisions/sprint-3.5/SUMMARY.md`
- `docs/decisions/sprint-3.5/decisions/D-018-ai-user-flow.md`
- `docs/decisions/sprint-3.5/decisions/D-019-rag-data-scope.md`
- `docs/decisions/sprint-3.5/decisions/D-020-embedding-storage.md`
- `docs/decisions/sprint-3.5/decisions/D-021-embedding-generation-timing.md`
- `docs/decisions/sprint-3.5/decisions/D-022-llm-provider-embedding-model.md`
- `docs/decisions/sprint-3.5/decisions/D-023-mcp-external-service.md`
- `docs/decisions/sprint-3.5/decisions/D-024-agent-role-tool-boundary.md`
- `docs/decisions/sprint-3.5/decisions/D-025-ai-result-save-policy.md`
- `docs/decisions/sprint-3.5/troubleshooting/*.md`
- `docs/decisions/sprint-4/ROADMAP.md`

각 파일의 기존 사용자 변경 여부:
- `docs/decisions/sprint-3.5/ROADMAP.md`는 기존 초안이 있었고, Codex가 이어서 갱신했다.
- `docs/decisions/DECISIONS.md`는 기존 변경이 있는 파일이며, Codex는 Sprint 3.5 인덱스만 추가/갱신했다.
- Sprint 3.5 Decision/troubleshooting/SUMMARY 문서는 이번 진행 중 새로 작성했다.
- Sprint 4 ROADMAP은 이번 진행 중 새로 작성한다.

Codex가 변경할 범위:
- Sprint 3.5 설계 Decision 기록
- Sprint 3.5 요약
- Sprint 4 진입 Roadmap

롤백 시 되돌릴 범위:
- Sprint 3.5 관련 Decision/troubleshooting/SUMMARY 문서
- `DECISIONS.md`의 Sprint 3.5 Active rows
- Sprint 4 Roadmap 중 Sprint 3.5 결과에 의존해 작성된 부분

롤백 확인 명령 또는 테스트:
- `git diff -- docs/decisions/DECISIONS.md docs/decisions/sprint-3.5 docs/decisions/sprint-4/ROADMAP.md`
- 기존 코드 테스트는 이번 문서 작업에서는 실행 대상이 아니다.
