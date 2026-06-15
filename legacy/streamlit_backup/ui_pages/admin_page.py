# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_pages/admin_page.py
# Date Updated: 2026-06-14
# Purpose:
#   Administration page with backend health and integration status.
# =============================================================================

from __future__ import annotations

import streamlit as st

from app.ui_components.api_client import health_check


def render_admin() -> None:
    st.markdown("# Administration")
    st.caption("RBAC, authentication, database, and integration status.")

    ok, health = health_check()

    if not ok:
        st.error("Backend unavailable. Start FastAPI on port 8001.")
        st.code(health.get("error", "Unknown error"))
        return

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Core Services")
        st.success(f"FastAPI Backend: {health.get('backend')}")
        st.success(f"SQLite Case Store: {health.get('database')}")
        st.success(f"Authentication: {health.get('auth')}")
        st.info(f"Local LLM: {health.get('ollama')}")

    with c2:
        st.markdown("### Planned Integrations")
        st.warning("Splunk Connector: Planned")
        st.warning("Grafana Webhook: Planned")
        st.warning("PDF Export: Planned")