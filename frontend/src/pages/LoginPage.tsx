import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Shield } from "lucide-react";
import { login } from "../api/client";
import "../styles/auth.css";

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await login({ username, password });

      const loginOk =
        result?.success === true ||
        result?.status === "success" ||
        result?.authenticated === true ||
        result?.message?.toLowerCase?.().includes("success");

      if (!loginOk && result?.detail) {
        throw new Error(result.detail);
      }

      localStorage.setItem("secops_auth", "true");
      localStorage.setItem("secops_username", result?.username || username);
      localStorage.setItem("secops_role", result?.role || "Administrator");

      navigate("/dashboard", { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Login failed. Check username/password or backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">
            <Shield size={30} />
          </div>
          <h1>Enterprise AI SecOps Copilot</h1>
          <p>AI-Powered SOC Operations Workspace</p>
        </div>

        <form onSubmit={handleLogin} className="auth-form">
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>

          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>

        <p className="auth-switch">
          New user? <Link to="/register">Create account</Link>
        </p>
      </section>
    </main>
  );
}