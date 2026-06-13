from fastapi import APIRouter

router = APIRouter(prefix="/security", tags=["security-study"])


@router.get("/study-guide")
def study_guide() -> dict:
    return {
        "sprint": "스프린트 2: 인증/인가 + 보안",
        "topic": "로그인 후 인증이 필요한 API를 호출할 때 전체 흐름은 어떻게 되는가?",
        "flow": [
            "POST /api/v1/auth/login 으로 이메일/비밀번호를 검증한다.",
            "서버는 user_sessions row를 만들고 access token과 refresh token을 발급한다.",
            "클라이언트는 Authorization: Bearer <access_token>으로 보호 API를 호출한다.",
            "access token이 만료되면 refresh token으로 /api/v1/auth/refresh를 호출한다.",
            "권한이 필요한 API는 role을 확인하고 403을 반환할 수 있다.",
            "logout은 서버 세션을 revoke해서 refresh token 재사용을 막는다.",
        ],
        "studyItems": {
            "Session": "서버 DB의 user_sessions가 로그인 상태, refresh token hash, CSRF token, 만료/폐기 시각을 가진다.",
            "JWT": "access/refresh token은 HS256 JWT 데모이며 sub, role, type, sid, exp claim을 담는다.",
            "access token / refresh token": "access token은 짧게, refresh token은 길게 두고 refresh 때 회전한다.",
            "OAuth2/OIDC": "이 예제는 자체 로그인이고, OAuth2/OIDC를 쓰면 외부 IdP가 인증하고 우리 서버는 code/id_token/userinfo를 검증한다.",
            "CORS": "main.py의 CORSMiddleware가 허용 origin을 제한한다.",
            "CSRF": "Authorization header 방식은 CSRF 위험이 작지만, 쿠키 세션 변경 요청은 X-CSRF-Token 검증이 필요하다.",
            "HTTPS": "운영에서는 TLS 뒤에서만 토큰/쿠키를 주고받아야 하며 HSTS와 Secure cookie를 사용한다.",
            "Rate limit": "SimpleRateLimitMiddleware가 IP+path 단위로 429를 반환하는 흐름을 보여준다.",
            "권한 처리": "/api/v1/auth/admin/report는 admin role만 접근 가능하다.",
        },
        "syncQuestions": [
            "로그인의 resource는 session인가 token인가 user인가?",
            "로그인 endpoint와 보호 API endpoint는 어떻게 나눌 것인가?",
            "request body에는 이메일/비밀번호 외에 무엇이 필요한가?",
            "로그인 성공 response에는 access token, refresh token, 만료 시간이 어떻게 들어가는가?",
            "인증 실패는 401, 권한 부족은 403으로 구분하고 있는가?",
            "access token은 어디에 저장하고 refresh token은 어디에 저장할 것인가?",
            "refresh token rotation과 재사용 감지는 필요한가?",
            "서버 DB에는 users, user_sessions 같은 테이블이 필요한가?",
            "권한 role 또는 permission은 JWT claim에 넣을 것인가 DB에서 매번 볼 것인가?",
            "CORS 허용 origin은 어디까지 열 것인가?",
            "쿠키 기반 인증이면 CSRF 토큰을 어느 요청에서 검사할 것인가?",
            "HTTPS는 로컬/운영에서 어디가 담당하는가?",
            "Rate limit 기준은 IP, user, endpoint 중 무엇으로 잡을 것인가?",
            "프론트는 로그인 loading/error/success와 token 만료를 어떻게 처리하는가?",
        ],
        "demoAccounts": [
            {"email": "member@sprint.local", "password": "password123", "role": "member"},
            {"email": "admin@sprint.local", "password": "admin123", "role": "admin"},
        ],
    }
