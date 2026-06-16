# Sprint 6 LangChain RAG 리팩토링 구현 기록

## 1. 목표

기존 Sprint 6 RAG는 OpenAI embedding 호출과 pgvector SQL 검색을 직접 구현했습니다.
이번 리팩토링의 목표는 **RAG 흐름을 LangChain 기반으로 바꾸고, Sprint 8 Agent에서 같은 검색 기능을 tool로 연결하기 쉬운 구조를 만드는 것**입니다.

이번 변경으로 아래 기준을 맞췄습니다.

```text
1. Embedding provider가 LangChain Embeddings 인터페이스를 따른다.
2. 게시글은 LangChain Document로 변환된다.
3. RAG 검색 index는 LangChain PGVector를 사용한다.
4. 기존 post_embeddings 테이블은 동기화 상태와 실패 기록으로 유지한다.
5. API 응답 형식과 프론트 호출 방식은 바꾸지 않는다.
```

## 2. 핵심 의사결정

| 항목 | 결정 |
| --- | --- |
| RAG framework | LangChain |
| Vector DB | PostgreSQL + pgvector |
| LangChain vector store | `langchain-postgres`의 `PGVector` |
| Embedding model | OpenAI `text-embedding-3-small` 기본값 |
| 테스트 embedding | LangChain `Embeddings` 인터페이스를 구현한 mock |
| 기존 `post_embeddings` | 제거하지 않고 상태/실패 기록 테이블로 유지 |
| LangChain collection | `LANGCHAIN_RAG_COLLECTION_NAME`, 기본값 `post_rag_documents` |

## 3. 왜 LangChain PGVector를 쓰는가

LangChain은 pgvector를 대체하지 않습니다.

```text
PostgreSQL + pgvector:
  vector 저장과 similarity search 담당

LangChain:
  Embeddings, Document, VectorStore, Retriever, Tool, Agent 연결 담당
```

이번 리팩토링에서는 LangChain의 `PGVector`를 사용해 게시글 RAG 검색 index를 만들었습니다.
그래서 Sprint 8에서 Agent를 만들 때 `search_related_posts` 같은 tool을 LangChain 기반으로 감싸기 쉬워졌습니다.

## 4. 변경된 구조

```text
기존:
PostService
-> PostEmbeddingService
-> OpenAI client 직접 호출
-> PostEmbeddingRepository
-> post_embeddings.embedding 저장
-> RagService
-> PostEmbeddingRepository.find_related_posts()
-> 직접 pgvector SQL

변경 후:
PostService
-> PostEmbeddingService
-> LangChain Embeddings
-> LangChainPostVectorIndex
-> PGVector.add_embeddings()
-> langchain_pg_embedding 저장
-> PostEmbeddingRepository
-> post_embeddings 상태 기록

RagService
-> LangChainPostVectorIndex
-> PGVector.similarity_search_with_score()
-> 현재 posts 테이블에서 결과 재확인
-> RelatedPostsResponse 반환
```

## 5. 게시글 저장 시 RAG index 동기화 흐름

```mermaid
sequenceDiagram
    participant API as Posts API
    participant PostService as PostService
    participant EmbedService as PostEmbeddingService
    participant Embeddings as LangChain Embeddings
    participant Index as LangChainPostVectorIndex
    participant PGVector as LangChain PGVector
    participant LCDB as langchain_pg_embedding
    participant StatusRepo as PostEmbeddingRepository
    participant StatusDB as post_embeddings

    API->>PostService: 1. 게시글 작성/수정 요청 처리
    PostService->>EmbedService: 2. embedding 대상 text/hash/metadata 생성
    EmbedService->>Embeddings: 3. embed_query() 호출
    PostService->>Index: 4. upsert_post(post, text, embedding, metadata)
    Index->>PGVector: 5. add_embeddings(texts, embeddings, metadatas, ids)
    PGVector->>LCDB: 6. LangChain vector document 저장
    PostService->>StatusRepo: 7. upsert_completed()
    StatusRepo->>StatusDB: 8. embedding 동기화 상태 저장
```

1. 게시글 작성/수정 요청 처리
   - 코드: `backend/app/services/post_service.py`
   - 함수: `PostService.create()`, `PostService.update()`
   - 확인: 게시글 본문 또는 태그가 바뀌면 `_sync_embedding()`이 호출됩니다.

2. embedding 대상 text/hash/metadata 생성
   - 코드: `backend/app/services/embedding_service.py`
   - 함수: `PostEmbeddingService.build_post_text()`, `build_content_hash()`, `build_metadata()`
   - 확인: `title`, `content`, `tags`를 하나의 embedding 대상 text로 만듭니다.

