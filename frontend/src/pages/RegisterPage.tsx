import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldPlus } from "lucide-react";
import { registerUser } from "../api/client";
import "../styles/auth.css";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser({ username, password });
      setSuccess("Account created successfully. Redirecting to login...");
      setTimeout(() => navigate("/login", { replace: true }), 700);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Registration failed. User may already exist.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">
            <ShieldPlus size={30} />
          </div>
          <h1>Create SecOps Account</h1>
          <p>Register local access for the AI SecOps workspace</p>
        </div>

        <form onSubmit={handleRegister} className="auth-form">
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>

          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>

          {error && <div className="auth-error">{error}</div>}
          {success && <div className="auth-success">{success}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Register"}
          </button>
        </form>

        <p className="auth-switch">
          Already have account? <Link to="/login">Login</Link>
        </p>
      </section>
    </main>
  );
}