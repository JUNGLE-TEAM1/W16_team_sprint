# D-013: 태그 모델을 어떤 구조로 저장할 것인가?

Sprint: 3
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Completed
Chosen: A. 정규화된 태그 테이블
Owner: User

Documents:
- Decision: docs/decisions/sprint-3/decisions/D-013-tag-model-structure.md
- Roadmap: docs/decisions/sprint-3/ROADMAP.md
- Troubleshooting: docs/decisions/sprint-3/troubleshooting/D-013-tag-model-structure-qna.md
- Rollback: Pending

## 현재 분기

Sprint 3는 태그, 페이징, 검색을 구현해야 한다.

첫 번째로 진행을 막는 분기는 태그 저장 모델이다.

- 태그를 별도 `tags` 테이블과 게시글-태그 관계 테이블로 정규화할 것인가?
- 아니면 `posts`에 단순 문자열 계열 필드로 직접 저장할 것인가?

이 결정이 먼저 정해져야 태그 입력 계약, 태그 필터링, 검색 + 태그 query 동작, 프론트엔드 제어 방식을 안정적으로 정할 수 있다.

## 선택지

### 선택지 A: 정규화된 태그 테이블

전용 `tags` 테이블과 게시글-태그 관계 테이블을 추가한다.

예상 구조:

- `tags.id`
- `tags.name`
- `post_tags.post_id`
- `post_tags.tag_id`

API는 계속 `tags: string[]`처럼 단순하게 노출하고, DB에는 재사용 가능한 태그 행으로 저장할 수 있다.

장점:
- 이후 RAG metadata와 태그 분석에 더 잘 맞는다.
- 게시글마다 태그 문자열이 중복 저장되는 것을 줄인다.
- 나중에 태그 목록 조회와 필터 query를 깔끔하게 만들 수 있다.

단점:
- 지금 작성해야 할 코드와 테스트가 늘어난다.
- 생성/수정 시 관계 처리 로직이 필요하다.
- 롤백 범위가 조금 커진다.

### 선택지 B: `posts`의 단순 필드

태그를 각 게시글에 단순 문자열 필드로 직접 저장한다. 예를 들면 comma-separated text 방식이다.

예상 구조:

- `posts.tags`

API는 `tags: string[]`로 노출하고, service 내부에서 직렬화/역직렬화할 수 있다.

장점:
- 가장 빠르게 구현할 수 있다.
- model/repository 변경 범위가 작다.
- Sprint 3 동작 데모 기준으로 설명하기 쉽다.

단점:
- 데이터 정합성이 약하다.
- 태그 필터링 구현이 덜 깔끔하다.
- 이후 RAG metadata로 옮길 때 정리 작업이 필요할 수 있다.

## Codex 추천

선택지 A를 추천한다.

이유:
- 이 프로젝트는 PostgreSQL과 이후 pgvector/RAG를 명시적으로 고려한다.
- Sprint 3 팀 싱크 체크 포인트에 "RAG에서 태그를 metadata로 활용할 수 있는 구조인가?"가 포함되어 있다.
- 정규화된 태그 모델은 프론트엔드 API를 단순하게 유지하면서도 Sprint 4에 더 적합한 DB 구조를 남긴다.

우선순위가 엄격하게 "작동 여부"와 최소 구현 시간이라면 선택지 B도 가능하다. 다만 이 경우 RAG 전에 마이그레이션 지점을 둔 의도적인 단축 경로로 기록해야 한다.

## 이번 결정으로 확정하지 않는 것

이 결정은 아래 항목을 자동으로 확정하지 않는다.

- create/update에서 `tags: string[]`를 받을지, comma-separated text를 받을지
- 태그 필터링을 `GET /posts?tag=...`만으로 둘지, 전용 tag endpoint도 둘지
- 페이징 계약을 `page/size`로 둘지, `limit/offset`으로 둘지
- 목록 응답을 `PostRead[]`에서 metadata 포함 object로 바꿀지
- 프론트엔드 필터 상태를 React local state에 둘지 URL query에 둘지

