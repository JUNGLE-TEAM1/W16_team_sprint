# D-029: 유사 게시글 추천 API 계약을 어떻게 둘 것인가?

Sprint: 4
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. 작성 폼 입력값으로 추천하는 별도 preview API
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-4/decisions/D-029-similar-posts-api-contract.md`
- Roadmap: `docs/decisions/sprint-4/ROADMAP.md`
- Troubleshooting: `docs/decisions/sprint-4/troubleshooting/D-029-similar-posts-api-contract-qna.md`
- Rollback: Pending

## 1. 현재 분기

D-026에서 local embedding model과 vector dimension을 확정했다.

D-027에서 게시글당 최신 embedding row 하나를 유지하기로 확정했다.

D-028에서 embedding 실패가 게시글 작성/수정을 rollback하지 않는다고 확정했다.

이제 글 작성 화면에서 입력 중인 제목/본문/태그로 유사 게시글을 찾는 API 계약을 정해야 한다.

이 결정은 API 경로, 요청 body, 응답 shape, frontend 호출 위치, 테스트 기대값에 직접 영향을 준다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 추천 API 계약만 확정한다.

다음 항목은 자동 확정하지 않는다.

- similarity threshold의 정확한 수치
- top-N 기본값의 정확한 수치
- LLM 요약 provider와 prompt 상세
- 반복 embedding 실패 시 degraded 또는 점검 모드
- background 재시도 방식

## 3. 선택지

### A. 작성 폼 입력값으로 추천하는 별도 preview API

경로 예시:

```text
POST /api/v1/ai/similar-posts
```

요청 예시:

```json
{
  "title": "JWT 인증 정리",
  "content": "토큰 발급과 current_user 흐름...",
  "tags": ["auth", "jwt"],
  "limit": 3
}
```

응답 예시:

```json
{
  "query_summary": "JWT 인증과 토큰 검증 흐름을 다루는 글입니다.",
  "items": [
    {
      "post_id": 1,
      "title": "JWT 로그인 구현",
      "preview": "로그인 성공 시 JWT를 발급하고...",
      "similarity": 0.82,
      "similarity_level": "high",
      "tags": ["auth", "jwt"]
    }
  ],
  "message": "비슷한 게시글 1개를 찾았습니다."
}
```

장점:
- 작성 전 미리보기 흐름에 맞다.
- 아직 저장되지 않은 글도 추천할 수 있다.
- 기존 게시글 CRUD 계약을 건드리지 않는다.
- D-025의 “미리보기 반환 후 사용자 확인 반영”과 맞다.

단점:
- 입력 본문을 API로 보내 embedding해야 하므로 요청 body가 커질 수 있다.
- 인증 적용 범위를 정해야 한다.

### B. 특정 게시글 ID 기준으로 추천하는 API

경로 예시:

```text
GET /api/v1/posts/{post_id}/similar
```

장점:
- 이미 저장된 게시글의 embedding을 기준으로 검색하므로 query embedding 생성이 단순하다.
- 게시글 상세 화면의 관련 글 추천에 적합하다.

단점:
- 글 작성 중 중복 방지에는 맞지 않는다.
- 저장 전 추천이라는 Sprint 4 추천 흐름과 어긋난다.

### C. 게시글 작성 API 응답에 유사 게시글 추천을 함께 포함한다

`POST /api/v1/posts` 응답에 추천 결과를 함께 반환한다.

장점:
- API 호출 횟수가 줄어든다.
- 저장 직후 추천 결과를 보여주기 쉽다.

단점:
- 기존 `PostRead` 응답 계약을 크게 바꾼다.
- 글 작성 전 중복 방지 목적에는 늦다.
- 게시글 기본 API가 AI 기능과 강하게 결합된다.

## 4. Codex 추천

추천은 A다.

Sprint 4의 추천 기능은 글 작성 중 기존 유사 글을 찾아 중복을 줄이는 흐름이다. 따라서 아직 저장되지 않은 입력값을 기준으로 검색하는 preview API가 가장 잘 맞다.

또한 기존 게시글 CRUD 응답 계약을 유지하면서 AI 기능을 별도 경로로 분리할 수 있어 D-028의 실패 처리 방향과도 일관된다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 선택한 이유가 있어야 한다.
- 작성 전 preview인지, 저장된 게시글 기준인지, 작성 API 결합인지가 명확해야 한다.
- DB/API/frontend/test 중 무엇이 이 선택의 영향을 받는지 언급해야 한다.
- 이번 결정 이후에도 남는 후속 분기를 구분해야 한다.
- 기존 게시글 API와 AI 추천 API를 분리할지 결합할지의 trade-off를 인식해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

추천 기준:

DB/API/frontend/test 영향:

trade-off:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현 파일을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- AI/RAG router
- 추천 요청/응답 schema
- embedding service와 retrieval service
- frontend 작성 화면의 추천 호출
- RAG API 테스트
- README 또는 Sprint note의 RAG API 설명

되돌릴 때 확인할 범위:
- 새 API router 등록
- frontend 작성 화면 호출 코드
- 추천 응답 타입
- 관련 테스트

DB 데이터 손실 가능성:
- API 계약 자체는 DB 데이터를 삭제하지 않는다.
- 구현 후에도 원본 게시글과 embedding row는 유지되어야 한다.

원래 상태 보장:
- 기존 게시글 CRUD API 계약은 유지되어야 한다.
- 추천 API가 실패해도 게시글 기본 기능은 동작해야 한다.

재검토 조건:
- Sprint 4 목표가 작성 중 중복 방지가 아니라 상세 화면 관련 글 추천으로 바뀌는 경우
- frontend에서 작성 전 preview UI를 제공하지 않기로 범위가 바뀌는 경우
- 추천 API가 반드시 저장된 게시글 기준이어야 하는 요구가 생기는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: 애초에 이 기능으로 만들려 했음

추천 기준: 작성 폼 입력값으로 유사 계시글 확인

DB/API/frontend/test 영향: 

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 A로 명확하다.
- 작성 폼 입력값으로 유사 게시글을 확인한다는 추천 기준도 명확하다.
- 이유는 기능 의도와 맞지만, DB/API/frontend/test 영향, trade-off, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 의견

사용자 의견:
- 유사 글을 찾는 것은 좋지만, 사용자가 판단할 지표가 있으면 좋겠다.
- 점수를 매기고 특정 점수를 초과하면 색을 다르게 표시하는 방식을 제안했다.

Codex 반영:
- 추천 API 응답에 `similarity` 원점수와 `similarity_level` 등급을 포함한다.
- frontend는 `similarity_level`에 따라 색상 또는 강조 스타일을 다르게 표시한다.
- 정확한 threshold 값은 D-029에서 고정하지 않고 후속 Level 2 결정으로 남긴다.

### 2026-06-15 최종 정리

사용자 답변과 보완 의견을 종합한 최종 답변:

```md
선택: A

