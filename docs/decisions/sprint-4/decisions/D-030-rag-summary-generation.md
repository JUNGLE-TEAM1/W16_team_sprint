# D-030: RAG 검색 결과 요약을 어떤 방식으로 생성할 것인가?

Sprint: 4
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: B. 로컬 LLM provider를 실제로 붙인다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-4/decisions/D-030-rag-summary-generation.md`
- Roadmap: `docs/decisions/sprint-4/ROADMAP.md`
- Troubleshooting: `docs/decisions/sprint-4/troubleshooting/D-030-rag-summary-generation-qna.md`
- Rollback: Pending

## 1. 현재 분기

D-029에서 유사 게시글 추천 API는 `POST /api/v1/ai/similar-posts`로 확정했다.

Sprint 4 완료 기준에는 유사 게시글 top-N 반환뿐 아니라 “LLM이 검색 결과를 요약한다”가 포함되어 있다.

D-022에서는 로컬 또는 오픈소스 model을 우선하기로 했지만, 실제 RAG 검색 결과 요약을 어떤 방식으로 생성할지는 아직 확정하지 않았다.

이 결정은 provider 의존성, API 응답 필드, 테스트 방식, 로컬 실행 부담에 영향을 준다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 RAG 검색 결과 요약 생성 방식만 확정한다.

다음 항목은 자동 확정하지 않는다.

- similarity threshold와 top-N 기본값
- 반복 실패 시 degraded 또는 점검 모드
- background 재시도 방식
- Sprint 5 MCP tool 구현
- Sprint 6 Agent loop 구조

## 3. 선택지

### A. Sprint 4에서는 deterministic local summarizer를 쓰고, LLM provider는 후속 고도화로 남긴다

검색 결과 title, preview, tags, similarity를 기반으로 서버에서 규칙 기반 요약 문장을 만든다.

예:

```text
비슷한 글 3개를 찾았습니다. 가장 가까운 글은 "JWT 로그인 구현"이며 유사도는 높음입니다.
```

장점:
- 외부 API key와 로컬 LLM 설치 없이 안정적으로 동작한다.
- 테스트가 빠르고 예측 가능하다.
- Sprint 4의 핵심인 embedding 저장과 similarity search에 집중할 수 있다.

단점:
- 엄밀한 의미의 LLM 요약은 아니다.
- Sprint 4 완료 기준의 “LLM 요약”을 축소 해석하게 된다.
- README에 MVP fallback 요약임을 명확히 설명해야 한다.

### B. 로컬 LLM provider를 실제로 붙인다

예를 들어 Ollama 같은 로컬 LLM 실행 환경을 전제로 검색 결과를 요약한다.

장점:
- Sprint 4 완료 기준의 LLM 요약에 가장 직접적으로 부합한다.
- 후속 Agent 구현과 provider 구조를 공유하기 쉽다.

단점:
- 로컬 LLM 설치와 실행 환경 부담이 크다.
- 테스트와 데모 안정성이 낮아질 수 있다.
- provider 실패 처리와 timeout 정책이 추가로 필요하다.

### C. OpenAI 등 외부 LLM provider를 요약에만 fallback으로 허용한다

embedding은 로컬 model을 유지하고, 요약만 외부 LLM API를 사용할 수 있게 한다.

장점:
- 요약 품질과 구현 속도가 좋다.
- 로컬 LLM 실행 부담을 줄일 수 있다.

단점:
- D-022의 로컬/오픈소스 우선 방향과 다소 어긋난다.
- API key와 비용, rate limit 정책이 필요하다.
- 테스트에서는 fake provider가 필요하다.

## 4. Codex 추천

추천은 A다.

Sprint 4에서 가장 중요한 것은 게시글 embedding 저장, pgvector similarity search, 작성 화면 preview 흐름이다. 로컬 LLM까지 붙이면 Sprint 4의 위험이 커진다.

다만 완료 기준과의 차이를 숨기면 안 된다. README와 SUMMARY에는 “Sprint 4 MVP에서는 deterministic local summarizer로 요약 필드를 제공하고, 실제 LLM provider 연동은 Sprint 6 Agent 또는 후속 고도화에서 연결한다”고 명시하는 편이 좋다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 선택한 이유가 있어야 한다.
- 실제 LLM을 붙일지, MVP 요약으로 축소할지 명확해야 한다.
- DB/API/frontend/test 중 무엇이 이 선택의 영향을 받는지 언급해야 한다.
- 완료 기준과 구현 안정성 사이의 trade-off를 인식해야 한다.
- 이번 결정 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

요약 생성 기준:

DB/API/frontend/test 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현 파일을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- RAG summary service
- 추천 API 응답의 summary/message 필드
- frontend 추천 결과 표시
- RAG API 테스트
- README 또는 Sprint note의 RAG 요약 설명

되돌릴 때 확인할 범위:
- summary service 구현
- provider 설정값
- 추천 API response schema
- frontend 표시 코드
- 관련 테스트

DB 데이터 손실 가능성:
- 요약 생성 방식 자체는 DB 데이터를 삭제하지 않는다.

원래 상태 보장:
- 요약 provider가 실패해도 유사 게시글 검색 결과 자체는 반환 가능해야 한다.
- 기존 게시글 CRUD API는 영향을 받지 않아야 한다.

재검토 조건:
- Sprint 4 완료 기준을 반드시 실제 LLM 호출로 충족해야 한다고 확정되는 경우
- 로컬 LLM 실행 환경이 이미 준비되어 있고 데모 안정성이 충분한 경우
- 외부 provider API key 사용이 허용되는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 질문

질문:
- `LLM provider`가 아까 말한 로컬 모델인지 물었다.
- `deterministic local summarizer`가 무엇인지 물었다.

Codex 답변 요지:
- D-026에서 정한 로컬 model은 embedding model이며, 문장을 숫자 vector로 바꾸는 역할이다.
- LLM provider는 검색 결과를 읽고 자연어 요약을 생성하는 실행 주체다.
- deterministic local summarizer는 LLM이 아니라 규칙 기반 요약 코드다.

### 2026-06-15 사용자 최종 답변

사용자 답변:

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
- 선택지가 명확하다.
- 실제 LLM 요약을 붙이는 이유가 Sprint 4 완료 기준과 후속 Agent 재사용 관점에서 충분하다.
- 요약 생성 기준과 테스트 대역이 구분되었다.
- DB/API/frontend/test 영향이 언급되었다.
- 로컬 model 설치, 실행 시간, timeout, 실패 처리 부담이라는 trade-off를 인식했다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- Sprint 1~3.5와 frontend 관련 기존 변경 및 미추적 파일이 다수 존재한다.
- D-030 처리 중에는 `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-4/decisions/D-030-rag-summary-generation.md`, `docs/decisions/sprint-4/troubleshooting/D-030-rag-summary-generation-qna.md`만 Decision 기록 범위로 변경한다.

구현 전 확정된 범위:
- RAG 검색 결과 요약은 로컬 LLM provider로 생성한다.
- 검색 결과 top-N의 `title`, `preview`, `tags`, `similarity`를 context로 전달한다.
- 테스트에서는 실제 LLM을 호출하지 않고 fake summary provider를 사용한다.
- LLM provider 실패 시에도 유사 글 목록은 반환할 수 있게 한다.

아직 구현 전 확정되지 않은 범위:
- 구체 로컬 LLM model 이름
- timeout/fallback 세부값
- similarity threshold와 top-N
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식
