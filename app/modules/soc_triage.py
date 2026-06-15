# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/soc_triage.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Build enterprise SOC triage output using deterministic analysis first.
# =============================================================================

from __future__ import annotations

from typing import Any

from app.modules.ai_guardrails import prepare_safe_input
from app.modules.classifier import detect_event_category, detect_log_type
from core.severity_engine import determine_severity
from app.modules.mitre_mapper import map_mitre
from app.modules.ollama_client import ask_llm
from app.modules.playbook_engine import get_playbook
from core.detection_engine import run_detection
from core.normalizer import NOT_PRESENT, normalize_log


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Formatting helpers.
# =============================================================================

def _bullet(items: list[str]) -> str:
    if not items:
        return "- Not present in provided log."
    return "\n".join(f"- {item}" for item in items)


def _field(value: Any) -> str:
    if value in [None, "", "unknown"]:
        return NOT_PRESENT
    return str(value)


def _mitre_text(matches: list[dict[str, Any]]) -> str:
    if not matches:
        return "- No deterministic MITRE mapping found from local rule base."

    return "\n".join(
        f"- {m.get('technique_id', NOT_PRESENT)} {m.get('technique_name', NOT_PRESENT)} | "
        f"Tactic: {m.get('tactic', NOT_PRESENT)} | Source: {m.get('mapping_source', NOT_PRESENT)}"
        for m in matches
    )


# =============================================================================
# End: Formatting helpers
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Case-ready SOC analysis builder.
# =============================================================================

def analyze_alert_case(log_text: str) -> dict[str, Any]:
    text = log_text or ""
    safe = prepare_safe_input(text)

    normalized = normalize_log(text)
    detection = run_detection(normalized)
    mitre_matches = map_mitre(text)
    severity_info = determine_severity(
        normalized=normalized,
        detection=detection,
        iocs=normalized.get("iocs", {}),
        )
    severity = severity_info["severity"]
    log_type = detect_log_type(text)
    category = detect_event_category(text)

    playbook = get_playbook(
        event_id=normalized.get("event_id", "unknown"),
        source_type=normalized.get("source_type", "generic_log"),
        severity=severity,
    )

    llm_summary = ""
    if not safe["prompt_injection"]["is_suspicious"]:
        prompt = f"""
You are a SOC analyst. Improve readability only. Do not invent facts.

Facts:
Log Type: {log_type}
Category: {category}
Severity: {severity}
Detection: {detection.get("name")}
Event ID: {normalized.get("event_id")}
Host: {normalized.get("host")}
User: {normalized.get("user")}
Source IP: {normalized.get("source_ip")}
Destination IP: {normalized.get("destination_ip")}

Write a concise 2 sentence analyst summary. If a fact is missing, do not invent it.
"""
        llm_summary = ask_llm(prompt, num_predict=120)

    if not llm_summary:
        llm_summary = "Deterministic SOC analysis completed. Analyst should validate the extracted entities and correlate related events."

    output = f"""
                1. Alert Summary:
                {llm_summary}

            2. Parsed Entities:
            - Timestamp: {_field(normalized.get("timestamp"))}
            - Hostname: {_field(normalized.get("host"))}
            - Source IP: {_field(normalized.get("source_ip"))}
            - Destination IP: {_field(normalized.get("destination_ip"))}
            - Username: {_field(normalized.get("user"))}
            - Process: {_field(normalized.get("process"))}
            - Command Line: {_field(normalized.get("command_line"))}
            - Event ID: {_field(normalized.get("event_id"))}
            - URL / Domain: {_field(normalized.get("url_domain"))}
            - File / Hash: {_field(normalized.get("file_hash"))}

            3. Log Source Classification:
            - Source Type: {log_type}
            - Normalized Source: {_field(normalized.get("source_type"))}
            - Event Category: {category}

            4. Severity Decision:
            - Severity: {severity}
            - Reasoning:
            {_bullet(severity_info.get("reasons", []))}

            5. Detection Reasoning:
            - Rule Matched: {detection.get("matched")}
            - Rule ID: {detection.get("rule_id")}
            - Detection Name: {detection.get("name")}
            - Alert Type: {detection.get("alert_type")}
            - Recommended Action: {detection.get("recommended_action")}

            6. MITRE ATT&CK Mapping:
            {_mitre_text(mitre_matches)}

            7. IOCs / Observables:
            - Source IP: {_field(normalized.get("source_ip"))}
            - Destination IP: {_field(normalized.get("destination_ip"))}
            - Hostname: {_field(normalized.get("host"))}
            - Username: {_field(normalized.get("user"))}
            - Process: {_field(normalized.get("process"))}
            - File / Hash: {_field(normalized.get("file_hash"))}
            - URL / Domain: {_field(normalized.get("url_domain"))}

            8. Splunk / SIEM Searches:
            {_bullet(playbook.get("splunk_queries", []))}

            9. Linux Validation Commands:
            {_bullet(playbook.get("linux_commands", []))}

            10. Windows Validation Commands:
            {_bullet(playbook.get("windows_commands", []))}

            11. Network Validation Commands:
            {_bullet(playbook.get("network_commands", []))}

            12. Immediate Containment:
            {_bullet(playbook.get("containment", []))}

            13. Investigation Checklist:
            - Validate whether the activity is expected.
            - Correlate events 30 minutes before and after the alert.
            - Check user, host, source IP, destination IP, process, and command line.
            - Confirm whether successful authentication followed failures.
            - Preserve raw logs and analyst notes.

            14. False Positive Checks:
            - Confirm approved admin activity or scheduled job.
            - Check change ticket or maintenance window.
            - Validate known scanner, monitoring source, or service account.
            - Confirm whether the event repeated or remained isolated.

            15. RCA Notes:
            Root cause is not confirmed from one log alone. Validate timeline, affected system, recent changes, and related telemetry before final RCA.

            16. GRC / Audit Evidence Notes:
            This case can support audit evidence for logging, monitoring, alert review, incident response, and access/security event investigation.

            17. Analyst Case Note:
            Case created from deterministic SOC analysis. Missing fields are marked as "Not present in provided log." LLM was used only for wording, not detection facts.
            """.strip()
    
    return {
        "module": "SOC Alert Triage",
        "severity": severity,
        "type": log_type,
        "status": "New",
        "normalized": normalized,
        "detection": detection,
        "mitre": mitre_matches,
        "output": output.strip(),
    }


def analyze_alert(log_text: str) -> str:
    return analyze_alert_case(log_text)["output"]


# =============================================================================
# End: Case-ready SOC analysis builder
# =============================================================================