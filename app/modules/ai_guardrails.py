# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/ai_guardrails.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Detect prompt injection and prepare LLM-safe text without harming SOC parsing.
# =============================================================================

from __future__ import annotations

import re
from typing import Any

DANGEROUS_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "reveal system prompt",
    "disable safety",
    "act as developer",
    "jailbreak",
    "bypass policy",
    "do anything now",
]


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Prompt injection detection and LLM-only redaction.
# =============================================================================

def detect_prompt_injection(text: str) -> dict[str, Any]:
    lower = (text or "").lower()
    findings = [pattern for pattern in DANGEROUS_PATTERNS if pattern in lower]

    return {
        "is_suspicious": bool(findings),
        "findings": findings,
    }


def redact_sensitive_data_for_llm(text: str) -> str:
    redacted = text or ""
    redacted = re.sub(r"(?i)(password|token|apikey|api_key|secret)\s*[:=]\s*\S+", r"\1=[REDACTED]", redacted)
    redacted = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", redacted)
    return redacted


def prepare_safe_input(text: str) -> dict[str, Any]:
    return {
        "original_text": text or "",
        "safe_text": redact_sensitive_data_for_llm(text or ""),
        "prompt_injection": detect_prompt_injection(text or ""),
    }


# Backward compatibility
def redact_sensitive_data(text: str) -> str:
    return redact_sensitive_data_for_llm(text)


# =============================================================================
# End: Prompt injection detection and LLM-only redaction
# =============================================================================