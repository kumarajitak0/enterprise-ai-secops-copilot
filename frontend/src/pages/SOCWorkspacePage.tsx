import { FormEvent, useMemo, useState } from "react";
import { BrainCircuit, ClipboardList, FileText, Info, ShieldCheck } from "lucide-react";
import { analyzeSOC, generateRCA, mapGRC } from "../api/client";
import "../styles/dashboard.css";

// =============================================================================
// 2026-06-14 21:40 - STRUCTURED OUTPUT FORMATTER
// Purpose: Convert backend markdown-style output into analyst report cards.
// =============================================================================

type ModuleType = "SOC Alert Triage" | "RCA Generator" | "GRC Evidence Mapping";

type ParsedLine =
  | { type: "title"; text: string }
  | { type: "section"; text: string }
  | { type: "bullet"; text: string }
  | { type: "number"; text: string }
  | { type: "label"; label: string; value: string }
  | { type: "info"; text: string }
  | { type: "text"; text: string };

const moduleOptions = [
  {
    label: "SOC Alert Triage" as ModuleType,
    description: "Analyze security logs, classify severity, map MITRE context, and recommend playbooks.",
    icon: <ShieldCheck size={20} />,
    buttonText: "Analyze Alert"
  },
  {
    label: "RCA Generator" as ModuleType,
    description: "Generate structured root-cause analysis for incident timelines and operational issues.",
    icon: <BrainCircuit size={20} />,
    buttonText: "Generate RCA"
  },
  {
    label: "GRC Evidence Mapping" as ModuleType,
    description: "Map evidence to security controls, audit readiness, and compliance frameworks.",
    icon: <ClipboardList size={20} />,
    buttonText: "Map Evidence"
  }
];

function formatResult(result: any): string {
  if (!result) return "";
  if (typeof result === "string") return result;
  if (typeof result.output === "string") return result.output;
  if (typeof result.result === "string") return result.result;
  if (typeof result.analysis === "string") return result.analysis;
  if (typeof result.response === "string") return result.response;
  return JSON.stringify(result, null, 2);
}

function cleanMarkdown(value: string): string {
  return value.replace(/\*\*/g, "").trim();
}

