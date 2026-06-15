# D-020: Embedding 저장 위치를 어떻게 둘 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: A. `post_embeddings` 별도 테이블을 둔다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-020-embedding-storage.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정했다.

D-019에서 RAG의 1차 embedding 입력은 게시글의 `title`, `content`, `tags`로 확정했다.

이제 embedding을 어디에 저장할지 정해야 한다.

팀 싱크 입력에서는 `post_embeddings` 별도 테이블을 추천했다.

추천 초안:

```text
post_embeddings
- id
- post_id
- embedding
- content_snapshot
- metadata
- created_at
```

## 2. 이번에 선택하지 않는 분기

이번 Decision은 embedding 저장 위치만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- embedding 생성 시점
- embedding model과 vector dimension
- `metadata` JSON 구조
- `content_snapshot` 구성 문자열
- 유사도 threshold
- top-3/top-5 개수
- 재색인 API 또는 관리 명령 여부

## 3. 선택지

### A. `post_embeddings` 별도 테이블을 둔다

게시글 본문 데이터와 embedding 데이터를 분리한다.

장점:
- 게시글 도메인 모델과 AI 검색 인덱스를 분리할 수 있다.
- `content_snapshot`, `metadata`, embedding model 정보 같은 AI 전용 필드를 담기 쉽다.
- 나중에 댓글, chunk, 재색인 이력을 확장하기 쉽다.
- 팀 싱크에서 정한 구조와 맞다.

단점:
- join 또는 별도 repository가 필요하다.
- 게시글 생성/수정/삭제와 embedding row의 동기화 전략이 필요하다.

### B. `posts` 테이블에 vector 컬럼을 추가한다

게시글 row에 embedding vector를 직접 저장한다.

장점:
- 구현이 단순하다.
- 게시글과 embedding이 항상 같은 row에 있어 조회가 쉽다.

단점:
- posts 모델이 AI 인덱스 책임까지 갖게 된다.
- model 변경, snapshot, 재색인 상태 같은 확장 필드를 붙이기 불편하다.
- 댓글 또는 chunk 확장 시 다시 구조를 바꿔야 할 가능성이 높다.

### C. Sprint 4에서는 저장하지 않고 요청 시 embedding만 계산한다

DB에 embedding을 저장하지 않고, 요청 때마다 기존 게시글을 embedding해서 비교한다.

장점:
- DB schema 변경을 늦출 수 있다.
- 초기 실험에는 단순해 보일 수 있다.

단점:
- 게시글 수가 늘면 매 요청 비용이 커진다.
- pgvector 검색 요구와 맞지 않는다.
- Sprint 4 완료 기준인 PostgreSQL embedding 저장과 어긋난다.

## 4. Codex 추천

추천은 A다.

이미 팀 싱크에서 `post_embeddings` 구조를 제안했고, D-019에서 게시글 `title`, `content`, `tags`를 1차 embedding 입력으로 확정했기 때문에 별도 테이블이 가장 자연스럽다.

Sprint 4 이후 댓글 포함, chunking, 재색인, model 변경을 다룰 수 있는 확장성도 가장 좋다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- `posts` 모델과 embedding 데이터를 분리할지 여부가 명확해야 한다.
- DB/API/테스트 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

posts와 embedding 분리 기준:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- embedding 모델 파일
- repository/service 계층
- DB migration 또는 metadata
- 유사 게시글 추천 API
- 관련 테스트

되돌릴 때 확인할 범위:
- `post_embeddings` 모델과 migration
- embedding repository/service
- 게시글 생성/수정/삭제와 embedding 동기화 코드
- RAG 추천 API

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- 후속 구현에서 `post_embeddings` 테이블 삭제가 필요하면 embedding row 손실 가능성이 있다.
- 원본 게시글 데이터는 별도 테이블 분리 시 보존된다.

원래 상태 보장:
- 기존 게시글 CRUD, 태그 검색, 댓글 테스트가 계속 통과해야 한다.

재검토 조건:
- 프로젝트 DB가 pgvector를 사용할 수 없는 환경으로 바뀌는 경우
- Sprint 4에서 DB migration이 불가능한 제약이 생기는 경우
- 팀이 AI 인덱스를 별도 저장하지 않는 방향으로 요구사항을 바꾸는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A
 
이유: 주후 확장이 용이해서 분리해놓는게 훨씬 나음, 이전 분기와 일관성이 이어짐

posts와 embedding 분리 기준:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 확장성과 이전 Decision과의 일관성을 근거로 하므로 충분하다.
- `posts`와 embedding 분리 기준, DB/API/테스트 영향, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 예시대로 적용한다.

정리된 최종 답변:

```md
선택: A

이유:
추후 확장이 용이해서 분리해놓는 게 훨씬 낫고, 이전 분기와 일관성이 이어진다.

posts와 embedding 분리 기준:
`posts`는 게시글 원본 데이터와 사용자-facing 필드를 책임지고, `post_embeddings`는 AI 검색 인덱스인 `embedding`, `content_snapshot`, `metadata`, `created_at`을 책임진다.

DB/API/테스트 영향:
DB에는 `post_embeddings` 테이블과 `post_id` 관계가 필요해진다. API는 유사 게시글 추천 API에서 `post_embeddings`를 조회하게 되고, 테스트는 게시글 원본과 embedding row가 연결되어 검색되는지 확인해야 한다.

아직 다음 분기로 남겨둘 것:
embedding 생성 시점, embedding model과 vector dimension, metadata JSON 구조, content_snapshot 구성, 유사도 threshold, top-3/top-5 개수는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- `posts`와 `post_embeddings`의 책임 분리가 명확하다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- embedding은 `posts` 테이블에 직접 넣지 않고 `post_embeddings` 별도 테이블에 저장한다.
- `posts`는 사용자-facing 원본 게시글 데이터를 책임진다.
- `post_embeddings`는 AI 검색 인덱스와 snapshot/metadata를 책임진다.

아직 구현 전 확정되지 않은 범위:
- embedding 생성 시점
- embedding model과 vector dimension
- metadata JSON 구조
- content_snapshot 구성
- 유사도 threshold
- top-3/top-5 개수
