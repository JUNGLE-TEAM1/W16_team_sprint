# 조선왕조실록 AI 게시판

조선왕조실록 XML 원문을 PostgreSQL에 저장하고, 사용자의 역사 질문 게시글과 관련된 실록 원문을 RAG로 검색한 뒤, LLM이 원문 근거 기반의 초벌 요약과 해석을 생성하는 AI 게시판 서비스입니다.

단순 챗봇이 아니라, 사용자가 질문 게시글을 작성하고 다른 사용자와 댓글로 토론할 수 있는 게시판 형태의 웹 애플리케이션을 목표로 합니다.

## 1. 사용자 문제

한국사 학습자와 역사 콘텐츠 작성자는 다음 문제를 겪습니다.

- 조선왕조실록 원문은 양이 많아 필요한 기사를 찾기 어렵습니다.
- 원문이 한문 중심이라 검색 결과의 맥락을 바로 이해하기 어렵습니다.
- 일반 LLM에 질문하면 답변의 원문 근거를 확인하기 어렵습니다.
- 역사 토론을 할 때 신뢰할 만한 근거 자료를 함께 보기 어렵습니다.

## 2. 핵심 가치

이 서비스는 사용자가 역사 질문 글을 작성하는 순간 관련 실록 원문을 함께 찾고, AI가 해당 원문만 근거로 초벌 요약과 쉬운 해석을 제공합니다.

핵심 장면은 다음과 같습니다.

```text
사용자 질문 게시글 작성
→ 관련 조선왕조실록 원문 검색
→ MCP tool로 원문 기사 조회
→ LLM이 원문 기반 초벌 요약/해석 생성
→ 추천 태그와 근거 기사 저장
→ 게시글 상세 화면에서 근거 기반 토론
```

## 3. 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Frontend | React, Vite, lucide-react |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL, pgvector |
| LLM | OpenAI API |
| Embedding | OpenAI `text-embedding-3-small` |
| RAG | PostgreSQL 원본 기사 + pgvector chunk 검색 |
| MCP | FastMCP 기반 실록 기사 조회 tool |
| Agent | 질문 분석, 검색, MCP 조회, reranking, 답변 생성 workflow |

## 4. 현재 구현된 기능

### 게시판 기능

- 회원가입
- 로그인
- 게시글 작성
- 게시글 목록 조회
- 게시글 상세 조회
- 게시글 제목 수정
- 게시글 삭제
- 댓글 작성
- 댓글 조회
- 게시글 검색
- 페이징
- 태그 필터
- AI 토론 도우미 스트리밍
- Realtime 음성 토론 모드

### AI 기능

- 조선왕조실록 XML `level5` 기사 파싱
- 원본 기사 저장
- 검색용 chunk 생성
- OpenAI embedding 생성
- pgvector 기반 벡터 유사도 검색
- 키워드 검색을 함께 사용하는 hybrid search
- 질문 기반 metadata filter
- 검색용 query rewrite
- LLM 기반 근거 reranking
- LLM 기반 초벌 요약/해석 생성
- AI 추천 태그 생성
- MCP tool을 통한 실록 기사 조회
- Agent trace 저장
- 게시글 근거와 댓글 맥락 기반 AI 토론 답변 스트리밍
- WebRTC 기반 마이크 입력 및 AI 음성 응답

## 5. 아키텍처

상세 Mermaid 다이어그램은 [`docs/architecture.md`](docs/architecture.md)에 정리되어 있습니다.

```text
React
  └─ 사용자가 글 작성 / 목록 조회 / 댓글 작성 / 태그 클릭

FastAPI
  ├─ Auth API
  ├─ Post API
  ├─ Comment API
  ├─ Search API
  └─ Agent workflow

Agent workflow
  ├─ 질문 분석
  ├─ metadata filter 추출
  ├─ 검색용 query rewrite
  ├─ RAG hybrid search
  ├─ MCP tool로 원문 기사 조회
  ├─ LLM reranking
  ├─ LLM 요약/해석 생성
  └─ 태그 추천

AI discussion stream
  ├─ 게시글 질문/요약/해석 조회
  ├─ 실록 근거 기사 조회
  ├─ 댓글 맥락 포함
  └─ SSE 방식으로 AI 답변 조각 전송

Realtime voice discussion
  ├─ React가 마이크 권한 요청
  ├─ WebRTC offer SDP 생성
  ├─ FastAPI가 OpenAI Realtime 세션 생성
  ├─ OpenAI Realtime API와 WebRTC 연결
  └─ 사용자 음성 입력과 AI 음성 출력 처리

PostgreSQL + pgvector
  ├─ users
  ├─ posts
  ├─ comments
  ├─ annals_articles
  └─ annals_chunks
```

## 6. 데이터베이스 구조

### `users`

회원 정보를 저장합니다.

```text
id
username
password_hash
created_at
```

### `posts`

질문 게시글과 AI 결과를 함께 저장합니다.

```text
id
user_id
title
question
ai_summary
ai_interpretation
suggested_tags
evidence_article_ids
agent_trace
created_at
updated_at
```

### `comments`

게시글에 달린 댓글을 저장합니다.

