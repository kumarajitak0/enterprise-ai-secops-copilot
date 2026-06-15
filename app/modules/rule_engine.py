# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/rule_engine.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Backward-compatible wrapper around the enterprise playbook engine.
# =============================================================================

from __future__ import annotations

from typing import Any

from core.normalizer import normalize_log
from app.modules.playbook_engine import get_playbook as get_dynamic_playbook


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Compatibility wrapper for old imports.
# =============================================================================

def get_playbook(log_type: str, text: str) -> dict[str, Any]:
    normalized = normalize_log(text)
    playbook = get_dynamic_playbook(
        event_id=normalized.get("event_id", "unknown"),
        source_type=normalized.get("source_type", log_type),
        severity="Low",
    )

    return {
        "checks": [
            "Validate timestamp, host, user, source IP, destination IP, process, and event ID.",
            "Correlate activity before and after the event.",
            "Confirm whether the event matches expected business or admin behavior.",
            "Escalate if suspicious behavior or production impact is confirmed.",
        ],
        "commands": (
            playbook.get("windows_commands", [])
            + playbook.get("linux_commands", [])
            + playbook.get("network_commands", [])
        ),
        "recommendations": playbook.get("containment", []) + playbook.get("severity_actions", []),
        "splunk_queries": playbook.get("splunk_queries", []),
    }


# =============================================================================
# End: Compatibility wrapper
# =============================================================================