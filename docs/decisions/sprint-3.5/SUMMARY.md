# Sprint 3.5 Summary

Date: 2026-06-15

## 1. Sprint 목표

Sprint 3.5의 목표는 RAG, MCP, Agent를 별도 데모가 아니라 게시판 작성 경험 하나로 연결하는 AI 기능 시나리오를 확정하는 것이다.

## 2. 완료 기준

- RAG, MCP, Agent 기능이 하나의 사용자 흐름으로 연결된다.
- pgvector embedding 테이블 구조 초안을 정했다.
- 사용할 LLM Provider와 Embedding Model 후보를 정했다.
- MCP가 호출할 외부 서비스를 정했다.
- Agent가 사용할 tool 목록을 정했다.
- Sprint 4 구현 전 필요한 설계 Decision을 문서화했다.

## 3. 완료된 Decision

| ID | 결정 | 결과 | Implementation |
| --- | --- | --- | --- |
| D-018 | AI 사용자 흐름 | 글 작성 시 유사 게시글 추천 + 중복 게시글 방지 | Planned |
| D-019 | RAG 데이터 범위 | 게시글 `title`, `content`, `tags` | Planned |
| D-020 | Embedding 저장 위치 | `post_embeddings` 별도 테이블 | Planned |
| D-021 | Embedding 생성 시점 | 게시글 작성/수정 성공 후 생성 또는 갱신 | Planned |
| D-022 | LLM Provider와 Embedding Model 후보 | 로컬 또는 오픈소스 model 우선 | Planned |
| D-023 | MCP 외부 서비스와 MVP tool | GitHub Issue 조회, `fetch_github_issue` | Planned |
| D-024 | Agent 역할과 tool 경계 | RAG/MCP를 사용하는 글쓰기 도우미 | Planned |
| D-025 | AI 결과 저장 정책 | 미리보기 반환 후 사용자 확인 반영 | Planned |

## 4. 구현 결과

Sprint 3.5는 설계 스코핑 스프린트다.

이번 단계에서는 backend/frontend 구현 파일을 수정하지 않았다. 구현 결과는 Sprint 4에서 RAG 기능부터 코드로 반영한다.

문서 구현 결과:
- Sprint 3.5 Decision Roadmap 갱신
- D-018~D-025 Decision 문서 생성 및 Accepted 처리
- D-018~D-025 Q&A/troubleshooting 문서 생성
- Implementation Batch Snapshot 기록
- Sprint 4 Roadmap 생성

## 5. 테스트 결과

이번 작업은 문서와 의사결정 기록만 변경했다.

실행한 확인:
- `rg`로 Sprint 3.5 Decision 문서와 전역 인덱스 연결 확인
- `git status --short`로 기존 사용자 변경과 이번 문서 변경 범위 확인

실행하지 않은 테스트:
- backend 테스트
- frontend 테스트

이유:
- 코드 구현 변경이 없고, Sprint 4 구현 전에 설계 문서만 갱신했다.

## 6. 낮아진 후보

아직 Level 1 또는 Level 2로 낮춘 구현 후보는 없다.

다만 Sprint 4에서 다음 항목은 상위 Decision 결과에 따라 Level 2 이하로 낮아질 수 있다.
- `content_snapshot` 구성 문자열
- top-3 또는 top-5 기본값
- Agent tool 실패 문구
- 미리보기 반영 버튼 문구

## 7. 다음 Sprint로 넘길 항목

Sprint 4로 넘길 항목:
- `post_embeddings` 테이블과 pgvector 준비
- 로컬 embedding model과 vector dimension 확정
- 게시글 작성/수정 후 embedding upsert 구현
- 유사 게시글 추천 API 구현
- 작성 화면의 유사 글 찾기 UI 구현
- GitHub Issue MCP tool 구현
- Agent 글쓰기 도우미 API 구현
- fake provider/fake tool 기반 테스트

## 8. 발표용 한 문장

Sprint 3.5에서는 글 작성 중 기존 게시글을 찾아 중복을 줄이고, GitHub Issue 참고자료와 Agent 초안 생성을 하나의 작성 흐름으로 연결하는 AI 기능 설계를 확정했다.
