import { useMemo, useState } from "react";

const methods = [
  { id: "session", label: "Session" },
  { id: "jwt", label: "JWT" },
  { id: "pair", label: "Token Pair" },
];

const loginEndpoints = {
  session: "/api/v1/auth/session/login",
  jwt: "/api/v1/auth/jwt/login",
  pair: "/api/v1/auth/token-pair/login",
};

const meEndpoints = {
  session: "/api/v1/auth/session/me",
  jwt: "/api/v1/auth/jwt/me",
  pair: "/api/v1/auth/token-pair/me",
};

export default function App() {
  const [method, setMethod] = useState("session");
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    username: "team1",
    password: "password123",
    display_name: "Team One",
  });
  const [tokens, setTokens] = useState({ accessToken: "", refreshToken: "" });
  const [status, setStatus] = useState({ text: "대기 중", isError: false });
  const [response, setResponse] = useState({});

  const isRegister = mode === "register";
  const responseText = useMemo(() => JSON.stringify(response, null, 2), [response]);

  function updateForm(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function submit(event) {
    event.preventDefault();

    if (isRegister) {
      await request("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });
      return;
    }

    const result = await request(loginEndpoints[method], {
      method: "POST",
      body: JSON.stringify({
        username: form.username,
        password: form.password,
      }),
    });
    saveTokens(result);
  }

  async function loadMe() {
    await request(meEndpoints[method], authOptions());
  }

  async function refreshTokenPair() {
    const result = await request("/api/v1/auth/token-pair/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: tokens.refreshToken }),
    });
    saveTokens(result);
  }

  async function logout() {
    if (method === "session") {
      await request("/api/v1/auth/session/logout", { method: "POST" });
    }

    if (method === "pair") {
      await request("/api/v1/auth/token-pair/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: tokens.refreshToken }),
      });
    }

    setTokens({ accessToken: "", refreshToken: "" });
  }

  function authOptions() {
    if (method === "session") {
      return {};
    }

    return {
      headers: {
        Authorization: `Bearer ${tokens.accessToken}`,
      },
    };
  }

  async function request(endpoint, options = {}) {
    setStatus({ text: "요청 중", isError: false });

    const res = await fetch(endpoint, {
      method: options.method ?? "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      },
      body: options.body,
    });

    const text = await res.text();
    const data = text ? JSON.parse(text) : {};
    setResponse(data);
    setStatus({ text: res.ok ? "완료" : "오류", isError: !res.ok });
    return data;
  }

  function saveTokens(data) {
    setTokens((current) => ({
      accessToken: data.access_token ?? current.accessToken,
      refreshToken: data.refresh_token ?? current.refreshToken,
    }));
  }

  return (
    <main className="shell">
      <section className="brand" aria-label="서비스 정보">
        <div className="brand-mark" aria-hidden="true">
          W16
        </div>
        <div className="brand-copy">
          <p className="eyebrow">Secure sprint lab</p>
          <h1>Auth Studio</h1>
          <p className="lede">안전하게 시작하세요.</p>
        </div>
      </section>

      <section className="auth-panel" aria-label="로그인">
        <div className="panel-topline">
          <div>
            <p className="eyebrow">Account</p>
            <h2>{isRegister ? "회원가입" : "로그인"}</h2>
          </div>
          <button
            className="ghost-button"
            type="button"
            onClick={() => setMode(isRegister ? "login" : "register")}
          >
            {isRegister ? "로그인" : "회원가입"}
          </button>
        </div>

        <div className="method-tabs" role="tablist" aria-label="인증 방식">
          {methods.map((item) => (
            <button
              className={`method-tab ${method === item.id ? "is-active" : ""}`}
              type="button"
              key={item.id}
              onClick={() => {
                setMethod(item.id);
                setStatus({ text: `${item.label} 선택됨`, isError: false });
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        <form className="auth-form" onSubmit={submit}>
          <label className="field">
            <span>Username</span>
            <input
              name="username"
              autoComplete="username"
              value={form.username}
              onChange={updateForm}
              required
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              name="password"
              type="password"
              autoComplete={isRegister ? "new-password" : "current-password"}
              value={form.password}
              onChange={updateForm}
              required
            />
          </label>

          {isRegister ? (
            <label className="field">
              <span>Display name</span>
              <input
                name="display_name"
                autoComplete="name"
                value={form.display_name}
                onChange={updateForm}
              />
            </label>
          ) : null}

          <button className="primary-button" type="submit">
            {isRegister ? "계정 생성" : "로그인"}
          </button>
        </form>

        <div className="action-row">
          <button className="secondary-button" type="button" onClick={loadMe}>
            내 정보
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={refreshTokenPair}
            disabled={method !== "pair"}
          >
            Refresh
          </button>
          <button className="secondary-button danger" type="button" onClick={logout}>
            로그아웃
          </button>
        </div>

        <div className={`status ${status.isError ? "is-error" : ""}`} aria-live="polite">
          <span className="status-dot" aria-hidden="true" />
          <span>{status.text}</span>
        </div>

        <pre className="response-view">{responseText}</pre>
      </section>
    </main>
  );
}
