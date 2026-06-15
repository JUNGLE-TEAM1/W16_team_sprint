# D-021: Embedding 생성 시점을 어떻게 둘 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: A. 게시글 작성/수정 성공 후 즉시 embedding을 생성하거나 갱신한다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-021-embedding-generation-timing.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정했다.

D-019에서 RAG의 1차 embedding 입력은 게시글의 `title`, `content`, `tags`로 확정했다.

D-020에서 embedding 저장 위치는 `post_embeddings` 별도 테이블로 확정했다.

이제 게시글 embedding을 언제 생성하고 갱신할지 정해야 한다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 embedding 생성 시점만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- embedding model과 vector dimension
- API 실패 시 사용자 메시지
- embedding 실패 재시도 정책
- 관리용 재색인 API 또는 CLI 여부
- 유사도 threshold
- top-3/top-5 개수

## 3. 선택지

### A. 게시글 작성/수정 성공 후 즉시 embedding을 생성하거나 갱신한다

게시글 저장이 끝난 뒤 `title`, `content`, `tags`로 embedding을 만들고 `post_embeddings`를 upsert한다.

장점:
- 게시글 데이터와 embedding이 비교적 최신 상태로 유지된다.
- 유사 게시글 추천 API가 저장된 embedding을 바로 사용할 수 있다.
- Sprint 4 완료 기준인 게시글 저장 시 embedding 저장 흐름과 잘 맞다.

단점:
- embedding provider 실패가 게시글 작성/수정 흐름에 영향을 줄 수 있다.
- API 응답 시간이 늘어날 수 있다.
- 실패 시 게시글 저장은 성공했지만 embedding 저장은 실패한 부분 성공 상태를 다뤄야 한다.

### B. 글 작성 화면에서 사용자가 “유사 글 찾기” 버튼을 누를 때만 query embedding을 만든다

기존 게시글 embedding은 별도 준비되어 있다고 보고, 초안 검색용 query embedding만 버튼 시점에 만든다.

장점:
- 작성 중인 초안 검색 흐름과 직관적으로 맞다.
- 저장 전 초안도 검색할 수 있다.

단점:
- 기존 게시글 embedding을 언제 만들지 별도 결정이 필요하다.
- 저장된 게시글의 embedding 갱신 문제가 남는다.
- 이 선택만으로는 `post_embeddings` 테이블을 채우는 전략이 부족하다.

### C. 수동 재색인 또는 관리 명령으로만 생성한다

게시글 생성/수정 API와 분리해서 관리자가 재색인을 실행할 때 embedding을 만든다.

장점:
- 게시글 작성/수정 API가 embedding provider 실패에 영향을 덜 받는다.
- 배치 처리와 재시도 전략을 분리하기 쉽다.

단점:
- Sprint 4 MVP에서는 구현 흐름이 더 복잡해질 수 있다.
- 새 글이 추천 검색에 늦게 반영된다.
- 발표에서 사용자 작성 흐름과 RAG 인덱싱 흐름이 분리되어 보일 수 있다.

## 4. Codex 추천

추천은 A다.

Sprint 4의 목표가 게시글 저장 시 embedding 결과를 PostgreSQL에 저장하고, 글 작성 화면에서 유사 게시글을 검색하는 것이므로 작성/수정 성공 후 즉시 upsert하는 방식이 가장 설명하기 쉽다.

단, embedding provider 실패가 게시글 저장 자체를 깨뜨리지 않도록 후속 구현에서는 부분 실패 처리나 재시도 후보를 남기는 것이 좋다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- 게시글 작성/수정 흐름과 embedding 생성 흐름의 관계가 설명되어야 한다.
- DB/API/테스트 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

게시글 작성/수정과 embedding 생성 관계:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- 게시글 생성/수정 service 흐름
- embedding 생성 service
- `post_embeddings` upsert repository
- embedding 실패 처리
- 관련 테스트

되돌릴 때 확인할 범위:
- 게시글 작성/수정 API에서 embedding 호출 제거
- embedding upsert 호출 제거
- 부분 실패 처리 코드 제거 또는 비활성화

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- 후속 구현에서 생성된 embedding row는 재생성 가능한 파생 데이터다.

원래 상태 보장:
- embedding provider가 실패해도 기존 게시글 CRUD 테스트의 기대 동작이 명확해야 한다.
- 기존 게시글 CRUD, 태그 검색, 댓글 테스트가 계속 통과해야 한다.

재검토 조건:
- embedding provider 응답 시간이 너무 길어 게시글 작성 UX를 해치는 경우
- provider 실패율이 높아 게시글 작성 흐름이 불안정해지는 경우
- 팀이 인덱싱을 배치/관리 명령 중심으로 설명하기로 바꾸는 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: 미리 생성해놔야 나중에 가져다 쓰기 편해보임 유사 게시글 검색 같은 기능 등에

게시글 작성/수정과 embedding 생성 관계: 작성 또는 수정시에 임베딩 생성

DB/API/테스트 영향: 작성 수정시에 db에 생성/수정이 필요하고, 관련api가 필요함, 테스트는 기본 임베딩 생성 확인

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 유사 게시글 검색에서 미리 생성된 embedding을 재사용하기 위한 것으로 충분하다.
- 게시글 작성/수정과 embedding 생성 관계가 설명되었다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 후속 분기 예시를 적용한다.

정리된 최종 답변:

```md
선택: A

이유:
미리 생성해놔야 유사 게시글 검색 같은 기능에서 나중에 가져다 쓰기 편하다.

게시글 작성/수정과 embedding 생성 관계:
게시글 작성 또는 수정 성공 후 embedding을 생성하거나 갱신한다.

DB/API/테스트 영향:
작성/수정 시 DB에 embedding row 생성/수정이 필요하고, 관련 API 흐름이 필요하다. 테스트는 기본 embedding 생성과 갱신을 확인한다.

아직 다음 분기로 남겨둘 것:
embedding model과 vector dimension, provider 실패 시 처리, 재시도/재색인 방식, 유사도 threshold, top-3/top-5 개수는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- 게시글 작성/수정과 embedding 생성 관계가 설명되었다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- 게시글 작성 또는 수정 성공 후 embedding을 생성하거나 갱신한다.
- 저장 위치는 D-020에 따라 `post_embeddings` 별도 테이블이다.

아직 구현 전 확정되지 않은 범위:
- embedding model과 vector dimension
- provider 실패 시 처리
- 재시도/재색인 방식
- 유사도 threshold
- top-3/top-5 개수
