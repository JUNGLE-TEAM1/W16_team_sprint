# Sprint 3 Decision Roadmap

Date: 2026-06-15

## 1. 목적

Sprint 3는 태그 + 페이징 + 검색을 구현한다.

기준 문서:
- `docs/taejung/development-order.md`

Sprint 3 완료 기준:
- 글 작성 시 태그를 추가할 수 있다.
- 태그로 게시글을 조회할 수 있다.
- 게시글 목록에 페이징이 적용된다.
- 검색어로 제목/본문을 검색할 수 있다.
- 프론트엔드에서 검색과 페이징을 사용할 수 있다.

## 2. Sprint 2에서 이미 구현된 기반

Backend:
- 회원가입/로그인/JWT Bearer 인증
- 게시글 CRUD와 작성자 권한 검사
- 댓글 생성/조회/수정/삭제
- 댓글 수정/삭제 작성자 권한 검사

Frontend:
- Vite + React + TypeScript 앱
- `localStorage` token 저장
- 게시글 목록/작성/수정/삭제
- 게시글 상세
- 댓글 작성/수정/삭제/조회

## 3. 전체 후보 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 태그 모델은 별도 테이블/관계로 둘 것인가, 문자열 배열처럼 단순화할 것인가? | Level 3 | Pending | Sprint 2 posts |
| 2 | C2 | 게시글 작성/수정 API에서 태그 입력 계약을 어떻게 둘 것인가? | Level 3 또는 2 | Pending | C1 |
| 3 | C3 | 태그 조회 API는 전용 endpoint로 둘 것인가, 게시글 목록 필터 query로 둘 것인가? | Level 2 또는 3 | Pending | C1 |
| 4 | C4 | 페이징 계약은 `page/size`로 둘 것인가, `limit/offset`으로 둘 것인가? | Level 3 | Pending | posts list |
| 5 | C5 | 검색은 제목/본문 `LIKE` 검색으로 시작할 것인가? | Level 2 | Pending | posts list |
| 6 | C6 | 게시글 목록 응답 shape를 list에서 metadata 포함 object로 바꿀 것인가? | Level 3 | Pending | C4 |
| 7 | C7 | 프론트엔드 목록 화면에서 검색/태그/페이징 상태를 URL query에 둘 것인가? | Level 2 | Pending | C2-C6 |

## 4. 예상 첫 Decision

예상 첫 후보:
- C1. 태그 모델은 별도 테이블/관계로 둘 것인가, 문자열 배열처럼 단순화할 것인가?

이유:
- 태그 저장 방식이 API 계약, 조회 필터, 테스트 데이터 구조를 좌우한다.
- 태그 모델이 정해져야 게시글 작성/수정 API와 태그 조회 방식을 안정적으로 정할 수 있다.

주의:
- 이 문서는 후보 지도다.
- 실제 사용자 선택이 필요한 후보만 Sprint 3 진행 시 `docs/decisions/DECISIONS.md`에 ID를 예약한 뒤 개별 Decision 문서로 승격한다.

## 5. Implementation Batch Snapshot

Date: 2026-06-15

필수 Level 3 통과:
- D-013: 태그 모델은 정규화된 `tags` 테이블과 게시글-태그 관계 테이블로 둔다.
- D-014: 게시글 생성/수정 API는 `tags: string[]`를 사용한다.
- D-015: 태그 조회는 `GET /api/v1/posts?tag=...` query param으로 처리한다.
- D-016: 페이징 계약은 `page` / `size`로 둔다.
- D-017: 게시글 목록 응답은 `items`, `total`, `page`, `size`, `pages` metadata object로 둔다.

Level 2로 낮춘 분기:
- 검색 query는 `q`로 받고 제목/본문 `LIKE` 검색으로 시작한다.
- 프론트엔드 검색/태그/페이징 상태는 이번 Sprint에서 React local state로 관리한다.

현재 git status 요약:
- 이미 수정된 파일이 많다. Sprint 1/2 작업 결과와 하네스 문서 변경이 섞여 있다.
- Codex는 기존 사용자/이전 작업 변경을 롤백 대상으로 포함하지 않는다.

수정 예정 파일:
- `backend/app/models/post.py`: 태그 relationship 연결
- `backend/app/models/tag.py`: 신규 태그 모델과 관계 테이블
- `backend/app/models/__init__.py`: 태그 모델 import/export
- `backend/app/schemas/post.py`: `tags`, `PostListResponse` 추가
- `backend/app/repositories/post_repository.py`: 태그 join/filter, 검색, count, paging
- `backend/app/services/post_service.py`: 태그 정규화, 생성/수정 연결, 목록 metadata 생성
- `backend/app/api/v1/posts.py`: `tag`, `q`, `page`, `size` query와 응답 모델 변경
- `backend/tests/test_posts_flow.py`: 태그, 검색, 페이징, metadata 테스트
- `frontend/src/api.ts`: 목록 API 응답 object와 query param 지원
- `frontend/src/App.tsx`: 태그 입력, 검색/태그/페이징 UI
- `frontend/src/styles.css`: Sprint 3 UI 스타일 보강
- `docs/decisions/DECISIONS.md`, `docs/decisions/sprint-3/*`: Decision 상태와 완료 기록

각 파일 기존 사용자 변경 여부:
- 위 코드 파일 다수는 이미 modified 또는 untracked 상태다.
- Sprint 3 변경은 태그/검색/페이징 구현에 필요한 부분으로 한정한다.

Codex가 변경할 범위:
- Sprint 3 완료 기준을 만족하는 백엔드 API와 프론트엔드 흐름
- Decision Harness 기록의 상태 갱신과 Sprint 3 SUMMARY 작성

롤백 시 되돌릴 범위:
- 위 수정 예정 파일에서 Sprint 3 태그/검색/페이징 관련 추가분
- 기존 Sprint 1/2 인증, 게시글 CRUD, 댓글 구현은 롤백 대상에서 제외

롤백 확인 명령 또는 테스트:
- `pytest backend/tests/test_posts_flow.py backend/tests/test_comments_flow.py`
- `npm test -- --run` 또는 repository의 프론트엔드 테스트 명령
- 수동 확인: 게시글 생성/목록/상세/댓글 기존 흐름이 태그 없이도 동작하는지 확인
