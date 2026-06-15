# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/playbook_engine.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Load and select deterministic SOC playbooks for case-ready investigations.
# =============================================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PLAYBOOK_FILE = Path(__file__).resolve().parents[1] / "knowledge_base" / "playbooks.json"


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Safe playbook loading.
# =============================================================================

def load_playbooks() -> dict[str, Any]:
    if not PLAYBOOK_FILE.exists():
        return {}

    try:
        with open(PLAYBOOK_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


# =============================================================================
# End: Safe playbook loading
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Category selection and default command packs.
# =============================================================================

DEFAULT_CATEGORY_COMMANDS = {
    "network_security": {
        "windows_commands": ["Get-NetTCPConnection", "Test-NetConnection <destination-host> -Port <port>"],
        "linux_commands": ["ss -antp", "ip route", "ping <destination-ip>"],
        "network_commands": ["nslookup <ip-or-domain>", "traceroute <destination-ip>"],
        "splunk_queries": ["index=* (blocked OR denied OR firewall) earliest=-24h"],
        "containment": ["Validate source/destination/port.", "Block confirmed malicious source only after evidence review."],
    },
    "cloud_iam": {
        "windows_commands": [],
        "linux_commands": [],
        "network_commands": [],
        "splunk_queries": ["index=* (CloudTrail OR ConsoleLogin OR AssumeRole OR iam) earliest=-24h"],
        "containment": ["Review IAM user/role activity.", "Revoke suspicious sessions or keys if confirmed."],
    },
    "endpoint_security": {
        "windows_commands": ["Get-Process", "Get-WinEvent -LogName Security -MaxEvents 50"],
        "linux_commands": ["ps aux", "journalctl --since '24 hours ago'"],
        "network_commands": ["netstat -ano", "ss -antp"],
        "splunk_queries": ["index=* (malware OR ransomware OR quarantined OR edr) earliest=-24h"],
        "containment": ["Isolate host only if malicious activity is confirmed.", "Preserve forensic evidence."],
    },
    "web_proxy": {
        "windows_commands": [],
        "linux_commands": ["tail -n 100 /var/log/nginx/access.log", "tail -n 100 /var/log/apache2/access.log"],
        "network_commands": ["curl -I <url>", "nslookup <domain>"],
        "splunk_queries": ["index=* (status=500 OR status=403 OR status=404 OR uri=*) earliest=-24h"],
        "containment": ["Validate user-agent, source IP, URL, status code, and request volume."],
    },
}


def _category_from_source(source_type: str, event_id: str) -> str:
    source_lower = (source_type or "").lower()

    if event_id == "4688":
        return "windows_process"
    if event_id == "4798":
        return "account_discovery"
    if event_id == "1102":
        return "defense_evasion"
    if event_id == "5857":
        return "windows_wmi_activity"
    if "windows" in source_lower:
        return "windows_authentication"
    if "linux" in source_lower:
        return "linux_authentication"
    if "network" in source_lower or "firewall" in source_lower:
        return "network_security"
    if "cloud" in source_lower:
        return "cloud_iam"
    if "endpoint" in source_lower or "edr" in source_lower:
        return "endpoint_security"
    if "web" in source_lower or "proxy" in source_lower:
        return "web_proxy"

    return "application_or_monitoring"


# =============================================================================
# End: Category selection and default command packs
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Main playbook selector.
# =============================================================================

def get_playbook(
    event_id: str = "unknown",
    source_type: str = "generic_log",
    severity: str = "Low",
) -> dict[str, Any]:
    playbooks = load_playbooks()

    event_playbooks = playbooks.get("event_playbooks", {})
    category_commands = playbooks.get("category_commands", {})
    severity_overrides = playbooks.get("severity_overrides", {})

    event_info = event_playbooks.get(str(event_id), {})
    category = event_info.get("category") or _category_from_source(source_type, event_id)

    command_pack = category_commands.get(category) or DEFAULT_CATEGORY_COMMANDS.get(category, {})

    return {
        "title": event_info.get("title", "Generic SOC Investigation Playbook"),
        "category": category,
        "event_id": event_id,
        "severity": event_info.get("severity", severity),
        "mitre": event_info.get("mitre", "No deterministic MITRE mapping"),
        "windows_commands": command_pack.get("windows_commands", []),
        "linux_commands": command_pack.get("linux_commands", []),
        "splunk_queries": command_pack.get("splunk_queries", []),
        "network_commands": command_pack.get("network_commands", []),
        "containment": command_pack.get("containment", []),
        "severity_actions": severity_overrides.get(severity, []),
    }


# =============================================================================
# End: Main playbook selector
# =============================================================================