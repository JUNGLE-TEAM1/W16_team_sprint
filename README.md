# AI 생활지원 매칭 보드

공공데이터 기반으로 복지정책, 청년지원, 공공시설, 생활 인프라 정보를 보여주고, 사용자의 개인 상황에 맞는 지원 후보를 AI로 찾아주는 학습용 MVP 레포입니다.

이 프로젝트는 기존 `AI 지식 공유 게시판`에서 피봇되었습니다. 현재 기준은 **공개 지원 정보 보드 + 비공개 AI 지원 매칭**입니다.

## 서비스 컨셉

사용자는 로그인하지 않아도 공개 지원 정보를 볼 수 있습니다. 다만 개인 상황을 입력해서 AI 매칭을 받거나, 매칭 요청 기록을 저장하려면 로그인이 필요합니다.

```text
지원 정보 탐색
-> 로그인
-> AI 지원 찾기
-> 내 상황 입력
-> RAG로 공개 지원/시설 카드 검색
-> AI가 관련 지원, 부족 조건, 체크리스트 요약
-> 내 상담 기록에 비공개 저장
```

## 핵심 도메인

| 항목 | 의미 |
| --- | --- |
| 지원 카드 | 복지정책, 청년지원, 주거지원, 취업지원 같은 공개 정책 정보 |
| 시설 카드 | 복지관, 청년센터, 상담센터, 생활 인프라 같은 공개 시설 정보 |
| 내 상담 요청 | 사용자가 자기 상황을 입력한 비공개 AI 매칭 요청 |
| 태그 | `청년`, `주거`, `취업`, `서울`, `마포구`, `저소득` 같은 매칭 기준 |
| RAG | 개인 상담 요청을 query로 사용해 공개 지원/시설 카드만 검색 |
| MCP | 공공데이터나 정책 출처를 JSON-RPC tool 형태로 조회하는 연결 지점 |
| Agent | RAG/MCP 결과를 조합해 신청 가능성, 부족 조건, 체크리스트를 생성할 후속 기능 |

## 공개/비공개 기준

| 데이터 | 공개 목록 | RAG index | 댓글 | 비고 |
| --- | --- | --- | --- | --- |
| `policy` | 노출 | 포함 | 없음 | 지원 카드 |
| `facility` | 노출 | 포함 | 없음 | 시설 카드 |
| `case` | 미노출 | 제외 | 없음 | 작성자 본인만 보는 내 상담 요청 |

개인 상담 요청에는 민감한 정보가 들어갈 수 있으므로 공개 게시판에 섞지 않고, 공용 vector index에도 저장하지 않습니다. 현재 입력값은 RAG 검색 query로만 사용합니다.

## 현재 구현 상태

완료된 기반:

- Session 기반 회원가입/로그인/로그아웃
- 게시글 CRUD 기반을 재사용한 지원 카드/시설 카드/상담 요청 모델
- PostgreSQL + pgvector 기반 RAG 저장 구조
- LangChain 기반 RAG index 연동
- OpenAI embedding 및 관련 지원 카드 요약
- 검색/태그/정렬/페이징
- 좋아요를 `관심 등록` 의미로 사용
- JSON-RPC MCP endpoint 기반 외부 참고자료 조회 틀
- private case 보호 정책

아직 필요한 MVP 작업:

- `내 상담 기록` 프론트 화면
- 공공데이터 import script
- `data-bot` 작성자 기반 지원/시설 카드 seed
- Stack Overflow MCP provider를 공공데이터/정책 출처 provider로 교체
- AI 지원 찾기 결과 화면 정리
- 정부/공공기관 톤 UI polishing

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Frontend | React + Vite |
| Backend/API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| AI/RAG | LangChain + OpenAI Embeddings |
| Vector DB | PostgreSQL + pgvector |
| Auth | Session 인증 |
| MCP | FastAPI 내부 JSON-RPC endpoint |

## 실행 방법

### Backend

```bash
cp .env.example .env
docker compose up -d db
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/uvicorn backend.app.main:app --reload --env-file .env
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

프론트엔드 개발 서버:

```text
http://127.0.0.1:5173
```

## 테스트 방법

```bash
docker compose up -d db
.venv/bin/python -m pytest backend/tests
cd frontend
npm run build
```

테스트도 PostgreSQL을 사용합니다. 로컬 DB schema를 크게 바꾼 뒤 테스트가 꼬이면 학습용 데이터 reset이 필요할 수 있습니다.

## 주요 코드 위치

| 영역 | 파일 |
| --- | --- |
| FastAPI app | `backend/app/main.py` |
| DB 설정 | `backend/app/db/session.py` |
| dev schema sync | `backend/app/db/schema.py` |
| 공통 설정 | `backend/app/core/config.py` |
| 인증 API | `backend/app/api/v1/auth.py` |
| 지원 정보 API | `backend/app/api/v1/posts.py` |
| RAG API | `backend/app/api/v1/ai.py` |
| MCP API | `backend/app/api/v1/mcp.py` |
| 게시판/상담 정책 | `backend/app/services/post_service.py` |
| LangChain RAG index | `backend/app/services/langchain_rag_index.py` |
| RAG 요약 | `backend/app/services/rag_summary_service.py` |
| MCP service | `backend/app/services/mcp_service.py` |
| 외부 참고자료 provider | `backend/app/services/external_reference_service.py` |
| React entry | `frontend/src/App.tsx` |
| 공개 지원 목록 | `frontend/src/components/PostList.tsx` |
| 지원/상담 상세 | `frontend/src/components/PostDetail.tsx` |
| AI 지원 찾기 modal | `frontend/src/components/ComposeModal.tsx` |
| 화면 controller | `frontend/src/hooks/useBoardController.ts` |

## 문서

- [피봇 1차 구현 기록](docs3/pivot-1/implementation-record.md)
- [피봇 2차 구현 기록](docs3/pivot-2/implementation-record.md)
- [피봇 3차 MVP 방향 및 데이터 계획](docs3/pivot-3/mvp-direction-and-data-plan.md)
- [Sprint 6 LangChain RAG 리팩토링 구현 기록](docs2/sprint-6/langchain-rag-refactor-record.md)
- [Sprint 7 MCP 개념 및 의사결정 가이드](docs2/sprint-7/mcp-concept-and-decision-guide.md)

## 다음 구현 순서

1. `내 상담 기록` 화면을 추가합니다.
2. 공공데이터 import script와 `data-bot` seed를 만듭니다.
3. MCP provider를 공공데이터/정책 출처 조회로 교체합니다.
4. AI 지원 찾기 결과 화면을 카드형으로 정리합니다.
5. UI를 밝은 공공서비스 톤으로 polishing합니다.