이유:
애초에 작성 폼에서 유사 글을 확인하는 기능으로 만들려 했고, 글 저장 전 중복 가능성을 사용자가 판단할 수 있어야 한다.

추천 기준:
작성 폼 입력값인 `title`, `content`, `tags`를 기준으로 유사 게시글을 검색한다.

DB/API/frontend/test 영향:
DB는 저장된 `post_embeddings`를 조회한다. API는 `POST /api/v1/ai/similar-posts`로 작성 폼의 `title`, `content`, `tags`, `limit`를 받는다. 응답에는 유사 게시글 목록, `similarity`, `similarity_level`, 요약 메시지를 포함한다. frontend는 글 작성 화면에서 유사 글 찾기 버튼으로 호출하고, `similarity_level`에 따라 색상 또는 강조 스타일을 다르게 표시한다. 테스트는 입력값 embedding으로 유사 게시글이 반환되고 점수와 등급이 포함되는지 확인한다.

trade-off:
작성 전에 중복을 줄일 수 있지만, 입력 중인 내용을 API로 보내야 하고 요청 body가 커질 수 있다. 점수는 절대적인 정답률이 아니라 embedding 기준 유사도이므로 보조 판단 지표로 표시해야 한다.

아직 다음 분기로 남겨둘 것:
similarity threshold/top-N 정확한 기본값, LLM 요약 provider/prompt, 반복 실패 시 degraded 정책, background 재시도 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- 작성 전 preview API 기준이 명확하다.
- DB/API/frontend/test 영향이 구분되었다.
- 기존 게시글 API와 AI 추천 API를 분리하는 trade-off를 인식했다.
- 점수와 등급 표시를 API 계약에 포함하되, 정확한 threshold는 후속 분기로 분리했다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- Sprint 1~3.5와 frontend 관련 기존 변경 및 미추적 파일이 다수 존재한다.
- D-029 처리 중에는 `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-4/decisions/D-029-similar-posts-api-contract.md`, `docs/decisions/sprint-4/troubleshooting/D-029-similar-posts-api-contract-qna.md`만 Decision 기록 범위로 변경한다.

구현 전 확정된 범위:
- 추천 API는 `POST /api/v1/ai/similar-posts`로 둔다.
- 요청은 작성 폼의 `title`, `content`, `tags`, `limit`를 받는다.
- 응답은 유사 게시글 목록, `similarity`, `similarity_level`, 요약 메시지를 포함한다.
- 기존 게시글 CRUD API 응답 계약은 변경하지 않는다.
- frontend는 작성 화면에서 추천 API를 호출하고 유사도 등급을 시각적으로 표시한다.

아직 구현 전 확정되지 않은 범위:
- similarity threshold와 top-N 기본값
- LLM 요약 방식
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식

## 11. Lowered Decisions

- similarity threshold와 top-N 기본값은 D-029에서 API 계약이 확정되어 Level 2로 낮춘다.
- `similarity_level` 색상 기준은 API 응답 필드가 확정되어 frontend 구현 중 Level 2로 처리한다.
