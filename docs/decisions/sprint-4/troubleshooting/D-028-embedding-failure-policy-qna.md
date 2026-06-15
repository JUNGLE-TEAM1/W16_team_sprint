# D-028 Q&A: embedding 실패 처리

Date: 2026-06-15
Decision: `docs/decisions/sprint-4/decisions/D-028-embedding-failure-policy.md`
Status: Accepted

## 1. 진행 중 질문

### Q1. rollback도 trade-off가 될 수 있는가?

Codex 답변:
- 될 수 있다.
- 핵심은 AI 인덱스 실패를 게시판 전체 장애로 볼지, AI 기능만 degraded 상태로 볼지다.
- AI 기능이 서비스의 핵심이면 반복 실패 시 기능 제한, degraded 상태, 점검 모드 같은 운영 정책이 필요할 수 있다.
- 다만 Sprint 4에서는 개별 요청의 embedding 실패가 게시글 저장을 rollback하지 않는 기준을 먼저 정하고, 반복 실패 운영 정책은 후속 분기로 남기는 것이 적절하다.

### Q2. embedding 실패가 나면 재시도는 있는가?

Codex 답변:
- 재시도는 있는 방향이 맞다.
- 실패를 버리는 것이 아니라 `status`, `last_error`, `retry_count` 같은 상태를 남겨 나중에 재생성할 수 있게 둔다.
- Sprint 4 최소 구현에서는 실패 상태 기록과 수동 재시도 가능성을 우선하고, background job이나 점검 모드는 후속으로 미룰 수 있다.

## 2. 사용자 1차 답변

```md
선택: A

이유: 게시판 기능이랑 분리해놔야 유지보수가 편함

게시글 저장과 embedding 저장 우선순위: 우선순위는 없고 그냥 분리해놓고 임베딩 문제 발생시에 로그만따로 저장하고 나중에 재시도 하는게 맞지않나

DB/API/테스트 영향: 

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택은 명확했지만 DB/API/테스트 영향, trade-off, 후속 분기가 비어 있어 보완 질문이 필요했다.

## 3. Final Accepted Prompt

통과된 Decision:
- D-028. embedding 실패 시 게시글 작성/수정 API는 어떻게 응답할 것인가?

사용자 최종 답변:

```md
게시글 저장을 우선 성공시키고, embedding 생성 실패 때문에 게시글 작성/수정을 rollback하지 않는다. 대신에 분리해서 재생서 시도를 한다.

DB에는 embedding 실패 상태나 last_error를 남길 수 있다. 기존 게시글 작성/수정 API 응답은 유지한다. 테스트는 embedding provider가 실패해도 게시글은 저장되고, 실패 상태가 기록되는지 확인한다.

기본 게시판은 안정적이지만 embedding이 실패한 게시글은 추천 검색에서 잠시 빠질 수 있다. 추천 API 계약, similarity threshold/top-N, LLM 요약 방식, 재시도 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 게시글 원본 저장과 AI embedding 저장의 우선순위가 구분되었다.
- DB/API/테스트 영향과 trade-off가 충족되었다.
- 후속 분기가 명확하다.

Pass 이유:
- embedding provider 실패가 기존 게시판 기능을 깨지 않도록 하는 API/transaction 기준이 확정되었다.

보완 질문 여부:
- 보완 질문과 개념 질문을 거쳐 Pass 처리했다.

아직 남은 후속 분기:
- 추천 API 계약
- similarity threshold/top-N
- LLM 요약 방식
- 재시도 방식
- 반복 실패 시 degraded 또는 점검 모드 정책

최종 결론:
- 게시글 작성/수정은 embedding 실패 때문에 rollback하지 않는다.
- embedding 실패는 상태와 오류 정보로 기록하고, 후속 재생성의 입력으로 남긴다.
- 기존 게시글 작성/수정 API 응답은 유지한다.
