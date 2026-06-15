import { ListChecks } from "lucide-react";
import { useNavigate } from "react-router-dom";

export type CaseRow = {
  id?: number | string;
  timestamp?: string;
  module?: string;
  severity?: string;
  type?: string;
  status?: string;
};

function badgeClass(value?: string) {
  const normalized = String(value || "unknown").toLowerCase();

  if (normalized === "high") return "badge red";
  if (normalized === "medium") return "badge amber";
  if (normalized === "compliance") return "badge purple";
  if (normalized === "low") return "badge green";
  if (normalized === "resolved" || normalized === "closed") return "badge green";
  if (normalized === "investigating" || normalized === "assigned") return "badge amber";

  return "badge blue";
}

export default function RecentQueue({ cases }: { cases: CaseRow[] }) {
  const navigate = useNavigate();

  return (
    <section className="dashboard-panel queue-panel">
      <div className="panel-heading row-between">
        <h2>
          <ListChecks size={19} />
          Recent Investigation Queue
        </h2>

        <button className="small-action-btn" type="button" onClick={() => navigate("/cases")}>
          View All Cases
        </button>
      </div>

      <div className="table-wrap">
        <table className="queue-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Module</th>
              <th>Severity</th>
              <th>Type</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {cases.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-row">
                  No investigations yet.
                </td>
              </tr>
            ) : (
              cases.map((item, index) => (
                <tr key={item.id || index}>
                  <td>{item.timestamp || "N/A"}</td>
                  <td>{item.module || "N/A"}</td>
                  <td>
                    <span className={badgeClass(item.severity)}>{item.severity || "Unknown"}</span>
                  </td>
                  <td>{item.type || "N/A"}</td>
                  <td>
                    <span className={badgeClass(item.status)}>{item.status || "New"}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}