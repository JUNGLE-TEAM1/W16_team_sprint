import type { FormEventHandler } from "react";
import { LogIn, PenLine, UserPlus } from "lucide-react";

import type { AuthForm, AuthMode, CurrentUser, PostMeta } from "../types";

type HeroSectionProps = {
  currentUser: CurrentUser | null;
  postMeta: PostMeta;
  showAuthPanel: boolean;
  authMode: AuthMode;
  authForm: AuthForm;
  authActionLabel: string;
  savingAuth: boolean;
  onAuthModeChange: (mode: AuthMode) => void;
  onAuthFormChange: (form: AuthForm) => void;
  onAuthSubmit: FormEventHandler<HTMLFormElement>;
  onShowAuthPanel: () => void;
};

export function HeroSection({
  currentUser,
  postMeta,
  showAuthPanel,
  authMode,
  authForm,
  authActionLabel,
  savingAuth,
  onAuthModeChange,
  onAuthFormChange,
  onAuthSubmit,
  onShowAuthPanel,
}: HeroSectionProps) {
  return (
    <section className="hero">
      <div className="heroCopy">
        <h1>
          글이 흐름이 되는 공간,
          <br />
          스프린트
        </h1>
        <p>스프린트에 담긴 구현 기록을 감상해 보세요.</p>
        <p>그리고 다시 꺼내 보세요.</p>
        <p>회의 전에 간직하고 있던 질문과 결정을.</p>
      </div>

      <aside className="heroSide">
        {currentUser ? (
          <section className="sessionPanel">
            <div className="avatar">{currentUser.email.slice(0, 1).toUpperCase()}</div>
            <div>
              <strong>{currentUser.email}</strong>
              <span>
                {currentUser.role} · {postMeta.total} posts
              </span>
            </div>
          </section>
        ) : (
          <section className={showAuthPanel ? "authPanel open" : "authPanel"}>
            {showAuthPanel ? (
              <form onSubmit={onAuthSubmit}>
                <div className="segmented">
                  <button
                    type="button"
                    className={authMode === "login" ? "active" : ""}
                    onClick={() => onAuthModeChange("login")}
                  >
                    <LogIn size={15} />
                    로그인
                  </button>
                  <button
                    type="button"
                    className={authMode === "signup" ? "active" : ""}
                    onClick={() => onAuthModeChange("signup")}
                  >
                    <UserPlus size={15} />
                    가입
                  </button>
                </div>
                <input
                  aria-label="이메일"
                  autoComplete="email"
                  placeholder="member@sprint.local"
                  value={authForm.email}
                  onChange={(event) => onAuthFormChange({ ...authForm, email: event.target.value })}
                  required
                />
                <input
                  aria-label="비밀번호"
                  autoComplete={authMode === "login" ? "current-password" : "new-password"}
                  placeholder="password"
                  type="password"
                  value={authForm.password}
                  onChange={(event) => onAuthFormChange({ ...authForm, password: event.target.value })}
                  required
                  minLength={8}
                />
                <button className="mintButton" type="submit" disabled={savingAuth}>
                  {savingAuth ? "처리 중" : authActionLabel}
                </button>
              </form>
            ) : (
              <button className="startCard" type="button" onClick={onShowAuthPanel}>
                <PenLine size={19} />
                <span>글을 쓰려면 로그인</span>
              </button>
            )}
          </section>
        )}
      </aside>
    </section>
  );
}
