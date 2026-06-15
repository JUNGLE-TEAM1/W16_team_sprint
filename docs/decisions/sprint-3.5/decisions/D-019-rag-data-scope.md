# D-019: RAG 데이터 범위를 어디까지 둘 것인가?

Sprint: 3.5
Date: 2026-06-15
Level: 3
Status: Accepted
Implementation: Planned
Chosen: A. 게시글 `title`, `content`, `tags`만 사용한다
Owner: 사용자

Documents:
- Decision: `docs/decisions/sprint-3.5/decisions/D-019-rag-data-scope.md`
- Roadmap: `docs/decisions/sprint-3.5/ROADMAP.md`
- Troubleshooting: Pending
- Rollback: Pending

## 1. 현재 분기

D-018에서 AI 사용자 흐름은 글 작성 시 유사 게시글 추천과 중복 게시글 방지로 확정했다.

이제 RAG가 어떤 데이터를 embedding하고 검색할지 정해야 한다.

Sprint 3까지의 게시판 데이터는 다음을 가진다.

- 게시글 `title`
- 게시글 `content`
- 게시글 `tags`
- 댓글
- 작성자 정보

이번 Decision은 similarity search의 1차 검색 대상과 embedding 입력 범위를 정한다.

## 2. 이번에 선택하지 않는 분기

이번 Decision은 RAG 데이터 범위만 확정한다.

다음 항목은 이번 선택으로 자동 확정하지 않는다.

- embedding 저장 위치
- embedding 생성 시점
- embedding model
- 유사도 threshold
- top-3 또는 top-5 개수
- LLM 요약 여부와 요약 프롬프트
- 댓글 요약을 어떤 시점에 만들지

## 3. 선택지

### A. 게시글 `title`, `content`, `tags`만 사용한다

게시글 단위 embedding을 만든다.

장점:
- 구현이 가장 단순하다.
- 글 작성 시 유사 게시글 추천 목적에 충분히 맞다.
- `post_embeddings` 별도 테이블과 잘 맞는다.
- 댓글 권한, 댓글 변경 시 재색인 문제를 피할 수 있다.

단점:
- 댓글에만 있는 해결책이나 핵심 답변은 검색 품질에 반영되지 않는다.
- 기존 글의 댓글 요약은 후속 기능으로 따로 처리해야 한다.

### B. 게시글 `title`, `content`, `tags`와 댓글 일부를 함께 사용한다

게시글 본문과 댓글 내용을 합쳐 게시글 단위 embedding을 만든다.

장점:
- 실제 해결책이 댓글에 있는 경우 검색 품질이 좋아질 수 있다.
- 유사 글 추천 결과에서 핵심 답변 요약까지 이어가기 쉽다.

단점:
- 댓글 작성/삭제/수정 시 embedding 재생성 전략이 필요하다.
- embedding 입력 길이와 snapshot 관리가 복잡해진다.
- Sprint 4 MVP 범위가 커질 수 있다.

### C. 문단 또는 댓글 단위 chunking까지 포함한다

게시글과 댓글을 작은 chunk로 나눠 embedding한다.

장점:
- 검색 정밀도가 가장 좋을 수 있다.
- 긴 게시글과 많은 댓글에도 부분 검색이 가능하다.

단점:
- chunk 모델, parent post 매핑, reranking, UI 표시 방식이 필요하다.
- Sprint 4 MVP 범위에는 과하다.
- 발표 설명은 좋지만 구현 리스크가 커진다.

## 4. Codex 추천

추천은 A다.

팀 싱크에서 제안한 첫 구조도 게시글의 `title`, `content`, `tags` embedding이며, Sprint 4 MVP 목표에 가장 잘 맞는다.

댓글은 검색 대상에 바로 넣기보다, 시간이 남으면 기존 글의 댓글 요약을 별도 후속 기능으로 확장하는 편이 안전하다.

## 5. Pass 기준

사용자 답변은 다음을 포함해야 Pass로 본다.

