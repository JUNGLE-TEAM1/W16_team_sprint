# Sprint 6 2시간 진행 계획

## 1. 오늘의 목표

Sprint 6 전체 목표는 **pgvector 기반 RAG 구현**입니다.

하지만 오늘 2시간 안에 전부 끝내려고 하지 않습니다. 오늘은 아래 Step 1~3까지만 진행합니다.

```text
Step 1. pgvector와 post_embeddings 테이블 준비
Step 2. 게시글 embedding 생성/저장 흐름 구현
Step 3. 유사 게시글 검색 API 구현
```

오늘 범위에서 제외하는 것:

```text
1. React 자동 유사글 사이드 패널
2. debounce 자동 검색 UX
3. LLM 요약
4. MCP
5. Agent
```

제외하는 이유는 RAG의 핵심인 **저장 구조 → embedding 생성 → vector 검색**을 먼저 이해해야 하기 때문입니다. 이 세 가지가 잡히면 이후 프론트 자동 추천과 LLM 요약은 그 위에 얹을 수 있습니다.

## 2. 오늘 확정한 Sprint 6 의사결정

| 결정 항목 | 결정 | 이유 |
| --- | --- | --- |
| RAG 기능 | 글 작성 중 유사 게시글 추천 | 게시판의 글쓰기 흐름과 가장 자연스럽게 연결된다. |
| Vector DB | pgvector | Sprint 계획에서 고정된 기술이며 PostgreSQL과 함께 관리할 수 있다. |
| Embedding 대상 | `title + content + tags` | 제목만으로는 맥락이 부족하고, 태그는 검색 metadata 성격을 보완한다. |
| Chunking | 게시글 단위 | MVP에서는 구현과 설명이 단순하다. 문단 chunking은 추후 확장이다. |
| 저장 구조 | `post_embeddings` 별도 테이블 | 게시글 본문 테이블과 vector 저장 책임을 분리할 수 있다. |
| 검색 개수 | top-3 | 글 작성 중 사이드 추천 UI에 적당한 개수다. |
| 유사도 기준 | cosine distance | 텍스트 embedding은 벡터 크기보다 의미 방향 비교가 중요하다. |
| Embedding 생성 시점 | 게시글 작성/수정 시 자동 생성 | RAG 검색 데이터가 게시글 변경과 함께 최신 상태를 유지한다. |
| 삭제 동기화 | 게시글 삭제 시 embedding도 삭제 | orphan embedding을 남기지 않는다. |
| 실패 처리 | AI 실패가 게시글 저장을 막지 않음 | 게시판 기본 기능이 AI 기능에 종속되지 않게 한다. |

## 3. 유사도 기준을 cosine으로 잡는 이유

pgvector에서 자주 쓰는 유사도 기준은 세 가지입니다.

| 기준 | 의미 | Sprint 6 적합도 |
| --- | --- | --- |
| cosine distance | 두 vector의 방향이 얼마나 비슷한지 본다. | 텍스트 의미 유사도 검색에 가장 무난하다. |
| L2 distance | 두 vector 좌표 사이의 실제 거리를 본다. | 이미지/수치 벡터처럼 거리 자체가 중요할 때 더 어울린다. |
| inner product | 방향과 크기를 함께 본다. | 모델이 inner product 기준으로 설계됐거나 vector 정규화 전략이 명확할 때 쓴다. |

이번 기능은 아래처럼 단어가 정확히 같지 않아도 의미가 가까운 글을 찾아야 합니다.

```text
작성 중인 글:
FastAPI JWT 인증에서 401 오류가 납니다.

기존 글:
Authorization Bearer 토큰 누락 문제
```

이 경우 중요한 것은 vector의 크기가 아니라 의미 방향입니다. 그래서 cosine distance를 기본값으로 선택합니다.

표시용 점수는 아래처럼 계산할 수 있습니다.

```text
similarity = 1 - cosine_distance
```

단, similarity threshold는 실제 데이터가 쌓인 뒤 조정합니다. 오늘 Step 3에서는 우선 top-3를 반환하고, threshold 필터링은 이후 UI 단계에서 조정합니다.

## 4. 2시간 진행 순서

### 0~10분: 시작 전 확인

목표:

```text
1. 현재 DB가 PostgreSQL인지 확인한다.
2. Docker image가 pgvector를 지원하는지 확인한다.
3. 오늘 수정할 파일 범위를 확인한다.
```

