# Sprint 4 Summary

Date: 2026-06-15

## 1. Sprint 목표

Sprint 4의 목표는 게시판 데이터와 연결된 RAG 기능을 구현하는 것이다.

구현된 흐름:
- 게시글 작성/수정 후 `title`, `content`, `tags`를 embedding한다.
- embedding 결과를 `post_embeddings` 별도 테이블에 저장한다.
- 작성 화면에서 입력 중인 글 기준으로 유사 게시글을 검색한다.
- 유사도 점수와 등급을 보여준다.
- 로컬 LLM provider인 Ollama로 검색 결과 요약을 생성한다.
- LLM provider 실패 시에도 유사 게시글 목록은 반환한다.

## 2. 완료 기준

완료:
- 게시글 제목/본문/태그 embedding 입력 구성
- pgvector extension 준비 코드
- `post_embeddings` 테이블 모델
- 게시글당 최신 embedding row upsert
- embedding 실패 상태와 `last_error` 기록
- `POST /api/v1/ai/similar-posts` 추천 API
- `similarity`, `similarity_level`, `summary`, `summary_error` 응답
- React 작성 화면의 유사 글 찾기 버튼과 결과 표시
- README의 pgvector, embedding model, Ollama 실행 안내

부분 확인:
- PostgreSQL/pgvector 실제 통합 테스트는 Docker daemon이 실행 중이지 않아 수행하지 못했다.

## 3. 완료된 Decision

| ID | 결정 | 결과 | Implementation |
| --- | --- | --- | --- |
| D-026 | 로컬 embedding model과 vector dimension | `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimension | Completed |
| D-027 | `post_embeddings` schema | 게시글당 최신 embedding row 1개 | Completed |
| D-028 | embedding 실패 처리 | 게시글 저장은 rollback하지 않고 실패 상태 기록 | Completed |
| D-029 | 유사 게시글 추천 API 계약 | `POST /api/v1/ai/similar-posts` preview API | Completed |
| D-030 | RAG 검색 결과 요약 방식 | 로컬 LLM provider 실제 연동 | Completed |
| D-031 | 로컬 LLM provider와 기본 model | Ollama + `qwen2.5:3b` | Completed |

## 4. 구현 결과

Backend:
- `PostEmbedding` 모델 추가
- `PostEmbeddingRepository` 추가
- `EmbeddingProvider`, `LocalSentenceTransformerEmbeddingProvider`, `HashEmbeddingProvider` 추가
- `OllamaSummaryProvider`, `FakeSummaryProvider` 추가
- `RagService` 추가
- `POST /api/v1/ai/similar-posts` 추가
- 게시글 작성/수정 후 embedding sync 연결
- embedding 실패 시 `failed` 상태와 `last_error` 기록

Frontend:
- 작성 화면에 유사 글 찾기 버튼 추가
- AI 요약과 유사 게시글 목록 표시
- 유사도 점수와 `high`, `medium`, `low` 등급별 강조 표시

Docs:
- README에 Sprint 4 RAG 실행 안내 추가
- Decision Harness의 Pass 후 다음 분기 제시 규칙 보강
- Sprint 4 Decision D-026~D-031 완료 처리

## 5. 테스트 결과

실행 완료:

```bash
python -m pytest backend/tests/test_post_service_di.py
python -m compileall backend/app
cd frontend && npm test
cd frontend && npm run build
```

결과:
- `backend/tests/test_post_service_di.py`: 3 passed
- `python -m compileall backend/app`: 성공
- frontend test: 1 passed
- frontend build: 성공

실행하지 못한 테스트:

```bash
docker compose up -d db
python -m pytest backend/tests
```

이유:
- Docker daemon이 실행 중이지 않아 `pgvector/pgvector:pg16` 컨테이너를 시작할 수 없었다.
- 오류: Docker socket 연결 실패

## 6. 낮아진 후보

Level 2로 낮춰 구현한 항목:
- similarity 기본값: `high >= 0.8`, `medium >= 0.6`
- 추천 기본 개수: `limit=3`, 최대 `5`
- Ollama timeout 기본값: `20초`
- LLM 요약 실패 시 fallback summary와 `summary_error` 반환
- 추천 preview API 인증 적용: 로그인 사용자만 호출 가능

## 7. 다음 Sprint로 넘길 항목

Sprint 5로 넘길 항목:
- MCP Server 구현
- JSON-RPC request/response 구현
- GitHub Issue 조회 tool 구현
- 외부 호출 실패 처리
- MCP 결과를 게시글 작성 흐름에 연결

후속 고도화 후보:
- embedding 실패 row 재시도 API 또는 관리 명령
- 반복 실패 시 degraded 또는 점검 모드
- chunk 기반 RAG
- RAG 검색 품질 평가
- Agent에서 RAG summary provider 재사용

## 8. 발표용 한 문장

Sprint 4에서는 게시글 작성 중 입력한 제목, 본문, 태그를 embedding해 기존 게시글과 비교하고, 유사도 점수와 로컬 LLM 요약으로 중복 가능성을 확인하는 RAG preview 흐름을 구현했다.
