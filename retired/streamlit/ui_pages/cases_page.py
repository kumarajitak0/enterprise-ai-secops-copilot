# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_pages/cases_page.py
# Date Updated: 2026-06-14
# Purpose:
#   Cases page connected to FastAPI /cases endpoint.
# =============================================================================

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui_components.api_client import get_cases


def render_cases() -> None:
    st.markdown("# Cases")
    st.caption("Saved investigations and case review.")

    ok, data = get_cases()

    if not ok:
        st.error("Backend unavailable. Start FastAPI on port 8001.")
        st.code(data.get("error", "Unknown error"))
        return

    cases = data.get("cases", [])

    if not cases:
        st.info("No cases saved yet.")
        return

    rows = [
        {
            "Case ID": c.get("id"),
            "Time": c.get("timestamp"),
            "Module": c.get("module"),
            "Severity": c.get("severity"),
            "Type": c.get("type"),
            "Status": c.get("status"),
        }
        for c in cases
    ]

    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    labels = [
        f"Case {c.get('id')} | {c.get('module')} | {c.get('severity')}"
        for c in cases
    ]

    selected = st.selectbox("Select case", labels)
    selected_case = cases[labels.index(selected)]

    st.markdown("### Input")
    st.code(selected_case.get("input_text", ""))

    st.markdown("### Output")
    st.markdown(selected_case.get("output_text", ""))