볼 파일:

```text
docker-compose.yml
requirements.txt
backend/app/core/config.py
backend/app/main.py
backend/app/models/post.py
backend/app/services/post_service.py
```

확인 질문:

```text
1. 현재 DB는 어느 port에서 뜨는가?
2. pgvector extension은 현재 DB image에서 바로 쓸 수 있는가?
3. AI/RAG 기능이 기존 게시글 CRUD와 어디에서 연결되는가?
```

## 5. Step 1 - pgvector와 post_embeddings 테이블 준비

### 5.1 구현 목표

PostgreSQL에서 vector 타입을 사용할 수 있게 하고, 게시글 embedding을 저장할 별도 테이블을 만든다.

```text
posts
  id
  title
  content
  ...

post_embeddings
  id
  post_id
  embedding
  content_snapshot
  metadata
  created_at
```

### 5.2 구현할 것

예상 변경 파일:

```text
docker-compose.yml
requirements.txt
backend/app/db/schema.py
backend/app/models/post_embedding.py
backend/app/models/__init__.py
backend/app/main.py
```

구현 내용:

```text
1. Docker DB image를 pgvector 지원 이미지로 변경한다.
2. Python에서 pgvector SQLAlchemy 타입을 사용할 수 있게 dependency를 추가한다.
3. `CREATE EXTENSION IF NOT EXISTS vector`가 실행되도록 한다.
4. `PostEmbedding` 모델을 만든다.
5. `post_embeddings.embedding`에 vector 컬럼을 둔다.
6. `posts` 삭제 시 embedding도 같이 삭제되게 FK/cascade를 맞춘다.
```

### 5.3 Step 1 완료 확인

명령:

```bash
.venv/bin/python -m pytest backend/tests/test_post_service.py
```

DB 확인:

```text
1. post_embeddings 테이블이 생성되는가?
2. embedding 컬럼이 vector 타입인가?
3. posts와 post_embeddings가 post_id로 연결되는가?
```

네가 이해해야 할 질문:

```text
1. embedding을 posts 테이블에 직접 넣지 않고 별도 테이블로 뺀 이유는 무엇인가?
2. pgvector extension은 왜 필요한가?
3. post_id FK는 어떤 문제를 막아주는가?
```

여기까지 확인한 뒤 Step 2로 넘어간다.

## 6. Step 2 - 게시글 embedding 생성/저장 흐름 구현

### 6.1 구현 목표

게시글을 만들거나 수정하면, RAG 검색에 쓸 텍스트를 만들고 embedding을 저장한다.

오늘은 실제 OpenAI embedding을 바로 강제하지 않습니다. 테스트와 로컬 개발을 위해 **결정적 mock embedding**을 먼저 둡니다.

```text
실제 서비스:
OpenAI embedding 사용

테스트/로컬 fallback:
같은 텍스트는 항상 같은 vector가 나오는 mock embedding 사용
```

이렇게 하는 이유:

```text
1. API key 없이도 테스트가 돌아간다.
2. 네트워크 실패 때문에 게시글 기능이 막히지 않는다.
3. RAG 저장/검색 구조를 먼저 이해할 수 있다.
```

### 6.2 구현할 것

예상 변경 파일:

```text
backend/app/core/config.py
backend/app/repositories/embedding_repository.py
backend/app/services/embedding_service.py
backend/app/services/post_service.py
backend/app/api/dependencies.py
backend/tests/test_posts_flow.py
```

구현 내용:

```text
1. embedding에 사용할 텍스트를 만든다.
   - title
   - content
   - tags

2. embedding service를 만든다.
   - embed_text(text) -> list[float]

3. post_embeddings에 저장한다.
   - post_id
   - embedding
   - content_snapshot
   - metadata

4. 게시글 수정 시 기존 embedding을 갱신한다.

5. embedding 생성 실패 시 게시글 저장 자체는 실패시키지 않는다.
```

### 6.3 Step 2 완료 확인

테스트에서 확인할 것:

```text
1. 게시글을 작성하면 post_embeddings row가 생긴다.
2. content_snapshot에 title/content/tags가 반영된다.
3. 게시글을 수정하면 embedding row도 갱신된다.
4. embedding 실패가 게시글 작성 자체를 막지 않는다.
```

