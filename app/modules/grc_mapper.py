# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/grc_mapper.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Deterministically map SOC evidence to audit/control language.
# =============================================================================

from __future__ import annotations

from typing import Any

from app.modules.classifier import detect_log_type
from app.modules.ollama_client import ask_llm
from core.normalizer import normalize_log


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Deterministic GRC mapper.
# =============================================================================

def map_grc_case(data: str) -> dict[str, Any]:
    text = data or ""
    normalized = normalize_log(text)
    log_type = detect_log_type(text)

    source_type = normalized.get("source_type", "generic_log")

    if source_type in ["windows_security", "linux_auth", "cloud_iam"]:
        control_area = "Access control, authentication monitoring, and security event review"
        nist = "NIST CSF: PR.AA, DE.CM, RS.AN"
        pci = "PCI DSS: Requirement 7, Requirement 8, Requirement 10"
        soc2 = "SOC 2: CC6, CC7"
    elif source_type in ["network_security", "endpoint_security"]:
        control_area = "Threat detection, network monitoring, and incident response"
        nist = "NIST CSF: DE.CM, RS.AN, RS.MI"
        pci = "PCI DSS: Requirement 10, Requirement 11, Requirement 12"
        soc2 = "SOC 2: CC7"
    else:
        control_area = "Logging, monitoring, operational resilience, and incident evidence"
        nist = "NIST CSF: DE.CM, RS.AN"
        pci = "PCI DSS: Requirement 10, Requirement 12"
        soc2 = "SOC 2: CC7"

    prompt = f"""
You are a GRC analyst. Improve wording only. Do not invent controls.

Evidence Type: {log_type}
Control Area: {control_area}
NIST: {nist}
PCI: {pci}
SOC2: {soc2}

Write a concise audit explanation.
"""
    explanation = ask_llm(prompt, num_predict=160)

    output = f"""
1. Evidence Summary:
Security/operations evidence was submitted for review. Source type: {log_type}.

2. Control Area:
{control_area}

3. NIST CSF Mapping:
{nist}

4. PCI DSS Mapping:
{pci}

5. SOC 2 Mapping:
{soc2}

6. Evidence Type:
Log / alert / case investigation evidence.

7. Risk Reduced:
Supports detection, investigation, access review, incident response, and audit traceability.

8. Control Owner:
Security Operations / IT Operations / System Owner.

9. Audit-Ready Explanation:
{explanation}

10. Evidence Fields:
- Timestamp: {normalized.get("timestamp")}
- Hostname: {normalized.get("host")}
- Username: {normalized.get("user")}
- Source IP: {normalized.get("source_ip")}
- Event ID: {normalized.get("event_id")}
""".strip()

    return {
        "module": "GRC Evidence Mapping",
        "severity": "Compliance",
        "type": log_type,
        "status": "New",
        "output": output,
    }


def map_grc(data: str) -> str:
    return map_grc_case(data)["output"]


# =============================================================================
# End: Deterministic GRC mapper
# =============================================================================