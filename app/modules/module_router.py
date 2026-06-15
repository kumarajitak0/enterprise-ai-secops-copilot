# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/module_router.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Recommend the correct analysis module with confidence and reason.
# =============================================================================

from __future__ import annotations


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Multi-signal module router.
# =============================================================================

def recommend_module(text: str) -> dict:
    lower = (text or "").lower()

    grc_hits = ["audit evidence", "control", "policy", "pci", "nist", "soc 2", "compliance"]
    rca_hits = ["outage", "service down", "latency", "timeout", "restart", "crash", "unavailable"]
    soc_hits = ["event id", "eventcode", "4625", "4672", "4688", "1102", "firewall", "failed logon", "mimikatz", "malware", "edr"]

    scores = {
        "GRC Evidence Mapping": sum(1 for word in grc_hits if word in lower),
        "RCA Generator": sum(1 for word in rca_hits if word in lower),
        "SOC Alert Triage": sum(1 for word in soc_hits if word in lower),
    }

    module = max(scores, key=scores.get)

    if scores[module] == 0:
        module = "SOC Alert Triage"

    return {
        "recommended_module": module,
        "confidence": "High" if scores[module] >= 2 else "Medium" if scores[module] == 1 else "Low",
        "scores": scores,
        "reason": f"Selected {module} based on deterministic keyword scoring.",
    }


# =============================================================================
# End: Multi-signal module router
# =============================================================================