# D-026: 로컬 embedding model과 vector dimension을 무엇으로 둘 것인가?

Sprint: 4
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: B. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimension
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-4/decisions/D-026-local-embedding-model-dimension.md`
- Roadmap: `docs/decisions/sprint-4/ROADMAP.md`
- Troubleshooting: `docs/decisions/sprint-4/troubleshooting/D-026-local-embedding-model-dimension-qna.md`
- Rollback: Pending

## 1. 현재 분기

Sprint 3.5 D-022에서 embedding은 로컬 또는 오픈소스 model을 우선 사용하기로 확정했다.

하지만 구체 model과 vector dimension은 후속 Decision으로 남겼다.

Sprint 4에서는 `post_embeddings` 테이블의 vector 컬럼 dimension, fake provider 테스트 fixture, 유사도 검색 쿼리가 이 값에 직접 묶인다.

따라서 구현 전에 로컬 embedding model과 vector dimension을 먼저 확정해야 한다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 embedding model과 dimension만 확정한다.

다음 항목은 자동 확정하지 않는다.

- `post_embeddings`의 전체 컬럼 구성
- pgvector index 종류
- embedding 실패 시 게시글 작성/수정 응답 방식
- 추천 API 경로와 요청/응답 shape
- similarity threshold와 top-N 기본값
- LLM 요약 provider와 prompt
- 프론트엔드 UI 배치

## 3. 선택지

### A. `sentence-transformers/all-MiniLM-L6-v2`, 384 dimension

로컬 embedding model로 `sentence-transformers/all-MiniLM-L6-v2`를 사용하고, vector dimension은 384로 둔다.

장점:
- 로컬 실행 비용이 낮고 모델이 비교적 가볍다.
- 학습용 프로젝트에서 설치와 실행 설명이 단순하다.
- 테스트 fake vector도 384 dimension 기준으로 만들기 쉽다.

단점:
- 한국어 또는 다국어 의미 검색 품질은 전용 다국어 모델보다 약할 수 있다.
- 검색 품질보다 구현 완성도와 데모 안정성을 우선하는 선택이다.

### B. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimension

로컬 embedding model로 다국어 MiniLM 계열을 사용하고, vector dimension은 384로 둔다.

장점:
- 한국어 게시글을 포함한 다국어 입력에 더 적합하다.
- dimension은 A와 같아 DB schema 부담이 작다.
- 로컬 실행 비용이 비교적 낮다.

단점:
- A보다 모델이 조금 더 무겁고 설치/실행 시간이 늘 수 있다.
- 프로젝트 환경에 따라 최초 모델 다운로드가 부담이 될 수 있다.

### C. model은 설정값으로 열어두고 기본 dimension만 384로 둔다

기본값은 384 dimension model로 두되, 실제 model 이름은 환경변수로 바꿀 수 있게 한다.

장점:
- model 교체 가능성이 가장 크다.
- 로컬 환경별 실험이 쉽다.

단점:
- dimension과 model이 어긋날 수 있어 런타임 검증이 필요하다.
- Sprint 4의 발표 설명과 테스트 기준이 흐려질 수 있다.
- schema가 model 선택과 느슨하게 결합되어 오류 가능성이 커진다.

## 4. Codex 추천

추천은 B다.

이 프로젝트의 응답과 문서가 한국어 중심이고, 게시글도 한국어 입력이 자연스럽다.

Sprint 4의 목표는 고급 retrieval 품질이 아니라 게시판 데이터와 연결된 RAG 흐름을 실제로 작동시키는 것이므로, 다국어 MiniLM 384 dimension은 실행 부담과 한국어 대응 사이의 균형이 좋다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 선택한 이유가 있어야 한다.
- DB schema, API, 테스트 중 무엇이 이 선택의 영향을 받는지 언급해야 한다.
- 이번 결정 이후에도 남는 후속 분기를 구분해야 한다.
- 검색 품질과 로컬 실행 부담 사이의 trade-off를 인식해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

DB/API/테스트 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현 파일을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- `post_embeddings` model과 vector dimension
- embedding provider 설정값
- fake embedding provider fixture
- pgvector similarity search 쿼리
- RAG 추천 API 테스트
- README 또는 Sprint note의 RAG 구조 설명

되돌릴 때 확인할 범위:
- `post_embeddings` 테이블 정의
- vector dimension 상수 또는 설정값
- provider 초기화 코드
- 테스트 fixture vector 길이
- 추천 API 응답 예시

DB 데이터 손실 가능성:
- 구현 후 dimension을 바꾸면 기존 embedding row를 재생성해야 한다.
- 아직 구현 전이므로 현재 단계의 데이터 손실은 없다.

원래 상태 보장:
- 기존 게시글 CRUD, 댓글, 태그, 검색, 페이징 테스트는 AI provider 없이 계속 통과해야 한다.
- RAG 관련 테스트는 실제 model 호출 대신 fake provider로 실행 가능해야 한다.

재검토 조건:
- 로컬 환경에서 선택한 model 다운로드 또는 실행이 반복적으로 실패하는 경우
- 한국어 유사도 품질이 데모를 방해할 정도로 낮은 경우
- 선택한 model의 vector dimension이 문서화된 값과 다르게 확인되는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: B

이유: 로컬 환경은 문제 없으니 한국어에 더 적합한 모델을 선택

DB/API/테스트 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 B로 명확하다.
- 이유는 로컬 환경에서 실행 가능하고 한국어에 더 적합한 모델을 고르겠다는 방향이므로 타당하다.
- DB/API/테스트 영향, trade-off, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 보완 내용으로 진행한다.

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
- 선택지가 명확하다.
- 한국어 대응과 로컬 실행 가능성을 이유로 제시했다.
- DB/API/테스트 영향이 구분되었다.
- 한국어 품질과 로컬 실행 부담 사이의 trade-off를 인식했다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- Sprint 1~3.5와 frontend 관련 기존 변경 및 미추적 파일이 다수 존재한다.
- D-026 처리 중에는 `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-4/decisions/D-026-local-embedding-model-dimension.md`, `docs/decisions/sprint-4/troubleshooting/D-026-local-embedding-model-dimension-qna.md`만 Decision 기록 범위로 변경한다.

구현 전 확정된 범위:
- embedding model은 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`로 둔다.
- vector dimension은 384로 둔다.
- DB embedding 컬럼은 후속 schema Decision에서 `vector(384)` 기준으로 검토한다.
- 테스트는 fake embedding provider를 기본으로 사용한다.

아직 구현 전 확정되지 않은 범위:
- `post_embeddings` 컬럼 구성과 index
- embedding 실패 처리
- 유사 게시글 추천 API 계약
- similarity threshold와 top-N
- LLM 요약 provider와 prompt
