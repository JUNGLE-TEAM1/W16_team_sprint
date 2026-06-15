# D-027: `post_embeddings` schema를 어떻게 정의할 것인가?

Sprint: 4
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. 게시글당 1개 embedding row를 유지하는 단순 upsert schema
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-4/decisions/D-027-post-embeddings-schema.md`
- Roadmap: `docs/decisions/sprint-4/ROADMAP.md`
- Troubleshooting: `docs/decisions/sprint-4/troubleshooting/D-027-post-embeddings-schema-qna.md`
- Rollback: Pending

## 1. 현재 분기

D-020에서 embedding 저장 위치는 `post_embeddings` 별도 테이블로 확정했다.

D-026에서 embedding model은 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, vector dimension은 384로 확정했다.

이제 실제 `post_embeddings` 테이블의 컬럼, 관계, uniqueness, metadata 구조, vector 컬럼 처리 방식을 정해야 한다.

이 결정은 DB schema, repository query, 게시글 작성/수정 후 embedding upsert, 유사 게시글 검색 API 테스트에 직접 영향을 준다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 `post_embeddings`의 schema만 확정한다.

다음 항목은 자동 확정하지 않는다.

- embedding provider 실패 시 게시글 작성/수정 API 응답 방식
- 추천 API 경로와 요청/응답 shape
- similarity threshold와 top-N 기본값
- LLM 요약 provider와 prompt
- 실제 pgvector index 튜닝
- 재색인 관리 명령 또는 API

## 3. 선택지

### A. 게시글당 1개 embedding row를 유지하는 단순 upsert schema

`post_embeddings`는 게시글 1개당 최신 embedding row 1개만 가진다.

예상 컬럼:
- `id`
- `post_id`
- `embedding vector(384)`
- `content_snapshot`
- `metadata`
- `model_name`
- `created_at`
- `updated_at`

제약:
- `post_id` unique
- `post_id`는 `posts.id`를 참조하고 게시글 삭제 시 함께 삭제

장점:
- Sprint 4 완료 기준에 가장 직접적이다.
- 게시글 작성/수정 후 upsert 흐름이 단순하다.
- 검색 API에서 최신 embedding만 보면 된다.
- 테스트가 쉽다.

단점:
- 과거 embedding 이력은 남지 않는다.
- chunking 또는 여러 model 병행 저장은 나중에 schema 확장이 필요하다.

### B. model별 embedding row를 여러 개 저장할 수 있는 schema

`post_id`, `model_name` 조합으로 unique를 두고, 게시글 하나가 여러 model embedding을 가질 수 있게 한다.

예상 컬럼:
- `id`
- `post_id`
- `model_name`
- `dimension`
- `embedding vector(384)`
- `content_snapshot`
- `metadata`
- `created_at`
- `updated_at`

제약:
- `post_id`, `model_name` unique
- 검색 시 사용할 model을 명시해야 한다.

장점:
- model 교체와 비교 실험에 유리하다.
- 재색인 중 이전 model 결과와 새 model 결과를 나란히 둘 수 있다.

단점:
- Sprint 4 MVP에는 복잡하다.
- 추천 API와 repository에서 model filter가 필수가 된다.
- dimension이 model별로 달라질 경우 pgvector 컬럼 설계가 복잡해진다.

### C. chunk 확장을 전제로 한 범용 embedding item schema

게시글 전체뿐 아니라 나중에 댓글, 문단 chunk, 외부 문서까지 넣을 수 있는 범용 테이블로 둔다.

예상 컬럼:
- `id`
- `source_type`
- `source_id`
- `chunk_index`
- `embedding vector(384)`
- `content_snapshot`
- `metadata`
- `model_name`
- `created_at`
- `updated_at`

장점:
- 장기 확장성이 가장 크다.
- 댓글, chunking, 외부 문서 RAG까지 한 테이블로 확장할 수 있다.

단점:
- 현재 Sprint 4의 게시글 기반 RAG에는 과하다.
- `posts`와의 명시적 FK가 약해질 수 있다.
- 삭제 동기화와 테스트 범위가 커진다.

## 4. Codex 추천

추천은 A다.

Sprint 4의 목표는 고급 chunking이나 model 비교가 아니라, 게시글 작성 데이터와 연결된 RAG가 실제로 동작하는 것이다.

D-019에서 RAG 데이터 범위도 게시글 `title`, `content`, `tags`로 제한했고, 제외 범위에 고급 chunking이 들어 있으므로 게시글당 1개 최신 embedding row가 가장 적절하다.

다만 `model_name`, `metadata`, `content_snapshot`, `updated_at`은 남겨서 나중에 재색인과 model 변경을 설명할 여지는 확보한다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 선택한 이유가 있어야 한다.
- 게시글당 1개 row인지, model별 여러 row인지, 범용 item 구조인지가 명확해야 한다.
- DB/API/테스트 중 무엇이 이 선택의 영향을 받는지 언급해야 한다.
- 이번 결정 이후에도 남는 후속 분기를 구분해야 한다.
- 확장성과 Sprint 4 단순성 사이의 trade-off를 인식해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

row 저장 기준:

DB/API/테스트 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현 파일을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- `backend/app/models/post_embedding.py`
- `backend/app/models/__init__.py`
- embedding repository/service
- 게시글 작성/수정/삭제와 embedding 동기화 코드
- 유사 게시글 검색 query
- RAG 관련 테스트 fixture
- README 또는 Sprint note의 RAG schema 설명

되돌릴 때 확인할 범위:
- `post_embeddings` 모델 정의
- `Base.metadata.create_all`로 생성되는 테이블
- pgvector extension 준비 코드
- embedding upsert 로직
- 추천 API 테스트

DB 데이터 손실 가능성:
- 구현 후 schema를 바꾸거나 테이블을 삭제하면 embedding row 손실 가능성이 있다.
- 원본 `posts` 데이터는 별도 테이블로 유지된다.

원래 상태 보장:
- 기존 게시글 CRUD, 댓글, 태그, 검색, 페이징 테스트는 계속 통과해야 한다.
- AI provider 없이도 기존 API가 실패하지 않아야 한다.

재검토 조건:
- Sprint 4 중 댓글 또는 chunking이 필수 범위로 바뀌는 경우
- 여러 embedding model을 동시에 비교해야 하는 요구가 생기는 경우
- pgvector `vector(384)` 컬럼을 현재 테스트 DB에서 사용할 수 없는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 질문

질문:
- `post_embeddings`의 schema가 무엇인지 확인했다.
- model을 하나만 쓰므로 row도 하나만 있는 게 맞지 않냐고 물었다.
- 최신 embedding row가 매번 embedding을 업데이트한다는 뜻인지 확인했다.

Codex 답변 요지:
- schema는 embedding 저장 테이블의 설계도다.
- Sprint 4에서는 model 하나를 쓰므로 게시글당 embedding row 하나가 적절하다.
- 최신 embedding row는 게시글 작성 시 생성하고, 게시글 수정 시 같은 row를 새 embedding으로 갱신한다는 뜻이다.
- 과거 embedding 이력은 저장하지 않는다.

### 2026-06-15 사용자 최종 답변

사용자 답변:

```md
선택: A

