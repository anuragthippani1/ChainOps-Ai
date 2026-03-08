import React, { useMemo } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Bot,
  ChevronRight,
  FileText,
  Home,
  LayoutDashboard,
  Moon,
  Route,
  Settings,
  Sun,
  Users,
  Wrench,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { isDeveloperModeEnabled } from "../utils/developerMode";

const NAV_ITEMS = [
  { id: "home", label: "Home", path: "/", icon: Home },
  { id: "dashboard", label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { id: "assistant", label: "AI Assistant", path: "/assistant", icon: Bot },
  { id: "route-planner", label: "Route Planner", path: "/route-planner", icon: Route },
  { id: "reports", label: "Reports", path: "/reports", icon: FileText },
  { id: "session-manager", label: "Session Manager", path: "/session-manager", icon: Users },
];

const AppShell = ({ children }) => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const developerModeEnabled = isDeveloperModeEnabled();

  const breadcrumbs = useMemo(() => {
    if (location.pathname === "/") return ["Home"];
    return location.pathname
      .split("/")
      .filter(Boolean)
      .map((token) => token.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()));
  }, [location.pathname]);

  return (
    <div className="nm-shell">
      <aside className="nm-sidebar">
        <Link to="/" className="nm-flat nm-brand-card">
          <img src="/logo.png" alt="ChainOps AI Logo" className="h-10 w-10 rounded-2xl" />
          <div>
            <p className="nm-heading text-lg">ChainOps AI</p>
          </div>
        </Link>

        <nav className="mt-8 flex-1 space-y-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link key={item.id} to={item.path} className={`nm-nav-link ${isActive ? "is-active" : ""}`}>
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}

          {developerModeEnabled && (
            <Link to="/thinking-logs" className={`nm-nav-link ${location.pathname === "/thinking-logs" ? "is-active" : ""}`}>
              <Wrench className="h-4 w-4" />
              <span>Thinking Logs</span>
            </Link>
          )}
        </nav>

        <button className="nm-button mt-6 w-full">
          <Settings className="h-4 w-4" />
          <span>Settings</span>
        </button>
      </aside>

      <section className="nm-main-shell">
        <header className="nm-flat nm-header">
          <div className="flex items-center gap-2 text-sm nm-subtext">
            {breadcrumbs.map((crumb, idx) => (
              <React.Fragment key={crumb}>
                {idx > 0 && <ChevronRight className="h-4 w-4 transition-transform duration-300 group-hover:rotate-90" />}
                <span className={idx === breadcrumbs.length - 1 ? "nm-heading text-sm" : ""}>{crumb}</span>
              </React.Fragment>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <button onClick={toggleTheme} className="nm-icon-btn" aria-label="Toggle theme">
              {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </button>
          </div>
        </header>

        <main className="nm-main-content">{children}</main>
      </section>
    </div>
  );
};

export default AppShell;
