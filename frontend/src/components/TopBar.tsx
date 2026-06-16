import type { BoardView, User } from "../types";

interface TopBarProps {
  currentUser: User | null;
  activeView: BoardView;
  onLogoClick: () => void;
  onShowSupport: () => void;
  onShowConsultations: () => void;
  onLogout: () => void;
  onShowLogin: () => void;
  onShowRegister: () => void;
}

export function TopBar({
  currentUser,
  activeView,
  onLogoClick,
  onShowSupport,
  onShowConsultations,
  onLogout,
  onShowLogin,
  onShowRegister,
}: TopBarProps) {
  return (
    <header className="topbar">
      <button className="brand-button" type="button" onClick={onLogoClick}>
        <span className="brand-symbol">복지</span>
        <span>AI 생활지원 매칭 보드</span>
      </button>

      <div className="topbar-right">
        <nav className="top-actions" aria-label="주요 메뉴">
          <button
            className={activeView === "support" ? "nav-button primary-nav" : "nav-button"}
            type="button"
            onClick={onShowSupport}
          >
            지원 정보
          </button>
          <button
            className={activeView === "consultations" ? "nav-button primary-nav" : "nav-button"}
            type="button"
            onClick={onShowConsultations}
          >
            내 상담 기록
          </button>
        </nav>

        <nav className="top-actions" aria-label="계정 메뉴">
          {currentUser ? (
            <>
              <span className="user-chip">{currentUser.display_name}</span>
              <button className="nav-button" type="button" onClick={onLogout}>
                로그아웃
              </button>
            </>
          ) : (
            <>
              <button className="nav-button" type="button" onClick={onShowLogin}>
                로그인
              </button>
              <button className="nav-button primary-nav" type="button" onClick={onShowRegister}>
                회원가입
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
