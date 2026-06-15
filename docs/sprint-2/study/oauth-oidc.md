# OAuth2와 OIDC 쉽게 이해하기

## 이 문서의 목표

OAuth2와 OIDC는 처음 보면 용어가 많아서 어렵습니다.

이 문서에서는 먼저 딱 하나의 상황만 생각합니다.

```text
사용자가 우리 서비스에서 "Google로 로그인" 버튼을 누른다.
```

이때 실제로 무슨 일이 일어나는지 순서대로 이해하는 것이 목표입니다.

## 먼저 결론

소셜 로그인은 아래처럼 생각하면 됩니다.

```text
우리 서비스가 직접 비밀번호를 받지 않는다.
대신 Google에게 "이 사람이 누구인지 확인해줘"라고 맡긴다.
Google이 "이 사람은 a@example.com이 맞아"라고 알려준다.
우리 서비스는 그 정보를 보고 우리 서비스용 계정을 만들거나 찾는다.
마지막으로 우리 서비스가 자체 로그인 token/session을 발급한다.
```

중요한 점은 마지막 줄입니다.

```text
Google 로그인이 끝났다고 해서 Google token을 우리 서비스 로그인 token처럼 그대로 쓰는 것이 아니다.
Google로 신원 확인을 한 뒤, 우리 서비스가 사용할 session 또는 JWT를 따로 발급한다.
```

## 왜 이런 방식이 필요한가?

직접 로그인 방식에서는 사용자가 우리 서비스에 비밀번호를 입력합니다.

```text
사용자 -> 우리 서비스
email/password 전달
```

소셜 로그인에서는 사용자가 Google에만 비밀번호를 입력합니다.

```text
사용자 -> Google
Google 계정으로 로그인

Google -> 우리 서비스
이 사용자가 누구인지 알려줌
```

우리 서비스는 Google 비밀번호를 절대 받지 않습니다.

이게 OAuth/OIDC 흐름의 핵심 장점입니다.

## OAuth2와 OIDC를 아주 쉽게 구분하기

둘을 처음부터 정확히 외우려고 하면 헷갈립니다. 일단 이렇게 구분하면 됩니다.

```text
OAuth2
다른 서비스의 기능이나 데이터에 접근할 권한을 받는 흐름

OIDC
OAuth2 흐름 위에서 "로그인한 사용자가 누구인지" 확인하는 흐름
```

예시로 보면 더 쉽습니다.

### OAuth2 예시

```text
우리 서비스가 사용자의 Google Calendar를 읽고 싶다.
사용자가 Google에서 "캘린더 읽기 허용"을 누른다.
우리 서비스는 Google Calendar API를 호출할 수 있는 token을 받는다.
```

이건 "사용자 정보 확인"보다 "Google Calendar 접근 권한"이 핵심입니다.

### OIDC 예시

```text
우리 서비스가 Google로 로그인을 제공하고 싶다.
사용자가 Google에서 로그인한다.
Google이 우리 서비스에 "이 사용자의 Google id는 123이고 email은 a@example.com이야"라고 알려준다.
```

이건 "이 사용자가 누구인지 확인"이 핵심입니다.

소셜 로그인은 보통 OIDC에 가깝게 이해하면 됩니다.

## 전체 흐름: Google 로그인 버튼을 눌렀을 때

아래 흐름만 먼저 외우면 됩니다.

```text
1. 사용자가 "Google로 로그인" 버튼을 누른다.
2. 우리 프론트엔드가 Google 로그인 화면으로 이동시킨다.
3. 사용자가 Google에서 로그인하고 동의한다.
4. Google이 우리 서비스로 다시 돌려보내면서 code를 붙여준다.
5. 우리 백엔드가 그 code를 Google에 다시 보낸다.
6. Google이 id_token과 access_token을 준다.
7. 우리 백엔드가 id_token을 검증해서 사용자가 누구인지 확인한다.
8. 우리 DB에서 해당 Google 계정과 연결된 user를 찾거나 새로 만든다.
9. 우리 서비스용 session 또는 JWT를 발급한다.
10. 프론트엔드는 이제 우리 서비스 로그인 상태가 된다.
```

그림으로 보면 이렇습니다.

