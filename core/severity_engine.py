# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/severity_engine.py
# Date Updated: 2026-06-15 15:10
# Purpose:
#   Decide event severity using deterministic SOC logic.
# =============================================================================

from __future__ import annotations

from typing import Any


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Deterministic severity scoring.
# =============================================================================

def determine_severity(
    normalized: dict[str, Any],
    detection: dict[str, Any] | None = None,
    iocs: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    raw = str(normalized.get("raw_log", "")).lower()
    event_id = normalized.get("event_id", "Not present in provided log.")
    source_type = normalized.get("source_type", "generic_log")

    score = 0
    reasons: list[str] = []

    if detection and detection.get("severity"):
        base = detection["severity"]
        if base == "Critical":
            score += 90
        elif base == "High":
            score += 70
        elif base == "Medium":
            score += 40
        elif base == "Low":
            score += 10
        reasons.append(f"Detection rule severity is {base}.")

    if event_id == "1102":
        score += 70
        reasons.append("Windows Security log clear event detected.")

    if event_id in ["4672", "7045"]:
        score += 50
        reasons.append("Privileged logon or new service event detected.")

    if event_id in ["4625", "4688", "4798"]:
        score += 30
        reasons.append("Security-relevant Windows Event ID detected.")

    critical_terms = ["ransomware", "data exfiltration", "credential dump", "mimikatz"]
    high_terms = ["production", "prod", "customer impact", "payment authorization", "exceeded threshold"]
    medium_terms = ["failed password", "failed logon", "timeout", "blocked", "denied", "suspicious"]

    if any(term in raw for term in critical_terms):
        score += 90
        reasons.append("Critical threat keyword detected.")

    if any(term in raw for term in high_terms):
        score += 50
        reasons.append("Production or business impact indicator detected.")

    if any(term in raw for term in medium_terms):
        score += 25
        reasons.append("Security or availability indicator detected.")

    if source_type in ["endpoint_security", "cloud_iam"]:
        score += 20
        reasons.append("Higher-risk source type detected.")

    if iocs:
        if iocs.get("ips"):
            score += 10
            reasons.append("IP observable detected.")
        if iocs.get("hashes"):
            score += 25
            reasons.append("Hash observable detected.")

    if score >= 90:
        severity = "Critical"
    elif score >= 70:
        severity = "High"
    elif score >= 35:
        severity = "Medium"
    elif score >= 10:
        severity = "Low"
    else:
        severity = "Informational"

    if not reasons:
        reasons.append("No deterministic high-risk indicators found.")

    return {
        "severity": severity,
        "score": score,
        "reasons": reasons,
    }


# =============================================================================
# End: Deterministic severity scoring
# =============================================================================