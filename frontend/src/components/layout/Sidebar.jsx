import { useNavigate, useLocation } from "react-router-dom";
import {
  Database,
  GitMerge,
  LogOut,
  List,
  Activity,
  Wrench,
  Bell,
  MessageSquare,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import clsx from "clsx";
import { CatalogSearch } from "../opensearch";
import logo from "../../assets/logo.png";

export function Sidebar({ isCollapsed, onToggle }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const allNavItems = [
    { name: "실시간 알림", path: "/demo/realtime-alerts", icon: Bell },
    { name: "AI에게 물어보기", path: "/demo/review-insights", icon: MessageSquare },
    { name: "데이터셋", path: "/dataset", icon: Database, requiresDatasetEtlAccess: true },
    { name: "ETL 작업", path: "/etl", icon: List, requiresDatasetEtlAccess: true },
    { name: "카탈로그", path: "/catalog", icon: Activity },
    { name: "관리자", path: "/admin", icon: Wrench, adminOnly: true },
  ];

  // Filter items based on user permissions
  const navItems = allNavItems.filter((item) => {
    // Admin can see everything
    if (user?.is_admin === true) {
      return true;
    }

    // Admin-only items
    if (item.adminOnly) {
      return false;
    }

    // Dataset/ETL access control - check both user-level and role-level permissions
    if (item.requiresDatasetEtlAccess) {
      return user?.etl_access === true || user?.role_dataset_etl_access === true;
    }

    // Query/AI access control - check role-level permission
    if (item.requiresQueryAiAccess) {
      return user?.role_query_ai_access === true;
    }

    return true;
  });

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div
      className={clsx(
        "h-screen bg-white border-r border-gray-200 text-gray-700 hidden md:flex flex-col fixed left-0 top-0 z-20 transition-all duration-300 ease-in-out",
        isCollapsed ? "w-20" : "w-64",
      )}
    >
      {/* Brand */}
      <div className="h-16 flex items-center px-4 border-b border-gray-200 overflow-hidden">
        <div
          className={clsx(
            "flex items-center overflow-hidden transition-all duration-300",
            isCollapsed ? "w-12 justify-center" : "w-44 justify-start"
          )}
        >
          <img
            src={logo}
            alt="AskLake"
            className={clsx(
              "object-contain transition-all duration-300",
              isCollapsed ? "h-8 max-w-none" : "h-10 w-auto"
            )}
          />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 px-3 space-y-6 overflow-y-auto overflow-x-hidden">
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                title={isCollapsed ? item.name : ""}
                className={clsx(
                  "w-full flex items-center p-2 text-sm font-medium rounded-md transition-all duration-200 group relative overflow-hidden",
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900",
                )}
              >
                {/* Icon container - fixed width */}
                <div className="w-5 h-5 flex items-center justify-center shrink-0">
                  <item.icon
                    className={clsx(
                      "w-5 h-5 transition-colors",
                      isActive
                        ? "text-blue-600"
                        : "text-gray-400 group-hover:text-gray-600",
                    )}
                  />
                </div>

                {/* Text label - fades out when collapsed */}
                <span
                  className={clsx(
                    "ml-3 truncate transition-all duration-300",
                    isCollapsed ? "opacity-0 w-0" : "opacity-100"
                  )}
                >
                  {item.name}
                </span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* User & Logout */}
      <div className="p-4 border-t border-gray-200 space-y-1">

        <button
          onClick={handleLogout}
          title={isCollapsed ? "로그아웃" : ""}
          className="flex items-center text-sm font-medium text-gray-500 hover:text-red-600 transition-colors w-full p-2 rounded-md hover:bg-red-50 relative overflow-hidden"
        >
          {/* Icon container - fixed width */}
          <div className="w-4 h-4 flex items-center justify-center shrink-0">
            <LogOut className="w-4 h-4" />
          </div>

          {/* Text label - fades out when collapsed */}
          <span
            className={clsx(
              "ml-2 transition-all duration-300",
              isCollapsed ? "opacity-0 w-0" : "opacity-100"
            )}
          >
            로그아웃
          </span>
        </button>
      </div>
    </div>
  );
}

export function Topbar({ isCollapsed }) {
  const { user } = useAuth();

  const initials = user?.name
    ? user.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
    : "??";

  // Check if user has AI access - check role-level permission
  const hasAiAccess = user?.is_admin || user?.role_query_ai_access === true;

  return (
    <div
      className={clsx(
        "h-16 bg-white border-b border-gray-200 flex items-center justify-between gap-3 px-3 fixed top-0 right-0 left-0 z-[1000] transition-all duration-300 ease-in-out sm:px-4 md:px-6",
        isCollapsed ? "md:left-20" : "md:left-64",
      )}
    >
      {/* Search */}
      <div className="min-w-0 flex-1">
        <CatalogSearch />
      </div>

      {/* Right Actions */}

      <div className="flex shrink-0 items-center space-x-2 sm:space-x-3">
        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium text-xs">
          {initials}
        </div>
        <div className="hidden md:block">
          <p className="text-sm font-medium text-gray-700">{user?.name || "사용자"}</p>
          <p className="text-xs text-gray-500">{user?.is_admin ? "관리자" : "사용자"}</p>
        </div>
      </div>
    </div>
  );
}
