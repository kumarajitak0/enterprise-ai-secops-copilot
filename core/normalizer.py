# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/normalizer.py
# Date Updated: 2026-06-15 15:10
# Purpose:
#   Normalize raw security logs into one enterprise SOC schema.
# =============================================================================

from __future__ import annotations

from datetime import datetime
from typing import Any

from core.entity_extractor import NOT_PRESENT, extract_entities
from core.ioc_extractor import extract_iocs


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Log source classification.
# =============================================================================

def detect_source_type(text: str) -> str:
    lower = (text or "").lower()

    if "cloudtrail" in lower or "eventsource" in lower or "consolelogin" in lower or "assumerole" in lower:
        return "cloud_iam"

    if "azure" in lower or "signinlogs" in lower:
        return "cloud_iam"

    if "microsoft-windows-security-auditing" in lower or "log name: security" in lower:
        return "windows_security"

    if "event id" in lower or "eventid" in lower or "eventcode" in lower:
        return "windows_security"

    if "sshd" in lower or "failed password" in lower or "auth.log" in lower or "sudo" in lower:
        return "linux_auth"

    if "firewall" in lower or "blocked" in lower or "deny" in lower or "denied" in lower:
        return "network_security"

    if "suricata" in lower or "snort" in lower or "ids" in lower or "ips" in lower:
        return "network_security"

    if "edr" in lower or "defender" in lower or "crowdstrike" in lower or "sentinelone" in lower:
        return "endpoint_security"

    if "nginx" in lower or "apache" in lower or "http" in lower or "status=500" in lower:
        return "web_proxy"

    if "index=" in lower or "sourcetype=" in lower:
        return "splunk_event"

    if "grafana" in lower or "threshold" in lower or "timeout" in lower or "latency" in lower:
        return "application_or_monitoring"

    return "generic_log"


# =============================================================================
# End: Log source classification
# =============================================================================


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Universal normalizer.
# =============================================================================

def normalize_log(raw_text: str) -> dict[str, Any]:
    text = raw_text or ""
    entities = extract_entities(text)
    iocs = extract_iocs(text)

    return {
        "normalized_at": datetime.now().isoformat(timespec="seconds"),
        "source_type": detect_source_type(text),
        "timestamp": entities["timestamp"],
        "hostname": entities["hostname"],
        "host": entities["hostname"],
        "source_ip": entities["source_ip"],
        "destination_ip": entities["destination_ip"],
        "username": entities["username"],
        "user": entities["username"],
        "event_id": entities["event_id"],
        "process": entities["process"],
        "command_line": entities["command_line"],
        "url_domain": entities["url_domain"],
        "file_hash": entities["file_hash"],
        "port": entities["port"],
        "action": entities["action"],
        "iocs": iocs,
        "raw_log": text,
    }


# =============================================================================
# End: Universal normalizer
# =============================================================================