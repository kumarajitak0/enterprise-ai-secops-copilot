# # =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_pages/dashboard_page.py
# Date Updated: 2026-06-14 19:40
# Purpose:
#   Fix raw HTML rendering by using safe HTML tags, removing problematic
#   semantic tags/links, and using Streamlit buttons for navigation.
# =============================================================================

from __future__ import annotations

from datetime import datetime
import html

import streamlit as st

from app.ui_components.api_client import get_dashboard_stats, health_check


def pct(part: int, total: int) -> str:
    if total <= 0:
        return "0.00%"
    return f"{(part / total) * 100:.2f}%"


def safe(value) -> str:
    if value is None:
        return "N/A"
    return html.escape(str(value))


def severity_badge(severity: str) -> str:
    sev = (severity or "Unknown").lower()

    if sev == "high":
        css = "badge-red"
    elif sev == "medium":
        css = "badge-amber"
    elif sev == "compliance":
        css = "badge-purple"
    elif sev == "low":
        css = "badge-green"
    else:
        css = "badge-blue"

    return f'<span class="soc-badge {css}">{safe(severity)}</span>'


def status_badge(status: str) -> str:
    value = status or "New"
    css = "badge-blue"

    if value.lower() in ["investigating", "assigned"]:
        css = "badge-amber"
    elif value.lower() in ["resolved", "closed"]:
        css = "badge-green"

    return f'<span class="soc-badge {css}">{safe(value)}</span>'


def mini_trend() -> str:
    return """
    <svg class="mini-trend" viewBox="0 0 130 36">
        <polyline
            points="2,28 18,26 34,18 50,21 66,14 82,17 98,11 124,24"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
        />
    </svg>
    """


def kpi_card(title: str, value: int, subtitle: str, icon: str, color: str) -> str:
    return f"""
    <div class="dash-kpi-card">
        <div class="kpi-top">
            <div class="dash-kpi-icon {color}">{icon}</div>
            <div>
                <div class="dash-kpi-title">{safe(title)}</div>
                <div class="dash-kpi-value">{value}</div>
            </div>
        </div>
        <div class="kpi-bottom">
            <span>{safe(subtitle)}</span>
            {mini_trend()}
        </div>
    </div>
    """


def go_to_page(page: str) -> None:
    st.session_state["page"] = page
    st.rerun()


