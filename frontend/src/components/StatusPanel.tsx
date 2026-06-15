import { Brain, Database, RadioTower, ShieldCheck, ServerCog } from "lucide-react";

type HealthStatus = {
  backend?: string;
  ollama?: string;
  auth?: string;
  database?: string;
};

function statusClass(value?: string) {
  const normalized = String(value || "").toLowerCase();

  if (["ready", "ok", "healthy", "active", "connected"].includes(normalized)) return "status-ready";
  if (["planned", "pending"].includes(normalized)) return "status-planned";
  if (["unknown", "error", "down", "failed"].includes(normalized)) return "status-error";

  return "status-active";
}

export default function StatusPanel({ health }: { health: HealthStatus }) {
  const rows = [
    {
      icon: <ServerCog size={18} />,
      label: "FastAPI Backend",
      value: health.backend || "unknown"
    },
    {
      icon: <Brain size={18} />,
      label: "Local LLM",
      value: health.ollama || "planned"
    },
    {
      icon: <ShieldCheck size={18} />,
      label: "RBAC / IAM",
      value: health.auth || "unknown"
    },
    {
      icon: <Database size={18} />,
      label: "SQLite Case Store",
      value: health.database || "unknown"
    },
    {
      icon: <RadioTower size={18} />,
      label: "Splunk Connector",
      value: "planned"
    }
  ];

  return (
    <section className="dashboard-panel status-panel">
      <div className="panel-heading">
        <h2>⌘ Platform Status</h2>
      </div>

      <div className="status-list">
        {rows.map((row) => (
          <div className="platform-status-row" key={row.label}>
            <span>
              {row.icon}
              {row.label}
            </span>
            <b className={statusClass(row.value)}>{row.value}</b>
          </div>
        ))}
      </div>
    </section>
  );
}