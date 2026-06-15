# D-016: 게시글 목록 페이징 계약을 어떻게 둘 것인가?

Sprint: 3
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. `page` / `size`
Owner: User

Documents:
- Decision: docs/decisions/sprint-3/decisions/D-016-post-pagination-contract.md
- Roadmap: docs/decisions/sprint-3/ROADMAP.md
- Troubleshooting: docs/decisions/sprint-3/troubleshooting/D-016-post-pagination-contract-qna.md
- Rollback: Pending

## 현재 분기

Sprint 3 완료 기준에는 "게시글 목록에 페이징이 적용된다"가 포함되어 있다.

D-015에서 태그 필터는 `GET /posts?tag=...`처럼 게시글 목록 query에 합치기로 했다.
이제 페이징 query 계약을 정해야 검색, 태그, 페이징이 같은 목록 API에서 함께 동작할 수 있다.

## 선택지

### 선택지 A: `page` / `size`

페이지 번호와 페이지 크기를 받는다.

예:

```text
GET /api/v1/posts?page=1&size=10
GET /api/v1/posts?tag=fastapi&q=검색어&page=1&size=10
```

장점:
- 프론트엔드 페이지 버튼 UI와 직접 맞다.
- 사용자가 "1페이지, 2페이지"로 이해하기 쉽다.
- Sprint 3 학습/발표에서 설명하기 쉽다.

단점:
- repository 내부에서는 결국 `offset = (page - 1) * size`로 변환해야 한다.
- 대용량 데이터에서는 cursor 방식보다 약하다.

### 선택지 B: `limit` / `offset`

가져올 개수와 건너뛸 개수를 받는다.

예:

```text
GET /api/v1/posts?limit=10&offset=0
GET /api/v1/posts?tag=fastapi&q=검색어&limit=10&offset=0
```

장점:
- SQL offset/limit과 직접 대응된다.
- API 소비자가 직접 조회 범위를 세밀하게 조절할 수 있다.

단점:
- 프론트엔드 페이지 UI에서는 page 계산을 별도로 해야 한다.
- 사용자에게 "몇 페이지인지"를 설명하기 덜 직관적이다.

## Codex 추천

선택지 A를 추천한다.

이유:
- Sprint 3 목표는 작동 여부와 설명 가능성이다.
- 프론트엔드에서 페이지 버튼을 만들기 쉽고, 발표 때 query 흐름을 설명하기 좋다.
- 내부 구현은 SQLAlchemy에서 `offset`/`limit`으로 변환하면 된다.

## 이번 결정으로 확정하지 않는 것

이 결정은 아래 항목을 자동으로 확정하지 않는다.

- 목록 응답을 단순 배열로 둘지, `items`, `total`, `page`, `size` 포함 object로 바꿀지
- 검색 query 이름을 `q`로 둘지, `search`로 둘지
- 프론트엔드 검색/태그/페이징 상태를 URL query에 둘지
- cursor paging 도입 여부

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
  - `backend/app/repositories/post_repository.py`
  - `backend/app/services/post_service.py`
  - `backend/tests/test_posts_flow.py`
  - `frontend/src/api.ts`
  - `frontend/src/App.tsx`
- 선택지 A를 되돌리면 `page`/`size` query 처리와 offset 변환 로직을 제거한다.
- 선택지 B를 되돌리면 `limit`/`offset` query 처리와 관련 테스트를 제거한다.
- 검색/태그 필터와 결합된 query 테스트는 페이징 제거 후에도 태그/검색만 동작하는지 확인해야 한다.

## Q&A

### 2026-06-15

사용자 1차 답변:

```text
선택:A
이유:확장성 메리트도 장단점이 명확해서 나중에 리팩토링한다 생각하고 좀더 직관적인 방식을 택함
감수할 trade-off: 추가기능 확장성
DB/API/테스트 영향:
다음 분기로 남길 것:
```

Codex 평가:

- 선택지 A와 이유는 명확하다.
- `limit/offset` 또는 cursor 방식으로 리팩토링할 수 있음을 알고 직관성을 우선한 점도 적절하다.
- 다만 DB/API/테스트 영향과 후속 분기가 비어 있어 Pass 전 확인이 필요하다.

사용자 보완 답변:

```text
1. 맞아
2. 맞아
```

Codex 최종 평가:

- Final Evaluation: Pass
- 사용자는 선택지 A를 명확히 선택했다.
- 확장성보다 직관성을 우선하고, 필요하면 나중에 `limit/offset` 또는 cursor 방식으로 리팩토링할 수 있음을 이해했다.
- DB/repository에서 `page`와 `size`를 `offset = (page - 1) * size`, `limit = size`로 변환한다고 확인했다.
- API는 `GET /api/v1/posts?page=1&size=10`을 받기로 했다.
- 테스트는 페이지별 결과 개수, 1페이지/2페이지 분리, 태그/검색 결합 동작을 확인한다.

## Pre-Implementation Notes

- 구현 전 상태: D-016은 Accepted / Planned다.
- 선택한 API 계약: `page` / `size`
- 내부 repository에서는 `offset` / `limit`으로 변환한다.
- 다음 필수 분기: D-017. 게시글 목록 응답 shape를 어떻게 둘 것인가?

## Lowered Decisions

- cursor paging은 Sprint 3 필수 완료 기준이 아니므로 후속 리팩토링 후보로 낮춘다.
