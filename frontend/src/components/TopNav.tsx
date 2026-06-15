import { LogOut, Moon, Radio, Shield, Sun } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

// =============================================================================
// 2026-06-14 21:05 - TOP NAV STRUCTURE
// Purpose: Brand, navigation, utilities, and logout separated cleanly.
// =============================================================================

const navItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "SOC Workspace", path: "/soc-workspace" },
  { label: "Cases", path: "/cases" },
  { label: "Administration", path: "/administration" }
];

export default function TopNav() {
  const navigate = useNavigate();
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");

  const username = localStorage.getItem("secops_username") || "Admin";
  const role = localStorage.getItem("secops_role") || "Administrator";
  const initial = username.charAt(0).toUpperCase();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  function toggleTheme() {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }

  function logout() {
    localStorage.removeItem("secops_auth");
    localStorage.removeItem("secops_username");
    localStorage.removeItem("secops_role");
    navigate("/login", { replace: true });
  }

  return (
    <header className="top-nav-shell">
      <div className="top-nav-brand">
        <div className="brand-logo">
          <Shield size={24} />
        </div>

        <div className="brand-text">
          <div className="brand-title">Enterprise AI SecOps Copilot</div>
          <div className="brand-subtitle">AI-Powered SOC Operations Workspace</div>
        </div>
      </div>

      <nav className="top-nav-center">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="top-nav-actions">
        <div className="local-pill">
          <Radio size={14} />
          <span>Local Mode</span>
        </div>

        <button className="icon-button" type="button" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === "dark" ? <Moon size={17} /> : <Sun size={17} />}
        </button>

        <div className="nav-divider" />

        <div className="user-box">
          <div className="avatar">{initial}</div>
          <div className="user-meta">
            <div className="user-name">{username}</div>
            <div className="user-role">{role}</div>
          </div>
        </div>

        <button className="logout-btn" type="button" onClick={logout}>
          <LogOut size={15} />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
}