이 항목들은 태그 저장 모델이 통과된 뒤 후속 분기로 남긴다.

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
  - `backend/app/models/post.py`
  - `backend/app/models/tag.py`
  - `backend/app/models/__init__.py`
  - `backend/app/schemas/post.py`
  - `backend/app/repositories/post_repository.py`
  - `backend/app/services/post_service.py`
  - `backend/app/api/v1/posts.py`
  - `backend/tests/test_posts_flow.py`
  - `frontend/src/api.ts`
  - `frontend/src/App.tsx`
- 선택지 A를 고르면 롤백 시 태그 관계 모델과 관계 처리 로직을 제거한다.
- 선택지 B를 고르면 롤백 시 `posts.tags` 필드와 직렬화 로직을 제거한다.
- DB 스키마 변경은 새로 만든 로컬 테스트 테이블 삭제 또는 로컬 개발 DB 재생성이 필요할 수 있다. 실제 데이터 입력 후 스키마를 되돌리면 태그 값이 손실될 수 있다.
- 테스트는 롤백 후에도 게시글 생성/목록/상세 조회가 태그 필드 없이 동작함을 보장해야 한다.
- 태그 필터링이 느려지거나, 프론트엔드 태그 UX에 자동완성이 필요해지거나, Sprint 4 RAG metadata가 다른 표현을 요구하면 재검토한다.

## Q&A

### 2026-06-15

사용자 질문:

> 롤백 또는 재검토 조건은 사용자 답변 요구사항에서 빼야 하는데 하네스에 반영되어 있지 않다.

반영:

- 사용자 답변 Pass 기준에서 롤백 또는 재검토 조건 요구를 제거한다.
- 롤백 계획, 재검토 조건, 재진입 조건은 Codex가 Decision 문서와 rollback 문서에 정리한다.

사용자 1차 답변:

```text
선택: A
이유: 태그 기반 검색을 할수 있고, 분석도 가능 db도 후반 확장이 용이함
감수할 trade-off: 무
DB/API/테스트 영향: db는 해봐야 테이블 추가, api는 태그 기반 api를 만들수 있게 되고, 테스트는 관련 api들을 테스트 가능하게 설정
다음 분기로 남길 것: 이번 분기로 해결 못하는 분기들
롤백 또는 재검토 조건: 이 조건은 빼라 아까 말했잖아 하네스에 추가안했어?
```

Codex 평가:

- 선택지 A와 이유는 명확하다.
- DB/API/테스트 영향도 큰 방향은 언급했다.
- 다만 정규화 모델의 구현 비용, 관계 처리, 테스트 증가 같은 trade-off를 "무"로 둔 점은 Pass 기준에 부족하다.
- 후속 분기도 "이번 분기로 해결 못하는 분기들"로만 적혀 있어, 어떤 결정을 아직 자동 확정하지 않는지 확인이 필요하다.

사용자 보완 답변:

```text
1. 맞아 그래도 정규화를 하면 나중에는 편해지니까
2. 다음 분기로 넘겨
```

Codex 최종 평가:

- Final Evaluation: Pass
- 사용자는 선택지 A를 명확히 선택했다.
- 정규화 모델의 후반 확장성과 태그 기반 검색/분석 가치를 이유로 제시했다.
- 테이블과 관계 처리 코드, create/update 테스트가 늘어나는 비용을 감수한다고 확인했다.
- `tags: string[]` 입력 계약, 태그 필터 방식, 페이징 응답 shape는 다음 분기로 넘긴다고 확인했다.

## Pre-Implementation Notes

- 구현 전 상태: D-013은 Accepted / Planned다.
- 선택한 구현 방향: `tags` 테이블과 게시글-태그 관계 테이블을 둔다.
- API 표현은 아직 확정하지 않는다.
- 다음 필수 분기: D-014. 게시글 작성/수정 API에서 태그 입력 계약을 어떻게 둘 것인가?

## Lowered Decisions

아직 없음.
