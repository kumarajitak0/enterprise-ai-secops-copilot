# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/case_enricher.py
# Date Updated: 2026-06-15 15:30
# Purpose:
#   Enrich saved cases with SOC dashboard metadata for React case cards.
# =============================================================================

from __future__ import annotations

from typing import Any

from core.normalizer import normalize_log
from app.modules.mitre_mapper import map_mitre


# =============================================================================
# 2026-06-15 15:30 - Added/Updated:
# Enrich case records for dashboard cards without changing database schema.
# =============================================================================

def enrich_case(case: dict[str, Any]) -> dict[str, Any]:
    input_text = (
        case.get("input_text")
        or case.get("raw_log")
        or case.get("text")
        or ""
    )

    normalized = normalize_log(input_text)
    mitre_matches = map_mitre(input_text)

    mitre_text = "Not present in provided log."
    if mitre_matches:
        mitre_text = ", ".join(
            [
                f"{item.get('technique_id')} {item.get('technique_name')}"
                for item in mitre_matches
            ]
        )

    enriched = dict(case)

    enriched["source_type"] = normalized.get("source_type", "Not present in provided log.")
    enriched["hostname"] = normalized.get("host", "Not present in provided log.")
    enriched["username"] = normalized.get("user", "Not present in provided log.")
    enriched["source_ip"] = normalized.get("source_ip", "Not present in provided log.")
    enriched["event_id"] = normalized.get("event_id", "Not present in provided log.")
    enriched["mitre"] = mitre_text

    enriched.setdefault("severity", case.get("severity", "Low"))
    enriched.setdefault("status", case.get("status", "New"))
    enriched.setdefault("module", case.get("module", "SOC Alert Triage"))
    enriched.setdefault("type", case.get("type", case.get("case_type", "Generic Case")))

    return enriched


def enrich_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [enrich_case(case) for case in cases]


# =============================================================================
# End: Enrich case records
# =============================================================================