```text
id
post_id
user_id
content
created_at
updated_at
```

### `annals_articles`

조선왕조실록 원본 기사를 보존하는 테이블입니다.

```text
article_id
source_file
title
king
reign_date
date
content
official_url
subject_classes
```

### `annals_chunks`

RAG 검색을 위한 chunk와 embedding vector를 저장합니다.

```text
chunk_id
article_id
chunk_index
chunk_text
embedding
embedding_model
token_count_estimate
```

현재 구조에서 `annals_articles`는 신뢰할 수 있는 원본 저장소이고, `annals_chunks`는 원본을 더 잘 찾기 위한 검색 색인입니다.

## 7. RAG 설명

RAG는 사용자의 질문을 LLM에 바로 보내지 않고, 먼저 관련 실록 원문을 검색한 뒤 그 원문을 LLM 입력에 붙이는 구조입니다.

이 프로젝트의 RAG 흐름은 다음과 같습니다.

```text
조선왕조실록 XML
→ level5 기사 단위 파싱
→ annals_articles에 원본 저장
→ 검색용 chunk 생성
→ OpenAI embedding 생성
→ annals_chunks에 vector 저장
→ 사용자 질문 embedding
→ pgvector 유사도 검색
→ keyword search와 결합
→ 관련 article_id 확보
→ 원문 기사 조회
→ LLM 프롬프트에 근거로 제공
```

검색은 벡터 검색만 사용하지 않고, 키워드 검색도 함께 사용하는 hybrid search 방식입니다. 예를 들어 `왕자의 난`처럼 역사적으로 중요한 표현은 벡터 유사도만으로 놓칠 수 있기 때문에, 키워드 점수도 함께 반영합니다.

## 8. MCP 설명

MCP는 Agent가 외부 도구 또는 내부 도구를 일정한 형식으로 호출할 수 있게 해주는 도구 인터페이스입니다.

현재 구현한 MCP tool은 하나입니다.

```text
get_annals_article(article_id)
```

역할:

```text
article_id를 입력받아
PostgreSQL의 annals_articles에서
실록 원문 기사와 공식 URL을 조회한다.
```

현재는 단순한 원문 조회 tool이지만, 과제 관점에서는 Agent가 직접 내부 함수를 호출하는 대신 MCP tool 인터페이스를 통해 원문 조회 도구를 사용하는 구조를 보여줍니다.

## 9. Agent 설명

이 프로젝트의 Agent는 FastAPI 서버 안에서 실행되는 게시글 생성 workflow입니다.

현재 Agent는 완전히 자유롭게 행동하는 범용 Agent가 아니라, 게시글 생성이라는 목적에 맞춘 고정된 추론 흐름입니다.

```text
1. 사용자 질문 분석
2. metadata filter 추출
3. 검색용 query rewrite
4. RAG hybrid search 실행
5. MCP tool로 원문 기사 조회
6. LLM reranking으로 관련 근거 선별
7. LLM으로 요약/해석 생성
8. 추천 태그 생성
9. agent_trace 저장
```

`agent_trace`에는 Agent가 어떤 단계를 거쳤는지 기록합니다.

예:

```text
question_analysis
rag_search
mcp_tool_lookup
evidence_rerank
llm_draft
tag_recommendation
```

이를 통해 사용자는 AI가 어떤 근거를 찾고 어떤 과정을 거쳐 답변을 만들었는지 추적할 수 있습니다.

## 10. 주요 API

### 인증

```text
POST /auth/register
POST /auth/login
```

### 게시글

```text
POST /posts
GET /posts
GET /posts/{post_id}
PUT /posts/{post_id}
DELETE /posts/{post_id}
```

`GET /posts`는 검색, 태그 필터, 페이징을 지원합니다.

```text
GET /posts?q=태조&page=1&size=10
GET /posts?tag=왕자의 난&page=1&size=10
```

### 댓글

```text
POST /posts/{post_id}/comments
```

게시글 상세 조회 응답에 댓글 목록이 함께 포함됩니다.

### AI 토론 도우미

```text
POST /posts/{post_id}/ai-discussion/stream
```

게시글의 기존 질문, AI 요약/해석, 실록 원문 근거, 댓글 맥락을 바탕으로 AI 토론 답변을 생성하고 SSE 방식으로 조각 단위 응답을 전송합니다.

### Realtime 음성 토론

```text
POST /posts/{post_id}/realtime/session
```

브라우저가 만든 WebRTC offer SDP를 FastAPI에 보내면, FastAPI가 OpenAI Realtime API와 세션을 생성하고 answer SDP를 반환합니다. 브라우저는 이 SDP로 Realtime 모델과 연결되어 마이크 음성을 보내고 AI 음성 답변을 재생합니다.

### 실록 검색

```text
GET /annals/search?query=태조 즉위&limit=3
```

## 11. 실행 방법

### 1. RAG 데이터 bundle

이 저장소에는 애플리케이션 코드와 실행용 RAG bundle을 함께 둡니다.

```text
data/annals_private_bundle.zip
```

`data/annals_private_bundle.zip`에는 미리 계산된 RAG 데이터가 들어갑니다.