```text
사용자
  -> 우리 프론트엔드: Google 로그인 버튼 클릭
  -> Google: 로그인/동의
  -> 우리 백엔드: Google이 준 code 전달
  -> Google: code를 token으로 교환
  -> 우리 DB: user 찾기 또는 생성
  -> 사용자: 우리 서비스 token/session 발급
```

## code는 왜 필요한가?

Google이 바로 token을 프론트엔드에 주지 않고 `code`를 주는 이유는 보안 때문입니다.

쉽게 말하면 `code`는 임시 교환권입니다.

```text
Google: "이 사용자는 인증됐어. 여기 임시 교환권(code)이야."
우리 백엔드: "이 code가 진짜인지 Google에 확인하고 token으로 바꿔줘."
Google: "확인했어. 여기 id_token이야."
```

즉, `authorization code`는 최종 로그인 token이 아닙니다.

```text
code
-> 짧게 쓰는 임시 값
-> 백엔드가 Google에 보내서 token으로 교환한다.
```

## id_token은 무엇인가?

`id_token`은 Google이 발급한 "이 사용자가 누구인지"에 대한 증명서입니다.

보통 이런 정보가 들어 있습니다.

```json
{
  "sub": "google-user-id-123",
  "email": "a@example.com",
  "name": "Team One",
  "iss": "https://accounts.google.com",
  "aud": "our-google-client-id",
  "exp": 1760000000
}
```

우리 백엔드는 이 값을 그냥 믿으면 안 됩니다.

검증해야 합니다.

```text
이 id_token을 진짜 Google이 발급했는가?
우리 서비스용 client_id로 발급된 token인가?
만료되지 않았는가?
```

검증이 끝나면 그때 `email`, `sub` 같은 정보를 사용합니다.

## Google access token은 무엇인가?

Google이 주는 `access_token`은 Google API를 호출할 때 쓰는 token입니다.

예를 들어 scope에 Calendar 읽기 권한을 요청했다면:

```text
Google access_token
-> Google Calendar API 호출에 사용
```

하지만 우리 서비스 API를 호출할 때 쓰는 token은 아닙니다.

```text
Google access_token
-> Google API용

우리 서비스 access token
-> 우리 백엔드 API용
```

이 둘을 섞으면 안 됩니다.

## 우리 서비스 user와 Google user는 다르다

Google이 알려주는 사용자는 Google 기준 사용자입니다.

우리 서비스는 우리 서비스 기준 user를 따로 가져야 합니다.

예를 들어 Google이 알려준 정보:

```text
provider = google
provider_user_id = google-user-id-123
email = a@example.com
```

우리 서비스 DB에는 이렇게 저장할 수 있습니다.

```text
users
- id: 1
- email: a@example.com
- display_name: Team One

oauth_accounts
- id: 1
- user_id: 1
- provider: google
- provider_user_id: google-user-id-123
```

왜 나누는가?

```text
한 사용자가 Google 로그인도 하고 GitHub 로그인도 연결할 수 있다.
Google의 user id와 우리 서비스의 user id는 다르다.
나중에 provider가 늘어나도 users 테이블 구조를 덜 흔들 수 있다.
```

## 실제 백엔드 코드는 어떤 모양인가?

세부 구현은 provider마다 다르지만 흐름은 대략 이렇습니다.

### 1. Google 로그인 시작

```python
@router.get("/auth/google/login")
def google_login():
    google_url = make_google_login_url(
        client_id=GOOGLE_CLIENT_ID,
        redirect_uri=GOOGLE_REDIRECT_URI,
        scope="openid email profile",
        state=create_state(),
    )
    return RedirectResponse(google_url)
```

이 endpoint는 사용자를 Google 로그인 화면으로 보냅니다.

### 2. Google callback 처리

```python
@router.get("/auth/google/callback")
def google_callback(code: str, state: str):
    verify_state(state)

    google_tokens = exchange_code_with_google(code)
    google_profile = verify_google_id_token(google_tokens.id_token)

    user = find_or_create_user_from_google(
        google_user_id=google_profile.sub,
        email=google_profile.email,
        display_name=google_profile.name,
    )

    our_access_token = create_access_token(user.id)
    return {"access_token": our_access_token, "token_type": "bearer"}
```

