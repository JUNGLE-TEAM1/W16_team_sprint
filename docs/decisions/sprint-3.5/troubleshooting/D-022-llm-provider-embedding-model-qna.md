# D-022 Q&A: LLM Provider와 Embedding Model 후보

Date: 2026-06-15
Decision: `docs/decisions/sprint-3.5/decisions/D-022-llm-provider-embedding-model.md`

## 진행 기록

D-021에서 게시글 작성 또는 수정 성공 후 embedding을 생성하거나 갱신하기로 확정했다.

D-022에서는 Sprint 4 RAG와 Agent 구현에서 사용할 provider/model 기준을 정했다.

## 보완 질문

초기 답변은 다음과 같았다.

```md
선택: B

이유: 어짜피 내 환경에서만 실행할거라  로컬 모델로 가는게 비용면에서 좋음 복잡한 만큼 관련 내용을 학습하기 좋아보임

embedding과 LLM 생성 provider 기준:

API key/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Pass 기준 중 embedding과 LLM 생성 provider 기준, API key/테스트 영향, 후속 분기가 비어 있어 Codex가 보완 질문을 했다.

사용자는 진행하라고 답했고, Codex가 제시한 예시를 최종 답변으로 적용했다.

## Final Accepted Prompt

통과된 Decision:
- D-022. LLM Provider와 Embedding Model 후보를 어떻게 둘 것인가?

사용자 최종 답변:

```md
선택: B

이유:
개인 로컬 환경에서 실행할 예정이라 로컬 모델을 쓰는 편이 비용면에서 좋다. 구현이 더 복잡하더라도 관련 내용을 학습하기 좋다.

embedding과 LLM 생성 provider 기준:
embedding은 로컬 또는 오픈소스 embedding model을 우선 사용한다. 요약/Agent 초안 생성도 가능하면 로컬 LLM을 우선하되, 구현 난이도나 성능 문제가 있으면 후속 Decision에서 fallback provider를 검토한다.

API key/테스트 영향:
기본 흐름은 외부 API key 없이 동작하는 방향으로 둔다. 테스트는 실제 로컬 모델을 매번 호출하지 않고 fake embedding provider와 fake LLM provider로 대체해 속도와 안정성을 확보한다.

아직 다음 분기로 남겨둘 것:
구체적인 로컬 embedding model, vector dimension, 로컬 LLM 실행 방식, fallback provider 여부, 모델 설치/실행 문서화, provider 실패 처리는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- 로컬 실행, 비용, 학습 목적이라는 이유가 충분하다.
- embedding과 LLM 생성 provider 기준이 구분되었다.
- API key와 테스트 대역 영향이 언급되었다.
- 후속 분기가 구분되었다.

Pass 이유:
- Level 3 Decision의 사용자 선택, 이유, 영향 범위, 후속 분기 구분이 충족되었다.

보완 질문 여부:
- 있음.

아직 남은 후속 분기:
- MCP 외부 서비스와 tool 계약
- Agent 역할과 tool 경계
- AI 결과 저장 정책

최종 결론:
- embedding은 로컬 또는 오픈소스 embedding model을 우선 사용한다.
- 요약/Agent 초안 생성도 가능하면 로컬 LLM을 우선한다.
- 테스트는 fake provider로 안정화한다.
