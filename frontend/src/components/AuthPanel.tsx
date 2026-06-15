import type { AuthFormState, AuthView, FieldChangeHandler, FormSubmitHandler } from "../types";

interface AuthPanelProps {
  authView: AuthView;
  authForm: AuthFormState;
  onChange: FieldChangeHandler;
  onClose: () => void;
  onLogin: FormSubmitHandler;
  onRegister: FormSubmitHandler;
}

export function AuthPanel({
  authView,
  authForm,
  onChange,
  onClose,
  onLogin,
  onRegister,
}: AuthPanelProps) {
  if (!authView) {
    return null;
  }

  const isLogin = authView === "login";

  return (
    <section className="auth-card" aria-label={isLogin ? "로그인" : "회원가입"}>
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">Account</p>
          <h2>{isLogin ? "로그인" : "회원가입"}</h2>
        </div>
        <button className="ghost-button" type="button" onClick={onClose}>
          닫기
        </button>
      </div>

      <form className="inline-form" onSubmit={isLogin ? onLogin : onRegister}>
        <label className="field">
          <span>Username</span>
          <input
            name="username"
            autoComplete="username"
            value={authForm.username}
            onChange={onChange}
            required
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            name="password"
            type="password"
            autoComplete={isLogin ? "current-password" : "new-password"}
            value={authForm.password}
            onChange={onChange}
            required
          />
        </label>

        {!isLogin ? (
          <label className="field">
            <span>Display name</span>
            <input
              name="display_name"
              autoComplete="name"
              value={authForm.display_name}
              onChange={onChange}
              required
            />
          </label>
        ) : null}

        <button className="submit-button" type="submit">
          {isLogin ? "로그인" : "계정 생성"}
        </button>
      </form>
    </section>
  );
}