function parseReport(output: string): ParsedLine[] {
  return output
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line): ParsedLine => {
      if (line.startsWith("## ")) {
        return { type: "title", text: cleanMarkdown(line.replace(/^##\s+/, "")) };
      }

      if (line.startsWith("### ")) {
        return { type: "section", text: cleanMarkdown(line.replace(/^###\s+/, "")) };
      }

      if (line.startsWith("- ")) {
        const text = cleanMarkdown(line.replace(/^-\s+/, ""));
        if (text.toLowerCase().includes("no specific recommendation found")) {
          return { type: "info", text };
        }
        return { type: "bullet", text };
      }

      if (/^\d+\.\s+/.test(line)) {
        return { type: "number", text: cleanMarkdown(line) };
      }

      const labelMatch = line.match(/^\*\*(.+?):\*\*\s*(.*)$/);
      if (labelMatch) {
        return {
          type: "label",
          label: cleanMarkdown(labelMatch[1]),
          value: cleanMarkdown(labelMatch[2] || "N/A")
        };
      }

      return { type: "text", text: cleanMarkdown(line) };
    });
}

function AnalystReport({ output }: { output: string }) {
  const parsed = parseReport(output);
  const title = parsed.find((item) => item.type === "title")?.text || "Structured Analyst Report";
  const body = parsed.filter((item) => item.type !== "title");

  const sections: { title: string; rows: ParsedLine[] }[] = [];
  let current: { title: string; rows: ParsedLine[] } | null = null;

  body.forEach((item) => {
    if (item.type === "section") {
      current = { title: item.text, rows: [] };
      sections.push(current);
    } else {
      if (!current) {
        current = { title: "Summary", rows: [] };
        sections.push(current);
      }
      current.rows.push(item);
    }
  });

  return (
    <div className="analyst-report">
      <div className="analyst-report-title">
        <ShieldCheck size={22} />
        <div>
          <h3>{title}</h3>
          <p>Generated SOC analyst-readable output</p>
        </div>
      </div>

      <div className="analyst-section-grid">
        {sections.map((section, index) => (
          <div className="analyst-section-card" key={`${section.title}-${index}`}>
            <div className="analyst-section-header">{section.title}</div>

            <div className="analyst-section-body">
              {section.rows.map((row, rowIndex) => {
                if (row.type === "label") {
                  return (
                    <div className="analyst-label-row" key={rowIndex}>
                      <span>{row.label}</span>
                      <b>{row.value}</b>
                    </div>
                  );
                }

                if (row.type === "bullet") {
                  return (
                    <div className="analyst-bullet-row" key={rowIndex}>
                      <span className="bullet-dot" />
                      <p>{row.text}</p>
                    </div>
                  );
                }

                if (row.type === "number") {
                  return (
                    <div className="analyst-number-row" key={rowIndex}>
                      <span>{row.text.split(".")[0]}</span>
                      <p>{row.text.replace(/^\d+\.\s*/, "")}</p>
                    </div>
                  );
                }

                if (row.type === "info") {
                  return (
                    <div className="analyst-info-pill" key={rowIndex}>
                      <Info size={15} />
                      {row.text}
                    </div>
                  );
                }

                return (
                  <p className="analyst-text-row" key={rowIndex}>
                    {row.text}
                  </p>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// 2026-06-14 21:40 - SOC WORKSPACE PAGE
// Purpose: Run selected module and render professional report output.
// =============================================================================

export default function SOCWorkspacePage() {
  const [selectedModule, setSelectedModule] = useState<ModuleType>("SOC Alert Triage");
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const activeModule = useMemo(
    () => moduleOptions.find((item) => item.label === selectedModule) || moduleOptions[0],
    [selectedModule]
  );

  async function submitWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult("");

    if (!inputText.trim()) {
      setError("Paste a log, alert, RCA notes, or compliance evidence before running analysis.");
      return;
    }

    setLoading(true);

    try {
      const payload = {
        text: inputText,
        input_text: inputText,
        log_text: inputText,
        alert_text: inputText
      };

      let response: any;

      if (selectedModule === "SOC Alert Triage") {
        response = await analyzeSOC(payload);
      } else if (selectedModule === "RCA Generator") {
        response = await generateRCA(payload);
      } else {
        response = await mapGRC(payload);
      }

      setResult(formatResult(response));
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Backend request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="workspace-page">
      <section className="dashboard-title-row">
        <div className="dashboard-title-left">
          <div className="dashboard-title-icon">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h1>SOC Workspace</h1>
            <p>Upload, paste, analyze, and triage security logs.</p>
          </div>
        </div>
      </section>

      <section className="workspace-grid">
        <form className="dashboard-panel workspace-form" onSubmit={submitWorkspace}>
          <div className="panel-heading">
            <h2>
              <FileText size={19} />
              Investigation Input
            </h2>
          </div>

          <label className="enterprise-label">
            Module
            <select value={selectedModule} onChange={(event) => setSelectedModule(event.target.value as ModuleType)}>
              {moduleOptions.map((item) => (
                <option key={item.label} value={item.label}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          <div className="module-context-card">
            <div className="module-context-icon">{activeModule.icon}</div>
            <div>
              <b>{activeModule.label}</b>
              <p>{activeModule.description}</p>
            </div>
          </div>

          <label className="enterprise-label">
            Log / Alert / Evidence Input
            <textarea
              value={inputText}
              onChange={(event) => setInputText(event.target.value)}
              placeholder="Paste security alert, firewall log, Linux event, Windows event, Grafana/Splunk alert, RCA notes, or GRC evidence here..."
            />
          </label>

          {error && <div className="dashboard-error">{error}</div>}

          <button className="primary-action-btn" type="submit" disabled={loading}>
            {loading ? "Running..." : activeModule.buttonText}
          </button>
        </form>

        <section className="dashboard-panel output-panel">
          <div className="panel-heading">
            <h2>
              <BrainCircuit size={19} />
              Structured Output
            </h2>
          </div>

          {result ? (
            <AnalystReport output={result} />
          ) : (
            <div className="empty-output">
              Select a module, paste input, and run analysis. A professional analyst report will appear here.
            </div>
          )}
        </section>
      </section>
    </main>
  );
}