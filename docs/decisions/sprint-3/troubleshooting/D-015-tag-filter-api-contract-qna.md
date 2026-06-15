# D-015 태그 필터 API 계약 Q&A

## Final Accepted Prompt

### 통과된 Decision

D-015. 태그로 게시글을 조회하는 API 계약을 어떻게 둘 것인가?

### 사용자 최종 답변

사용자는 선택지 A를 선택했다.

> A로 진행해야 뒤에 기능 개발할때 확장이 용이함

보완 답변:

> 맞아
> join으로 하는것은 맞고 주소방식맞고, 테스트도 다 맞네 진행해

### Codex 평가

Final Evaluation: Pass

Pass 이유:
- 사용자가 선택지 A를 명확히 골랐다.
- 전용 태그 endpoint, tag cloud, 자동완성 API는 지금 만들지 않고 게시글 목록 query에 합치는 trade-off를 확인했다.
- DB/repository는 `tags` 관계를 join해서 필터링한다는 점을 확인했다.
- API는 `GET /api/v1/posts?tag=fastapi` 방식으로 진행한다고 확인했다.
- 테스트는 태그가 있는 글만 조회되고, 없는 태그는 빈 결과가 나오는지 확인한다고 정리했다.

보완 질문 여부:
- 질문함.
- 빈 항목이 있던 trade-off와 DB/API/테스트 영향을 확인했다.

### 아직 남은 후속 분기

- D-016. 게시글 목록 페이징 계약을 어떻게 둘 것인가?
- 게시글 목록 응답 shape를 list에서 metadata 포함 object로 바꿀 것인가?
- 검색은 제목/본문 `LIKE` 검색으로 시작할 것인가?
- 프론트엔드 목록 화면에서 검색/태그/페이징 상태를 URL query에 둘 것인가?

### 최종 결론

D-015는 통과되었지만 Sprint 3 구현 전 후속 필수 분기가 남아 있다.
다음으로 D-016을 진행한다.
