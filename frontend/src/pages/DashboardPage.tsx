import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Home, RefreshCw } from "lucide-react";
import { getDashboardStats } from "../api/client";
import StatCard from "../components/StatCard";
import RecentQueue, { CaseRow } from "../components/RecentQueue";
import UseCaseCard from "../components/UseCaseCard";
import "../styles/dashboard.css";

type DashboardStats = {
  total_cases?: number;
  high_severity?: number;
  medium_severity?: number;
  grc_evidence?: number;
  recent_cases?: CaseRow[];
};

function percent(part: number, total: number) {
  if (!total || total <= 0) return "0.00%";
  return `${((part / total) * 100).toFixed(2)}%`;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const statsData = await getDashboardStats();
      setStats(statsData || {});
    } catch {
      setError("Backend unavailable. Start FastAPI on port 8001.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const total = Number(stats.total_cases || 0);
  const high = Number(stats.high_severity || 0);
  const medium = Number(stats.medium_severity || 0);
  const grc = Number(stats.grc_evidence || 0);
  const recentCases = Array.isArray(stats.recent_cases) ? stats.recent_cases : [];

  const moduleCounts = useMemo(() => {
    return {
      soc: recentCases.filter((item) => item.module === "SOC Alert Triage").length,
      rca: recentCases.filter((item) => item.module === "RCA Generator").length,
      grc: recentCases.filter((item) => item.module === "GRC Evidence Mapping").length,
    };
  }, [recentCases]);

  return (
    <main className="dashboard-page">
      <section className="dashboard-title-row">
        <div className="dashboard-title-left">
          <div className="dashboard-title-icon">
            <Home size={24} />
          </div>
          <div>
            <h1>Dashboard</h1>
            <p>Overview of active SOC operations, case volume, and investigation queue.</p>
          </div>
        </div>

        <div className="dashboard-actions">
          <div className="date-pill">
            <CalendarDays size={17} />
            {new Date().toLocaleString(undefined, {
              month: "long",
              day: "2-digit",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>

          <button className="refresh-btn" type="button" onClick={loadDashboard}>
            <RefreshCw size={17} />
            Refresh
          </button>
        </div>
      </section>

      {error && <div className="dashboard-error">{error}</div>}
      {loading && <div className="dashboard-loading">Loading dashboard...</div>}

      <section className="stat-grid">
        <StatCard title="Total Cases" value={total} subtitle="All time investigations" tone="blue" />
        <StatCard title="High Severity" value={high} subtitle={`${percent(high, total)} of total`} tone="red" />
        <StatCard title="Medium Severity" value={medium} subtitle={`${percent(medium, total)} of total`} tone="amber" />
        <StatCard title="GRC Evidence" value={grc} subtitle={`${percent(grc, total)} of total`} tone="green" />
      </section>

      <section className="dashboard-panel">
        <RecentQueue cases={recentCases.slice(0, 8)} />
      </section>

      <section className="usecase-section">
        <div className="panel-heading">
          <h2>▰ Investigation Coverage</h2>
        </div>

        <div className="usecase-grid-react">
          <UseCaseCard
            tone="blue"
            icon="🛡"
            title="SOC Alert Triage"
            description="Security log triage, severity classification, MITRE mapping, and playbook recommendations."
            count={moduleCounts.soc}
            percentage={`${percent(moduleCounts.soc, total)} of recent queue`}
          />

          <UseCaseCard
            tone="purple"
            icon="🔎"
            title="RCA Generator"
            description="Root cause notes for outage, timeout, service failure, and operational incident evidence."
            count={moduleCounts.rca}
            percentage={`${percent(moduleCounts.rca, total)} of recent queue`}
          />

          <UseCaseCard
            tone="green"
            icon="📋"
            title="GRC Evidence Mapping"
            description="Audit evidence mapping for logging, access review, monitoring, and incident response controls."
            count={moduleCounts.grc}
            percentage={`${percent(moduleCounts.grc, total)} of recent queue`}
          />
        </div>
      </section>

      <footer className="dashboard-footer">
        <span>Enterprise AI SecOps Copilot v1.0.0</span>
        <span>© 2026 SecOps Copilot</span>
      </footer>
    </main>
  );
}