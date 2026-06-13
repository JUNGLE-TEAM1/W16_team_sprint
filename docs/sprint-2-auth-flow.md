# 스프린트 2 인증/인가 흐름

이번 스프린트 예제는 같은 사용자 계정으로 세 가지 인증 방식을 비교합니다.

## 공통 사용자 등록

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"team1","password":"password123","display_name":"Team One"}'
```

사용자 비밀번호는 DB에 원문으로 저장하지 않고 PBKDF2 해시로 저장합니다.

## 1. Session 방식

```text
로그인 -> 서버가 세션 ID 생성 -> 세션 ID 해시를 DB에 저장 -> 브라우저에는 HttpOnly cookie 저장
요청 -> 브라우저가 cookie 자동 전송 -> 서버가 DB 세션 조회 -> 현재 사용자 확인
```

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/session/login \
  -H "Content-Type: application/json" \
  -d '{"username":"team1","password":"password123"}'
```

```bash
curl http://127.0.0.1:8000/api/v1/auth/session/me \
  -b "session_id=<login response cookie>"
```

특징:

- 서버가 세션 상태를 저장합니다.
- 브라우저 기반 서비스와 잘 맞습니다.
- cookie를 쓰므로 CSRF 방어 전략을 함께 결정해야 합니다.

## 2. JWT access token 방식

```text
로그인 -> 서버가 짧은 만료 시간의 access token 발급
요청 -> 클라이언트가 Authorization: Bearer <token> 전송 -> 서버가 서명/만료 검증
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/jwt/login \
  -H "Content-Type: application/json" \
  -d '{"username":"team1","password":"password123"}'
```

```bash
curl http://127.0.0.1:8000/api/v1/auth/jwt/me \
  -H "Authorization: Bearer <access_token>"
```

특징:

- 서버가 access token 상태를 저장하지 않습니다.
- 토큰 만료 전 강제 로그아웃/폐기가 어렵습니다.
- access token 저장 위치에 따라 XSS 위험이 달라집니다.

## 3. access token + refresh token 방식

```text
로그인 -> access token + refresh token 발급
요청 -> access token으로 API 호출
만료 -> refresh token으로 새 access token과 새 refresh token 재발급
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token-pair/login \
  -H "Content-Type: application/json" \
  -d '{"username":"team1","password":"password123"}'
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token-pair/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

특징:

- access token은 짧게, refresh token은 길게 가져갈 수 있습니다.
- refresh token은 DB에 해시로 저장하고 재발급 시 회전합니다.
- refresh token 탈취를 고려해 재사용 감지, 기기별 폐기, 저장 위치 정책이 필요합니다.

## 구현 파일

- `backend/app/api/v1/auth.py`: 인증 API endpoint
- `backend/app/services/auth_service.py`: 인증 비즈니스 로직
- `backend/app/repositories/auth_repository.py`: 세션/refresh token 저장소
- `backend/app/repositories/user_repository.py`: 사용자 저장소
- `backend/app/models/user.py`: 사용자 테이블
- `backend/app/models/auth.py`: session, refresh token 테이블
- `backend/app/core/security.py`: 비밀번호 해시, opaque token, JWT 유틸
