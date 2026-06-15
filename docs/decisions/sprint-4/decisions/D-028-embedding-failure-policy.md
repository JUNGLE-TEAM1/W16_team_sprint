# D-028: embedding 실패 시 게시글 작성/수정 API는 어떻게 응답할 것인가?

Sprint: 4
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. 게시글 작성/수정은 성공시키고 embedding 실패는 별도 상태로 기록한다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-4/decisions/D-028-embedding-failure-policy.md`
- Roadmap: `docs/decisions/sprint-4/ROADMAP.md`
- Troubleshooting: `docs/decisions/sprint-4/troubleshooting/D-028-embedding-failure-policy-qna.md`
- Rollback: Pending

## 1. 현재 분기

D-021에서 게시글 작성/수정 성공 후 embedding을 생성하거나 갱신하기로 확정했다.

D-026에서 로컬 embedding model과 384 dimension을 확정했다.

D-027에서 게시글당 최신 embedding row 하나를 유지하기로 확정했다.

이제 embedding provider가 실패했을 때 기존 게시글 작성/수정 API까지 실패시킬지, 게시글은 저장하고 AI 검색 인덱스만 실패 상태로 둘지 정해야 한다.

이 결정은 사용자 경험, API 응답, transaction 범위, 테스트 기대값에 직접 영향을 준다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 게시글 작성/수정과 embedding 실패의 관계만 확정한다.

다음 항목은 자동 확정하지 않는다.

- 추천 API 경로와 응답 shape
- similarity threshold와 top-N
- LLM 요약 방식
- 재시도 횟수와 background job 구조
- 관리자용 재색인 명령
- frontend 오류 문구 상세

## 3. 선택지

### A. 게시글 작성/수정은 성공시키고 embedding 실패는 별도 상태로 기록한다

게시글 원본 저장을 우선한다. embedding 생성이 실패하면 게시글 API는 성공 응답을 반환하되, `post_embeddings` row를 만들지 않거나 `status=failed`로 기록한다.

장점:
- 게시판 기본 기능이 AI provider 상태에 묶이지 않는다.
- 로컬 model 다운로드 실패나 실행 실패가 있어도 글 작성 자체는 가능하다.
- Sprint 4 이후 재색인으로 회복할 수 있다.

단점:
- 추천 검색에서 embedding이 없는 게시글은 누락될 수 있다.
- 실패 상태와 재처리 전략을 설명해야 한다.
- 테스트에서 게시글 성공과 embedding 실패를 분리해 확인해야 한다.

### B. embedding 실패 시 게시글 작성/수정 전체를 실패시킨다

게시글과 embedding을 하나의 강한 일관성 단위로 본다.

장점:
- 저장된 게시글은 항상 검색 가능한 embedding을 가진다는 설명이 단순하다.
- 데이터 동기화 상태가 명확하다.

단점:
- AI provider 문제 때문에 게시판 기본 작성/수정이 막힌다.
- 로컬 model 초기 다운로드 실패가 사용자 흐름 전체를 깨뜨릴 수 있다.
- Sprint 4의 안정적인 데모에는 부담이 크다.

### C. 게시글은 성공시키되 즉시 embedding 실패 상태를 사용자 응답에 포함한다

게시글 작성/수정은 성공시키지만 응답에 `embedding_status` 같은 AI 상태를 포함한다.

장점:
- 사용자가 글 저장은 성공했고 AI 검색 준비만 실패했다는 점을 알 수 있다.
- frontend에서 AI 상태를 표시할 수 있다.

단점:
- 기존 `PostRead` API 계약을 바꿔야 한다.
- 게시글 기본 응답에 AI 인덱스 상태가 섞인다.
- Sprint 4 이전 API 테스트와 프론트엔드 타입에 영향이 커진다.

## 4. Codex 추천

추천은 A다.

게시판 기본 기능은 AI 기능보다 우선되어야 한다. 특히 로컬 embedding model은 최초 다운로드, 메모리, 실행 환경 문제로 실패할 수 있으므로 글 작성/수정까지 막으면 Sprint 4 데모 안정성이 떨어진다.

다만 실패를 조용히 삼키지는 않고, backend 로그와 `post_embeddings.status` 또는 `last_error` 같은 필드로 기록하는 편이 좋다. 사용자-facing 응답 계약은 기존 게시글 API를 유지하고, 추천 API에서 검색 가능한 embedding이 없을 때 빈 결과 또는 안내 메시지를 반환하게 한다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 선택한 이유가 있어야 한다.
- 게시글 원본 저장과 AI embedding 저장의 우선순위를 구분해야 한다.
- DB/API/테스트 중 무엇이 이 선택의 영향을 받는지 언급해야 한다.
- 이번 결정 이후에도 남는 후속 분기를 구분해야 한다.
- 데이터 일관성과 사용자 경험 사이의 trade-off를 인식해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

게시글 저장과 embedding 저장 우선순위:

DB/API/테스트 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현 파일을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- post service의 transaction 처리
- embedding service 호출 위치
- `post_embeddings` 상태 또는 오류 필드
- embedding 실패 테스트
- 추천 API의 embedding 누락 처리
- README 또는 Sprint note의 실패 처리 설명

되돌릴 때 확인할 범위:
- 게시글 작성/수정 API 응답 계약
- embedding 실패 시 rollback 여부
- `post_embeddings` 실패 상태 저장 로직
- 기존 CRUD 테스트와 RAG 테스트

DB 데이터 손실 가능성:
- 게시글 원본과 embedding row의 일시적 불일치가 생길 수 있다.
- 원본 게시글 데이터 손실은 없어야 한다.

원래 상태 보장:
- embedding provider가 실패해도 기존 게시글 CRUD 테스트의 성공/실패 기준이 명확해야 한다.
- AI provider 없이도 기본 게시판 기능은 계속 동작해야 한다.

재검토 조건:
- 프로젝트 요구사항이 “모든 게시글은 반드시 검색 가능해야 한다”로 바뀌는 경우
- 재색인 없이 embedding 실패를 회복할 방법이 없는 경우
- frontend가 글 저장 성공과 AI 준비 실패를 반드시 같은 응답에서 표시해야 하는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 질문

질문:
- chunk가 무엇인지, 지금 필요한지 물었다.
- 후속 기능을 위해 chunk가 필요하다고 보는지 물었다.

Codex 답변 요지:
- chunk는 긴 문서를 검색하기 좋은 작은 조각으로 나눈 단위다.
- Sprint 4의 유사 게시글 추천에는 필요하지 않다.
- 후속 지식 Q&A나 고급 RAG에서는 필요해질 가능성이 높다.
- 지금은 게시글당 embedding 1개로 가고, 나중에 chunk로 확장할 여지만 남기는 균형이 좋다.

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: 게시판 기능이랑 분리해놔야 유지보수가 편함

게시글 저장과 embedding 저장 우선순위: 우선순위는 없고 그냥 분리해놓고 임베딩 문제 발생시에 로그만따로 저장하고 나중에 재시도 하는게 맞지않나

DB/API/테스트 영향: 

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 A로 명확하다.
- 게시판 기능과 AI embedding 처리를 분리해 유지보수성을 높이겠다는 이유는 타당하다.
- embedding 문제 발생 시 로그를 남기고 나중에 재시도한다는 방향은 A와 일치한다.
- 다만 게시글 저장과 embedding 저장의 우선순위 표현이 애매하다. 실제 구현에서는 게시글 원본 저장을 먼저 성공시키고, embedding 실패는 게시글 저장 실패로 rollback하지 않는다는 기준이 필요하다.
- DB/API/테스트 영향, trade-off, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 질문

질문:
- rollback과 trade-off가 연결될 수 있는지 물었다.
- AI 기능이 주가 되는 사이트라면 embedding 실패를 계속 허용하는 것이 문제가 될 수 있지 않은지 물었다.
- embedding 실패 시 재시도가 있는지 물었다.

Codex 답변 요지:
- trade-off의 핵심은 AI 인덱스 실패를 게시판 전체 장애로 볼지, AI 기능만 degraded 상태로 볼지다.
- Sprint 4에서는 개별 embedding 실패가 게시글 저장을 rollback하지 않게 하되, 실패 상태를 기록해 재시도 가능하게 둔다.
- 반복 실패 시 점검 모드, 기능 제한, degraded 상태 표시는 운영 정책이므로 후속 분기로 남긴다.

### 2026-06-15 사용자 최종 답변

사용자 답변:

```md
게시글 저장을 우선 성공시키고, embedding 생성 실패 때문에 게시글 작성/수정을 rollback하지 않는다. 대신에 분리해서 재생서 시도를 한다.

