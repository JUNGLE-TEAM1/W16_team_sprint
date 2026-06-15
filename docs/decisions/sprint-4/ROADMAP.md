# Sprint 4 Decision Roadmap

Date: 2026-06-15

## 1. Sprint 목표

Sprint 4의 목표는 Sprint 3.5에서 확정한 설계를 바탕으로 게시판 데이터와 연결된 RAG 기능을 구현하는 것이다.

핵심 흐름:
- 게시글 작성/수정 성공 후 `title`, `content`, `tags`를 embedding한다.
- embedding 결과를 `post_embeddings` 별도 테이블에 저장한다.
- 글 작성 화면에서 유사 게시글을 검색한다.
- 검색 결과 top-N과 요약을 사용자에게 보여준다.
- AI 결과는 자동 저장하지 않고 사용자가 확인해야 작성 폼에 반영한다.

## 2. 완료 기준

- 게시글 제목/본문/태그를 embedding한다.
- pgvector를 사용할 수 있는 DB 구조가 준비되어 있다.
- PostgreSQL에 embedding 결과를 저장한다.
- 새 글 작성 내용과 유사한 게시글을 검색한다.
- 유사 게시글 top 3 또는 top 5를 보여준다.
- LLM 또는 로컬 모델이 검색 결과를 요약한다.
- 프론트엔드에서 추천 결과를 확인할 수 있다.
- README 또는 sprint note에 RAG 구조를 설명할 수 있다.

## 3. 이전 Sprint에서 이미 확정된 기반

Sprint 3.5 Decision 결과:
- AI 사용자 흐름: 글 작성 시 유사 게시글 추천 + 중복 게시글 방지
- RAG 데이터 범위: 게시글 `title`, `content`, `tags`
- Embedding 저장 위치: `post_embeddings` 별도 테이블
- Embedding 생성 시점: 게시글 작성/수정 성공 후 생성 또는 갱신
- Provider 기준: 로컬 또는 오픈소스 model 우선, 테스트는 fake provider
- MCP MVP: `fetch_github_issue`
- Agent 역할: RAG/MCP를 사용하는 글쓰기 도우미
- AI 결과 저장 정책: 미리보기 반환 후 사용자 확인 반영

## 4. 후보 분기 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 로컬 embedding model과 vector dimension을 무엇으로 둘 것인가? | Level 3 | Pending | Sprint 3.5 D-022 |
| 2 | C2 | pgvector extension과 `post_embeddings` schema를 어떻게 정의할 것인가? | Level 3 | Pending | C1, Sprint 3.5 D-020 |
| 3 | C3 | embedding provider 실패 시 게시글 작성/수정 API는 어떻게 응답할 것인가? | Level 3 | Pending | C1, C2 |
| 4 | C4 | 유사 게시글 추천 API 계약을 어떻게 둘 것인가? | Level 3 | Pending | C2 |
| 5 | C5 | similarity threshold와 top-N 기본값을 어떻게 둘 것인가? | Level 2 또는 3 | Pending | C4 |
| 6 | C6 | RAG 결과 요약을 어느 provider로 생성할 것인가? | Level 3 | Pending | C1, C4 |
| 7 | C7 | 작성 화면에서 유사 글 찾기 UI를 어떻게 배치할 것인가? | Level 2 | Pending | C4 |
| 8 | C8 | fake provider와 테스트 DB 전략을 어떻게 구성할 것인가? | Level 2 또는 3 | Pending | C1, C2 |

## 5. 예상 첫 Decision

예상 첫 후보:
- C1. 로컬 embedding model과 vector dimension을 무엇으로 둘 것인가?

이유:
- vector dimension이 정해져야 pgvector 컬럼 schema를 정의할 수 있다.
- embedding model이 정해져야 테스트 fixture와 fake provider shape를 안정적으로 만들 수 있다.
- D-022에서 로컬 또는 오픈소스 model 우선만 확정했고, 구체 model은 후속 분기로 남겼다.

## 6. 의존성

- C1이 C2의 schema를 막는다.
- C2가 C4 추천 API 구현을 막는다.
- C3는 게시글 작성/수정 API의 실패 처리와 테스트 기대값을 바꿀 수 있다.
- C4가 C5와 C7의 입력이 된다.
- C6은 로컬 LLM 성능과 fallback 여부에 따라 Level 3로 유지될 수 있다.

## 7. 이번 선택으로 자동 확정하지 않는 것

Sprint 3.5에서 큰 방향은 확정했지만, Sprint 4에서는 다음을 자동 확정하지 않는다.

- 구체적인 로컬 embedding model
- vector dimension
- `post_embeddings.metadata` 구조
- provider 실패 응답 방식
- similarity threshold
- top-3 또는 top-5 기본값
- RAG 요약 prompt
- 프론트엔드 UI 문구와 배치

## 8. 구현 가능 조건

Sprint 4 구현 전 최소 필수 Decision:
- 로컬 embedding model과 vector dimension
- `post_embeddings` schema
- embedding 실패 처리
- 유사 게시글 추천 API 계약

