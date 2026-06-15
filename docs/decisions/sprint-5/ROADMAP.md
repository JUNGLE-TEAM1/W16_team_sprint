# Sprint 5 Decision Roadmap

Date: 2026-06-15

## 1. Sprint 목표

Sprint 5의 목표는 외부 서비스를 호출하는 MCP Server를 구현하고 게시판 작성 흐름과 연결하는 것이다.

추천 흐름:
- 글 작성 화면에서 GitHub Issue 정보를 입력한다.
- MCP tool `fetch_github_issue`를 호출한다.
- 외부 Issue 제목, 상태, 요약, 링크를 가져온다.
- 결과를 게시글 작성 참고자료로 표시하거나 삽입한다.

## 2. 완료 기준

- MCP Server가 존재한다.
- JSON-RPC 요청/응답 형태가 구현되어 있다.
- GitHub Issue 조회 tool이 실제로 동작한다.
- API key 또는 권한 관리 방식을 README에 설명한다.
- 외부 호출 실패 시 에러 처리가 있다.
- 프론트엔드에서 결과를 확인할 수 있다.
- 게시판 작성 흐름 안에서 MCP 결과가 사용된다.

## 3. 이전 Sprint에서 이미 구현된 기반

Sprint 4 기반:
- 작성 화면에 AI preview 영역이 생겼다.
- RAG 추천 API가 별도 AI 경로로 분리되었다.
- 로컬 provider/fake provider 테스트 패턴이 생겼다.
- AI 결과는 자동 저장하지 않고 미리보기로 보여주는 정책이 유지된다.

## 4. 후보 분기 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | MCP Server를 backend 내부 모듈로 둘 것인가, 별도 process로 둘 것인가? | Level 3 | Pending | 없음 |
| 2 | C2 | JSON-RPC endpoint 계약을 어떻게 둘 것인가? | Level 3 | Pending | C1 |
| 3 | C3 | GitHub Issue 입력 계약은 owner/repo/issue_number인가, URL인가? | Level 3 | Pending | C2 |
| 4 | C4 | GitHub API 인증은 optional token인가, public only인가? | Level 3 | Pending | C3 |
| 5 | C5 | MCP 결과를 작성 폼에 자동 삽입할지, preview 후 사용자 확인으로 둘지? | Level 3 또는 2 | Pending | C2, C3 |
| 6 | C6 | 외부 호출 timeout과 실패 메시지를 어떻게 둘 것인가? | Level 2 | Pending | C2 |
| 7 | C7 | MCP tool 결과를 Agent에서 재사용할 interface를 둘 것인가? | Level 2 또는 3 | Pending | C1, C2 |

## 5. 예상 첫 Decision

예상 첫 후보:
- C1. MCP Server를 backend 내부 모듈로 둘 것인가, 별도 process로 둘 것인가?

이유:
- process 경계가 정해져야 JSON-RPC endpoint 위치, 테스트 방식, 실행 방법이 정해진다.
- Sprint 6 Agent에서 MCP tool을 재사용할 경계에도 영향을 준다.

## 6. 의존성

- C1이 C2의 endpoint 위치와 실행 방식을 막는다.
- C2가 C3~C7의 request/response 구조를 막는다.
- C3와 C4는 GitHub 호출 구현과 README 안내를 결정한다.
- C5는 D-025의 AI 결과 저장 정책과 연결된다.

## 7. 이번 ROADMAP에서 자동 확정하지 않는 것

- MCP Server process 경계
- JSON-RPC endpoint shape
- GitHub Issue 입력 방식
- GitHub token 사용 여부
- 작성 폼 반영 방식
- Agent 재사용 interface

## 8. 구현 가능 조건

필수 Level 3 결정이 모두 Pass된 뒤 Implementation Batch Snapshot을 기록하고 구현한다.
