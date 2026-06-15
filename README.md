# W16 팀 스프린트

팀 스프린트 학습을 위한 저장소입니다.

이 레포는 나만무 프로젝트를 시작하기 전에 팀원들이 같은 기술 언어로 의사결정할 수 있도록, 핵심 학습 주제와 산출물을 정리하고 공유하는 공간입니다. 목표는 모든 사람이 모든 영역을 같은 깊이로 아는 것이 아니라, 회의에서 막히지 않을 정도의 공통 이해를 맞추는 것입니다.

## 학습 기준

학습 주제는 단순히 "중요해 보이는가"가 아니라 아래 기준으로 고릅니다.

- 나중에 알면 구조를 크게 바꿔야 하는가
- 프론트엔드, 백엔드, DB, AI 기능이 함께 영향을 받는가
- 팀원이 같은 말을 이해하지 못하면 의사결정이 느려지는가
- 실패했을 때 보안, 데이터, 일정, 품질에 치명적인가
- 1-2시간 학습 후, 30분-1시간 싱크로 공통 이해를 만들 수 있는가

## 우선 학습 주제

1. API 계약 + 도메인/데이터 모델링 + 요청 흐름
2. 인증/인가 + 보안 기본
3. 프로젝트 구조/아키텍처 + 에러 처리/로깅/설정
4. 프론트엔드-백엔드 연결 방식 + 상태 관리
5. AI/RAG/LLM 기능 흐름
6. 비동기 처리/캐싱/실시간/신뢰성

AI 기능이 프로젝트의 핵심 가치라면 `AI/RAG/LLM 기능 흐름`은 2순위까지 올립니다. 반대로 비동기 처리, 캐싱, 실시간 기능은 실제 요구사항이 있을 때 깊게 다룹니다.

## 첫 번째 스프린트

첫 주제는 API 계약과 데이터 흐름입니다.

핵심 질문은 다음과 같습니다.

> 하나의 핵심 기능이 실행될 때, 프론트 요청부터 백엔드 처리, DB 저장, 응답과 에러 처리까지 어떤 흐름으로 지나가는가?

현재 저장소에는 작은 `posts` API 예제가 구현되어 있습니다. 이 예제의 목적은 아래 흐름을 코드로 확인하는 것입니다.

```text
클라이언트 요청 -> API 라우터 -> 검증/스키마 -> 서비스 -> 레포지토리 -> DB -> 응답/에러
```

## 스프린트 산출물

각 스프린트가 끝나면 최소 하나 이상의 산출물을 남깁니다.

- 예시 기능의 요청 흐름
- API endpoint 초안
- request/response 예시
- error response 형식
- 필요한 DB 테이블과 관계
- 인증 또는 권한 처리 기준
- 프로젝트 폴더 구조 초안
- 체크리스트
- 아직 결정하지 못한 질문 목록
- ADR 초안

## 완료 기준

각 주제는 팀원들이 아래 질문에 답할 수 있을 때 완료로 봅니다.

1. 이 개념은 무엇인가?
2. 왜 필요한가?
3. 어떤 선택지가 있는가?
4. 선택지별 장단점은 무엇인가?
5. 우리 프로젝트에서는 언제 필요할 가능성이 높은가?
6. 프론트엔드, 백엔드, DB, AI 중 어디에 영향을 주는가?
7. 나중에 더 깊게 팔 담당자는 누구인가?
8. 지금 팀 차원에서 합의할 기본값은 무엇인가?

## 운영 원칙

지금은 지식을 많이 쌓는 시간이 아니라 팀의 의사결정 언어를 맞추는 시간입니다.

따라서 학습은 긴 발표보다 짧은 개인 학습, 핵심 요점 공유, 질문 정리, 팀 합의 산출물 작성에 집중합니다. 매 스프린트의 목표는 "좋은 이야기를 했다"가 아니라, 다음 구현 의사결정에 바로 쓸 수 있는 기준을 남기는 것입니다.

## 실행 방법

```bash
cp .env.example .env
docker compose up -d db
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --env-file .env
```

기본 DB는 PostgreSQL입니다. `.env.example`의 `DATABASE_URL`은 `docker-compose.yml`로 실행되는 로컬 PostgreSQL 컨테이너를 가리킵니다.

API 문서는 아래 주소에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

## 테스트 방법

테스트도 같은 PostgreSQL DB를 사용합니다.

```bash
docker compose up -d db
./.venv/bin/python -m pytest backend/tests
```

## 요청 예시

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"스프린트 1","content":"API와 DB 흐름","author_name":"team1"}'
```

```bash
curl http://127.0.0.1:8000/api/v1/posts
```

```bash
curl http://127.0.0.1:8000/api/v1/posts/1
```

## 문서

- [학습 우선순위 정리](learning-priorities.md)
- [스프린트 1 파일 구조](docs/sprint-1-file-structure.md)
- [스프린트 1 API 데이터 흐름](docs/sprint-1-api-data-flow.md)
## Sprint 로드맵 업데이트

- Sprint 1은 API 계약, 데이터 흐름, 기본 구조를 이미 진행한 기준 스프린트로 둡니다.
- Sprint 2는 회원가입/로그인과 인증/인가를 구현 완료형 기준으로 둡니다.
- Sprint 3 아키텍처/프로젝트 구조는 별도 이론 스프린트로 크게 잡지 않고, 기능 구현 중 `router/service/repository/schema/model`로 계속 적용합니다.
- Sprint 4 프론트-백엔드 연결은 모든 기능 스프린트의 완료 기준에 포함합니다.
- 기준: API만 끝나면 미완료. React 화면에서 실제로 사용할 수 있어야 완료.
- 전체 기준은 [Sprint 로드맵](docs/sprint-roadmap.md)을 참고하세요.
## Sprint 6 RAG 구현

이번 RAG는 MCP/Agent 없이 게시판 내부 데이터만 사용합니다.

구조:

```text
글 작성/수정
-> title + content + tag 텍스트를 embedding
-> post_embeddings 테이블에 vector_json으로 저장
-> 글 작성 폼의 RAG duplicate check 버튼
-> POST /api/v1/rag/assist
-> 현재 초안 embedding과 기존 글 embedding 유사도 계산
-> 유사 게시글, 중복 위험도, 간단 요약/추천 문구 반환
-> React 화면에 결과 표시
```

현재 구현은 embedding으로 후보 글을 찾은 뒤 OpenAI Responses API의 LLM으로 추천 문구와 후보별 요약을 생성합니다. `OPENAI_API_KEY`가 없는 로컬 테스트 환경에서만 deterministic embedding과 규칙 기반 요약 fallback을 사용합니다. 나중에 pgvector를 붙이면 `post_embeddings.vector_json` 저장 방식과 `RagService`의 similarity 계산 부분을 교체하면 됩니다.

## OpenAI API 설정

RAG 임베딩은 `.env`에서 OpenAI API 사용 준비가 되어 있습니다.

```env
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
OPENAI_LLM_MODEL=gpt-4o-mini
OPENAI_LLM_MAX_OUTPUT_TOKENS=700
OPENAI_TIMEOUT_SECONDS=20
```

`OPENAI_API_KEY`가 비어 있으면 로컬 hash embedding과 규칙 기반 추천으로 fallback됩니다. API 키를 넣고 서버를 다시 실행하면 `POST /api/v1/rag/assist`가 OpenAI embedding API와 OpenAI Responses API 기반 LLM 추천을 사용합니다.

기존에 64차원 로컬 벡터가 저장되어 있어도, OpenAI 1536차원 설정으로 바뀌면 RAG 실행 시 기존 게시글 임베딩을 자동으로 다시 생성합니다.
