# D-031: 로컬 LLM provider와 기본 model을 무엇으로 둘 것인가?

Sprint: 4
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: B. Ollama + `qwen2.5:3b`
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-4/decisions/D-031-local-llm-provider-model.md`
- Roadmap: `docs/decisions/sprint-4/ROADMAP.md`
- Troubleshooting: `docs/decisions/sprint-4/troubleshooting/D-031-local-llm-provider-model-qna.md`
- Rollback: Pending

## 1. 현재 분기

D-030에서 RAG 검색 결과 요약은 실제 로컬 LLM provider를 붙이기로 확정했다.

이제 어떤 로컬 LLM 실행 방식을 기준으로 하고, 기본 model 이름을 무엇으로 둘지 정해야 한다.

이 결정은 로컬 실행 준비, 환경변수, timeout/fallback, README 안내, 테스트 fake provider 구조에 영향을 준다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 로컬 LLM provider와 기본 model만 확정한다.

다음 항목은 자동 확정하지 않는다.

- similarity threshold와 top-N 기본값
- frontend 색상 기준
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식
- Sprint 6 Agent loop 상세

## 3. 선택지

### A. Ollama + `llama3.2:3b`

로컬 LLM provider는 Ollama로 두고, 기본 model은 `llama3.2:3b`로 둔다.

장점:
- 로컬 실행과 HTTP API 호출 방식이 단순하다.
- 비교적 가벼운 model이라 개인 로컬 환경에서 시도하기 좋다.
- 후속 Agent 구현에서도 같은 provider 구조를 재사용하기 쉽다.

단점:
- 사용자가 Ollama와 model을 별도로 설치해야 한다.
- 한국어 요약 품질은 더 큰 model보다 약할 수 있다.
- 로컬 machine 성능에 따라 응답 시간이 달라진다.

### B. Ollama + `qwen2.5:3b`

로컬 LLM provider는 Ollama로 두고, 기본 model은 `qwen2.5:3b`로 둔다.

장점:
- 비교적 가벼운 로컬 model 후보다.
- 한국어를 포함한 다국어 응답에서 무난한 선택지가 될 수 있다.
- Ollama HTTP API 구조를 그대로 쓸 수 있다.

단점:
- model availability와 실제 설치 이름을 로컬에서 확인해야 한다.
- 팀원 환경에 따라 다운로드와 실행 편차가 있다.
- 후속 문서에 설치 명령과 fallback을 명확히 써야 한다.

### C. Ollama provider는 고정하되 model 이름은 환경변수 기본값으로만 둔다

코드에서는 `OLLAMA_MODEL` 같은 환경변수를 사용하고, 기본값을 문서에 추천 model로 적는다.

장점:
- 사용자의 로컬 환경에 맞춰 model을 쉽게 바꿀 수 있다.
- model 변경 시 코드 수정이 줄어든다.
- 테스트는 fake provider를 사용하므로 model 이름에 덜 묶인다.

단점:
- 발표와 README에서 “기준 model” 설명이 흐려질 수 있다.
- 사용자가 어떤 model을 받아야 하는지 결정해야 한다.
- model별 품질 차이를 통제하기 어렵다.

## 4. Codex 추천

추천은 C에 가깝지만, 기본값은 `llama3.2:3b`로 두는 절충안이다.

실제 코드는 Ollama provider와 `OLLAMA_MODEL` 환경변수를 사용하고, 기본값을 `llama3.2:3b`로 둔다. 이렇게 하면 Sprint 4에서는 설치 안내가 명확하고, 사용자의 로컬 환경에 맞춰 model을 바꿀 수도 있다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 선택한 이유가 있어야 한다.
- provider와 model 이름을 고정할지, 환경변수로 열어둘지 명확해야 한다.
- API/frontend/test/README 중 무엇이 이 선택의 영향을 받는지 언급해야 한다.
- 로컬 실행 안정성과 model 교체 가능성 사이의 trade-off를 인식해야 한다.
- 이번 결정 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

provider/model 기준:

API/frontend/test/README 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현 파일을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- LLM provider client
- 환경변수 설정
- RAG summary service
- README 또는 Sprint note 설치 안내
- fake summary provider 테스트

되돌릴 때 확인할 범위:
- Ollama client 코드
- provider 설정값
- summary service 호출부
- 추천 API 테스트
- 문서의 model 설치 안내

DB 데이터 손실 가능성:
- LLM provider와 model 선택 자체는 DB 데이터를 삭제하지 않는다.

원래 상태 보장:
- Ollama가 실행 중이지 않아도 테스트는 fake provider로 통과해야 한다.
- LLM provider 실패 시에도 유사 게시글 목록은 반환 가능해야 한다.

재검토 조건:
- 로컬 환경에서 선택한 model 다운로드 또는 실행이 어렵다고 확인되는 경우
- 한국어 요약 품질이 데모를 방해할 정도로 낮은 경우
- Ollama 대신 다른 로컬 LLM 실행 방식이 필요해지는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: B

이유: 실제로 추가를 해놔야 결과를 확인가능하다

provider/model 기준: 

API/frontend/test/README 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 B로 명확하다.
- 실제 model을 추가해야 결과를 확인할 수 있다는 이유는 Sprint 4의 실제 LLM 요약 목표와 맞다.
- provider/model 기준, API/frontend/test/README 영향, trade-off, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 보완 내용으로 진행한다.

정리된 최종 답변:

```md
선택: B

