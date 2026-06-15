# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/mitre_cache_builder.py
# Date Created: 2026-05-26
# Date Updated: 2026-05-26
# Purpose:
#   Download and cache official MITRE ATT&CK Enterprise STIX data locally.
#   This reduces hallucination by using verified ATT&CK metadata.
# =============================================================================

import json
import urllib.request
from datetime import datetime
from pathlib import Path


MITRE_ENTERPRISE_URL = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
    "master/enterprise-attack/enterprise-attack.json"
)

CACHE_DIR = Path("knowledge_base/mitre")
RAW_FILE = CACHE_DIR / "enterprise-attack.json"
TECHNIQUE_CACHE_FILE = CACHE_DIR / "enterprise_techniques_cache.json"


def download_enterprise_attack() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] Downloading MITRE ATT&CK Enterprise STIX data...")
    urllib.request.urlretrieve(MITRE_ENTERPRISE_URL, RAW_FILE)
    print(f"[OK] Saved raw MITRE data to: {RAW_FILE}")


def extract_external_id(attack_pattern: dict) -> str:
    for ref in attack_pattern.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id", "N/A")

    return "N/A"


def extract_reference_url(attack_pattern: dict) -> str:
    for ref in attack_pattern.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("url", "N/A")

    return "N/A"


def build_technique_cache() -> None:
    if not RAW_FILE.exists():
        download_enterprise_attack()

    with open(RAW_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    techniques = {}

    for item in data.get("objects", []):
        if item.get("type") != "attack-pattern":
            continue

        if item.get("revoked") is True or item.get("x_mitre_deprecated") is True:
            continue

        technique_id = extract_external_id(item)

        if technique_id == "N/A":
            continue

        techniques[technique_id] = {
            "technique_id": technique_id,
            "name": item.get("name", "Unknown"),
            "description": item.get("description", ""),
            "url": extract_reference_url(item),
            "platforms": item.get("x_mitre_platforms", []),
            "data_sources": item.get("x_mitre_data_sources", []),
            "kill_chain_phases": [
                phase.get("phase_name")
                for phase in item.get("kill_chain_phases", [])
                if phase.get("kill_chain_name") == "mitre-attack"
            ],
            "modified": item.get("modified"),
            "created": item.get("created")
        }

    output = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": MITRE_ENTERPRISE_URL,
        "technique_count": len(techniques),
        "techniques": techniques
    }

    with open(TECHNIQUE_CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print(f"[OK] Built MITRE technique cache: {TECHNIQUE_CACHE_FILE}")
    print(f"[OK] Technique count: {len(techniques)}")


if __name__ == "__main__":
    download_enterprise_attack()
    build_technique_cache()