# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/rca_generator.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Generate RCA notes from deterministic facts without inventing root cause.
# =============================================================================

from __future__ import annotations

from typing import Any

from app.modules.classifier import detect_event_category, detect_log_type, estimate_severity
from app.modules.ollama_client import ask_llm
from core.normalizer import NOT_PRESENT, normalize_log


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# RCA builder.
# =============================================================================

def generate_rca_case(data: str) -> dict[str, Any]:
    text = data or ""
    normalized = normalize_log(text)
    log_type = detect_log_type(text)
    severity = estimate_severity(text)
    category = detect_event_category(text)

    prompt = f"""
You are an RCA analyst. Use only provided facts. Do not invent root cause.

Facts:
Log Type: {log_type}
Category: {category}
Severity: {severity}
Timestamp: {normalized.get("timestamp")}
Host: {normalized.get("host")}
User: {normalized.get("user")}
Source IP: {normalized.get("source_ip")}
Destination IP: {normalized.get("destination_ip")}
Event ID: {normalized.get("event_id")}

Write a concise RCA summary. Say root cause is not confirmed if evidence is insufficient.
"""
    narrative = ask_llm(prompt, num_predict=180)

    output = f"""
    1. Incident Summary:
    {narrative}

    2. Business / Technical Impact:
    Not confirmed from one log alone. Validate affected service, host, user count, transaction impact, and alert duration.

    3. Likely Root Cause:
    Root cause is not confirmed from the provided log alone.

    4. Evidence Observed:
    - Log Type: {log_type}
    - Category: {category}
    - Severity: {severity}
    - Timestamp: {normalized.get("timestamp", NOT_PRESENT)}
    - Host: {normalized.get("host", NOT_PRESENT)}
    - User: {normalized.get("user", NOT_PRESENT)}
    - Source IP: {normalized.get("source_ip", NOT_PRESENT)}
    - Destination IP: {normalized.get("destination_ip", NOT_PRESENT)}
    - Event ID: {normalized.get("event_id", NOT_PRESENT)}

    5. Missing Evidence Needed:
    - Related logs before, during, and after the event.
    - Monitoring metrics.
    - Recent deployment or configuration change records.
    - Service health data.
    - Authentication or session history.
    - Network connectivity evidence.

    6. Validation Steps:
    - Confirm exact incident timeline.
    - Confirm affected host, service, user, and business function.
    - Review correlated logs from the same time window.
    - Check recent deployments, patching, firewall, DNS, or certificate changes.
    - Confirm recovery evidence.

    7. Linux Validation Commands:
    - systemctl status <service-name>
    - journalctl --since '30 minutes ago'
    - journalctl -u <service-name> --since '30 minutes ago'
    - df -h
    - free -m
    - top
    - ss -antp

    8. Windows Validation Commands:
    - Get-WinEvent -LogName System -MaxEvents 50
    - Get-WinEvent -LogName Application -MaxEvents 50
    - Get-Service
    - Get-Process
    - Get-NetTCPConnection
    - Test-NetConnection <host> -Port <port>

    9. Splunk / SIEM Searches:
    - index=* host=<host> earliest=-30m
    - index=* ("error" OR "failed" OR "timeout" OR "unavailable") earliest=-30m
    - index=* sourcetype=* earliest=-30m | stats count by host, sourcetype
    - index=* ("restart" OR "crash" OR "connection refused") earliest=-24h

    10. Immediate Remediation:
    Remediate only after root cause is validated. Avoid restarting, blocking, or changing production systems without incident/change approval.

    11. Prevention Plan:
    - Improve alert tuning.
    - Add service health checks.
    - Improve dashboard visibility.
    - Document recurring incidents.
    - Add runbook steps for known failure patterns.

    12. Final RCA Summary:
    RCA remains preliminary until supporting evidence confirms cause, scope, impact, action taken, and recovery.
    """.strip()
    
    return {
        "module": "RCA Generator",
        "severity": severity,
        "type": log_type,
        "status": "New",
        "output": output,
    }


def generate_rca(data: str) -> str:
    return generate_rca_case(data)["output"]


# =============================================================================
# End: RCA builder
# =============================================================================