# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/detection_engine.py
# Date Updated: 2026-06-15 15:10
# Purpose:
#   Apply deterministic event-id, keyword, and source-based SOC detections.
# =============================================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.entity_extractor import NOT_PRESENT

RULE_FILE = Path("rules/detection_rules.json")


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Safe rule loading.
# =============================================================================

def load_rules() -> list[dict[str, Any]]:
    if not RULE_FILE.exists():
        return []

    try:
        with open(RULE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("rules", [])
    except Exception:
        return []


# =============================================================================
# End: Safe rule loading
# =============================================================================


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Result builder.
# =============================================================================

def build_detection(
    matched: bool,
    rule_id: str,
    name: str,
    severity: str,
    alert_type: str,
    recommended_action: str,
    normalized_event: dict[str, Any],
    mitre_id: str = "N/A",
    mitre_name: str = "N/A",
    tactic: str = "N/A",
) -> dict[str, Any]:
    return {
        "matched": matched,
        "rule_id": rule_id,
        "name": name,
        "severity": severity,
        "alert_type": alert_type,
        "mitre_id": mitre_id,
        "mitre_name": mitre_name,
        "tactic": tactic,
        "recommended_action": recommended_action,
        "evidence": {
            "event_id": normalized_event.get("event_id", NOT_PRESENT),
            "host": normalized_event.get("host", NOT_PRESENT),
            "user": normalized_event.get("user", NOT_PRESENT),
            "source_ip": normalized_event.get("source_ip", NOT_PRESENT),
            "destination_ip": normalized_event.get("destination_ip", NOT_PRESENT),
            "source_type": normalized_event.get("source_type", NOT_PRESENT),
        },
    }


# =============================================================================
# End: Result builder
# =============================================================================


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Enterprise deterministic detection.
# =============================================================================

def run_detection(normalized_event: dict[str, Any]) -> dict[str, Any]:
    event_id = normalized_event.get("event_id", NOT_PRESENT)
    source_type = normalized_event.get("source_type", "generic_log")
    raw = str(normalized_event.get("raw_log", "")).lower()

    for rule in load_rules():
        if rule.get("event_id") == event_id:
            return build_detection(
                matched=True,
                rule_id=rule.get("rule_id", "UNKNOWN_RULE"),
                name=rule.get("name", "Unnamed Detection Rule"),
                severity=rule.get("severity", "Low"),
                alert_type=rule.get("alert_type", "Security Event"),
                mitre_id=rule.get("mitre_id", "N/A"),
                mitre_name=rule.get("mitre_name", "N/A"),
                tactic=rule.get("tactic", "N/A"),
                recommended_action=rule.get("recommended_action", "Review manually."),
                normalized_event=normalized_event,
            )

    behavior_rules = [
        {
            "keywords": ["failed password", "invalid user"],
            "source_type": "linux_auth",
            "rule_id": "LINUX-SSH-FAILED-AUTH",
            "name": "Linux SSH Failed Authentication",
            "severity": "Medium",
            "alert_type": "Authentication Failure",
            "mitre_id": "T1110",
            "mitre_name": "Brute Force",
            "tactic": "Credential Access",
            "action": "Review source IP, account name, and successful-login follow-up.",
        },
        {
            "keywords": ["mimikatz", "credential dump"],
            "source_type": None,
            "rule_id": "CRED-DUMP-INDICATOR",
            "name": "Credential Dumping Indicator",
            "severity": "Critical",
            "alert_type": "Credential Access",
            "mitre_id": "T1003",
            "mitre_name": "OS Credential Dumping",
            "tactic": "Credential Access",
            "action": "Escalate to IR and preserve endpoint evidence.",
        },
        {
            "keywords": ["ransomware"],
            "source_type": None,
            "rule_id": "RANSOMWARE-INDICATOR",
            "name": "Ransomware Indicator",
            "severity": "Critical",
            "alert_type": "Malware / Impact",
            "mitre_id": "T1486",
            "mitre_name": "Data Encrypted for Impact",
            "tactic": "Impact",
            "action": "Isolate affected host and escalate immediately.",
        },
        {
            "keywords": ["blocked", "denied", "deny"],
            "source_type": "network_security",
            "rule_id": "NETWORK-BLOCKED-TRAFFIC",
            "name": "Blocked or Denied Network Traffic",
            "severity": "Medium",
            "alert_type": "Network Security",
            "mitre_id": "N/A",
            "mitre_name": "N/A",
            "tactic": "N/A",
            "action": "Validate source, destination, port, and repetition.",
        },
        {
            "keywords": ["timeout", "not connecting", "threshold"],
            "source_type": "application_or_monitoring",
            "rule_id": "APP-MONITORING-TIMEOUT",
            "name": "Application Timeout / Monitoring Alert",
            "severity": "Medium",
            "alert_type": "Service Availability",
            "mitre_id": "N/A",
            "mitre_name": "N/A",
            "tactic": "N/A",
            "action": "Validate service health, latency, traffic, and recent changes.",
        },
    ]

    for rule in behavior_rules:
        source_ok = rule["source_type"] is None or rule["source_type"] == source_type
        keyword_ok = any(keyword in raw for keyword in rule["keywords"])

        if source_ok and keyword_ok:
            return build_detection(
                matched=True,
                rule_id=rule["rule_id"],
                name=rule["name"],
                severity=rule["severity"],
                alert_type=rule["alert_type"],
                mitre_id=rule["mitre_id"],
                mitre_name=rule["mitre_name"],
                tactic=rule["tactic"],
                recommended_action=rule["action"],
                normalized_event=normalized_event,
            )

    return build_detection(
        matched=False,
        rule_id="NO_RULE_MATCH",
        name="No deterministic rule matched",
        severity="Low",
        alert_type="Unknown / Informational",
        recommended_action="Review manually and validate against source logs.",
        normalized_event=normalized_event,
    )


# =============================================================================
# End: Enterprise deterministic detection
# =============================================================================