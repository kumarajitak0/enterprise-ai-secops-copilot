# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_components/pages.py
# Date Created: 2026-05-27
# Date Updated: 2026-06-14
# Purpose:
#   Compatibility wrapper that imports page renderers from app/ui_pages.
# =============================================================================

from app.ui_pages.dashboard_page import render_dashboard
from app.ui_pages.analyze_page import render_analyze_logs
from app.ui_pages.cases_page import render_cases
from app.ui_pages.admin_page import render_admin_settings