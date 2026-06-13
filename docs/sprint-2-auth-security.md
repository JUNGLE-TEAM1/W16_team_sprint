# 스프린트 2: 인증/인가 + 보안

주제: 로그인 후 인증이 필요한 API를 호출할 때 전체 흐름은 어떻게 되는가?

## 실행해서 볼 API

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/session-action`
- `GET /api/v1/auth/admin/report`
- `GET /api/v1/security/study-guide`

## 데모 계정

- member: `member@sprint.local` / `password123`
- admin: `admin@sprint.local` / `admin123`

## 흐름

1. 로그인 요청이 들어오면 서버가 이메일/비밀번호를 검증한다.
2. 서버는 `user_sessions` row를 만들고 refresh token hash와 CSRF token을 저장한다.
3. 서버는 access token과 refresh token을 JWT로 발급한다.
4. 클라이언트는 `Authorization: Bearer <access_token>`으로 보호 API를 호출한다.
5. 서버는 JWT 서명, 만료, token type, session 상태를 검증한다.
6. 권한이 필요한 API는 role을 검사하고 부족하면 `403 FORBIDDEN`을 반환한다.
7. access token이 만료되면 refresh token으로 새 token pair를 발급받는다.
8. logout은 session을 revoke해서 refresh token 재사용을 막는다.

## 공부할 것

- Session: `user_sessions` 테이블에 서버 측 로그인 상태를 저장한다.
- JWT: access/refresh token에 `sub`, `role`, `type`, `sid`, `exp` claim을 담는다.
- access token / refresh token: access token은 짧게, refresh token은 길게 두고 refresh 때 회전한다.
- OAuth2/OIDC: 이 예제는 자체 로그인이고, 외부 IdP를 쓰면 authorization code, id token, userinfo 검증 흐름이 추가된다.
- CORS: `main.py`의 `CORSMiddleware`에서 허용 origin을 제한한다.
- CSRF: 쿠키 기반 인증의 상태 변경 요청은 `X-CSRF-Token` 검증이 필요하다.
- HTTPS: 운영에서는 TLS 뒤에서만 token/cookie를 주고받는다.
- Rate limit: `SimpleRateLimitMiddleware`가 IP+path 기준으로 과도한 요청에 `429`를 반환한다.
- 권한 처리: `/api/v1/auth/admin/report`는 admin role만 접근한다.

## 싱크 때 확인할 질문

- 로그인의 resource는 session인가 token인가 user인가?
- 로그인 endpoint와 보호 API endpoint는 어떻게 나눌 것인가?
- request body에는 이메일/비밀번호 외에 무엇이 필요한가?
- 로그인 성공 response에는 access token, refresh token, 만료 시간이 어떻게 들어가는가?
- 인증 실패는 401, 권한 부족은 403으로 구분하고 있는가?
- access token은 어디에 저장하고 refresh token은 어디에 저장할 것인가?
- refresh token rotation과 재사용 감지는 필요한가?
- 서버 DB에는 users, user_sessions 같은 테이블이 필요한가?
- 권한 role 또는 permission은 JWT claim에 넣을 것인가 DB에서 매번 볼 것인가?
- CORS 허용 origin은 어디까지 열 것인가?
- 쿠키 기반 인증이면 CSRF 토큰을 어느 요청에서 검사할 것인가?
- HTTPS는 로컬/운영에서 어디가 담당하는가?
- Rate limit 기준은 IP, user, endpoint 중 무엇으로 잡을 것인가?
- 프론트는 로그인 loading/error/success와 token 만료를 어떻게 처리하는가?
