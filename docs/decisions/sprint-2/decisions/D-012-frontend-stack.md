# D-012. 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가?

Date: 2026-06-15
Sprint: 2
Level: 3
Status: Accepted
Implementation: Completed
Owner: User
Chosen: A. Vite + React + TypeScript 앱을 `frontend/`에 만든다.

## Evaluation Status

Current Evaluation: Pass

Reason:
- 사용자는 A를 명확히 선택했다.
- 현대 프론트엔드 구조 학습과 이후 확장성을 이유로 들었다.
- 새 의존성 비용은 이후 구조화된 인터페이스에 도움이 된다면 감수 가능하다고 판단했다.
- 앱 디렉터리는 `frontend/`로 둔다.
- token 저장 방식은 Sprint 1 인증 흐름과 일관되게 `localStorage` + `Authorization: Bearer <token>`으로 둔다.
- HttpOnly Cookie 전환은 백엔드 auth API 계약, CORS, CSRF 전략까지 바꾸므로 추후 보안 개선 Decision으로 분리한다.

## 1. 현재 분기 위치

Roadmap:
- `docs/decisions/sprint-2/ROADMAP.md`

선행 결정:
- D-009: 댓글 모델은 `id`, `post_id`, `user_id`, `content`, `created_at`, `updated_at`을 가진다.
- D-010: 댓글 API는 게시글 하위 nested API로 통일한다.
- D-011: 이번 repository에 Sprint 2 최소 프론트엔드 화면을 구현한다.

현재 Decision:
- D-012. 프론트엔드 스택과 앱 구조를 어떻게 둘 것인가?

이번 선택으로 자동 확정하지 않는 것:
- 화면의 세부 디자인
- Sprint 3 검색/태그/페이징 UI
- 배포 방식

## 2. 한 줄 요약

이번 결정은 새 프론트엔드 앱을 어떤 기술과 디렉터리 구조로 만들지 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- 프론트엔드 기술 스택
- 빌드 도구
- 앱 디렉터리 위치
- token 저장 방식의 기본 방향

## 4. 왜 먼저 결정해야 하나?

프론트엔드는 현재 repository에 새로 생기는 큰 구조다.

스택에 따라 다음이 달라진다.

- `package.json`과 의존성
- dev server 실행 방법
- API client 구성
- 라우팅 방식
- 테스트/브라우저 검증 방식
- 이후 Sprint 3 UI 확장 방식

## 5. 선택지

### A. Vite + React + TypeScript 앱을 `frontend/`에 만든다.

구성:
- `frontend/package.json`
- Vite
- React
- TypeScript
- fetch 기반 API client
- token은 우선 `localStorage`에 저장

의미:
- 이후 Sprint 3 검색/페이징 UI 확장에 유리하다.
- 새 의존성은 가장 많다.
- 현대적인 앱 구조를 학습하기 좋다.

### B. Vite + vanilla TypeScript 앱을 `frontend/`에 만든다.

구성:
- `frontend/package.json`
- Vite
- TypeScript
- 직접 DOM 렌더링
- token은 우선 `localStorage`에 저장

의미:
- React 의존성 없이 최소 화면을 구현한다.
- 상태와 라우팅을 직접 관리해야 한다.
- UI가 커지면 유지보수성이 빠르게 떨어질 수 있다.

### C. 정적 HTML/CSS/JS를 `frontend/`에 만든다.

구성:
- `frontend/index.html`
- `frontend/styles.css`
- `frontend/app.js`
- 별도 빌드 도구 없음
- token은 우선 `localStorage`에 저장

의미:
- 의존성이 가장 적다.
- 실행과 배포가 단순하다.
- 이후 Sprint 3 이상의 UI 확장에는 한계가 있다.

## 6. 선택지 비교

| 기준 | A. Vite React TS | B. Vite Vanilla TS | C. 정적 HTML/JS |
| --- | --- | --- | --- |
| 새 의존성 | 높음 | 중간 | 낮음 |
| Sprint 2 구현 속도 | 중간 | 중간 | 높음 |
| 이후 Sprint 확장성 | 높음 | 중간 | 낮음 |
| 코드 구조 학습 가치 | 높음 | 중간 | 낮음 |
| 검증 편의성 | 높음 | 중간 | 중간 |
| 되돌리기 비용 | 높음 | 중간 | 낮음 |

