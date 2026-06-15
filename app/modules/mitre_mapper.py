# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/mitre_mapper.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Deterministically map normalized security events to MITRE ATT&CK.
# =============================================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.normalizer import NOT_PRESENT, normalize_log

MAPPING_FILE = Path(__file__).resolve().parents[1] / "knowledge_base" / "mitre_mapping.json"


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Local MITRE loading and normalized result handling.
# =============================================================================

def load_mitre_mapping() -> dict[str, Any]:
    if not MAPPING_FILE.exists():
        return {}

    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def _mitre_result(
    technique_id: str,
    technique_name: str,
    tactic: str,
    description: str,
    source: str,
    event_id: str = NOT_PRESENT,
    recommended_queries: list[str] | None = None,
    defensive_actions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "technique_id": technique_id,
        "technique_name": technique_name,
        "tactic": tactic,
        "description": description,
        "mapping_source": source,
        "recommended_queries": recommended_queries or [],
        "defensive_actions": defensive_actions or [],
    }


# =============================================================================
# End: Local MITRE loading and normalized result handling
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Event ID and behavior-based deterministic MITRE mapping.
# =============================================================================

def map_mitre(text: str) -> list[dict[str, Any]]:
    normalized = normalize_log(text)
    event_id = normalized.get("event_id", NOT_PRESENT)
    lower = (text or "").lower()
    mappings = load_mitre_mapping()
    results: list[dict[str, Any]] = []

    if event_id != NOT_PRESENT and event_id in mappings:
        item = mappings[event_id]
        results.append(
            _mitre_result(
                technique_id=item.get("technique_id", NOT_PRESENT),
                technique_name=item.get("technique_name", NOT_PRESENT),
                tactic=item.get("tactic", NOT_PRESENT),
                description=item.get("description", NOT_PRESENT),
                source="event_id_rule",
                event_id=event_id,
                recommended_queries=item.get("recommended_queries", []),
                defensive_actions=item.get("defensive_actions", []),
            )
        )

    behavior_rules = [
        ("failed password", "T1110", "Brute Force", "Credential Access"),
        ("failed logon", "T1110", "Brute Force", "Credential Access"),
        ("mimikatz", "T1003", "OS Credential Dumping", "Credential Access"),
        ("powershell", "T1059.001", "PowerShell", "Execution"),
        ("cmd.exe", "T1059.003", "Windows Command Shell", "Execution"),
        ("sudo", "T1548", "Abuse Elevation Control Mechanism", "Privilege Escalation"),
        ("security log cleared", "T1070.001", "Clear Windows Event Logs", "Defense Evasion"),
        ("cloudtrail", "T1078", "Valid Accounts", "Defense Evasion / Persistence"),
        ("assumerole", "T1098", "Account Manipulation", "Persistence"),
    ]

    existing = {r["technique_id"] for r in results}

    for keyword, technique_id, technique_name, tactic in behavior_rules:
        if keyword in lower and technique_id not in existing:
            results.append(
                _mitre_result(
                    technique_id=technique_id,
                    technique_name=technique_name,
                    tactic=tactic,
                    description=f"Keyword/behavior indicator observed: {keyword}",
                    source="behavior_rule",
                    event_id=event_id,
                )
            )
            existing.add(technique_id)

    return results


def format_mitre_context(text: str) -> str:
    matches = map_mitre(text)

    if not matches:
        return "No deterministic MITRE mapping found from local rule base."

    lines = ["Deterministic MITRE Mapping:"]
    for match in matches:
        lines.append(
            f"- {match.get('technique_id')} {match.get('technique_name')} | "
            f"Tactic: {match.get('tactic')} | Source: {match.get('mapping_source')}"
        )

    return "\n".join(lines)


# =============================================================================
# End: Event ID and behavior-based deterministic MITRE mapping
# =============================================================================