# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/ioc_extractor.py
# Date Updated: 2026-06-15 15:10
# Purpose:
#   Extract IOCs and observables from raw logs.
# =============================================================================

from __future__ import annotations

import re


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# IOC extraction.
# =============================================================================

def extract_iocs(text: str) -> dict[str, list[str]]:
    raw = text or ""

    ips = sorted(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw)))

    urls = sorted(set(re.findall(r"https?://[^\s\"']+", raw, flags=re.IGNORECASE)))

    domains = sorted(
        set(
            re.findall(
                r"\b(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b",
                raw,
                flags=re.IGNORECASE,
            )
        )
    )

    md5 = sorted(set(re.findall(r"\b[A-Fa-f0-9]{32}\b", raw)))
    sha1 = sorted(set(re.findall(r"\b[A-Fa-f0-9]{40}\b", raw)))
    sha256 = sorted(set(re.findall(r"\b[A-Fa-f0-9]{64}\b", raw)))

    emails = sorted(
        set(
            re.findall(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                raw,
            )
        )
    )

    return {
        "ips": ips,
        "domains": domains,
        "urls": urls,
        "hashes": md5 + sha1 + sha256,
        "emails": emails,
    }


# =============================================================================
# End: IOC extraction
# =============================================================================