이유:
Sprint 4에서는 embedding model을 하나만 쓰므로 게시글당 최신 embedding row 하나만 두는 게 적당함

row 저장 기준:
게시글 하나당 `post_embeddings` row 하나를 둔다. 게시글 수정 시 기존 row를 갱신하고, 삭제 시 함께 삭제한다. `model_name`은 현재 하나의 model만 쓰더라도 추후 재색인 설명을 위해 저장함.

DB/API/테스트 영향:
DB에는 `post_id` unique 제약을 둔다. API는 최신 embedding 기준으로 유사 게시글을 검색한다. 테스트는 게시글 생성/수정 후 embedding row가 1개로 유지되는지 확인한다.

trade-off:
구조는 단순하지만 model별 비교나 chunk 단위 검색은 바로 지원하지 않는다. 다만 Sprint 4 범위에서는 단순성이 더 중요하다.

아직 다음 분기로 남겨둘 것:
embedding 실패 처리, 추천 API 계약, similarity threshold/top-N, LLM 요약 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- Sprint 4에서는 embedding model 하나만 사용한다는 이유가 명확하다.
- 게시글당 최신 embedding row 하나를 유지한다는 row 저장 기준이 명확하다.
- DB/API/테스트 영향이 구분되었다.
- 단순성과 확장성 사이의 trade-off를 인식했다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- Sprint 1~3.5와 frontend 관련 기존 변경 및 미추적 파일이 다수 존재한다.
- D-027 처리 중에는 `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-4/decisions/D-027-post-embeddings-schema.md`, `docs/decisions/sprint-4/troubleshooting/D-027-post-embeddings-schema-qna.md`만 Decision 기록 범위로 변경한다.

구현 전 확정된 범위:
- `post_embeddings`는 게시글당 최신 embedding row 1개를 유지한다.
- `post_id`에는 unique 제약을 둔다.
- 게시글 수정 시 기존 embedding row를 갱신한다.
- 게시글 삭제 시 embedding row도 함께 삭제한다.
- `model_name`은 현재 model이 하나여도 저장한다.
- 과거 embedding 이력, model별 여러 row, chunk 단위 row는 Sprint 4 범위에서 제외한다.

아직 구현 전 확정되지 않은 범위:
- embedding 실패 처리
- 추천 API 계약
- similarity threshold와 top-N
- LLM 요약 방식
