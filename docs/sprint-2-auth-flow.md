# 스프린트 2 Session 인증/인가 흐름

Sprint 2는 **Session only** 기준으로 진행합니다.

JWT access token과 access/refresh token pair 코드는 이번 구현에서 제거했습니다. OAuth/OIDC는 현재 MVP 필수 범위가 아니며, 추후 소셜 로그인이나 외부 서비스 권한 위임이 필요할 때 다시 다룹니다.

## 목표

```text
회원가입
-> Session 로그인
-> 현재 로그인 사용자 확인
-> 로그인 사용자만 게시글 작성
-> 로그아웃
```

## 공통 사용자 등록

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"team1","password":"password123","display_name":"Team One"}'
```

사용자 비밀번호는 DB에 원문으로 저장하지 않고 PBKDF2 해시로 저장합니다.

## Session 로그인

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/session/login \
  -H "Content-Type: application/json" \
  -d '{"username":"team1","password":"password123"}'
```

서버는 로그인 성공 시 원본 session token을 `HttpOnly` cookie로 내려줍니다.

DB에는 원본 token을 저장하지 않고 `token_hash`, `user_id`, `expires_at`만 저장합니다.

## 현재 사용자 확인

```bash
curl http://127.0.0.1:8000/api/v1/auth/session/me \
  -b "session_id=<login response cookie>"
```

흐름:

```text
Cookie session_id
-> 서버에서 session_id 원본 token을 hash
-> auth_sessions.token_hash 조회
-> expires_at 확인
-> users.id 조회
-> 현재 사용자 반환
```

## 게시글 작성

게시글 작성은 보호 API입니다. 로그인한 사용자의 session cookie가 필요합니다.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -b "session_id=<login response cookie>" \
  -d '{"title":"Sprint 2","content":"Session 인증으로 작성자를 연결합니다."}'
```

성공하면 서버는 `posts.author_id`에 현재 사용자의 id를 저장합니다.

## 로그아웃

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/session/logout \
  -b "session_id=<login response cookie>"
```

로그아웃 시 서버는 현재 세션 row를 삭제하고, 브라우저에는 `Delete-Cookie` 응답을 보냅니다.

## 구현 파일

- `frontend/src/App.jsx`: Session 전용 회원가입/로그인/내 정보/로그아웃/게시글 작성 UI
- `backend/app/api/v1/auth.py`: Session auth endpoint와 `get_session_user`
- `backend/app/services/auth_service.py`: 회원가입, 로그인, 세션 조회, 로그아웃 흐름
- `backend/app/repositories/auth_repository.py`: `auth_sessions` 조회/저장/삭제
- `backend/app/repositories/user_repository.py`: 사용자 조회/저장
- `backend/app/models/user.py`: `users` 테이블
- `backend/app/models/auth.py`: `auth_sessions` 테이블
- `backend/app/core/security.py`: 비밀번호 hash, opaque token 생성, session token hash
