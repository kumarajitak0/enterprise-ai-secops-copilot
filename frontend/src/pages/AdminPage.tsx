import { useEffect, useState } from "react";
import { Activity, Database, KeyRound, PlugZap, ShieldCheck, UserCheck } from "lucide-react";
import { healthCheck } from "../api/client";
import "../styles/dashboard.css";

// =============================================================================
// 2026-06-14 21:15 - TYPES AND STATUS HELPERS
// Purpose: Normalize health status values for admin platform display.
// =============================================================================

type HealthStatus = {
  backend?: string;
  ollama?: string;
  auth?: string;
  database?: string;
};

function valueOrDefault(value: unknown, fallback: string) {
  return typeof value === "string" && value.trim() ? value : fallback;
}

// =============================================================================
// 2026-06-14 21:15 - ADMINISTRATION PAGE
// Purpose: Show access controls, integrations, and live platform health from FastAPI.
// =============================================================================

export default function AdminPage() {
  const [health, setHealth] = useState<HealthStatus>({});
  const [error, setError] = useState("");

  async function loadHealth() {
    try {
      setError("");
      const data = await healthCheck();
      setHealth(data || {});
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Unable to load platform health.");
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  const accessControls = [
    {
      icon: <UserCheck size={19} />,
      label: "Login",
      value: "Enabled",
      tone: "status-ready"
    },
    {
      icon: <ShieldCheck size={19} />,
      label: "RBAC / IAM",
      value: valueOrDefault(health.auth, "Enabled"),
      tone: "status-ready"
    },
    {
      icon: <KeyRound size={19} />,
      label: "Audit Trail",
      value: "Planned",
      tone: "status-planned"
    }
  ];

  const integrations = [
    {
      icon: <PlugZap size={19} />,
      label: "Splunk Connector",
      value: "Planned",
      tone: "status-planned"
    },
    {
      icon: <Activity size={19} />,
      label: "Grafana Webhook",
      value: "Planned",
      tone: "status-planned"
    },
    {
      icon: <Database size={19} />,
      label: "SQLite Case Store",
      value: valueOrDefault(health.database, "Unknown"),
      tone: "status-active"
    }
  ];

  return (
    <main className="admin-page">
      <section className="dashboard-title-row">
        <div className="dashboard-title-left">
          <div className="dashboard-title-icon">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h1>Administration</h1>
            <p>RBAC, integrations, audit controls, and platform settings.</p>
          </div>
        </div>
      </section>

      {error && <div className="dashboard-error">{error}</div>}

      <section className="admin-grid">
        <div className="dashboard-panel">
          <div className="panel-heading">
            <h2>Access Controls</h2>
          </div>

          <div className="status-list">
            {accessControls.map((item) => (
              <div className="platform-status-row" key={item.label}>
                <span>
                  {item.icon}
                  {item.label}
                </span>
                <b className={item.tone}>{item.value}</b>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-panel">
          <div className="panel-heading">
            <h2>Integrations</h2>
          </div>

          <div className="status-list">
            {integrations.map((item) => (
              <div className="platform-status-row" key={item.label}>
                <span>
                  {item.icon}
                  {item.label}
                </span>
                <b className={item.tone}>{item.value}</b>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="dashboard-panel admin-health-panel">
        <div className="panel-heading">
          <h2>Platform Health</h2>
        </div>

        <div className="admin-health-grid">
          <div className="health-tile">
            <span>FastAPI Backend</span>
            <b className="status-ready">{valueOrDefault(health.backend, "Unknown")}</b>
          </div>

          <div className="health-tile">
            <span>Local LLM</span>
            <b className="status-planned">{valueOrDefault(health.ollama, "Local/Planned")}</b>
          </div>

          <div className="health-tile">
            <span>Auth</span>
            <b className="status-ready">{valueOrDefault(health.auth, "Unknown")}</b>
          </div>

          <div className="health-tile">
            <span>Database</span>
            <b className="status-active">{valueOrDefault(health.database, "Unknown")}</b>
          </div>
        </div>
      </section>
    </main>
  );
}