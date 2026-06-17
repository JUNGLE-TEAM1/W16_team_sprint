# AI 반려견 케어 상담 보드

반려견 건강, 성장, 질병 관련 질문을 공개 게시판에 올리고, AIHub 반려견 말뭉치 기반 RAG로 참고 답변과 행동 계획을 생성하는 학습용 MVP입니다.

이전 `AI 지식 공유 게시판`, `AI 생활지원 매칭 보드` 기록은 학습 이력으로 남아 있지만, 현재 구현 기준은 **AI 반려견 케어 상담 보드**입니다.

## 핵심 흐름

```text
사용자 질문 작성
-> 공개 상담 질문으로 저장
-> AIHub 반려견 Q&A/원천 말뭉치 검색
-> AI 답변 + 행동 계획 + 참고 근거 표시
-> 댓글로 추가 경험이나 보충 질문 작성
```

## 도메인 매핑

| 기존 구조 | 현재 의미 |
| --- | --- |
| `Post` | 공개 반려견 케어 상담 질문 |
| `Comment` | 댓글, 추가 경험, 보충 질문 |
| `Tag` | 기침, 구토, 피부, 안과, 자견, 노령견 같은 케어 메타데이터 |
| `knowledge_documents` | AIHub 원본 JSON 문서 단위 메타데이터 |
| `knowledge_chunks` | RAG 검색용 chunk와 embedding |
| RAG | 사용자 질문과 유사한 AIHub Q&A/말뭉치 검색 |
| Agent | 참고 답변, 병원 방문 기준, 보호자 행동 체크리스트 생성 |

AI 답변은 확정 진단이 아니라 참고 정보입니다. 응급 증상, 악화, 지속 증상은 수의사 상담을 권장합니다.

## 실행

백엔드:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

프론트엔드:

```bash
cd frontend
npm run dev
```

기본 접속:

```text
http://127.0.0.1:5173
```

## AIHub 데이터 적재

AIHub 원본 데이터는 용량과 라이선스 때문에 repo에 커밋하지 않습니다. 로컬에 다운로드한 뒤 import script로 DB와 pgvector index에 적재합니다.

기본 기대 경로:

```text
/Users/liamtsy/Downloads/59.반려견 성장 및 질병 관련 말뭉치 데이터/3.개방데이터/1.데이터
```

OpenAI embedding으로 실제 적재:

```bash
python3 -m backend.app.scripts.import_aihub_pet_care --embedding-provider openai
```

빠른 구조 확인용 적재:

```bash
python3 -m backend.app.scripts.import_aihub_pet_care --embedding-provider none --limit 10
```

테스트/로컬 검증용 mock embedding:

```bash
python3 -m backend.app.scripts.import_aihub_pet_care --embedding-provider mock --limit 10
```

## 주요 API

| 기능 | Endpoint |
| --- | --- |
| 질문 목록 | `GET /api/v1/posts` |
| 질문 작성 | `POST /api/v1/posts` |
| 내 질문 | `GET /api/v1/posts/my-consultations` |
| 댓글 | `GET/POST /api/v1/posts/{post_id}/comments` |
| AI 답변 조회 | `GET /api/v1/ai/pet-care/posts/{post_id}/advice` |
| AI 답변 생성/저장 | `POST /api/v1/ai/pet-care/posts/{post_id}/advice` |

## 주요 파일

| 영역 | 파일 |
| --- | --- |
| 게시판 API | `backend/app/api/v1/posts.py` |
| AI 답변 API | `backend/app/api/v1/ai.py` |
| AIHub importer | `backend/app/scripts/import_aihub_pet_care.py` |
| AIHub parser/import service | `backend/app/services/aihub_pet_care_import_service.py` |
| Knowledge RAG index | `backend/app/services/knowledge_rag_index.py` |
| Pet-care advice service | `backend/app/services/pet_care_advice_service.py` |
| 프론트 컨트롤러 | `frontend/src/hooks/useBoardController.ts` |
| AI 답변 hook | `frontend/src/hooks/usePetCareAdvice.ts` |
| 질문 상세 UI | `frontend/src/components/PostDetail.tsx` |

## 문서

- [Pet-care pivot decision record](docs3/pet-care-pivot/decision-record.md)
- [Pet-care pivot implementation record](docs3/pet-care-pivot/implementation-record.md)

과거 스프린트 문서는 `docs2/**`, 과거 생활지원 피봇 문서는 `docs3/pivot-*`에 남아 있습니다.
