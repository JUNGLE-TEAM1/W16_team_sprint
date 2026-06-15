# D-031 Q&A: 로컬 LLM provider와 기본 model

Date: 2026-06-15
Decision: `docs/decisions/sprint-4/decisions/D-031-local-llm-provider-model.md`
Status: Accepted

## 1. 사용자 1차 답변

```md
선택: B

이유: 실제로 추가를 해놔야 결과를 확인가능하다

provider/model 기준: 

API/frontend/test/README 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택은 명확했지만 provider/model 기준, 영향 범위, trade-off, 후속 분기가 비어 있어 보완 질문이 필요했다.

## 2. Final Accepted Prompt

통과된 Decision:
- D-031. 로컬 LLM provider와 기본 model을 무엇으로 둘 것인가?

사용자 최종 답변:
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
- 선택, 이유, provider/model 기준, 영향 범위, trade-off, 후속 분기가 모두 충족되었다.

Pass 이유:
- Sprint 4의 실제 LLM 요약 확인을 위한 로컬 provider와 기본 model이 확정되었다.

보완 질문 여부:
- 보완 질문 3개를 거쳐 Pass 처리했다.

아직 남은 후속 분기:
- timeout/fallback 세부값
- similarity threshold/top-N
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식

최종 결론:
- 로컬 LLM provider는 Ollama로 둔다.
- 기본 model은 `qwen2.5:3b`로 둔다.
- 코드에서는 `OLLAMA_MODEL` 환경변수로 model을 바꿀 수 있게 한다.
- 테스트는 fake summary provider를 사용한다.
