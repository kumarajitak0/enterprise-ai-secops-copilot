import { AlertTriangle, ClipboardCheck, LayoutDashboard } from "lucide-react";

type Props = {
  title: string;
  value: number;
  subtitle: string;
  tone: "blue" | "red" | "amber" | "green";
};

function IconByTone({ tone }: { tone: Props["tone"] }) {
  if (tone === "red" || tone === "amber") return <AlertTriangle size={23} />;
  if (tone === "green") return <ClipboardCheck size={23} />;
  return <LayoutDashboard size={23} />;
}

export default function StatCard({ title, value, subtitle, tone }: Props) {
  return (
    <article className="stat-card">
      <div className="stat-card-top">
        <div className={`stat-icon ${tone}`}>
          <IconByTone tone={tone} />
        </div>

        <div>
          <div className="stat-title">{title}</div>
          <div className="stat-value">{value}</div>
        </div>
      </div>

      <div className="stat-bottom">
        <span>{subtitle}</span>

        <svg className="mini-trend" viewBox="0 0 130 36" aria-hidden="true">
          <polyline
            points="2,28 18,26 34,18 50,21 66,14 82,17 98,11 124,24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </article>
  );
}