## 7. Codex 추천

추천: A

이유:
- Sprint 3에서 검색/페이징/태그 화면이 이어질 가능성이 높다.
- 로그인 상태, 게시글 상세, 댓글 목록/입력처럼 상태가 있는 화면을 React 컴포넌트로 나누면 설명과 유지보수가 쉽다.
- TypeScript를 쓰면 API 응답 계약을 프론트엔드 타입으로 표현할 수 있다.
- 새 의존성 비용은 있지만 D-011에서 이미 프론트엔드 앱 도입을 결정했으므로 확장성 쪽 이점이 더 크다.

## 8. Pass 기준

사용자 답변이 Pass 되려면 다음을 포함해야 한다.

- A, B, C 중 하나를 명확히 선택한다.
- 새 의존성 비용과 이후 확장성 trade-off를 이해한다.
- 앱 디렉터리를 `frontend/`로 둘지 확인한다.
- token 저장을 우선 `localStorage`로 둘지 확인한다.
- 세부 디자인과 Sprint 3 기능은 이번 결정으로 자동 확정하지 않는다는 점을 인정한다.

## 9. 사용자 답변 템플릿

```md
선택:

이유:

새 의존성 비용에 대한 생각:

앱 디렉터리:

token 저장 방식:

아직 다음 분기로 남겨둘 것:
```

## 10. Lowered Decisions

아직 없음.

## 11. Q&A

### Q1. 사용자 1차 답변 평가

사용자 답변:

```md
선택: A

이유: 현대 프론트 엔드 구조를 학습하기 위해서, 이후 확장에 용이할 거라 판단

새 의존성 비용에 대한 생각: 비용이 별로 크다고 생각안함. 어짜피 구조화되어잇는 인터페이스라 이후로 도움이 되면 된다 생각

앱 디렉터리:

token 저장 방식:

아직 다음 분기로 남겨둘 것:
```

Codex 평가:
- Hold

좋은 점:
- A 선택이 명확하다.
- 현대 프론트엔드 구조 학습과 이후 확장성을 선택 이유로 제시했다.
- 새 의존성 비용을 감수할 수 있다는 판단이 명확하다.

보완이 필요한 점:
- 앱 디렉터리가 비어 있다. 추천안은 `frontend/`다.
- token 저장 방식이 비어 있다. 추천안은 Sprint 2 최소 구현 기준으로 `localStorage`다.
- 아직 다음 분기로 남겨둘 항목이 비어 있다. 디자인 세부사항, Sprint 3 검색/태그/페이징 UI, 배포 방식은 이번 결정으로 자동 확정하지 않는 것으로 정리할 수 있다.

### Q2. 사용자 token 저장 방식 답변 평가

Codex 설명:

```md
token 저장 방식 후보:
1. localStorage
2. sessionStorage
3. HttpOnly Secure Cookie
```

사용자 답변:

```md
3번으로 할래
```

Codex 평가:
- Hold

좋은 점:
- token 저장 방향을 HttpOnly Cookie로 명확히 선택했다.
- XSS로부터 token을 JS가 직접 읽지 못하게 하는 보안 방향이다.

보완이 필요한 점:
- HttpOnly Cookie는 단순 프론트엔드 저장 방식이 아니라 백엔드 auth API 계약을 바꾸는 선택이다.
- 로그인 응답은 JSON token 저장 중심에서 `Set-Cookie` 중심으로 바뀐다.
- 보호 API 호출은 `Authorization: Bearer <token>` 중심에서 cookie credential 포함 요청으로 바뀔 수 있다.
- 쿠키 기반 상태 변경 요청에는 CSRF token/header 전략이 필요하다.
- CORS도 credential 허용 방식으로 조정해야 한다.
- 따라서 D-012의 프론트엔드 스택 결정만으로 자동 확정하기 어렵고, 별도 Level 3 auth/token transport Decision으로 분리할 필요가 있다.

### Q3. 사용자 token 저장 방식 최종 방향 평가

Codex 설명:

```md
Sprint 1의 기존 흐름은 login 응답으로 token을 받고, 프론트가 저장한 뒤,
보호 API 요청에 `Authorization: Bearer <token>`을 붙이는 방식이다.

HttpOnly Cookie로 바꾸면 백엔드 auth API 계약, CORS, CSRF 전략까지 재설계해야 한다.
일관성 유지 기준으로는 이번 Sprint 2에서 localStorage + Bearer token이 적합하다.
```

사용자 답변:

```md
음 그러면 일단은 이방식으로 하자
```

Codex 평가:
- Hold

좋은 점:
- Sprint 2에서는 기존 Sprint 1 인증 흐름과 일관되게 Bearer token 방식을 유지하는 방향으로 정리됐다.
- token 저장 방식은 `localStorage`로 두고, 보호 API 요청에는 `Authorization: Bearer <token>`을 사용한다.
- HttpOnly Cookie 전환은 백엔드 auth API 계약까지 바뀌는 별도 보안 개선 분기로 남긴다.

보완이 필요한 점:
- 앱 디렉터리 확인이 아직 비어 있다. 추천안은 `frontend/`다.
- 아직 다음 분기로 남겨둘 항목도 최종 확인이 필요하다. 추천안은 화면 세부 디자인, Sprint 3 검색/태그/페이징 UI, 배포 방식이다.

### Q4. 사용자 최종 확인 평가

Codex 확인:

```md
앱 디렉터리: frontend/
아직 다음 분기로 남겨둘 것: 화면 세부 디자인, Sprint 3 검색/태그/페이징 UI, 배포 방식
```

사용자 답변:

```md
문제는 없어보이네 반영해
```

Codex 평가:
- Pass

통과 이유:
- A 선택이 명확하다.
- 앱 디렉터리를 `frontend/`로 두는 데 동의했다.
- token 저장 방식은 `localStorage`, API 인증 방식은 Bearer token으로 정리됐다.
- 화면 세부 디자인, Sprint 3 검색/태그/페이징 UI, 배포 방식은 이번 결정으로 자동 확정하지 않는다.

## 12. 롤백 계획

예상 변경 파일:

- `frontend/`
- `frontend/package.json`
- `frontend/src/` 또는 정적 파일
- README 실행 안내

DB 영향:
- 없음

롤백 방법:
- 새 프론트엔드 앱 디렉터리와 의존성 파일을 제거한다.
- 백엔드 댓글 API 구현과 분리해 되돌릴 수 있게 유지한다.

롤백 확인:

```bash
python3 -m pytest backend/tests
```

재검토 조건:
- 선택한 스택이 Sprint 2 최소 화면 구현에 과하다고 판단된다.
- 설치/실행 환경 문제로 dev server 검증이 어렵다.
- 이후 Sprint 3 화면 확장 요구가 크게 달라진다.

## 12.1 Pre-Implementation Notes

Recorded: 2026-06-15

선택:
- A. Vite + React + TypeScript 앱을 `frontend/`에 만든다.

구현 전 상태:
- 현재 repository에는 프론트엔드 앱 구조가 없다.
- Sprint 2 백엔드 댓글 API도 아직 구현 전이다.

확정 범위:
- `frontend/` 디렉터리 추가
- Vite + React + TypeScript
- token은 `localStorage`에 저장
- 보호 API 요청은 `Authorization: Bearer <token>` 사용
- HttpOnly Cookie는 이번 Sprint 2에서 적용하지 않는다.

이번 결정으로 확정하지 않는 것:
- 화면 세부 디자인
- Sprint 3 검색/태그/페이징 UI
- 배포 방식

## 13. 다음 분기

D-012가 Pass되었으므로 남은 Level 2 후보를 재분류하고 Implementation Batch Snapshot을 기록한다.

## 14. 구현 결과

Completed: 2026-06-15

구현 내용:
- `frontend/`에 Vite + React + TypeScript 앱을 추가했다.
- token은 `localStorage`에 저장한다.
- 보호 API 요청에는 `Authorization: Bearer <token>`을 사용한다.
- Vite/esbuild audit 취약점은 Vite 8 계열로 업데이트해 해소했다.

검증:
- `cd frontend && npm test` -> `1 passed`
- `cd frontend && npm run build` -> 성공
- `cd frontend && npm audit --json` -> `0 vulnerabilities`