3. embed_query() 호출
   - 코드: `backend/app/services/embedding_service.py`
   - 함수: `OpenAIEmbeddingProvider.embed_query()`, `MockEmbeddingProvider.embed_query()`
   - 확인: 실제 앱은 LangChain `OpenAIEmbeddings`, 테스트는 mock embedding을 사용합니다.

4. upsert_post(post, text, embedding, metadata)
   - 코드: `backend/app/services/langchain_rag_index.py`
   - 함수: `LangChainPostVectorIndex.upsert_post()`
   - 확인: 게시글을 LangChain `Document` 구조로 변환한 뒤 vector index에 넘깁니다.

5. add_embeddings(texts, embeddings, metadatas, ids)
   - 코드: `backend/app/services/langchain_rag_index.py`
   - 함수: `LangChainPostVectorIndex.upsert_post()`
   - 확인: 이미 생성한 embedding을 넘겨 중복 OpenAI embedding 호출을 피합니다.

6. LangChain vector document 저장
   - 코드: `langchain-postgres`의 `PGVector`
   - DB: `langchain_pg_collection`, `langchain_pg_embedding`
   - 확인: LangChain이 관리하는 pgvector collection에 RAG 검색용 document가 저장됩니다.

7. upsert_completed()
   - 코드: `backend/app/repositories/embedding_repository.py`
   - 함수: `PostEmbeddingRepository.upsert_completed()`
   - 확인: LangChain index 저장까지 성공한 뒤 기존 상태 테이블을 `completed`로 기록합니다.

8. embedding 동기화 상태 저장
   - 코드: `backend/app/models/post_embedding.py`
   - 테이블: `post_embeddings`
   - 확인: 학습과 운영 확인을 위해 embedding vector, content hash, status, attempt count를 유지합니다.

## 6. 유사 게시글 검색 흐름

```mermaid
sequenceDiagram
    participant UI as RelatedPostsPanel
    participant API as AI API
    participant RagService as RagService
    participant EmbedService as PostEmbeddingService
    participant Index as LangChainPostVectorIndex
    participant PGVector as LangChain PGVector
    participant Embeddings as LangChain Embeddings
    participant LCDB as langchain_pg_embedding
    participant PostDB as posts/tags
    participant Summary as RagSummaryProvider

    UI->>API: 1. 작성 중인 제목/본문/태그 전송
    API->>RagService: 2. find_related_posts(payload)
    RagService->>EmbedService: 3. 검색 query text 생성
    RagService->>Index: 4. find_related_posts(query_text)
    Index->>PGVector: 5. similarity_search_with_score(query_text)
    PGVector->>Embeddings: 6. query embedding 생성
    PGVector->>LCDB: 7. pgvector similarity search 실행
    Index->>PostDB: 8. 현재 posts/tags 기준으로 결과 재확인
    RagService->>Summary: 9. 유사 게시글 summary 생성
    RagService-->>API: 10. RelatedPostsResponse 반환
```

1. 작성 중인 제목/본문/태그 전송
   - 코드: `frontend/src/hooks/useRelatedPosts.ts`
   - 확인: 프론트는 기존과 동일하게 `/api/v1/ai/rag/related-posts`를 호출합니다.

2. find_related_posts(payload)
   - 코드: `backend/app/api/v1/ai.py`, `backend/app/services/rag_service.py`
   - 함수: `find_related_posts()`, `RagService.find_related_posts()`
   - 확인: API endpoint와 response schema는 바꾸지 않았습니다.

3. 검색 query text 생성
   - 코드: `backend/app/services/embedding_service.py`
   - 함수: `PostEmbeddingService.build_text()`
   - 확인: 작성 중인 글의 `title`, `content`, `tags`를 검색 query text로 합칩니다.

4. find_related_posts(query_text)
   - 코드: `backend/app/services/langchain_rag_index.py`
   - 함수: `LangChainPostVectorIndex.find_related_posts()`
   - 확인: RAG 검색 책임이 repository SQL에서 LangChain index service로 이동했습니다.

5. similarity_search_with_score(query_text)
   - 코드: `backend/app/services/langchain_rag_index.py`
   - 함수: `LangChainPostVectorIndex.find_related_posts()`
   - 확인: LangChain `PGVector`가 query text를 받아 similarity search를 실행합니다.

6. query embedding 생성
   - 코드: `backend/app/services/embedding_service.py`
   - 함수: `as_langchain_embeddings()`, `OpenAIEmbeddingProvider.embed_query()`
   - 확인: 실제 앱에서는 OpenAI embedding이 호출되고, 테스트에서는 mock embedding이 호출됩니다.

7. pgvector similarity search 실행
   - 코드: `langchain-postgres`의 `PGVector`
   - DB: `langchain_pg_embedding`
   - 확인: LangChain이 관리하는 pgvector collection에서 후보 document를 찾습니다.