- 선택지가 명확해야 한다.
- 그 선택을 고른 이유가 있어야 한다.
- 게시글/태그/댓글 중 무엇이 embedding 입력에 들어가는지 구분해야 한다.
- DB/API/테스트 중 어떤 항목이 후속으로 바뀔 수 있는지 언급해야 한다.
- 이번 Decision 이후에도 남는 후속 분기를 구분해야 한다.

## 6. 답변 템플릿

```md
선택:

이유:

embedding 입력 범위:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

## 7. 롤백 계획 초안

이 Decision 자체는 아직 구현을 변경하지 않는다.

구현 단계에서 바뀔 수 있는 범위:
- embedding 생성 서비스
- embedding snapshot 필드
- 유사 게시글 추천 API
- 관련 테스트 fixture

되돌릴 때 확인할 범위:
- RAG 모델과 서비스
- post embedding 생성 코드
- 유사 글 추천 응답 schema

데이터 손실 가능성:
- 이 Decision 단계에서는 없음
- 후속 구현에서 embedding 테이블 생성 시 별도 판단한다.

원래 상태 보장:
- 기존 게시글 CRUD, 태그 검색, 댓글 테스트가 계속 통과해야 한다.

재검토 조건:
- 팀이 댓글 기반 해결 요약을 Sprint 4 필수 범위로 올리는 경우
- 게시글 본문만으로 유사 글 품질이 발표에 부족한 경우

## 8. Lowered Decisions

아직 없음.

## 9. Q&A

### 2026-06-15 사용자 1차 답변

사용자 답변:

```md
선택: A

이유: post_embeddings 테이블과 pgvector 검색으로 바로 이어가기 쉬움, 그리고 지금 미리 분리 해놓아야 스프린트4에서 구현이 편할것 같음
embedding 입력 범위:

DB/API/테스트 영향:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택지는 명확하다.
- 이유는 Sprint 4 구현과 `post_embeddings`/pgvector 연결성을 근거로 제시되어 충분하다.
- embedding 입력 범위, DB/API/테스트 영향, 후속 분기가 비어 있다.
- Pass 전 보완 질문이 필요하다.

### 2026-06-15 사용자 보완 답변

사용자 답변:
- Codex가 제시한 예시대로 진행한다.

정리된 최종 답변:

```md
선택: A

이유:
`post_embeddings` 테이블과 pgvector 검색으로 바로 이어가기 쉽고, 지금 미리 분리해 놓아야 Sprint 4에서 구현이 편하다.

embedding 입력 범위:
게시글의 `title`, `content`, `tags`만 embedding 입력에 포함한다. 댓글은 Sprint 4 MVP의 1차 embedding 입력에서는 제외한다.

DB/API/테스트 영향:
DB는 후속 Decision에서 `post_embeddings` 테이블을 검토하고, API는 유사 게시글 추천 API가 필요해질 수 있다. 테스트는 `title`/`content`/`tags` 기반으로 유사 게시글이 검색되는지 확인해야 한다.

아직 다음 분기로 남겨둘 것:
embedding 저장 위치, embedding 생성 시점, embedding model, 유사도 threshold, top-3/top-5 개수, 댓글 요약 포함 여부는 후속 Decision으로 남긴다.
```

Codex 평가:
- 선택지가 명확하다.
- embedding 입력 범위가 게시글 `title`, `content`, `tags`로 구분되었다.
- DB/API/테스트 영향이 언급되었다.
- 후속 분기가 구분되었다.
- Pass 처리한다.

## 10. Pre-Implementation Notes

현재 git 상태:
- 기존 Sprint 1~3 관련 변경과 `frontend/`, `docs/decisions/sprint-3.5/` 미추적 파일이 존재한다.
- 이 Decision의 현재 단계에서는 구현 파일을 변경하지 않았고, Decision 문서와 인덱스만 변경한다.

구현 전 확정된 범위:
- RAG의 1차 embedding 입력은 게시글의 `title`, `content`, `tags`로 둔다.
- 댓글은 Sprint 4 MVP의 1차 embedding 입력에서 제외한다.

아직 구현 전 확정되지 않은 범위:
- embedding 저장 위치
- embedding 생성 시점
- embedding model
- 유사도 threshold
- top-3/top-5 개수
- 댓글 요약 포함 여부
