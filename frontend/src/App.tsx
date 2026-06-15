import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactElement } from "react";
import AppShell from "./components/AppShell";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import SOCWorkspacePage from "./pages/SOCWorkspacePage";
import CasesPage from "./pages/CasesPage";
import AdminPage from "./pages/AdminPage";

// =============================================================================
// 2026-06-14 21:15 - AUTH ROUTE HELPERS
// Purpose: Keep protected pages behind localStorage session without changing backend.
// =============================================================================

function isAuthenticated() {
  return localStorage.getItem("secops_auth") === "true";
}

function ProtectedRoute({ children }: { children: ReactElement }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function PublicOnlyRoute({ children }: { children: ReactElement}) {
  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// =============================================================================
// 2026-06-14 21:15 - APPLICATION ROUTES
// Purpose: Route Dashboard, SOC Workspace, Cases, and Admin pages to real components.
// =============================================================================

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/register"
        element={
          <PublicOnlyRoute>
            <RegisterPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/soc-workspace" element={<SOCWorkspacePage />} />
        <Route path="/cases" element={<CasesPage />} />
        <Route path="/administration" element={<AdminPage />} />
      </Route>

      <Route path="*" element={<Navigate to={isAuthenticated() ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
}