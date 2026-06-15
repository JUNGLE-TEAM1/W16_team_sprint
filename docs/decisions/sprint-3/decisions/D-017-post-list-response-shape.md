# D-017: 게시글 목록 응답 shape를 어떻게 둘 것인가?

Sprint: 3
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: B. metadata 포함 object
Owner: User

Documents:
- Decision: docs/decisions/sprint-3/decisions/D-017-post-list-response-shape.md
- Roadmap: docs/decisions/sprint-3/ROADMAP.md
- Troubleshooting: docs/decisions/sprint-3/troubleshooting/D-017-post-list-response-shape-qna.md
- Rollback: Pending

## 현재 분기

D-016에서 페이징 query는 `page` / `size`로 정했다.

이제 게시글 목록 응답을 기존처럼 게시글 배열만 줄지, 아니면 페이징 metadata를 포함한 object로 바꿀지 정해야 한다.

## 선택지

### 선택지 A: 기존 배열 유지

응답을 기존처럼 `PostRead[]`로 유지한다.

예:

```json
[
  {"id": 1, "title": "글 1", "content": "내용", "created_at": "...", "tags": ["fastapi"]}
]
```

장점:
- 기존 API와 프론트엔드 변경이 적다.
- 구현이 빠르다.

단점:
- 전체 게시글 수와 전체 페이지 수를 알 수 없다.
- 프론트엔드에서 "다음 페이지가 있는지" 판단하기 어렵다.
- Sprint 3의 페이징 설명이 약해진다.

### 선택지 B: metadata 포함 object

응답을 `items`, `total`, `page`, `size`, `pages`를 포함한 object로 바꾼다.

예:

```json
{
  "items": [
    {"id": 1, "title": "글 1", "content": "내용", "created_at": "...", "tags": ["fastapi"]}
  ],
  "total": 23,
  "page": 1,
  "size": 10,
  "pages": 3
}
```

장점:
- 프론트엔드에서 페이지 버튼과 결과 없음 상태를 안정적으로 만들 수 있다.
- 검색/태그/페이징이 함께 동작하는 흐름을 설명하기 좋다.
- 테스트에서 total, page, size, pages를 명확히 검증할 수 있다.

단점:
- 기존 `GET /posts` 응답 계약이 배열에서 object로 바뀐다.
- 프론트엔드 `listPosts`와 테스트를 함께 수정해야 한다.

## Codex 추천

선택지 B를 추천한다.

이유:
- Sprint 3 완료 기준에 페이징과 검색 결과 없음 상태가 포함되어 있다.
- 프론트엔드에서 전체 페이지 수와 빈 결과를 안정적으로 표시하려면 metadata가 필요하다.
- API 계약 변경 비용은 있지만 Sprint 3의 사용성 목표에 더 잘 맞다.

## 이번 결정으로 확정하지 않는 것

이 결정은 아래 항목을 자동으로 확정하지 않는다.

- 검색 query 이름을 `q`로 둘지, `search`로 둘지
- 검색을 제목/본문 `LIKE`로 시작할지
- 프론트엔드 검색/태그/페이징 상태를 URL query에 둘지

## Pass 기준

사용자 답변에는 다음이 포함되어야 한다.

- 선택지 A와 선택지 B 중 명확한 선택
- 선택 이유
- 감수할 trade-off
- DB/API/테스트 영향에 대한 이해
- 후속 결정으로 남길 항목

## 사용자 답변 템플릿

```text
선택:
이유:
감수할 trade-off:
DB/API/테스트 영향:
다음 분기로 남길 것:
```

## 롤백 계획

이 결정이 구현된 뒤 되돌린다면 다음 범위를 확인한다.

- 변경 파일 후보:
  - `backend/app/api/v1/posts.py`
  - `backend/app/schemas/post.py`
  - `backend/app/services/post_service.py`
  - `backend/app/repositories/post_repository.py`
  - `backend/tests/test_posts_flow.py`
  - `frontend/src/api.ts`
  - `frontend/src/App.tsx`
- 선택지 B를 되돌리면 `PostListResponse` 같은 metadata 응답 schema와 프론트엔드 파싱 로직을 제거하고 `PostRead[]` 응답으로 되돌린다.
- 선택지 A를 되돌릴 경우 metadata object로 바꾸는 변경을 새 Decision 또는 후속 리팩토링으로 다시 진행한다.

## Q&A

### 2026-06-15

사용자 1차 답변:

```text
선택: B
이유: 스프린트 일관성을 위해서 있어야 할 부분이고 추후 확장이 용이해짐
감수할 trade-off: 개발 비용
DB/API/테스트 영향: 응답 데이터 추가/ 응답 api데이터 추가/ 응답 데이터 확인 및 실사용 여부
다음 분기로 남길 것:
```

Codex 평가:

- 선택지 B와 이유는 명확하다.
- 개발 비용 증가를 trade-off로 인식했다.
- API 응답 데이터 추가와 테스트에서 응답 데이터 확인이 필요하다는 점을 이해했다.
- 후속 분기 항목이 비어 있어 Pass 전 확인이 필요하다.

사용자 보완 답변:

```text
맞아
```

Codex 최종 평가:

- Final Evaluation: Pass
- 사용자는 선택지 B를 명확히 선택했다.
- Sprint 3의 페이징/검색 결과 없음 상태와 일관성을 위해 metadata가 필요하다는 점을 이해했다.
- 기존 목록 API가 배열에서 object로 바뀌고, 프론트엔드와 테스트 수정 비용이 생긴다는 trade-off를 감수했다.
- 검색 query 방식과 프론트엔드 상태 위치는 다음 분기로 남긴다고 확인했다.

## Pre-Implementation Notes

- 구현 전 상태: D-017은 Accepted / Planned다.
- 선택한 응답 shape: `items`, `total`, `page`, `size`, `pages` 포함 object
- 기존 `GET /posts` 응답 계약이 `PostRead[]`에서 metadata object로 바뀐다.
- 검색 query 방식과 프론트엔드 상태 위치는 Level 2로 낮춰 구현 중 짧게 알리고 진행한다.

## Lowered Decisions

- 검색 query 이름과 방식은 Sprint 3 요구사항에 맞춰 `q` query param과 제목/본문 `LIKE` 검색으로 시작하는 Level 2 결정으로 낮춘다.
- 프론트엔드 검색/태그/페이징 상태는 이번 Sprint에서 React local state로 시작하는 Level 2 결정으로 낮춘다.
