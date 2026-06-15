# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/mitre_lookup.py
# Date Created: 2026-05-26
# Date Updated: 2026-05-26
# Purpose:
#   Lookup verified MITRE ATT&CK technique metadata from local cache.
# =============================================================================

import json
from pathlib import Path
from typing import Any


TECHNIQUE_CACHE_FILE = Path("knowledge_base/mitre/enterprise_techniques_cache.json")


def load_technique_cache() -> dict[str, Any]:
    if not TECHNIQUE_CACHE_FILE.exists():
        return {}

    with open(TECHNIQUE_CACHE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("techniques", {})


def get_technique(technique_id: str) -> dict[str, Any]:
    techniques = load_technique_cache()
    return techniques.get(technique_id, {})


def enrich_detection_with_mitre(detection_result: dict) -> dict:
    technique_id = detection_result.get("mitre_id")

    if not technique_id or technique_id == "N/A":
        detection_result["mitre_verified"] = False
        return detection_result

    technique = get_technique(technique_id)

    if not technique:
        detection_result["mitre_verified"] = False
        return detection_result

    detection_result["mitre_verified"] = True
    detection_result["mitre_official_name"] = technique.get("name")
    detection_result["mitre_url"] = technique.get("url")
    detection_result["mitre_platforms"] = technique.get("platforms", [])
    detection_result["mitre_data_sources"] = technique.get("data_sources", [])
    detection_result["mitre_tactics"] = technique.get("kill_chain_phases", [])

    return detection_result