8. 현재 posts/tags 기준으로 결과 재확인
   - 코드: `backend/app/services/langchain_rag_index.py`
   - 함수: `LangChainPostVectorIndex._hydrate_related_posts()`
   - 확인: 오래된 LangChain document가 있어도 현재 `posts` 테이블에 없는 글은 응답에서 제외합니다.

9. 유사 게시글 summary 생성
   - 코드: `backend/app/services/rag_summary_service.py`
   - 함수: `OpenAIRagSummaryProvider.summarize()`
   - 확인: 유사 게시글이 있으면 각 글마다 2-3문장 summary를 생성합니다.

10. RelatedPostsResponse 반환
    - 코드: `backend/app/schemas/ai.py`
    - 클래스: `RelatedPostsResponse`, `RelatedPostItem`
    - 확인: 프론트가 기대하는 `post_id`, `title`, `content_preview`, `tags`, `similarity`, `summary` 형식은 유지됩니다.

## 7. 실패 처리 흐름

```mermaid
sequenceDiagram
    participant PostService as PostService
    participant EmbedService as PostEmbeddingService
    participant Index as LangChainPostVectorIndex
    participant StatusRepo as PostEmbeddingRepository
    participant StatusDB as post_embeddings

    PostService->>EmbedService: 1. embedding 생성 시도
    EmbedService--xPostService: 2. embedding 실패 또는 차원 불일치
    PostService->>StatusRepo: 3. upsert_failed()
    StatusRepo->>StatusDB: 4. status=failed 저장
    PostService-->>PostService: 5. 게시글 저장 흐름은 계속 진행
```

1. embedding 생성 시도
   - 코드: `backend/app/services/post_service.py`
   - 함수: `PostService._sync_embedding()`
   - 확인: 게시글 저장 후 embedding 동기화를 시도합니다.

2. embedding 실패 또는 차원 불일치
   - 코드: `backend/app/services/embedding_service.py`, `backend/app/services/langchain_rag_index.py`
   - 확인: OpenAI embedding 실패, LangChain PGVector 저장 실패, 차원 불일치가 모두 실패로 처리됩니다.

3. upsert_failed()
   - 코드: `backend/app/repositories/embedding_repository.py`
   - 함수: `PostEmbeddingRepository.upsert_failed()`
   - 확인: 실패해도 게시글 작성/수정 자체는 막지 않습니다.

4. status=failed 저장
   - 코드: `backend/app/models/post_embedding.py`
   - 테이블: `post_embeddings`
   - 확인: 실패 사유는 `error_message`, 시도 횟수는 `attempt_count`에 남습니다.

5. 게시글 저장 흐름은 계속 진행
   - 코드: `backend/app/services/post_service.py`
   - 함수: `PostService.create()`, `PostService.update()`
   - 확인: Sprint 6 결정대로 embedding 실패는 게시글 저장 실패로 전파하지 않습니다.

## 8. 주요 코드 위치

| 파일 | 볼 것 |
| --- | --- |
| `backend/app/services/embedding_service.py` | LangChain `Embeddings` 기반 OpenAI/mock provider, legacy adapter |
| `backend/app/services/langchain_rag_index.py` | LangChain `PGVector` upsert/search/delete, Document 변환 |
| `backend/app/services/post_service.py` | 게시글 작성/수정/삭제 시 RAG index 동기화 |
| `backend/app/services/rag_service.py` | RAG API가 LangChain index를 호출하는 흐름 |
| `backend/app/api/dependencies.py` | `LangChainPostVectorIndex` 의존성 주입 |
| `backend/app/core/config.py` | `LANGCHAIN_RAG_COLLECTION_NAME` 설정 |
| `requirements.txt` | `langchain`, `langchain-openai`, `langchain-postgres` 의존성 |

## 9. 테스트 결과

```text
python3 -m pytest backend/tests/test_embedding_flow.py backend/tests/test_ai_rag_flow.py
9 passed

python3 -m pytest backend/tests
25 passed
```

테스트는 localhost PostgreSQL 접속이 필요해서 sandbox 밖에서 실행했습니다.

## 10. Sprint 8로 이어지는 포인트

다음 Sprint 8 Agent에서는 이 구조를 그대로 tool로 감싸면 됩니다.

```text
search_related_posts tool
-> LangChainPostVectorIndex.find_related_posts()

fetch_reference_doc tool
-> Sprint 7 MCP JSON-RPC tool

writing assistant agent
-> RAG tool + MCP tool 결과를 조합
-> 초안/태그/참고자료 제안
```

즉, 이번 리팩토링의 핵심은 RAG를 단순 API 기능이 아니라 **Agent가 호출 가능한 LangChain 기반 검색 도구 후보**로 바꾼 것입니다.
