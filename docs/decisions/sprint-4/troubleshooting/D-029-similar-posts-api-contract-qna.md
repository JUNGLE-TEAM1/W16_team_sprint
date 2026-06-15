# D-029 Q&A: 유사 게시글 추천 API 계약

Date: 2026-06-15
Decision: `docs/decisions/sprint-4/decisions/D-029-similar-posts-api-contract.md`
Status: Accepted

## 1. 사용자 1차 답변

```md
선택: A

이유: 애초에 이 기능으로 만들려 했음

추천 기준: 작성 폼 입력값으로 유사 계시글 확인

DB/API/frontend/test 영향: 

trade-off:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- 선택과 추천 기준은 명확했다.
- DB/API/frontend/test 영향, trade-off, 후속 분기가 비어 있어 보완이 필요했다.

## 2. 보완 의견

사용자 의견:
- 유사 글을 찾는 것은 좋지만, 사용자가 판단할 지표가 있으면 좋겠다.
- 점수를 매기고 특정 점수를 초과하면 색을 다르게 표시하는 방식을 제안했다.

Codex 반영:
- API 응답에 `similarity`와 `similarity_level`을 포함한다.
- frontend는 `similarity_level`에 따라 색상 또는 강조 스타일을 다르게 표시한다.
- 정확한 high/medium/low 기준값은 후속 Level 2 결정으로 남긴다.

## 3. Final Accepted Prompt

통과된 Decision:
- D-029. 유사 게시글 추천 API 계약을 어떻게 둘 것인가?

사용자 답변과 보완 의견을 종합한 최종 답변:

```md
선택: A

이유:
애초에 작성 폼에서 유사 글을 확인하는 기능으로 만들려 했고, 글 저장 전 중복 가능성을 사용자가 판단할 수 있어야 한다.

추천 기준:
작성 폼 입력값인 `title`, `content`, `tags`를 기준으로 유사 게시글을 검색한다.

DB/API/frontend/test 영향:
DB는 저장된 `post_embeddings`를 조회한다. API는 `POST /api/v1/ai/similar-posts`로 작성 폼의 `title`, `content`, `tags`, `limit`를 받는다. 응답에는 유사 게시글 목록, `similarity`, `similarity_level`, 요약 메시지를 포함한다. frontend는 글 작성 화면에서 유사 글 찾기 버튼으로 호출하고, `similarity_level`에 따라 색상 또는 강조 스타일을 다르게 표시한다. 테스트는 입력값 embedding으로 유사 게시글이 반환되고 점수와 등급이 포함되는지 확인한다.

trade-off:
작성 전에 중복을 줄일 수 있지만, 입력 중인 내용을 API로 보내야 하고 요청 body가 커질 수 있다. 점수는 절대적인 정답률이 아니라 embedding 기준 유사도이므로 보조 판단 지표로 표시해야 한다.

아직 다음 분기로 남겨둘 것:
similarity threshold/top-N 정확한 기본값, LLM 요약 provider/prompt, 반복 실패 시 degraded 정책, background 재시도 방식은 다음 분기로 남긴다.
```

Codex 평가:
- 선택, 이유, 추천 기준, 영향 범위, trade-off, 후속 분기가 모두 충족되었다.

Pass 이유:
- 작성 전 preview API 기준과 응답 shape의 핵심 필드가 확정되었다.
- 사용자가 판단할 수 있는 유사도 점수와 등급 표시 기준이 API 계약에 포함되었다.

보완 질문 여부:
- 보완 의견을 받아 API 응답 계약에 반영하고 Pass 처리했다.

아직 남은 후속 분기:
- similarity threshold/top-N 기본값
- LLM 요약 방식
- 반복 실패 시 degraded 또는 점검 모드 정책
- background 재시도 방식

최종 결론:
- 추천 API는 `POST /api/v1/ai/similar-posts`로 둔다.
- 작성 폼 입력값을 기준으로 유사 게시글을 검색한다.
- 응답에는 `similarity`와 `similarity_level`을 포함한다.
