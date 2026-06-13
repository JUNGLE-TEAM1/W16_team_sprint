# Sprint 2: 인증/인가 + 보안

## 주제

로그인 후 인증이 필요한 API를 호출할 때 전체 흐름은 어떻게 되는가?

## 구현된 흐름

```text
회원가입 -> 로그인 -> access token / refresh token / session cookie / csrf token 발급
-> 보호 API 호출 -> 사용자 식별 -> 권한 확인 -> CORS/CSRF/Rate limit 통과
-> 비즈니스 로직 -> DB 저장 -> 응답
```

## 구현된 API

| 기능 | Endpoint | 의미 |
| --- | --- | --- |
| 회원가입 | `POST /api/v1/auth/register` | 이메일, 비밀번호, role로 사용자 생성 |
| 로그인 | `POST /api/v1/auth/login` | access token, refresh token, session cookie, csrf token 발급 |
| 내 정보 | `GET /api/v1/auth/me` | Bearer token 또는 session cookie로 사용자 식별 |
| 토큰 재발급 | `POST /api/v1/auth/refresh` | refresh token을 회전시키고 새 토큰 발급 |
| 관리자 사용자 목록 | `GET /api/v1/admin/users` | admin role만 접근 가능 |
| 보호 게시글 작성 | `POST /api/v1/posts/protected` | 로그인 사용자만 작성 가능, cookie 방식은 CSRF 필요 |
| AI 요청 | `POST /api/v1/ai/requests` | 로그인 사용자만 AI 요청 기록 생성 |

## status code 기준

- `401 Unauthorized`: 로그인 증명이 없거나 access token/session/refresh token이 잘못됨
- `403 Forbidden`: 로그인은 됐지만 권한이 부족하거나 CSRF 검증 실패
- `409 Conflict`: 이미 가입된 이메일
- `422 Unprocessable Entity`: request body validation 실패
- `429 Too Many Requests`: 로그인 요청 rate limit 초과

## 싱크 때 확인할 질문

1. 인증과 인가는 무엇이 다른가?
2. 우리 서비스에 로그인은 꼭 필요한가?
3. JWT를 쓴다면 access token은 어디에 저장하는가?
4. refresh token은 필요한가?
5. 백엔드는 사용자를 어떻게 식별하는가?
6. 인증 실패와 권한 실패는 어떤 status code인가?
7. CORS는 왜 생기는가?
8. CSRF는 언제 문제가 되는가?

## 코드 위치

```text
backend/app/api/v1/auth.py              # register/login/refresh/me
backend/app/api/v1/admin.py             # admin-only API
backend/app/api/v1/ai_requests.py       # authenticated AI request API
backend/app/api/deps.py                 # current user, admin, CSRF dependency
backend/app/core/security.py            # password hash, access token signing/verification
backend/app/core/rate_limit.py          # login rate limit middleware
backend/app/models/user.py              # users, sessions, refresh tokens
backend/app/models/ai_request.py        # AI request record
backend/tests/test_auth_security_flow.py # auth/security contract tests
```