이유:
실제로 model을 추가해 둬야 RAG 검색 결과 요약을 확인할 수 있다.

provider/model 기준:
로컬 LLM provider는 Ollama로 고정하고, 기본 model은 `qwen2.5:3b`로 둔다. 코드에서는 `OLLAMA_MODEL` 환경변수로 바꿀 수 있게 하되 README 기본 예시는 `qwen2.5:3b`로 쓴다.

API/frontend/test/README 영향:
API 응답에는 LLM 요약 `summary`를 포함한다. frontend는 유사 글 목록 위나 아래에 요약을 표시한다. 테스트는 실제 Ollama를 호출하지 않고 fake summary provider를 사용한다. README에는 Ollama 설치와 `qwen2.5:3b` pull/run 안내를 적는다.

trade-off:
실제 model 기준이 있어 결과 확인은 쉽지만, 로컬 설치와 실행 시간이 늘고 환경 차이가 생긴다.

아직 다음 분기로 남겨둘 것:
timeout/fallback 세부값, similarity threshold/top-N, 반복 실패 시 degraded 정책, background 재시도 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- 실제 요약 결과 확인이라는 이유가 Sprint 4 목표와 맞다.
- provider와 model 기준이 명확하다.
- API/frontend/test/README 영향이 구분되었다.
- 로컬 설치와 실행 시간, 환경 차이라는 trade-off를 인식했다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- Sprint 1~3.5와 frontend 관련 기존 변경 및 미추적 파일이 다수 존재한다.
- D-031 처리 중에는 `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-4/decisions/D-031-local-llm-provider-model.md`, `docs/decisions/sprint-4/troubleshooting/D-031-local-llm-provider-model-qna.md`만 Decision 기록 범위로 변경한다.

구현 전 확정된 범위:
- 로컬 LLM provider는 Ollama로 둔다.
- 기본 model은 `qwen2.5:3b`로 둔다.
- 코드에서는 `OLLAMA_MODEL` 환경변수로 model을 바꿀 수 있게 한다.
- 테스트는 fake summary provider를 사용한다.
- README 또는 Sprint note에는 Ollama와 `qwen2.5:3b` 준비 방법을 기록한다.

아직 구현 전 확정되지 않은 범위:
- timeout/fallback 세부값
- similarity threshold와 top-N
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식

## 11. Lowered Decisions

- similarity threshold와 top-N 기본값은 추천 API 계약과 응답 필드가 확정되어 Level 2로 낮춘다.
- LLM timeout/fallback 세부값은 provider 실패 시 유사 글 목록을 반환한다는 D-030 기준이 확정되어 Level 2로 낮춘다.
- 반복 실패 시 degraded 또는 점검 모드 정책은 Sprint 4 구현 필수 범위에서 제외하고 후속 스프린트 후보로 넘긴다.
- background 재시도 방식은 Sprint 4 구현 필수 범위에서 제외하고 후속 스프린트 후보로 넘긴다.
