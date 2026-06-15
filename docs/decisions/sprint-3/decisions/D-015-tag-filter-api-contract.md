# D-015: 태그로 게시글을 조회하는 API 계약을 어떻게 둘 것인가?

Sprint: 3
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. 게시글 목록 query param으로 필터링
Owner: User

Documents:
- Decision: docs/decisions/sprint-3/decisions/D-015-tag-filter-api-contract.md
- Roadmap: docs/decisions/sprint-3/ROADMAP.md
- Troubleshooting: docs/decisions/sprint-3/troubleshooting/D-015-tag-filter-api-contract-qna.md
- Rollback: Pending

## 현재 분기

D-013에서 태그는 정규화된 테이블로 저장하기로 했다.
D-014에서 게시글 작성/수정 API는 `tags: string[]`를 사용하기로 했다.

이제 Sprint 3 완료 기준인 "태그로 게시글을 조회할 수 있다"를 어떤 API 계약으로 구현할지 정해야 한다.

## 선택지

### 선택지 A: 게시글 목록 query param으로 필터링

기존 게시글 목록 API에 `tag` query param을 추가한다.

예:

```text
GET /api/v1/posts?tag=fastapi
```

장점:
- "게시글 목록을 조건으로 좁힌다"는 흐름이 단순하다.
- 검색어, 페이징과 같은 목록 query에 합치기 쉽다.
- 프론트엔드가 하나의 목록 API만 호출하면 된다.

단점:
- 태그 목록 자체를 보여주는 API는 별도로 제공하지 않는다.
- 나중에 tag cloud나 자동완성이 필요하면 별도 endpoint를 추가해야 한다.

### 선택지 B: 전용 태그 endpoint로 조회

태그별 게시글 조회 endpoint를 별도로 둔다.

예:

```text
GET /api/v1/tags/fastapi/posts
```

장점:
- 태그를 독립 리소스로 드러낼 수 있다.
- 이후 tag 상세, tag cloud, 자동완성 API로 확장하기 쉽다.

단점:
- Sprint 3의 검색/페이징 query와 API 흐름이 나뉜다.
- 프론트엔드 목록 화면에서 호출 경로가 늘어난다.
- 지금 필요한 완료 기준보다 API 표면이 커질 수 있다.

## Codex 추천

선택지 A를 추천한다.

이유:
- Sprint 3 목표는 태그, 검색, 페이징이 함께 동작하는 목록 query 흐름을 설명하는 것이다.
- `GET /posts?tag=...&q=...&page=...` 형태로 합치는 편이 프론트엔드와 테스트가 단순하다.
- 전용 태그 endpoint는 자동완성이나 tag cloud가 필요해지는 시점에 추가해도 된다.

## 이번 결정으로 확정하지 않는 것

이 결정은 아래 항목을 자동으로 확정하지 않는다.

- 페이징 계약을 `page/size`로 둘지, `limit/offset`으로 둘지
- 검색 query 이름을 `q`로 둘지, `search`로 둘지
- 목록 응답을 metadata 포함 object로 바꿀지
- 태그 목록 조회 또는 자동완성 endpoint를 만들지
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
  - `backend/app/repositories/post_repository.py`
  - `backend/app/services/post_service.py`
  - `backend/tests/test_posts_flow.py`
  - `frontend/src/api.ts`
  - `frontend/src/App.tsx`
- 선택지 A를 되돌리면 `GET /posts?tag=...` query 처리와 관련 repository filter를 제거한다.
- 선택지 B를 되돌리면 전용 tag route와 관련 service/repository/test를 제거한다.
- DB 정규화 모델과 `tags: string[]` 입력 계약은 각각 D-013, D-014 범위이므로 이 Decision의 롤백 대상에 포함하지 않는다.

## Q&A

### 2026-06-15

사용자 1차 답변:

```text
선택: A
이유: A로 진행해야 뒤에 기능 개발할때 확장이 용이함
감수할 trade-off:
DB/API/테스트 영향:
다음 분기로 남길 것:
```

Codex 평가:

- 선택지 A는 명확하다.
- 다만 trade-off, DB/API/테스트 영향, 후속 분기가 비어 있어 Pass 기준에 부족하다.
- 선택지 A의 핵심 장점은 전용 태그 리소스 확장성보다 검색/페이징과 같은 게시글 목록 조건을 한 API 흐름으로 합치기 쉽다는 점이다.

사용자 보완 답변:

```text
1. 맞아
2. join으로 하는것은 맞고 주소방식맞고, 테스트도 다 맞네 진행해
```

Codex 최종 평가:

- Final Evaluation: Pass
- 사용자는 선택지 A를 명확히 선택했다.
- 전용 태그 endpoint, tag cloud, 자동완성 API는 지금 만들지 않고 게시글 목록 query에 합치는 trade-off를 감수한다고 확인했다.
- DB/repository는 `tags` 관계를 join해서 필터링하고, API는 `GET /api/v1/posts?tag=fastapi`를 추가하며, 테스트는 태그별 조회와 빈 결과를 확인한다는 점을 확인했다.

## Pre-Implementation Notes

- 구현 전 상태: D-015는 Accepted / Planned다.
- 선택한 API 계약: `GET /api/v1/posts?tag=...`
- 전용 tag endpoint는 Sprint 3 필수 구현에서 제외한다.
- 다음 필수 분기: D-016. 게시글 목록 페이징 계약을 어떻게 둘 것인가?

## Lowered Decisions

- 태그 목록 조회 또는 자동완성 endpoint는 Sprint 3 필수 완료 기준이 아니므로 후속 스프린트 후보로 낮춘다.
