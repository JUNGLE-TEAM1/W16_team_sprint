# D-026 Q&A: 로컬 embedding model과 vector dimension

Date: 2026-06-15
Decision: `docs/decisions/sprint-4/decisions/D-026-local-embedding-model-dimension.md`
Status: Accepted

## 1. 진행 중 질문

### Q1. 384 dimension이 무엇을 의미하는가?

Codex 답변:
- embedding vector의 길이를 뜻한다.
- 게시글 제목/본문을 embedding하면 숫자 배열이 나오며, 숫자가 384개면 384 dimension이다.
- pgvector 컬럼을 `vector(384)`로 정의하면 384개짜리 vector만 저장할 수 있다.
- model을 768 dimension 등으로 바꾸면 schema 변경이나 embedding 재생성이 필요할 수 있다.

### Q2. 왜 384개인가?

Codex 답변:
- 사용자가 임의로 정하는 값이 아니라, 후보 embedding model의 출력 크기다.
- MiniLM 계열 model은 가볍고 빠른 문장 의미 비교를 목표로 하며, 후보 model은 384 dimension embedding을 출력한다.
- 큰 model은 768, 1024, 1536 dimension을 쓰기도 하지만, 저장 공간과 계산량이 늘어난다.
- Sprint 4에서는 RAG 작동 흐름을 배우는 것이 핵심이므로 384 dimension이 적절한 균형점이다.

### Q3. 로컬 model을 다운로드해서 학습까지 시켜야 하는가?

Codex 답변:
- 직접 학습할 필요는 없다.
- 이미 학습된 model을 다운로드해서 inference 용도로 사용한다.
- 게시글마다 embedding을 생성해 PostgreSQL에 저장하고, 새 글과 기존 글 vector를 비교한다.
- 검색 품질 개선용 fine-tuning은 Sprint 4 제외 범위에 가깝다.

## 2. 사용자 1차 답변

```md
선택: B

이유: 로컬 환경은 문제 없으니 한국어에 더 적합한 모델을 선택

DB/API/테스트 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 B로 명확하다.
- 이유는 타당하다.
- DB/API/테스트 영향, trade-off, 후속 분기가 비어 있어 보완 질문이 필요했다.

## 3. 보완 질문

Codex는 다음을 확인했다.

1. DB는 `vector(384)` 기준으로 저장하고, 테스트는 fake embedding provider를 써도 되는가?
2. 한국어 대응은 더 좋지만 최초 model 다운로드와 로컬 실행 부담은 조금 늘어나는 trade-off를 받아들이는가?
3. `post_embeddings` schema, embedding 실패 처리, 추천 API 계약, similarity threshold/top-N, LLM 요약 방식은 다음 분기로 남기는가?

## 4. Final Accepted Prompt

통과된 Decision:
- D-026. 로컬 embedding model과 vector dimension을 무엇으로 둘 것인가?

사용자 최종 답변:
- 보완 내용으로 진행한다.

정리된 최종 답변:

```md
선택: B

이유:
로컬 환경은 문제 없으니 한국어에 더 적합한 모델을 선택한다.

DB/API/테스트 영향:
DB는 `vector(384)` 기준으로 embedding을 저장한다. API는 이 model 선택 자체를 직접 노출하지 않고, 추천 API 구현에서 query embedding과 저장 embedding의 dimension이 일치한다는 전제를 사용한다. 테스트는 실제 model을 매번 호출하지 않고 fake embedding provider로 대체한다.

trade-off:
한국어 대응은 A보다 더 좋지만, 최초 model 다운로드와 로컬 실행 부담은 A보다 조금 늘어날 수 있다. Sprint 4에서는 검색 품질보다 게시판 데이터와 연결된 RAG 흐름 완성을 우선한다.

아직 다음 분기로 남겨둘 것:
`post_embeddings` schema, embedding 실패 처리, 추천 API 계약, similarity threshold/top-N, LLM 요약 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택, 이유, DB/API/테스트 영향, trade-off, 후속 분기가 모두 충족되었다.

Pass 이유:
- Sprint 4 schema와 테스트 fixture를 안정적으로 진행할 수 있는 model과 dimension이 확정되었다.

보완 질문 여부:
- 보완 질문 3개를 거쳐 Pass 처리했다.

아직 남은 후속 분기:
- `post_embeddings` schema
- embedding 실패 처리
- 추천 API 계약
- similarity threshold/top-N
- LLM 요약 방식

최종 결론:
- Sprint 4 embedding model은 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`로 둔다.
- vector dimension은 384로 둔다.
- 실제 model 호출은 운영 흐름에서 사용하고, 테스트는 fake provider를 사용한다.