DB에는 embedding 실패 상태나 last_error를 남길 수 있다. 기존 게시글 작성/수정 API 응답은 유지한다. 테스트는 embedding provider가 실패해도 게시글은 저장되고, 실패 상태가 기록되는지 확인한다.

기본 게시판은 안정적이지만 embedding이 실패한 게시글은 추천 검색에서 잠시 빠질 수 있다. 추천 API 계약, similarity threshold/top-N, LLM 요약 방식, 재시도 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택지는 A로 명확하다.
- 게시글 원본 저장을 우선 성공시키고 embedding 실패로 rollback하지 않는 기준이 명확하다.
- DB/API/테스트 영향이 구분되었다.
- 기본 게시판 안정성과 검색 누락 가능성 사이의 trade-off를 인식했다.
- 추천 API 계약, similarity threshold/top-N, LLM 요약 방식, 재시도 방식이 후속 분기로 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- Sprint 1~3.5와 frontend 관련 기존 변경 및 미추적 파일이 다수 존재한다.
- D-028 처리 중에는 `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-4/decisions/D-028-embedding-failure-policy.md`, `docs/decisions/sprint-4/troubleshooting/D-028-embedding-failure-policy-qna.md`만 Decision 기록 범위로 변경한다.

구현 전 확정된 범위:
- 게시글 작성/수정은 embedding 실패 때문에 rollback하지 않는다.
- embedding 실패는 별도 상태와 `last_error`로 기록할 수 있게 둔다.
- 기존 게시글 작성/수정 API 응답 계약은 유지한다.
- embedding provider 실패 테스트는 게시글 저장 성공과 실패 상태 기록을 함께 확인한다.

아직 구현 전 확정되지 않은 범위:
- 추천 API 계약
- similarity threshold와 top-N
- LLM 요약 방식
- 재시도 방식
- 반복 실패 시 degraded 또는 점검 모드 정책