def render_dashboard() -> None:
    ok, stats = get_dashboard_stats()

    if not ok:
        st.error("Backend unavailable. Start FastAPI on port 8001.")
        st.code(stats.get("error", "Unknown backend error"))
        return

    health_ok, health = health_check()
    if not health_ok:
        health = {}

    total = int(stats.get("total_cases") or 0)
    high = int(stats.get("high_severity") or 0)
    medium = int(stats.get("medium_severity") or 0)
    grc = int(stats.get("grc_evidence") or 0)
    recent_cases = stats.get("recent_cases", [])

    soc_count = len([c for c in recent_cases if c.get("module") == "SOC Alert Triage"])
    rca_count = len([c for c in recent_cases if c.get("module") == "RCA Generator"])
    grc_count = len([c for c in recent_cases if c.get("module") == "GRC Evidence Mapping"])

    queue_rows = ""

    for case in recent_cases[:5]:
        queue_rows += f"""
        <tr>
            <td>{safe(case.get("timestamp"))}</td>
            <td>{safe(case.get("module"))}</td>
            <td>{severity_badge(case.get("severity"))}</td>
            <td>{safe(case.get("type"))}</td>
            <td>{status_badge(case.get("status"))}</td>
        </tr>
        """

    if not queue_rows:
        queue_rows = """
        <tr>
            <td colspan="5" class="empty-row">No investigations yet.</td>
        </tr>
        """

    dashboard_html = f"""
    <div class="dash-page">

        <div class="dash-title-row">
            <div class="dash-title-wrap">
                <div class="dash-title-icon">⌂</div>
                <div>
                    <h1>Dashboard</h1>
                    <p>Overview of your security operations</p>
                </div>
            </div>

            <div class="dash-actions">
                <div class="dash-date">📅 {datetime.now().strftime("%B %d, %Y %I:%M %p")}</div>
                <div class="dash-refresh">⟳ Refresh</div>
            </div>
        </div>

        <div class="dash-kpi-grid">
            {kpi_card("Total Cases", total, "All time cases", "▣", "blue")}
            {kpi_card("High Severity", high, f"{pct(high, total)} of total", "!", "red")}
            {kpi_card("Medium Severity", medium, f"{pct(medium, total)} of total", "!", "amber")}
            {kpi_card("GRC Evidence", grc, f"{pct(grc, total)} of total", "▤", "green")}
        </div>

        <div class="dash-main-grid">
            <div class="dash-panel">
                <h2>▧ Recent Investigation Queue</h2>
                <div class="soc-table-wrapper">
                    <table class="soc-table">
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
                            {queue_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="dash-panel">
                <h2>⌘ Platform Status</h2>

                <div class="platform-row">
                    <span>🚀 FastAPI Backend</span>
                    <b class="ready">{safe(health.get("backend", "unknown"))}</b>
                </div>

                <div class="platform-row">
                    <span>🧠 Local LLM</span>
                    <b class="planned">{safe(health.get("ollama", "planned"))}</b>
                </div>

                <div class="platform-row">
                    <span>🛡 RBAC / IAM</span>
                    <b class="ready">{safe(health.get("auth", "unknown"))}</b>
                </div>

                <div class="platform-row">
                    <span>🗄 SQLite Case Store</span>
                    <b class="active">{safe(health.get("database", "unknown"))}</b>
                </div>

                <div class="platform-row">
                    <span>⌁ Splunk Connector</span>
                    <b class="planned">planned</b>
                </div>
            </div>
        </div>
    </div>
    """

    # =============================================================================
    # 2026-06-14 19:40 - Added/Updated:
    # Render safe HTML only. Do not render semantic tags or raw links that may appear as text.
    # =============================================================================
    st.markdown(dashboard_html, unsafe_allow_html=True)

    if st.button("☰ View All Cases", key="dash_view_all_cases"):
        go_to_page("Cases")

    usecase_html_open = """
    <div class="dash-panel usecase-panel">
        <h2>▰ Use Case Overview</h2>
    </div>
    """
    st.markdown(usecase_html_open, unsafe_allow_html=True)

    u1, u2, u3 = st.columns(3)

    with u1:
        st.markdown(
            f"""
            <div class="usecase-card blue-border">
                <div class="usecase-icon blue">🛡</div>
                <h3>SOC Alert Triage</h3>
                <p>Detect, analyze, and respond to security alerts with MITRE mapping and recommended playbooks.</p>
                <div class="usecase-footer">
                    <span><b>{soc_count}</b> Cases</span>
                    <span>{pct(soc_count, total)} of total</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Workspace →", key="dash_soc_workspace", use_container_width=True):
            go_to_page("SOC Workspace")

    with u2:
        st.markdown(
            f"""
            <div class="usecase-card purple-border">
                <div class="usecase-icon purple">🔎</div>
                <h3>RCA Generator</h3>
                <p>Perform root cause analysis for incidents and generate structured RCA reports.</p>
                <div class="usecase-footer">
                    <span><b>{rca_count}</b> Cases</span>
                    <span>{pct(rca_count, total)} of total</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Workspace →", key="dash_rca_workspace", use_container_width=True):
            go_to_page("SOC Workspace")

    with u3:
        st.markdown(
            f"""
            <div class="usecase-card green-border">
                <div class="usecase-icon green">📋</div>
                <h3>GRC Evidence Mapping</h3>
                <p>Map controls, frameworks, and evidence for compliance and audit readiness.</p>
                <div class="usecase-footer">
                    <span><b>{grc_count}</b> Cases</span>
                    <span>{pct(grc_count, total)} of total</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Workspace →", key="dash_grc_workspace", use_container_width=True):
            go_to_page("SOC Workspace")

    st.markdown(
        """
        <div class="dash-footer">
            <span>Enterprise AI SecOps Copilot v1.0.0</span>
            <span>© 2026 SecOps Copilot</span>
        </div>
        """,
        unsafe_allow_html=True,
    )