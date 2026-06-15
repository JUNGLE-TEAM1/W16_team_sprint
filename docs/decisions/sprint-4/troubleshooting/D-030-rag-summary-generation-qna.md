# D-030 Q&A: RAG 검색 결과 요약 생성

Date: 2026-06-15
Decision: `docs/decisions/sprint-4/decisions/D-030-rag-summary-generation.md`
Status: Accepted

## 1. 진행 중 질문

### Q1. `LLM provider`가 아까 말한 로컬 모델인가?

Codex 답변:
- 아니다.
- D-026에서 정한 로컬 model은 embedding model이며, 문장을 숫자 vector로 바꾸는 역할이다.
- LLM provider는 검색 결과를 읽고 자연어 요약을 생성하는 실행 주체다.

### Q2. `deterministic local summarizer`는 무엇인가?

Codex 답변:
- LLM이 아니라 규칙 기반 요약 코드다.
- 항상 같은 입력이면 같은 출력을 만든다.
- 안정성과 테스트 용이성은 높지만, 실제 LLM 요약은 아니다.

## 2. Final Accepted Prompt

통과된 Decision:
- D-030. RAG 검색 결과 요약을 어떤 방식으로 생성할 것인가?

사용자 최종 답변:

```md
선택: B

이유:
Sprint 4 완료 기준에 LLM 요약이 있고, RAG가 단순 검색이 아니라 검색 결과를 context로 넣어 자연어 요약을 만드는 흐름까지 확인하는 것이 중요하다. 후속 Agent 구현에서도 provider 구조를 재사용할 수 있다.

요약 생성 기준:
Ollama 같은 로컬 LLM provider를 기준으로 검색 결과 top-N의 title, preview, tags, similarity 정보를 context로 전달해 요약을 생성한다. 테스트에서는 실제 LLM을 호출하지 않고 fake summary provider를 사용한다.

DB/API/frontend/test 영향:
DB 변경은 없다. API 응답에는 summary/message 필드를 포함한다. frontend는 유사 글 목록과 함께 LLM 요약을 표시한다. 테스트는 fake provider로 요약 결과가 응답에 포함되는지 확인한다.

trade-off:
실제 LLM 요약을 붙이면 완료 기준과 학습 목표에 더 잘 맞지만, 로컬 모델 설치, 실행 시간, timeout, 실패 처리 부담이 늘어난다. provider 실패 시에도 유사 글 목록은 반환할 수 있게 한다.

아직 다음 분기로 남겨둘 것:
구체 로컬 LLM model 이름, timeout/fallback 세부값, similarity threshold/top-N, 반복 실패 시 degraded 정책, background 재시도 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택, 이유, 요약 생성 기준, 영향 범위, trade-off, 후속 분기가 모두 충족되었다.

Pass 이유:
- Sprint 4 완료 기준의 LLM 요약을 실제 provider 연동으로 충족하는 방향이 확정되었다.
- 테스트 안정성을 위해 fake summary provider 기준도 함께 확정되었다.

보완 질문 여부:
- 개념 확인 질문 이후 최종 답변은 Pass 기준을 충족해 추가 보완 질문은 하지 않았다.

아직 남은 후속 분기:
- 구체 로컬 LLM model 이름
- timeout/fallback 세부값
- similarity threshold/top-N
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식

최종 결론:
- RAG 검색 결과 요약은 로컬 LLM provider를 실제로 붙인다.
- provider 실패 시에도 유사 글 목록은 반환 가능하게 둔다.
- 테스트는 fake summary provider를 사용한다.
