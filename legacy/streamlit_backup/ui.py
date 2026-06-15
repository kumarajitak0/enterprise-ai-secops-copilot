# # =============================================================================
# # Project: Enterprise AI SecOps Copilot
# # File: app/ui.py
# # Date Updated: 2026-06-14
# # Purpose:
# #   Streamlit entry point with auth routing and SaaS top navigation shell.
# # =============================================================================

# from __future__ import annotations

# import sys
# from pathlib import Path

# import streamlit as st

# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# sys.path.append(str(PROJECT_ROOT))

# from app.ui_components.api_client import login, register
# from app.ui_components.layout import render_top_navigation, get_active_page
# from app.ui_pages.dashboard_page import render_dashboard
# from app.ui_pages.analyze_page import render_soc_workspace
# from app.ui_pages.cases_page import render_cases
# from app.ui_pages.admin_page import render_admin


# CUSTOM_CSS = PROJECT_ROOT / "app" / "styles" / "custom.css"
# AUTH_CSS = PROJECT_ROOT / "app" / "styles" / "auth.css"


# def load_css(path: Path) -> None:
#     if path.exists():
#         st.markdown(
#             f"<style>{path.read_text(encoding='utf-8')}</style>",
#             unsafe_allow_html=True,
#         )


# def is_authenticated() -> bool:
#     return st.session_state.get("authenticated", False)


# def logout() -> None:
#     st.session_state.clear()
#     st.rerun()


# def render_login_register() -> None:
#     load_css(AUTH_CSS)

#     st.markdown(
#         """
#         <div class="auth-hero">
#             <div class="auth-badge">RBAC Enabled · Local AI Mode · SOC Workspace</div>
#             <h1>Enterprise AI SecOps Copilot</h1>
#             <p>Secure login for SOC triage, RCA generation, GRC evidence mapping, and case tracking.</p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     left, right = st.columns([1.1, 0.9])

#     with left:
#         login_tab, register_tab = st.tabs(["Login", "Register"])

#         with login_tab:
#             st.markdown("### Secure Login")
#             username = st.text_input("Username", key="login_username")
#             password = st.text_input("Password", type="password", key="login_password")

#             if st.button("Login", type="primary", use_container_width=True):
#                 ok, data = login(username, password)

#                 if ok and data.get("success"):
#                     st.session_state["authenticated"] = True
#                     st.session_state["username"] = data.get("username")
#                     st.session_state["role"] = data.get("role", "Viewer")
#                     st.session_state["page"] = "Dashboard"
#                     st.success("Login successful.")
#                     st.rerun()
#                 else:
#                     st.error(data.get("message", "Login failed. Start backend or check credentials."))

#         with register_tab:
#             st.markdown("### Register User")
#             username = st.text_input("Create Username", key="register_username")
#             password = st.text_input("Create Password", type="password", key="register_password")
#             role = st.selectbox(
#                 "Role",
#                 ["Admin", "SOC Analyst", "GRC Analyst", "Viewer"],
#                 key="register_role",
#             )

#             if st.button("Register", type="primary", use_container_width=True):
#                 ok, data = register(username, password, role)

#                 if ok and data.get("success"):
#                     st.success("Registration successful. Go to Login tab.")
#                 else:
#                     st.error(data.get("message", "Registration failed."))

#     with right:
#         st.markdown(
#             """
#             <div class="auth-card">
#                 <h3>Access Model</h3>
#                 <p><b>Admin</b> Full workspace access.</p>
#                 <p><b>SOC Analyst</b> Dashboard, SOC Workspace, Cases.</p>
#                 <p><b>GRC Analyst</b> Dashboard, GRC evidence, Cases.</p>
#                 <p><b>Viewer</b> Read-only dashboard and cases.</p>
#             </div>

#             <div class="auth-card green">
#                 <h3>Security Design</h3>
#                 <p>Passwords hashed with bcrypt.</p>
#                 <p>SQLite local authentication.</p>
#                 <p>Session-based Streamlit access.</p>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )


# def main() -> None:
#     st.set_page_config(
#         page_title="Enterprise AI SecOps Copilot",
#         layout="wide",
#         initial_sidebar_state="collapsed",
#     )

#     load_css(CUSTOM_CSS)

#     if not is_authenticated():
#         render_login_register()
#         return

#     render_top_navigation()

#     page = get_active_page()

#     if page == "Dashboard":
#         render_dashboard()

#     elif page == "SOC Workspace":
#         render_soc_workspace()

#     elif page == "Cases":
#         render_cases()

#     elif page == "Administration":
#         render_admin()

#     st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
#     if st.button("Logout", key="logout_button"):
#         logout()
#     st.markdown("</div>", unsafe_allow_html=True)


# if __name__ == "__main__":
#     main()


#=====================================================================

# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui.py
# Date Updated: 2026-06-14 19:11
# Purpose:
#   Fix session persistence, page navigation, Go to Workspace routing,
#   theme toggle, and horizontal overflow.
# =============================================================================

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.ui_components.api_client import login, register
from app.ui_components.layout import render_top_navigation, get_active_page
from app.ui_pages.dashboard_page import render_dashboard
from app.ui_pages.analyze_page import render_soc_workspace
from app.ui_pages.cases_page import render_cases
from app.ui_pages.admin_page import render_admin


CUSTOM_CSS = PROJECT_ROOT / "app" / "styles" / "custom.css"
AUTH_CSS = PROJECT_ROOT / "app" / "styles" / "auth.css"


def load_css(path: Path) -> None:
    if path.exists():
        st.markdown(
            f"<style>{path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


# =============================================================================
# 2026-06-14 19:11 - Added/Updated: Session initialization
# =============================================================================

def init_session() -> None:
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("role", "Viewer")
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("theme", "dark")


# =============================================================================
# 2026-06-14 19:11 - Added/Updated: Query action handling
# =============================================================================

def handle_query_actions() -> None:
    query_page = st.query_params.get("page")
    logout_requested = st.query_params.get("logout")
    theme_toggle = st.query_params.get("theme_toggle")

    if query_page in ["Dashboard", "SOC Workspace", "Cases", "Administration"]:
        st.session_state["page"] = query_page

    if theme_toggle == "1":
        st.session_state["theme"] = (
            "light" if st.session_state.get("theme") == "dark" else "dark"
        )
        current_page = st.session_state.get("page", "Dashboard")
        st.query_params.clear()
        st.query_params["page"] = current_page
        st.rerun()

    if logout_requested == "1":
        for key in ["authenticated", "username", "role", "page"]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state["authenticated"] = False
        st.session_state["theme"] = st.session_state.get("theme", "dark")
        st.query_params.clear()
        st.rerun()


def inject_theme_class() -> None:
    theme = st.session_state.get("theme", "dark")
    st.markdown(
        f"""
        <style>
        .stApp {{
            --active-theme: "{theme}";
        }}
        </style>
        <div class="theme-root theme-{theme}"></div>
        """,
        unsafe_allow_html=True,
    )


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))


def render_login_register() -> None:
    load_css(AUTH_CSS)

    st.markdown(
        """
        <div class="auth-hero">
            <div class="auth-badge">RBAC Enabled · Local AI Mode · SOC Workspace</div>
            <h1>Enterprise AI SecOps Copilot</h1>
            <p>Secure login for SOC triage, RCA generation, GRC evidence mapping, and case tracking.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 0.9])

    with left:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            st.markdown("### Secure Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", type="primary", use_container_width=True):
                ok, data = login(username, password)

                if ok and data.get("success"):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = data.get("username", username)
                    st.session_state["role"] = data.get("role", "Viewer")
                    st.session_state["page"] = "Dashboard"
                    st.query_params.clear()
                    st.query_params["page"] = "Dashboard"
                    st.rerun()
                else:
                    st.error(
                        data.get(
                            "message",
                            "Login failed. Start backend or check credentials.",
                        )
                    )

        with register_tab:
            st.markdown("### Register User")
            username = st.text_input("Create Username", key="register_username")
            password = st.text_input(
                "Create Password",
                type="password",
                key="register_password",
            )
            role = st.selectbox(
                "Role",
                ["Admin", "SOC Analyst", "GRC Analyst", "Viewer"],
                key="register_role",
            )

            if st.button("Register", type="primary", use_container_width=True):
                ok, data = register(username, password, role)

                if ok and data.get("success"):
                    st.success("Registration successful. Go to Login tab.")
                else:
                    st.error(data.get("message", "Registration failed."))

    with right:
        st.markdown(
            """
            <div class="auth-card">
                <h3>Access Model</h3>
                <p><b>Admin</b> Full workspace access.</p>
                <p><b>SOC Analyst</b> Dashboard, SOC Workspace, Cases.</p>
                <p><b>GRC Analyst</b> Dashboard, GRC evidence, Cases.</p>
                <p><b>Viewer</b> Read-only dashboard and cases.</p>
            </div>

            <div class="auth-card green">
                <h3>Security Design</h3>
                <p>Passwords hashed with bcrypt.</p>
                <p>SQLite local authentication.</p>
                <p>Session-based Streamlit access.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="Enterprise AI SecOps Copilot",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_session()
    load_css(CUSTOM_CSS)
    handle_query_actions()
    inject_theme_class()

    if not is_authenticated():
        render_login_register()
        return

    render_top_navigation()

    page = get_active_page()

    if page == "Dashboard":
        render_dashboard()

    elif page == "SOC Workspace":
        render_soc_workspace()

    elif page == "Cases":
        render_cases()

    elif page == "Administration":
        render_admin()


if __name__ == "__main__":
    main()