네가 이해해야 할 질문:

```text
1. embedding 대상 텍스트는 어디에서 조립되는가?
2. post_service가 왜 embedding_service를 호출하는가?
3. embedding 실패를 게시글 저장 실패로 보지 않는 이유는 무엇인가?
```

여기까지 확인한 뒤 Step 3으로 넘어간다.

## 7. Step 3 - 유사 게시글 검색 API 구현

### 7.1 구현 목표

사용자 입력을 embedding한 뒤, pgvector cosine distance로 기존 게시글 중 유사한 글 top-3를 찾는다.

오늘은 프론트 자동 검색까지 붙이지 않고, API로 먼저 검증한다.

### 7.2 API 초안

```http
POST /api/v1/ai/rag/related-posts
```

request:

```json
{
  "title": "FastAPI JWT 인증에서 401 오류가 납니다",
  "content": "current_user dependency에서 계속 인증 실패가 납니다.",
  "tags": ["fastapi", "jwt", "auth"]
}
```

response:

```json
{
  "items": [
    {
      "post_id": 3,
      "title": "Authorization Bearer 누락 문제",
      "similarity": 0.86,
      "summary": null
    }
  ]
}
```

오늘 Step 3에서는 `summary`를 `null`로 둬도 됩니다. LLM 요약은 다음 단계입니다.

### 7.3 구현할 것

예상 변경 파일:

```text
backend/app/schemas/ai.py
backend/app/repositories/embedding_repository.py
backend/app/services/rag_service.py
backend/app/api/v1/ai.py
backend/app/main.py
backend/tests/test_ai_rag_flow.py
```

구현 내용:

```text
1. RAG request/response schema를 만든다.
2. 사용자 입력을 embedding한다.
3. post_embeddings에서 cosine distance 기준으로 가까운 게시글 top-3를 찾는다.
4. 검색 결과를 posts title/content/tags와 함께 반환한다.
5. 결과가 없으면 items: []를 반환한다.
```

### 7.4 Step 3 완료 확인

테스트에서 확인할 것:

```text
1. 유사한 글이 있으면 top-3 안에 포함된다.
2. 전혀 데이터가 없으면 items: []가 나온다.
3. 자기 자신을 제외하는 옵션이 필요하면 request에 exclude_post_id를 둘 수 있다.
4. 응답이 게시글 id/title/similarity를 포함한다.
```

네가 이해해야 할 질문:

```text
1. 사용자의 입력도 왜 embedding해야 하는가?
2. DB에 저장된 embedding과 query embedding은 어떻게 비교되는가?
3. cosine distance가 작다는 것은 무슨 의미인가?
4. API 응답에서 similarity는 왜 1 - distance로 바꾸는가?
```

## 8. 오늘의 최종 완료 기준

오늘 2시간이 끝났을 때 아래를 만족하면 성공입니다.

```text
1. pgvector extension과 post_embeddings 테이블이 준비되어 있다.
2. 게시글 작성/수정 시 embedding row가 저장/갱신된다.
3. RAG API로 유사 게시글 top-3를 검색할 수 있다.
4. 테스트로 Step 1~3 흐름이 검증되어 있다.
5. docs2/sprint-6에 구현 기록을 남길 준비가 되어 있다.
```

오늘 끝나고 바로 작성할 구현 기록:

```text
docs2/sprint-6/implementation-record.md
```

기록에 반드시 포함할 것:

```text
1. Step 1~3에서 바뀐 파일
2. post_embeddings ERD
3. 게시글 작성 -> embedding 저장 흐름 mermaid
4. RAG 검색 요청 -> top-3 응답 흐름 mermaid
5. 각 Step별 확인 명령
6. 네가 코드 읽을 때 따라갈 함수 순서
```

## 9. 진행 중 멈춰서 확인할 타이밍

이번 Sprint는 아래 세 번 멈춰서 이해를 확인합니다.

```text
1. Step 1 완료 후
   - DB 구조와 pgvector extension 이해

2. Step 2 완료 후
   - 게시글 저장과 embedding 저장이 어떻게 연결되는지 이해

3. Step 3 완료 후
   - query embedding과 DB embedding이 어떻게 비교되는지 이해
```

각 시점마다 구현 기록을 짧게 업데이트하고, 그 문서를 보면서 다음 Step으로 넘어갑니다.
