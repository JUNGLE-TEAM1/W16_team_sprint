# Sprint 3 Summary

Date: 2026-06-15

## 완료 기준

- 글 작성 시 태그를 추가할 수 있다.
- 태그로 게시글을 조회할 수 있다.
- 게시글 목록에 페이징이 적용된다.
- 검색어로 제목/본문을 검색할 수 있다.
- 프론트엔드에서 검색과 페이징을 사용할 수 있다.
- 검색 결과 없음 상태가 표시된다.
- 태그, 검색, 페이징이 함께 동작할 때의 query 흐름을 설명할 수 있다.

## 완료된 Decision

| ID | 결정 | 결과 | Implementation |
| --- | --- | --- | --- |
| D-013 | 태그 모델 구조 | 정규화된 `tags` 테이블과 게시글-태그 관계 테이블 | Completed |
| D-014 | 게시글 태그 입력 계약 | `tags: string[]` | Completed |
| D-015 | 태그 조회 API 계약 | `GET /api/v1/posts?tag=...` | Completed |
| D-016 | 페이징 계약 | `page` / `size` | Completed |
| D-017 | 목록 응답 shape | `items`, `total`, `page`, `size`, `pages` metadata object | Completed |

## 구현 결과

Backend:
- `Tag` 모델과 `post_tags` 관계 테이블을 추가했다.
- 게시글 생성/수정 요청과 응답에 `tags: string[]`를 추가했다.
- 게시글 목록 API에 `tag`, `q`, `page`, `size` query param을 추가했다.
- 게시글 목록 응답을 metadata 포함 object로 변경했다.
- repository에서 태그 join 필터, 제목/본문 검색, count, offset/limit paging을 처리한다.

Frontend:
- 게시글 작성/수정 화면에 쉼표 구분 태그 입력을 추가했다.
- 게시글 목록에 검색어, 태그 필터, 페이지 이동 UI를 추가했다.
- 목록 API의 metadata를 사용해 전체 개수, 빈 결과, 페이지 상태를 표시한다.
- 게시글 목록/상세에 태그 pill을 표시한다.

## 테스트 결과

- `DATABASE_URL=sqlite+pysqlite:///./.tmp_sprint3_test.db PYTHONPATH=. pytest backend/tests`
  - 22 passed
  - 경고: 기존 `datetime.utcnow()` deprecation warning
- `npm test`
  - 1 passed
- `npm run build`
  - 성공
- Browser 확인
  - `http://127.0.0.1:3001/`에서 데스크톱/모바일 렌더링 확인
  - 백엔드 서버가 켜져 있지 않아 화면에는 `Failed to fetch`가 표시됨

주의:
- Docker 데몬이 실행 중이 아니어서 PostgreSQL docker-compose 기반 테스트는 실행하지 못했다.
- 임시 SQLite 검증은 테스트 실행용이며, 프로젝트 DB 전략을 바꾸지 않는다.

## 낮아진 후보

- 검색 query 이름과 방식은 Level 2로 낮춰 `q` query param + 제목/본문 `LIKE` 검색으로 구현했다.
- 프론트엔드 검색/태그/페이징 상태 위치는 Level 2로 낮춰 React local state로 구현했다.
- 태그 목록 조회, tag cloud, 자동완성 endpoint는 Sprint 3 필수 범위가 아니므로 후속 후보로 남겼다.
- cursor paging은 Sprint 3 필수 범위가 아니므로 후속 리팩토링 후보로 남겼다.

## 다음 스프린트로 넘길 항목

- RAG, MCP, Agent를 하나의 게시판 경험으로 묶는 AI 기능 시나리오 확정
- RAG 데이터 범위에 게시글, 댓글, 태그를 어디까지 포함할지 결정
- embedding 저장 위치와 생성 시점 결정
- LLM Provider와 Embedding Model 후보 선정
- MCP 외부 서비스와 Agent tool 목록 선정