필수 Level 3 결정이 모두 Pass된 뒤 Implementation Batch Snapshot을 기록하고 구현한다.

## 9. Implementation Batch Snapshot

Date: 2026-06-15

### 현재 git status

```text
 M .gitignore
 M AGENTS.md
 M DECISION_HARNESS.md
 M backend/app/api/dependencies.py
 M backend/app/api/v1/auth.py
 M backend/app/api/v1/posts.py
 M backend/app/models/__init__.py
 M backend/app/models/post.py
 M backend/app/repositories/post_repository.py
 M backend/app/schemas/auth.py
 M backend/app/schemas/post.py
 M backend/app/services/auth_service.py
 M backend/app/services/post_service.py
 M backend/tests/test_auth_security_flow.py
 M backend/tests/test_post_service_di.py
 M backend/tests/test_posts_flow.py
 M docs/decisions/DECISIONS.md
 M docs/decisions/decision-harness-flow.md
 M docs/decisions/sprint-1/ROADMAP.md
 M docs/decisions/sprint-1/decisions/D-006-post-user-id.md
 M docs/decisions/sprint-1/decisions/D-007-author-name-retention.md
 M docs/taejung/development-order.md
?? backend/app/models/comment.py
?? backend/app/models/tag.py
?? backend/app/repositories/comment_repository.py
?? backend/app/schemas/comment.py
?? backend/app/services/comment_service.py
?? backend/tests/test_comment_service_di.py
?? backend/tests/test_comments_flow.py
?? docs/decisions/sprint-1/SUMMARY.md
?? docs/decisions/sprint-1/decisions/D-008-registration-api-contract.md
?? docs/decisions/sprint-2/
?? docs/decisions/sprint-3/
?? docs/decisions/sprint-3.5/
?? docs/decisions/sprint-4/
?? docs/taejung/reference/
?? frontend/
```

### 수정 예정 파일

- `docker-compose.yml`: pgvector extension 사용 가능한 PostgreSQL image로 보정
- `requirements.txt`: `pgvector`, `sentence-transformers` 의존성 추가
- `backend/app/core/config.py`: embedding/LLM 설정 추가
- `backend/app/main.py`: pgvector extension 준비와 model import 보강
- `backend/app/models/post_embedding.py`: `post_embeddings` 모델 추가
- `backend/app/models/__init__.py`: 모델 export 추가
- `backend/app/repositories/post_embedding_repository.py`: embedding upsert/search 추가
- `backend/app/services/embedding_provider.py`: local/fake embedding provider 추가
- `backend/app/services/summary_provider.py`: Ollama/fake summary provider 추가
- `backend/app/services/rag_service.py`: 유사 게시글 추천 orchestration 추가
- `backend/app/services/post_service.py`: 게시글 작성/수정 후 embedding sync 추가
- `backend/app/api/dependencies.py`: RAG 관련 dependency 추가
- `backend/app/api/v1/ai.py`: 추천 API 추가
- `backend/app/schemas/rag.py`: 추천 API request/response 추가
- `backend/tests/test_rag_flow.py`: RAG API와 실패 처리 테스트 추가
- `frontend/src/api.ts`: 추천 API client/type 추가
- `frontend/src/App.tsx`: 작성 화면 유사 글 찾기 UI 추가
- `frontend/src/styles.css`: 추천 결과 표시 스타일 추가
- `frontend/src/App.test.tsx`: Sprint 4 UI smoke test 보강
- `README.md`: Sprint 4 RAG 실행 설명 추가
- `docs/decisions/sprint-4/SUMMARY.md`: Sprint 4 구현 결과 기록

### 기존 사용자 변경 여부

- `backend/app/api/dependencies.py`, `backend/app/models/__init__.py`, `backend/app/services/post_service.py`, `backend/app/schemas/post.py`, `frontend/` 전체는 이미 변경 또는 미추적 상태다.
- 이 변경들은 사용자 또는 이전 스프린트 작업물로 보고 되돌리지 않는다.
- Codex는 Sprint 4 RAG 구현에 필요한 범위만 추가 편집한다.

### Codex 변경 범위

- RAG embedding 저장, similarity search, summary API, frontend preview UI, 테스트, 문서만 변경한다.
- 기존 인증, 댓글, 태그, 검색, 페이징 동작은 유지한다.

### 롤백 시 되돌릴 범위

- 새로 추가한 RAG 모델/레포지토리/서비스/API/schema/test 파일
- `post_service.py`의 embedding sync 연결부
- `dependencies.py`, `main.py`, `models/__init__.py`의 RAG 연결부
- frontend의 유사 글 추천 UI/API client 추가분
- `requirements.txt`, `docker-compose.yml`, README의 Sprint 4 추가분
- Sprint 4 Decision의 Implementation 상태 갱신분

### 롤백 확인 명령 또는 테스트

```bash
python -m pytest backend/tests
cd frontend && npm test -- --run
cd frontend && npm run build
```
