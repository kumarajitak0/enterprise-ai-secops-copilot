import { useNavigate } from "react-router-dom";

type Props = {
  tone: "blue" | "purple" | "green";
  icon: string;
  title: string;
  description: string;
  count: number;
  percentage: string;
};

export default function UseCaseCard({ tone, icon, title, description, count, percentage }: Props) {
  const navigate = useNavigate();

  return (
    <article className={`usecase-card-react ${tone}`}>
      <div className={`usecase-icon-react ${tone}`}>{icon}</div>

      <h3>{title}</h3>
      <p>{description}</p>

      <div className="usecase-meta-row">
        <span>
          <b>{count}</b> Cases
        </span>
        <span>{percentage}</span>
      </div>

      <button
        className={`workspace-button ${tone}`}
        type="button"
        onClick={() => navigate("/soc-workspace")}
      >
        Go to Workspace →
      </button>
    </article>
  );
}