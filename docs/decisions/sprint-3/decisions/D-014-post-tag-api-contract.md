# D-014: 게시글 작성/수정 API에서 태그 입력 계약을 어떻게 둘 것인가?

Sprint: 3
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. `tags: string[]`
Owner: User

Documents:
- Decision: docs/decisions/sprint-3/decisions/D-014-post-tag-api-contract.md
- Roadmap: docs/decisions/sprint-3/ROADMAP.md
- Troubleshooting: docs/decisions/sprint-3/troubleshooting/D-014-post-tag-api-contract-qna.md
- Rollback: Pending

## 현재 분기

D-013에서 태그는 정규화된 `tags` 테이블과 게시글-태그 관계 테이블로 저장하기로 했다.

이제 게시글 작성/수정 API가 태그를 어떤 입력 형태로 받을지 정해야 한다.

## 선택지

### 선택지 A: `tags: string[]`

게시글 생성/수정 요청에서 태그를 문자열 배열로 받는다.

예:

```json
{
  "title": "검색 구현",
  "content": "제목과 본문을 검색한다.",
  "tags": ["fastapi", "search"]
}
```

장점:
- 프론트엔드 상태와 API 계약이 명확하다.
- 태그 단위 validation을 적용하기 쉽다.
- DB는 정규화하되 API는 단순하게 유지할 수 있다.

단점:
- 사용자가 쉼표로 입력한 UI 값을 프론트엔드에서 배열로 변환해야 한다.
- 기존 `PostCreate`, `PostUpdate` schema와 테스트가 변경된다.

### 선택지 B: `tags_text: string`

게시글 생성/수정 요청에서 쉼표로 구분된 문자열을 받는다.

예:

```json
{
  "title": "검색 구현",
  "content": "제목과 본문을 검색한다.",
  "tags_text": "fastapi, search"
}
```

장점:
- 단순 입력창 하나와 바로 연결하기 쉽다.
- 구현 초반에 빠르게 붙일 수 있다.

단점:
- API 계약이 UI 입력 방식에 끌려간다.
- 서버가 문자열 파싱 규칙을 책임져야 한다.
- 이후 tag chip, 자동완성, 중복 제거 UI로 확장할 때 다시 정리할 가능성이 높다.

## Codex 추천

선택지 A를 추천한다.

이유:
- D-013에서 DB를 정규화하기로 했으므로 API도 태그를 개별 값으로 다루는 편이 자연스럽다.
- 프론트엔드는 입력칸에서 쉼표로 받은 값을 `string[]`로 변환하면 된다.
- 테스트에서 태그 중복 제거, 빈 태그 제거, 생성/수정 응답의 `tags` 확인을 명확하게 검증할 수 있다.

## 이번 결정으로 확정하지 않는 것

이 결정은 아래 항목을 자동으로 확정하지 않는다.

- 태그 필터링을 `GET /posts?tag=...`만으로 둘지, 전용 tag endpoint도 둘지
- 페이징 계약을 `page/size`로 둘지, `limit/offset`으로 둘지
- 목록 응답을 metadata 포함 object로 바꿀지
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
  - `backend/app/schemas/post.py`
  - `backend/app/services/post_service.py`
  - `backend/app/repositories/post_repository.py`
  - `backend/app/api/v1/posts.py`
  - `backend/tests/test_posts_flow.py`
  - `frontend/src/api.ts`
  - `frontend/src/App.tsx`
- 선택지 A를 되돌리면 `tags: string[]` 요청/응답 필드와 배열 validation을 제거한다.
- 선택지 B를 되돌리면 `tags_text` 파싱 규칙과 관련 테스트를 제거한다.
- DB 정규화 모델 자체는 D-013 범위이므로 이 Decision의 롤백 대상에 포함하지 않는다.
- 테스트는 롤백 후 게시글 생성/수정이 태그 입력 없이도 기존처럼 동작하는지 확인해야 한다.

## Q&A

### 2026-06-15

사용자 1차 답변:

```text
선택: A
이유: 문자열을 분리 해놓으면 배열 형식으로 프론트 엔드 조작이 편함
감수할 trade-off: 데이터 베이스 공간 분리
DB/API/테스트 영향: db에서 시간복잡도가 커지고, api는 그냥 배열로 받아오면 됌, 테스트는 배열이 깨지지않는지 확인
다음 분기로 남길 것: 이외의 내용
```

Codex 평가:

- 선택지 A와 이유는 명확하다.
- API가 배열을 받는다는 점과 테스트에서 배열 보존을 확인해야 한다는 점은 적절하다.
- 다만 D-014의 핵심 trade-off는 DB 분리보다 프론트엔드 입력 변환, 백엔드 schema 변경, 배열 validation 테스트 증가에 가깝다.
- 후속 분기인 태그 필터 방식, 페이징 계약, 목록 응답 shape가 자동 확정되지 않는지 추가 확인이 필요하다.

사용자 보완 답변:

```text
1. 맞아, 사실 두 방식의 시간복잡도는 요청과 응답의 차이이고 통틀어서 보면 차이가 없지. 하지만 나중에 기능이 많아지면 db조작이 편리해져.
2. 맞아
```

Codex 최종 평가:

- Final Evaluation: Pass
- 사용자는 선택지 A를 명확히 선택했다.
- 프론트엔드에서 배열 형태로 조작하기 쉽다는 이유를 제시했다.
- 프론트엔드 입력 변환, 백엔드 schema/validation/test 변경 비용을 감수한다고 확인했다.
- 태그 필터 방식, 페이징 계약, 목록 응답 shape는 다음 분기로 남긴다고 확인했다.

## Pre-Implementation Notes

- 구현 전 상태: D-014는 Accepted / Planned다.
- 선택한 API 계약: 게시글 생성/수정 요청과 응답에서 `tags: string[]`를 사용한다.
- 프론트엔드는 쉼표 입력값을 `string[]`로 변환한다.
- 백엔드는 빈 태그와 중복 태그를 정리하고, 정규화된 tag model에 연결한다.
- 다음 필수 분기: D-015. 태그로 게시글을 조회하는 API 계약을 어떻게 둘 것인가?

## Lowered Decisions

아직 없음.
