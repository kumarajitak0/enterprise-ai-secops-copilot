# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_pages/analyze_page.py
# Date Updated: 2026-06-14
# Purpose:
#   Working SOC Workspace connected to backend analysis endpoints.
# =============================================================================

from __future__ import annotations

import streamlit as st

from app.ui_components.api_client import analyze_soc, generate_rca, map_grc


def render_result(data: dict) -> None:
    st.markdown("## Analysis Result")

    c1, c2, c3 = st.columns(3)
    c1.metric("Module", data.get("module", "N/A"))
    c2.metric("Severity", data.get("severity", "N/A"))
    c3.metric("Type", data.get("type", "N/A"))

    st.markdown(data.get("output", "No output returned."))


def render_soc_workspace() -> None:
    st.markdown("# SOC Workspace")
    st.caption("Analyze logs, generate RCA, map GRC evidence, and save cases automatically.")

    module = st.selectbox(
        "Analysis Module",
        ["SOC Alert Triage", "RCA Generator", "GRC Evidence Mapping"],
    )

    input_text = st.text_area(
        "Paste Windows Event Log, Splunk event, firewall log, application error, or incident note",
        height=300,
        placeholder="""Example:
Log Name: Security
Source: Microsoft-Windows-Security-Auditing
Event ID: 4625
Computer: DC-PROD-01
An account failed to log on.
Source Network Address: 192.168.10.55""",
    )

    if st.button("Run Analysis", type="primary", use_container_width=True):
        if not input_text.strip():
            st.warning("Paste a log or event before running analysis.")
            return

        with st.spinner("Running backend analysis..."):
            if module == "SOC Alert Triage":
                ok, data = analyze_soc(input_text)
            elif module == "RCA Generator":
                ok, data = generate_rca(input_text)
            else:
                ok, data = map_grc(input_text)

        if not ok:
            st.error("Backend unavailable. Start FastAPI on port 8001.")
            st.code(data.get("error", "Unknown error"))
            return

        render_result(data)
        st.success("Analysis completed and saved as a case.")