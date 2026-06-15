import { useEffect, useMemo, useState } from "react";
import { BriefcaseBusiness, RefreshCw, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { getCases } from "../api/client";
import { CaseRow } from "../components/RecentQueue";
import "../styles/dashboard.css";

type EnrichedCaseRow = CaseRow & {
  source_type?: string;
  hostname?: string;
  username?: string;
  source_ip?: string;
  event_id?: string;
  mitre?: string;
  output_text?: string;
  output?: string;
  input_text?: string;
};

const PAGE_SIZE = 20;

function badgeClass(value?: string) {
  const normalized = String(value || "unknown").toLowerCase();

  if (["critical", "high"].includes(normalized)) return "badge red";
  if (normalized === "medium") return "badge amber";
  if (normalized === "compliance") return "badge purple";
  if (["low", "resolved", "closed"].includes(normalized)) return "badge green";
  if (["investigating", "assigned"].includes(normalized)) return "badge amber";

  return "badge blue";
}

function normalizeCases(data: any): EnrichedCaseRow[] {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.cases)) return data.cases;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function clean(value?: string) {
  return value && value !== "unknown" ? value : "Not present";
}

export default function CasesPage() {
  const [cases, setCases] = useState<EnrichedCaseRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [expandedId, setExpandedId] = useState<string | number | null>(null);
  const [page, setPage] = useState(1);

  async function loadCases() {
    try {
      setLoading(true);
      setError("");
      const data = await getCases();
      setCases(normalizeCases(data));
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Unable to load cases from backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCases();
  }, []);

  const filteredCases = useMemo(() => {
    const filtered = cases.filter((item) => {
      const searchable = [
        item.id,
        item.timestamp,
        item.module,
        item.severity,
        item.type,
        item.status,
        item.source_type,
        item.hostname,
        item.username,
        item.source_ip,
        item.event_id,
        item.mitre,
      ]
        .join(" ")
        .toLowerCase();

      const matchesQuery = searchable.includes(query.toLowerCase());
      const matchesSeverity =
        severityFilter === "All" || String(item.severity || "").toLowerCase() === severityFilter.toLowerCase();
      const matchesStatus =
        statusFilter === "All" || String(item.status || "").toLowerCase() === statusFilter.toLowerCase();

      return matchesQuery && matchesSeverity && matchesStatus;
    });

    return filtered;
  }, [cases, query, severityFilter, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredCases.length / PAGE_SIZE));

  const paginatedCases = filteredCases.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

  function goPrevious() {
    setPage((current) => Math.max(1, current - 1));
  }

  function goNext() {
    setPage((current) => Math.min(totalPages, current + 1));
  }

  useEffect(() => {
    setPage(1);
  }, [query, severityFilter, statusFilter]);

  return (
    <main className="cases-page">
      <section className="dashboard-title-row">
        <div className="dashboard-title-left">
          <div className="dashboard-title-icon">
            <BriefcaseBusiness size={24} />
          </div>
          <div>
            <h1>Cases</h1>
            <p>Saved investigations with SOC metadata, MITRE context, and case status.</p>
          </div>
        </div>

        <button className="refresh-btn" type="button" onClick={loadCases}>
          <RefreshCw size={17} />
          Refresh
        </button>
      </section>

      <section className="dashboard-panel cases-filter-panel">
        <div className="case-search-box">
          <Search size={18} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by host, user, IP, MITRE, module, severity..."
          />
        </div>

        <select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}>
          <option>All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
          <option>Compliance</option>
        </select>

        <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option>All</option>
          <option>New</option>
          <option>Investigating</option>
          <option>Assigned</option>
          <option>Resolved</option>
          <option>Closed</option>
        </select>
      </section>

      {error && <div className="dashboard-error">{error}</div>}
      {loading && <div className="dashboard-loading">Loading cases...</div>}

      <section className="dashboard-panel cases-table-panel">
        <div className="cases-pagination-top">
          <span>
            Showing {paginatedCases.length} of {filteredCases.length} cases
          </span>

          <div className="pagination-controls">
            <button type="button" onClick={goPrevious} disabled={page === 1}>
              <ChevronLeft size={16} />
              Previous
            </button>

            <span>
              Page {page} / {totalPages}
            </span>

            <button type="button" onClick={goNext} disabled={page === totalPages}>
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        </div>

        <div className="table-wrap">
          <table className="queue-table cases-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Time</th>
                <th>Severity</th>
                <th>Source Type</th>
                <th>Hostname</th>
                <th>Username</th>
                <th>Source IP</th>
                <th>MITRE</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {paginatedCases.length === 0 ? (
                <tr>
                  <td colSpan={9} className="empty-row">
                    No saved cases found.
                  </td>
                </tr>
              ) : (
                paginatedCases.map((item, index) => {
                  const caseId = item.id || index + 1;
                  const isExpanded = expandedId === caseId;

                  return (
                    <>
                      <tr
                        key={`case-${caseId}`}
                        className="case-click-row"
                        onClick={() => setExpandedId(isExpanded ? null : caseId)}
                      >
                        <td>{caseId}</td>
                        <td>{item.timestamp || "N/A"}</td>
                        <td><span className={badgeClass(item.severity)}>{item.severity || "Unknown"}</span></td>
                        <td><span className="badge blue">{clean(item.source_type || item.type)}</span></td>
                        <td>{clean(item.hostname)}</td>
                        <td>{clean(item.username)}</td>
                        <td>{clean(item.source_ip)}</td>
                        <td><span className="badge purple">{clean(item.mitre)}</span></td>
                        <td><span className={badgeClass(item.status)}>{item.status || "New"}</span></td>
                      </tr>

                      {isExpanded && (
                        <tr key={`details-${caseId}`} className="case-detail-row">
                          <td colSpan={9}>
                            <div className="case-detail-box">
                              <div><strong>Module:</strong> {item.module || "N/A"}</div>
                              <div><strong>Type:</strong> {item.type || "N/A"}</div>
                              <div><strong>Event ID:</strong> {clean(item.event_id)}</div>
                              <div>
                                <strong>Analyst Output:</strong>
                                <pre>{item.output_text || item.output || "No output saved."}</pre>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}