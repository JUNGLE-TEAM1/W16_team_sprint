import { LogOut, Menu, RefreshCw } from "lucide-react";

import type { CurrentUser } from "../types";

type AppHeaderProps = {
  currentUser: CurrentUser | null;
  onRefresh: () => void;
  onLogout: () => void;
  onToggleAuthPanel: () => void;
};

export function AppHeader({
  currentUser,
  onRefresh,
  onLogout,
  onToggleAuthPanel,
}: AppHeaderProps) {
  return (
    <header className="brunchHeader">
      <div className="brandCluster">
        <button className="plainIcon" type="button" aria-label="메뉴">
          <Menu size={25} />
        </button>
        <span className="wordmark">suwon youth</span>
      </div>

      <div className="pageTitle">AI 수원 청년정책 매칭</div>

      <div className="headerActions">
        <button className="plainIcon" type="button" onClick={onRefresh} aria-label="새로고침">
          <RefreshCw size={19} />
        </button>
        {currentUser ? (
          <button className="outlineButton" type="button" onClick={onLogout}>
            <LogOut size={15} />
            로그아웃
          </button>
        ) : (
          <button className="outlineButton" type="button" onClick={onToggleAuthPanel}>
            상담 시작
          </button>
        )}
      </div>
    </header>
  );
}
