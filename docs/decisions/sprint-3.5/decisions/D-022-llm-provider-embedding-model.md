# D-022: LLM Provider와 Embedding Model 후보를 어떻게 둘 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: B. 로컬 또는 오픈소스 embedding model을 우선한다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-022-llm-provider-embedding-model.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정했다.

D-019에서 RAG의 1차 embedding 입력은 게시글의 `title`, `content`, `tags`로 확정했다.

D-020에서 embedding 저장 위치는 `post_embeddings` 별도 테이블로 확정했다.

D-021에서 게시글 작성/수정 성공 후 embedding을 생성하거나 갱신하기로 확정했다.

이제 어떤 LLM Provider와 Embedding Model 후보를 기준으로 설계할지 정해야 한다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 provider/model 후보와 운영 기준만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- 실제 API key 값
- production 배포 방식
- provider 실패 재시도 횟수
- 유사도 threshold
- top-3/top-5 개수
- LLM 요약 프롬프트 상세
- Agent loop 제한 상세

## 3. 선택지

### A. OpenAI API를 기준 provider로 둔다

Embedding은 OpenAI embedding model 후보를 사용하고, 요약/Agent 초안 생성도 OpenAI chat model 후보를 사용한다.

장점:
- embedding, 요약, Agent 초안 생성을 한 provider 기준으로 설명하기 쉽다.
- API key 관리 전략을 단순하게 둘 수 있다.
- 테스트에서는 provider client를 mock 또는 fake로 대체하기 쉽다.

단점:
- 외부 API key가 필요하다.
- 비용과 rate limit을 고려해야 한다.
- model dimension에 따라 pgvector 컬럼 dimension이 묶인다.

### B. 로컬 또는 오픈소스 embedding model을 우선한다

Embedding은 로컬 모델이나 오픈소스 provider를 쓰고, 요약/Agent는 별도 LLM을 사용한다.

장점:
- embedding 비용과 외부 의존성을 줄일 수 있다.
- API key 없이 일부 기능을 설명할 수 있다.

단점:
- 로컬 실행 환경과 모델 설치가 무거워질 수 있다.
- 팀원 환경 차이가 커질 수 있다.
- LLM 요약/Agent와 provider가 분리되어 설명이 복잡해진다.

### C. Sprint 3.5에서는 provider를 추상화만 하고 실제 후보를 고정하지 않는다

코드에서는 interface만 두고 실제 provider/model은 Sprint 4에서 결정한다.

장점:
- 구현 세부 선택을 늦출 수 있다.
- provider 교체 가능성을 강조할 수 있다.

단점:
- pgvector dimension, 테스트 fixture, API key 관리 설명이 흐려진다.
- Sprint 4 시작 전에 다시 Level 3 Decision이 필요하다.
- 팀 싱크용 설계로는 덜 구체적이다.

## 4. Codex 추천

추천은 A다.

팀 구현 싱크 목적이라면 provider를 하나로 고정해 DB dimension, API key 관리, mock 테스트 전략을 명확히 하는 편이 좋다.

다만 실제 model명과 dimension은 구현 시점의 최신 공식 문서를 확인해 확정해야 한다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- embedding과 요약/Agent 생성에 어떤 provider 기준을 둘지 구분해야 한다.
- API key/권한 관리와 테스트 대역 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

embedding과 LLM 생성 provider 기준:

API key/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- embedding client
- LLM summary/agent client
- 환경변수 이름
- provider mock/fake 테스트
- vector dimension 관련 schema

되돌릴 때 확인할 범위:
- provider client 구현
- 환경변수 사용 위치
- model dimension에 묶인 DB schema
- 테스트 fixture와 fake client

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- 후속 구현에서 vector dimension을 바꾸면 기존 embedding row 재생성이 필요할 수 있다.

원래 상태 보장:
- provider key가 없어도 기존 게시글 CRUD 테스트는 깨지지 않아야 한다.
- AI 관련 테스트는 fake provider로 실행 가능해야 한다.

재검토 조건:
- 팀 환경에서 OpenAI API key를 사용할 수 없는 경우
- 비용 또는 rate limit 제약이 발표/테스트를 막는 경우
- 공식 model dimension 변경 또는 provider 정책 변경이 있는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: B

이유: 어짜피 내 환경에서만 실행할거라  로컬 모델로 가는게 비용면에서 좋음 복잡한 만큼 관련 내용을 학습하기 좋아보임

embedding과 LLM 생성 provider 기준:

API key/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 개인 로컬 실행 환경, 비용 절감, 로컬 모델 학습 목적을 근거로 하므로 충분하다.
- 추천안 A와 다르지만 프로젝트 학습 목표 관점에서는 타당한 선택이다.
- embedding과 LLM 생성 provider 기준, API key/테스트 영향, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 예시대로 진행한다.

정리된 최종 답변:

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
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- embedding은 로컬 또는 오픈소스 embedding model을 우선 사용한다.
- 요약/Agent 초안 생성도 가능하면 로컬 LLM을 우선한다.
- 테스트에서는 fake embedding provider와 fake LLM provider를 사용한다.

아직 구현 전 확정되지 않은 범위:
- 구체적인 로컬 embedding model
- vector dimension
- 로컬 LLM 실행 방식
- fallback provider 여부
- 모델 설치/실행 문서화
- provider 실패 처리