```text
manifest.json
annals_articles.jsonl
annals_chunks.jsonl
```

`annals_chunks.jsonl`에는 OpenAI embedding이 이미 포함되어 있으므로 팀원이 XML 전체를 다시 파싱하거나 embedding을 다시 만들 필요가 없습니다.

### 2. 팀원 실행

```bash
cp .env.example .env
```

`.env`에 OpenAI API key를 넣습니다. API key가 없어도 게시판 화면과 키워드 검색 fallback은 뜨지만, 게시글 작성 시 LLM 답변과 벡터 검색 품질은 제한됩니다.

```text
OPENAI_API_KEY=...
```

그 다음 한 번에 실행합니다.

```bash
docker compose up --build
```

기본 접속 주소:

```text
http://127.0.0.1:5173
```

백엔드 컨테이너는 시작할 때 `data/annals_private_bundle.zip`을 찾습니다. zip이 있으면 `annals_articles`와 `annals_chunks`를 PostgreSQL에 자동 복원하고, 이미 복원된 데이터가 있으면 다시 import하지 않습니다.

zip을 바꿔서 다시 넣고 싶다면 DB volume을 지우고 다시 실행합니다.

```bash
docker compose down -v
docker compose up --build
```

### 3. 개발 모드로 따로 실행

```bash
docker compose up -d postgres
```

이 프로젝트는 `pgvector/pgvector:pg16` 이미지를 사용합니다.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.import_private_bundle --skip-missing --skip-if-present
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

프론트엔드는 별도 터미널에서 실행합니다.

```bash
cd frontend
npm install
npm run dev
```

### 4. 비공개 RAG bundle 만들기

로컬 DB에 `annals_articles`와 `annals_chunks`가 이미 seed되어 있다면 다음 명령으로 팀 공유용 zip을 만들 수 있습니다.

```bash
cd backend
source .venv/bin/activate
python -m scripts.export_private_bundle --output ../data/annals_private_bundle.zip
```

전체 XML에서 새로 seed해야 할 때는 OpenAI API key가 필요합니다.

```bash
cd backend
source .venv/bin/activate
python -m scripts.seed_annals --xml-file "/path/to/2nd_waa_101.xml" --limit 100
python -m scripts.export_private_bundle --output ../data/annals_private_bundle.zip
```

embedding 없이 XML 파싱과 원본 저장만 먼저 확인하려면 다음 명령을 사용할 수 있습니다.

```bash
python -m scripts.seed_annals --limit 10 --skip-embeddings
```

## 12. 테스트 방법

### 백엔드 테스트

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

### 백엔드 문법 확인

```bash
cd backend
source .venv/bin/activate
python -m compileall app
```

### 프론트엔드 빌드 확인

```bash
cd frontend
npm run build
```

## 13. 예시 사용 흐름

1. 회원가입 또는 로그인합니다.
2. 질문 게시글을 작성합니다.
3. FastAPI가 게시글 생성 요청을 받습니다.
4. Agent가 질문을 분석하고 검색용 문장을 만듭니다.
5. RAG가 관련 실록 기사를 검색합니다.
6. MCP tool이 article_id로 원문 기사를 조회합니다.
7. LLM이 근거 기반 초벌 요약과 해석을 생성합니다.
8. 추천 태그와 근거 기사 ID가 게시글에 저장됩니다.
9. 상세 화면에서 AI 답변, 근거 원문, 댓글을 확인합니다.
10. 태그를 눌러 같은 주제의 게시글을 필터링합니다.
11. AI 토론 도우미에 후속 질문을 입력하고 스트리밍 답변을 확인합니다.
12. 음성 토론 모드에서 마이크로 질문하고 AI 음성 답변을 듣습니다.

## 14. 현재 한계

- 로그인은 학습용 최소 구현이며 JWT 기반 인증은 아직 적용하지 않았습니다.
- 게시글 수정은 현재 제목 수정만 지원합니다.
- 댓글 수정/삭제는 아직 없습니다.
- AI 토론 도우미 대화 내용은 아직 DB에 저장하지 않습니다.
- Realtime 음성 대화 내용은 아직 DB에 저장하지 않습니다.
- 전체 조선왕조실록 데이터가 항상 seed되어 있다고 가정하지 않습니다.
- 검색 품질은 seed된 XML 범위와 chunk 전략에 크게 영향을 받습니다.
- Agent는 고정 workflow 기반이며, 완전한 LangGraph 스타일의 자유로운 tool 선택 loop는 아직 아닙니다.
- MCP tool은 현재 실록 기사 조회 하나만 제공합니다.

## 15. 다음 개선 방향

- JWT 또는 세션 기반 인증 추가
- 게시글/댓글 권한 체크 강화
- 댓글 수정/삭제 추가
- 전체 실록 XML 대상 seed와 embedding batch 처리
- 긴 기사에 대한 문단/문장 단위 chunk 전략 개선
- MCP tool 추가: 왕대별 검색, 공식 URL 검증, 연도별 기사 조회
- Agent 상태 관리와 tool 선택 loop 고도화
- README 기반 발표 자료 작성
