# D-012 Frontend Stack Q&A

Date: 2026-06-15
Sprint: 2
Decision: D-012. 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가?

## Final Accepted Prompt

통과된 Decision:
- D-012. 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가?

사용자 최종 답변:

```md
선택: A

이유: 현대 프론트엔드 구조를 학습하고 이후 확장에 용이하다고 판단한다.

새 의존성 비용에 대한 생각: 비용이 크게 문제 된다고 보지 않는다. 구조화된 인터페이스가 이후에 도움이 되면 된다.

앱 디렉터리: `frontend/`

token 저장 방식: `localStorage`

API 인증 방식: `Authorization: Bearer <token>`

아직 다음 분기로 남겨둘 것: 화면 세부 디자인, Sprint 3 검색/태그/페이징 UI, 배포 방식
```

Codex 평가:
- Pass

Pass 이유:
- A 선택이 명확하다.
- 새 의존성 비용과 이후 확장성 trade-off를 이해했다.
- 앱 디렉터리를 `frontend/`로 확정했다.
- Sprint 1 인증 흐름과 일관되게 `localStorage` + Bearer token을 선택했다.
- HttpOnly Cookie는 백엔드 auth API 계약, CORS, CSRF 전략까지 바꾸는 별도 보안 개선 Decision으로 분리했다.

보완 질문 여부:
- 있음.
- token 저장 방식 후보를 설명했고, HttpOnly Cookie 선택 시 auth API 재설계가 필요함을 확인했다.
- 최종적으로 이번 Sprint 2에서는 Bearer token 흐름을 유지하기로 정리했다.

아직 남은 후속 분기:
- 없음. 필수 Level 3 후보는 모두 Pass.
- 댓글 권한 검사 계층, 게시글 CRUD 보강, 세부 UI 구현 방식은 Level 1/2로 처리한다.

최종 결론:
- Sprint 2는 백엔드 댓글 CRUD와 Vite + React + TypeScript 프론트엔드 최소 화면을 구현한다.
