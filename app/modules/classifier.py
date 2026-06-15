# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/classifier.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Deterministically classify log type, event category, and severity.
# =============================================================================

from __future__ import annotations

from typing import Any

from core.normalizer import NOT_PRESENT, normalize_log


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Log type and category classification.
# =============================================================================

SOURCE_LABELS = {
    "windows_security": "Windows Security Event",
    "linux_auth": "Linux Authentication Log",
    "network_security": "Firewall / Network Security Log",
    "endpoint_security": "Endpoint Security Alert",
    "cloud_iam": "Cloud / IAM Log",
    "web_proxy": "Web / Proxy / Application Access Log",
    "splunk_event": "Splunk Event",
    "application_or_monitoring": "Application / Monitoring Alert",
    "generic_log": "Generic Security / Operations Log",
}


def detect_log_type(text: str) -> str:
    normalized = normalize_log(text)
    return SOURCE_LABELS.get(normalized["source_type"], SOURCE_LABELS["generic_log"])


def detect_event_category(text: str) -> str:
    lower = (text or "").lower()
    normalized = normalize_log(text)
    event_id = normalized.get("event_id")

    if event_id == "4625" or "failed password" in lower or "failed logon" in lower:
        return "Authentication Failure"
    if event_id == "4624" or "accepted password" in lower:
        return "Successful Authentication"
    if event_id == "4672" or "privileged logon" in lower:
        return "Privileged Access"
    if event_id == "4688" or "powershell" in lower or "cmd.exe" in lower:
        return "Process / Command Execution"
    if event_id == "1102" or "log cleared" in lower:
        return "Defense Evasion / Log Tampering"
    if event_id == "4798" or "enumerated" in lower:
        return "Account Discovery"
    if "deny" in lower or "blocked" in lower or "firewall" in lower:
        return "Network Block / Policy Deny"
    if "malware" in lower or "ransomware" in lower or "quarantined" in lower:
        return "Malware / Endpoint Detection"
    if "cloudtrail" in lower or "consolelogin" in lower or "assumerole" in lower:
        return "Cloud IAM Activity"
    if "timeout" in lower or "latency" in lower or "service down" in lower:
        return "Service Availability / Performance"
    if "status=500" in lower or "http 500" in lower:
        return "Web/Application Error"

    return "General Security / Operations Event"


# =============================================================================
# End: Log type and category classification
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Evidence-backed severity decision.
# =============================================================================

def estimate_severity_with_reason(text: str) -> dict[str, Any]:
    lower = (text or "").lower()
    normalized = normalize_log(text)
    reasons: list[str] = []

    severity = "Low"

    critical_terms = [
        "ransomware",
        "data exfiltration",
        "domain admin compromised",
        "production outage",
        "service down",
        "customer impact",
    ]

    high_terms = [
        "security log cleared",
        "event id: 1102",
        "eventid=1102",
        "credential dump",
        "mimikatz",
        "privilege escalation",
        "unauthorized admin",
        "multiple hosts",
        "payment authorization delays",
        "exceeded threshold",
        "not connecting",
        "prod",
        "production",
    ]

    medium_terms = [
        "4625",
        "failed logon",
        "failed password",
        "blocked",
        "denied",
        "port scan",
        "suspicious",
        "timeout",
        "connection refused",
        "status=500",
        "malware detected",
    ]

    if any(term in lower for term in critical_terms):
        severity = "Critical"
        reasons.append("Critical impact keyword observed.")
    elif any(term in lower for term in high_terms):
        severity = "High"
        reasons.append("High-risk keyword or production impact indicator observed.")
    elif any(term in lower for term in medium_terms):
        severity = "Medium"
        reasons.append("Security or availability indicator observed.")
    else:
        reasons.append("No high-risk indicator was deterministically found.")

    if normalized.get("event_id") == "1102":
        severity = "High"
        reasons.append("Windows Security Event ID 1102 indicates log clearing.")

    return {
        "severity": severity,
        "reasons": reasons,
        "category": detect_event_category(text),
    }


def estimate_severity(text: str) -> str:
    return estimate_severity_with_reason(text)["severity"]


# =============================================================================
# End: Evidence-backed severity decision
# =============================================================================