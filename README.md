# AI 생활지원 매칭 보드

공공데이터 기반으로 사용자의 상황에 맞는 복지정책, 청년지원, 공공시설, 생활 인프라를 찾아주는 AI 상담 보드입니다.

기존 게시판 구조를 유지하되 `Post`는 `data-bot`이 적재한 지원 카드 중심으로 재해석합니다. 사용자가 입력한 현재 상황은 저장하지 않는 일회성 RAG/Agent 요청으로만 처리합니다. `Tag`는 청년, 주거, 취업, 복지시설 같은 조건 필터가 되고, RAG는 사용자의 현재 상황과 미리 적재된 생활지원 카드를 매칭합니다.

## 현재 컨셉

- 서비스명: AI 생활지원 매칭 보드
- 사용자 입력: "서울 거주 24세 취준생, 월세 60만 원, 소득 없음. 받을 수 있는 지원 있나요?" 같은 일회성 매칭 요청
- AI 결과: 청년월세, 취업지원, 복지시설, 신청 체크리스트, 상담 경로
- 데이터: `data-bot`이 등록한 공공데이터 기반 지원 카드 50개 seed
- 확장: 공공데이터포털, 온통청년, 서울 열린데이터광장 CSV/API 행을 `Post` 카드로 변환 가능

## DB 목표 구조와 v1 매핑

장기 목표는 역할별 테이블을 분리하는 것입니다.

- `support_cards`: 공공데이터 API/CSV에서 가져온 지원 정책, 복지시설, 생활 인프라 카드
- `consultation_cases`: 사용자가 입력한 상담 상황. v1에서는 저장하지 않고, 이후 필요할 때 별도 테이블로 분리
- `data_sources`: 공공데이터포털, 온통청년, 서울 열린데이터광장, 복지로 같은 API/URL 출처
- `tags`: 청년, 주거, 취업, 복지시설, 마포구 같은 분류
- `embeddings`: AI 매칭용 벡터

v1에서는 새 마이그레이션 없이 기존 구현과 충돌을 줄이기 위해 아래처럼 매핑합니다.

- `support_cards` -> `posts` 중 `author_name="data-bot"`인 지원 카드
- `consultation_cases` -> v1에서는 DB에 저장하지 않음. 프론트 입력값은 RAG/Agent 요청 본문으로만 전송
- `data_sources` -> 카드 본문 안의 `출처 URL`과 RAG 요청의 `reference_urls`
- `tags` -> 기존 `tags`, `post_tags`
- `embeddings` -> 기존 `post_embeddings`. v1에서는 `data-bot` 지원 카드만 저장하고 사용자 매칭 요청은 저장하거나 query embedding으로 만들지 않음

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
  -d '{"title":"서울 청년 월세 상담","content":"서울 거주 24세 취준생이고 월세 60만 원을 내고 있습니다.","tag_names":["청년","주거","서울"]}'
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
## AI 생활지원 RAG 구현

RAG는 게시판 내부 지원 카드와 MCP/외부 참고자료를 함께 사용합니다.

구조:

```text
내 상황 일회성 입력
-> 작성 폼의 AI 매칭 버튼
-> POST /api/v1/rag/assist
-> 입력값은 저장하지 않고 query embedding도 만들지 않음
-> `data-bot` 지원 카드 텍스트/태그를 기준으로 유사 후보 계산
-> 받을 수 있는 지원 후보, 조건 확인, 신청 체크리스트, 상담 경로 반환
-> React 화면에 결과 표시
```

현재 구현은 `post_embeddings`에 저장된 `data-bot` 지원 카드 인덱스와 카드 텍스트/태그를 기준으로 후보 지원 카드를 찾은 뒤 MCP 서버의 `fetch_reference_materials` tool로 공공데이터/정책 참고자료를 가져오고, OpenAI Responses API의 LLM으로 추천 문구와 후보별 요약을 생성합니다. 사용자가 입력한 매칭 요청은 `posts`나 `post_embeddings`에 저장하지 않고 query embedding도 만들지 않습니다. `OPENAI_API_KEY`가 없는 로컬 테스트 환경에서는 deterministic support-card embedding과 규칙 기반 요약 fallback을 사용합니다. 나중에 pgvector를 붙이면 지원 카드용 `post_embeddings.vector_json` 저장 방식과 `RagService`의 similarity 계산 부분을 교체하면 됩니다.

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
REFERENCE_FETCH_ENABLED=true
REFERENCE_API_URL=
REFERENCE_MAX_ITEMS=3
REFERENCE_TIMEOUT_SECONDS=2.5
```

`OPENAI_API_KEY`가 비어 있으면 1536차원 로컬 hash embedding과 규칙 기반 추천으로 fallback됩니다. API 키를 넣고 서버를 다시 실행하면 `POST /api/v1/rag/assist`가 OpenAI Responses API 기반 LLM 추천을 사용합니다. v1에서는 사용자 입력을 저장하거나 query embedding으로 만들지 않기 위해 지원 카드 인덱스만 로컬 1536차원 벡터로 유지합니다.

기존에 64차원 로컬 벡터가 저장되어 있어도, 1536차원 기본 설정으로 바뀌면 RAG 실행 시 기존 카드 임베딩을 자동으로 다시 생성합니다.

참고자료 수집은 `REFERENCE_FETCH_ENABLED=true`일 때 동작합니다. RAG 서비스가 stdio MCP client로 `backend.app.mcp.reference_server`를 실행하고, MCP tool이 참고자료를 반환합니다. `POST /api/v1/rag/assist` 요청에 `reference_urls`를 넣으면 해당 URL만 참고자료로 가져오고, URL이 없을 때만 `REFERENCE_API_URL` 외부 API와 공공데이터포털, 온통청년, 서울 열린데이터광장, 복지로 fallback을 사용합니다.

MCP 서버만 따로 확인하려면 아래처럼 실행할 수 있습니다.

```bash
python -m backend.app.mcp.reference_server
```