여기서 가장 중요한 줄은 이 부분입니다.

```python
user = find_or_create_user_from_google(...)
our_access_token = create_access_token(user.id)
```

Google 사용자를 우리 서비스 user로 바꾼 뒤, 우리 서비스 token을 발급합니다.

## state는 왜 필요한가?

`state`는 로그인 요청이 중간에 바뀌지 않았는지 확인하는 값입니다.

쉽게 말하면 "로그인 요청 번호표"입니다.

```text
1. 우리 서비스가 state=abc123을 만들어 저장한다.
2. Google 로그인 URL에 state=abc123을 붙여 보낸다.
3. Google이 callback으로 code와 state=abc123을 돌려준다.
4. 우리 서비스는 저장해둔 state와 돌아온 state가 같은지 확인한다.
```

같지 않으면 위험한 요청일 수 있으므로 중단합니다.

지금은 이렇게 기억하면 됩니다.

```text
state는 OAuth 로그인 흐름에서 CSRF를 막기 위한 값이다.
```

## PKCE는 지금 어느 정도만 알면 되는가?

PKCE는 code가 중간에 탈취되어도 다른 사람이 token으로 바꾸기 어렵게 만드는 보강 장치입니다.

지금은 구현 세부를 외우지 않아도 됩니다.

일단 이렇게만 기억합니다.

```text
PKCE는 authorization code 흐름을 더 안전하게 만드는 장치다.
SPA나 모바일 앱처럼 secret을 안전하게 숨기기 어려운 클라이언트에서 중요하다.
```

## 직접 로그인, JWT, OAuth/OIDC 비교

| 방식 | 사용자가 하는 일 | 우리 서버가 하는 일 | 핵심 |
| --- | --- | --- | --- |
| 직접 로그인 + Session | 우리 서비스에 username/password 입력 | 비밀번호 확인 후 session 저장 | 서버가 로그인 상태 저장 |
| 직접 로그인 + JWT | 우리 서비스에 username/password 입력 | 비밀번호 확인 후 JWT 발급 | token으로 사용자 확인 |
| Google 로그인(OIDC) | Google에서 로그인 | Google id_token 검증 후 우리 서비스 token 발급 | 외부 서비스로 신원 확인 |

## AI 게시판에서 OAuth/OIDC는 언제 필요한가?

처음 MVP에서는 필수가 아닐 수 있습니다.

먼저 자체 로그인 + access/refresh token으로도 충분히 학습할 수 있습니다.

하지만 아래 상황이면 OAuth/OIDC를 고려합니다.

```text
사용자가 Google/GitHub 계정으로 쉽게 가입해야 한다.
학교/팀 계정 기반 로그인이 필요하다.
외부 서비스 API를 사용자 권한으로 호출해야 한다.
MCP 도구가 Google Drive, Calendar 같은 외부 자원에 접근해야 한다.
```

특히 MCP나 Agent가 외부 서비스를 호출한다면 OAuth2가 중요해집니다.

```text
Agent가 사용자의 Google Drive 문서를 읽는다.
-> 사용자가 Google Drive 접근 권한을 허용해야 한다.
-> 우리 서비스는 Google access_token으로 Drive API를 호출한다.
```

이 경우는 단순 소셜 로그인보다 "외부 서비스 권한 위임"에 가깝습니다.

## 팀 기본값 후보

```text
Sprint 2 구현은 직접 로그인 + JWT 또는 session 흐름으로 먼저 잡는다.
OAuth/OIDC는 MVP 필수 여부를 따로 판단한다.

다만 users 테이블을 설계할 때,
나중에 oauth_accounts 테이블을 붙일 수 있다는 점은 질문으로 남긴다.
```

## 체크 질문

- Google 로그인 후 Google access token을 우리 서비스 access token처럼 쓰면 안 되는 이유는 무엇인가?
- authorization code는 최종 token인가, 임시 교환권인가?
- id_token은 무엇을 증명하는가?
- 우리 서비스 user와 Google user를 왜 분리해야 하는가?
- state는 어떤 공격을 막기 위한 값인가?
- OAuth2와 OIDC 중 소셜 로그인에 더 직접적으로 연결되는 것은 무엇인가?
