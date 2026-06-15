# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_pages/analysis_output.py
# Date Created: 2026-06-14
# Purpose:
#   Module-specific result rendering and SQLite case save.
# =============================================================================

import requests
import streamlit as st

from app.ui_components.api_client import save_case
from app.ui_components.result_panels import (
    render_guardrail_warning,
    render_mitre_mapping,
    render_pipeline_details,
    render_dynamic_playbook,
    render_analyst_notes_guidance,
)


def render_soc_output(data: dict) -> None:
    render_guardrail_warning(data)
    render_mitre_mapping(data)
    render_pipeline_details(data)
    render_dynamic_playbook(data)

    with st.expander("SOC Analyst Summary", expanded=True):
        st.markdown(data.get("result", "No result returned."))


def render_rca_output(data: dict) -> None:
    with st.expander("RCA Report", expanded=True):
        st.markdown(data.get("result", "No result returned."))

    with st.expander("RCA Validation Steps", expanded=True):
        st.markdown(
            """
            1. Confirm exact incident timestamp.
            2. Identify affected host, service, user, or application.
            3. Review logs before, during, and after the incident.
            4. Validate business or service impact.
            5. Confirm recovery or remaining issue.
            6. Document root cause and prevention.
            """
        )


def render_grc_output(data: dict) -> None:
    with st.expander("GRC Evidence Mapping", expanded=True):
        st.markdown(data.get("result", "No result returned."))

    with st.expander("Audit Evidence Handling", expanded=True):
        st.markdown(
            """
            1. Save original evidence or log sample.
            2. Identify control area.
            3. Map evidence to framework requirement.
            4. Document control owner.
            5. Record reviewer notes.
            6. Store evidence for audit review.
            """
        )


def render_analysis_output(
    data: dict,
    elapsed: float,
    module: str,
    input_text: str,
    analyst_note: str,
    case_status: str = "New",
) -> None:
    st.markdown("## Analysis Result")

    r1, r2, r3 = st.columns(3)
    r1.metric("Severity", data.get("severity", "N/A"))
    r2.metric("Detected Type", data.get("log_type", "N/A"))
    r3.metric("Runtime", f"{elapsed}s")

    if "log_type" in data:
        st.info(f"Detected Log Type: {data.get('log_type')}")

    st.divider()

    if module == "SOC Alert Triage":
        render_soc_output(data)
    elif module == "RCA Generator":
        render_rca_output(data)
    elif module == "GRC Evidence Mapping":
        render_grc_output(data)
    else:
        st.warning("Unknown module selected.")
        st.markdown(data.get("result", "No result returned."))

    ai_output = data.get("result", "No result returned.")

    case_payload = {
        "module": module,
        "severity": data.get("severity", "Unknown"),
        "log_type": data.get("log_type", "Unknown"),
        "input_text": input_text,
        "analyst_note": analyst_note,
        "ai_output": ai_output,
        "case_status": case_status,
    }

    try:
        save_response = save_case(case_payload)

        if save_response.status_code == 200:
            st.success("Case saved to SQLite with analyst notes.")
        else:
            st.warning("Analysis completed, but case was not saved.")
            st.code(save_response.text)

    except requests.exceptions.RequestException as error:
        st.warning(f"Analysis completed, but save-case API failed: {error}")

    render_analyst_notes_guidance()