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
          수원시 청년정책을 찾는,
          <br />
          AI 매칭 보드
        </h1>
        <p>경기도 수원시 청년지원사업 OpenAPI 데이터로 지원 카드를 채웁니다.</p>
        <p>입력 내용은 저장하지 않고 일회성 매칭에만 사용합니다.</p>
        <p>월세, 취업, 창업, 교육, 문화 지원을 한 화면에서 비교하세요.</p>
        <p>조건 확인과 신청 체크리스트까지 빠르게 정리합니다.</p>
      </div>

      <aside className="heroSide">
        {currentUser ? (
          <section className="sessionPanel">
            <div className="avatar">{currentUser.email.slice(0, 1).toUpperCase()}</div>
            <div>
              <strong>{currentUser.email}</strong>
              <span>
                {currentUser.role} · {postMeta.total} cards
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
                <span>상담하려면 로그인</span>
              </button>
            )}
          </section>
        )}
      </aside>
    </section>
  );
}
