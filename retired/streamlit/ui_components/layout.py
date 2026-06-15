# # =============================================================================
# # Project: Enterprise AI SecOps Copilot
# # File: app/ui_components/layout.py
# # Date Updated: 2026-06-14 17:18
# # Purpose:
# #   Final reference-match layout fix for enterprise SaaS dashboard.
# # =============================================================================

# from __future__ import annotations

# import html
# import streamlit as st

# PAGES = ["Dashboard", "SOC Workspace", "Cases", "Administration"]


# def get_active_page() -> str:
#     query_page = st.query_params.get("page")

#     if query_page in PAGES:
#         st.session_state["page"] = query_page

#     if "page" not in st.session_state:
#         st.session_state["page"] = "Dashboard"

#     return st.session_state["page"]


# def render_top_navigation() -> None:
#     active = get_active_page()
#     username = html.escape(st.session_state.get("username", "Admin"))
#     role = html.escape(st.session_state.get("role", "Administrator"))
#     initial = username[:1].upper() if username else "A"

#     nav_items = ""
#     for page in PAGES:
#         active_class = "active" if page == active else ""
#         nav_items += f"""
#         <a class="top-nav-item {active_class}" href="/?page={page}">
#             {page}
#         </a>
#         """

#     st.html(
#         f"""
#         <div class="top-nav-shell">
#             <div class="top-brand">
#                 <div class="brand-logo">🛡</div>
#                 <div>
#                     <div class="brand-title">Enterprise AI SecOps Copilot</div>
#                     <div class="brand-subtitle">AI-Powered SOC Operations Workspace</div>
#                 </div>
#             </div>

#             <div class="top-nav-center">
#                 {nav_items}
#             </div>

#             <div class="top-right">
#                 <div class="local-pill">Local Mode</div>
#                 <div class="theme-icon">☼</div>
#                 <div class="top-divider"></div>
#                 <div class="avatar">{initial}</div>
#                 <div>
#                     <div class="user-name">{username}</div>
#                     <div class="user-role">{role}</div>
#                 </div>
#             </div>
#         </div>
#         """
#     )

#=============================================================================

# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_components/layout.py
# Date Updated: 2026-06-14 19:11
# Purpose:
#   Fix session persistence, page navigation, Go to Workspace routing,
#   theme toggle, and horizontal overflow.
# =============================================================================

from __future__ import annotations

import html
from urllib.parse import quote

import streamlit as st

PAGES = ["Dashboard", "SOC Workspace", "Cases", "Administration"]


def get_active_page() -> str:
    page = st.session_state.get("page", "Dashboard")

    if page not in PAGES:
        page = "Dashboard"
        st.session_state["page"] = page

    return page


# =============================================================================
# 2026-06-14 19:11 - Added/Updated: Enterprise top navigation
# =============================================================================

def render_top_navigation() -> None:
    active = get_active_page()
    username = html.escape(st.session_state.get("username", "Admin") or "Admin")
    role = html.escape(st.session_state.get("role", "Administrator") or "Administrator")
    initial = username[:1].upper()
    theme = st.session_state.get("theme", "dark")
    theme_icon = "☀" if theme == "dark" else "☾"

    nav_html = ""

    for page in PAGES:
        active_class = "active" if page == active else ""
        nav_html += f"""
        <a class="top-nav-item {active_class}" href="/?page={quote(page)}">
            <span>{page}</span>
        </a>
        """

    st.markdown(
        f"""
        <header class="top-nav-shell">
            <div class="top-brand">
                <div class="brand-logo">🛡</div>
                <div class="brand-copy">
                    <div class="brand-title">Enterprise AI SecOps Copilot</div>
                    <div class="brand-subtitle">AI-Powered SOC Operations Workspace</div>
                </div>
            </div>

            <nav class="top-nav-center">
                {nav_html}
            </nav>

            <div class="top-right">
                <div class="local-pill">Local Mode</div>
                <a class="theme-toggle" href="/?page={quote(active)}&theme_toggle=1">{theme_icon}</a>
                <div class="top-divider"></div>
                <div class="avatar">{initial}</div>
                <div class="user-meta">
                    <div class="user-name">{username}</div>
                    <div class="user-role">{role}</div>
                </div>
                <a class="logout-pill" href="/?logout=1">Logout</a>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )