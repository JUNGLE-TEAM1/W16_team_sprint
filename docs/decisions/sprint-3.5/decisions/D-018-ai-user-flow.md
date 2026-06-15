# D-018: AI 사용자 흐름을 무엇으로 고정할 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: A. 글 작성 시 유사 게시글 추천 + 중복 게시글 방지
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-018-ai-user-flow.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

Sprint 3.5는 RAG, MCP, Agent를 별도 데모가 아니라 게시판 작성 경험 하나로 연결하는 스프린트다.

가장 먼저 정해야 할 것은 AI 기능의 중심 사용자 흐름이다.

현재 팀 싱크 입력은 다음 흐름을 강하게 제안한다.

- 사용자가 글 작성 화면에서 제목과 본문 초안을 입력한다.
- RAG가 기존 게시글의 `title`, `content`, `tags` 기반 embedding을 검색한다.
- top-3 또는 top-5 유사 글을 보여준다.
- 충분히 비슷하면 중복 가능성을 알려준다.
- 필요하면 기존 글의 핵심 답변 또는 댓글 요약을 보여준다.
- MCP는 GitHub Issue 같은 외부 참고자료를 가져온다.
- Agent는 RAG/MCP 결과를 사용해 글쓰기 초안과 추천 태그를 제안한다.
- 사용자가 확인해야만 게시글 작성 화면에 반영한다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 AI 사용자 흐름만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- RAG 데이터 범위를 게시글만 둘지, 댓글/태그까지 포함할지
- `post_embeddings` 별도 테이블을 실제로 사용할지
- embedding 생성 시점을 게시글 작성 시점, 버튼 실행, 재색인 중 어디로 둘지
- LLM Provider와 Embedding Model을 무엇으로 둘지
- MCP tool을 `fetch_github_issue` 하나로 시작할지, 외부 URL metadata까지 포함할지
- Agent API 계약과 loop 제한 값을 어떻게 둘지
- AI 결과를 일회성 표시로 둘지, 사용자 확인 후 저장할지

## 3. 선택지

### A. 글 작성 시 유사 게시글 추천 + 중복 게시글 방지

사용자가 새 글을 작성하는 흐름 안에서 기존 게시글과의 유사도를 확인한다.

장점:
- 게시판 도메인과 가장 자연스럽게 연결된다.
- Sprint 4 RAG 구현으로 바로 이어진다.
- `pgvector`, embedding 저장, similarity search를 설명하기 쉽다.
- 중복 글 방지라는 명확한 사용자 가치가 있다.

단점:
- embedding 저장 구조와 생성 시점 Decision이 후속으로 필요하다.
- 유사도 기준, 요약 방식, 권한별 검색 범위 같은 후속 분기가 생긴다.

### B. 지식 Q&A

사용자가 게시판 전체에 질문하면 RAG가 관련 게시글을 찾아 답변한다.

장점:
- RAG 데모로 직관적이다.
- 질의응답 결과를 발표하기 쉽다.

단점:
- 게시글 작성 흐름과 분리될 가능성이 크다.
- 출처 표시, 환각 방지, 답변 품질 기준이 더 무겁다.
- Sprint 3.5의 팀 싱크 내용과 덜 맞는다.

### C. 태그 추천 중심

사용자가 글을 작성하면 AI가 태그를 추천한다.

장점:
- 구현 범위가 작다.
- UI 반영이 쉽다.

단점:
- RAG/MCP/Agent를 모두 보여주기에는 기능이 약하다.
- 중복 방지나 외부 참고자료 흐름과의 연결이 약하다.

## 4. Codex 추천

추천은 A다.

팀이 정해온 방향과 Sprint 4 RAG 완료 기준을 함께 보면, 글 작성 시 유사 게시글 추천과 중복 게시글 방지가 가장 자연스럽다.

이 선택은 MCP와 Agent도 억지로 붙이지 않고 같은 사용자 흐름 안에서 연결할 수 있다.

- RAG: 유사 게시글 검색과 요약
- MCP: GitHub Issue 같은 외부 참고자료 카드
- Agent: RAG/MCP 결과를 참고한 글쓰기 초안과 추천 태그

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- RAG, MCP, Agent가 어떻게 하나의 작성 흐름으로 연결되는지 설명해야 한다.
- DB/API/테스트 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

사용자에게 롤백 계획이나 재검토 조건 작성을 요구하지 않는다.
롤백 계획과 재검토 조건은 Codex가 정리한다.

## 6. 답변 템플릿

```md
선택:

이유:

RAG/MCP/Agent 연결 방식:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- RAG 추천 API
- embedding 저장 모델
- MCP tool API
- Agent API
- 글 작성 화면의 AI 보조 UI
- 관련 테스트

되돌릴 때 확인할 범위:
- AI 관련 라우터, 서비스, 모델, 스키마, 테스트
- 프론트엔드 작성 화면의 AI 보조 영역
- 문서의 Sprint 3.5/Sprint 4 설명

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- 후속 embedding 테이블 구현 시 별도 판단 필요

원래 상태 보장:
- 기존 게시글 작성/수정/목록/검색/태그/댓글 테스트가 계속 통과해야 한다.

재검토 조건:
- 팀 요구가 지식 Q&A 중심으로 바뀌는 경우
- MCP 외부 자료 연동이 필수 발표 범위에서 제외되는 경우
- Sprint 4 일정상 embedding 저장과 similarity search 구현이 불가능한 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: 팀 결정에 맞춰야함

RAG/MCP/Agent 연결 방식:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 있으나 팀 결정 외의 기능적 근거와 trade-off가 부족하다.
- RAG/MCP/Agent 연결 방식, DB/API/테스트 영향, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- RAG/MCP/Agent 연결 방식은 예시대로 적용한다.
- DB/API/테스트 영향은 예시대로 적용한다.
- 아직 다음 분기로 남겨둘 항목도 예시대로 적용한다.

정리된 최종 답변:

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
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 둔다.
- RAG/MCP/Agent는 글 작성 화면에서 이어지는 하나의 보조 흐름으로 설계한다.

아직 구현 전 확정되지 않은 범위:
- RAG 데이터 범위
- embedding 저장 위치
- embedding 생성 시점
- LLM Provider와 Embedding Model
- MCP tool 계약
- Agent 역할과 API 계약
- AI 결과 저장 정책
