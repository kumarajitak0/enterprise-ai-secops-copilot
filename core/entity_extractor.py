# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: core/entity_extractor.py
# Date Updated: 2026-06-15 15:10
# Purpose:
#   Extract common SOC entities from raw logs using deterministic regex.
# =============================================================================

from __future__ import annotations

import re
from typing import Any

NOT_PRESENT = "Not present in provided log."


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Safe regex helper functions.
# =============================================================================

def first_match(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
    return NOT_PRESENT


def all_matches(pattern: str, text: str) -> list[str]:
    values = re.findall(pattern, text, flags=re.IGNORECASE)
    output: list[str] = []

    for value in values:
        if isinstance(value, tuple):
            value = next((item for item in value if item), "")
        cleaned = str(value).strip()
        if cleaned and cleaned not in output:
            output.append(cleaned)

    return output


# =============================================================================
# End: Safe regex helper functions
# =============================================================================


# =============================================================================
# 2026-06-15 15:10 - Added/Updated:
# Enterprise SOC entity extraction.
# =============================================================================

def extract_entities(text: str) -> dict[str, Any]:
    raw = text or ""

    ips = all_matches(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw)

    source_ip = first_match(
        [
            r"Source Network Address[:=]\s*((?:\d{1,3}\.){3}\d{1,3})",
            r"src_ip[=:]\s*((?:\d{1,3}\.){3}\d{1,3})",
            r"src[=:]\s*((?:\d{1,3}\.){3}\d{1,3})",
            r"from\s+((?:\d{1,3}\.){3}\d{1,3})",
        ],
        raw,
    )

    destination_ip = first_match(
        [
            r"dest_ip[=:]\s*((?:\d{1,3}\.){3}\d{1,3})",
            r"dst_ip[=:]\s*((?:\d{1,3}\.){3}\d{1,3})",
            r"dst[=:]\s*((?:\d{1,3}\.){3}\d{1,3})",
            r"to\s+((?:\d{1,3}\.){3}\d{1,3})",
        ],
        raw,
    )

    if source_ip == NOT_PRESENT and ips:
        source_ip = ips[0]

    if destination_ip == NOT_PRESENT and len(ips) > 1:
        destination_ip = ips[1]

    return {
        "timestamp": first_match(
            [
                r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[-+]\d{2}:\d{2})?)",
                r"TimeCreated[:=]\s*([^\n\r]+)",
                r"TimeGenerated[:=]\s*([^\n\r]+)",
                r"timestamp[=:]\s*([^\s,]+)",
                r"^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",
            ],
            raw,
        ),
        "hostname": first_match(
            [
                r"ComputerName[:=]\s*([A-Za-z0-9._-]+)",
                r"Computer[:=]\s*([A-Za-z0-9._-]+)",
                r"hostname[=:]\s*([A-Za-z0-9._-]+)",
                r"\bhost[=:]\s*([A-Za-z0-9._-]+)",
                r"\d{4}-\d{2}-\d{2}[T\s][^\s]+\s+([A-Za-z0-9._-]+)\s+",
            ],
            raw,
        ),
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "username": first_match(
            [
                r"Account Name[:=]\s*([A-Za-z0-9._$@\\/-]+)",
                r"TargetUserName[\"']?\s*>?[:=]?\s*([A-Za-z0-9._$@\\/-]+)",
                r"user(?:name)?[=:]\s*([A-Za-z0-9._$@\\/-]+)",
                r"for invalid user\s+([A-Za-z0-9._$@\\/-]+)",
                r"for user\s+([A-Za-z0-9._$@\\/-]+)",
            ],
            raw,
        ),
        "event_id": first_match(
            [
                r"Event\s*ID[:=]\s*(\d+)",
                r"EventID[=:]\s*(\d+)",
                r"EventCode[=:]\s*(\d+)",
            ],
            raw,
        ),
        "process": first_match(
            [
                r"New Process Name[:=]\s*([^\n\r]+)",
                r"Process Name[:=]\s*([^\n\r]+)",
                r"process_name[=:]\s*([A-Za-z0-9._:\\/-]+)",
                r"process[=:]\s*([A-Za-z0-9._:\\/-]+)",
            ],
            raw,
        ),
        "command_line": first_match(
            [
                r"Command Line[:=]\s*([^\n\r]+)",
                r"cmdline[=:]\s*([^\n\r]+)",
                r"command_line[=:]\s*([^\n\r]+)",
            ],
            raw,
        ),
        "url_domain": first_match(
            [
                r"(https?://[^\s]+)",
                r"domain[=:]\s*([A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                r"url[=:]\s*([^\s]+)",
            ],
            raw,
        ),
        "file_hash": first_match(
            [
                r"sha256[=:]\s*([A-Fa-f0-9]{64})",
                r"sha1[=:]\s*([A-Fa-f0-9]{40})",
                r"md5[=:]\s*([A-Fa-f0-9]{32})",
                r"file[=:]\s*([A-Za-z0-9._:\\/-]+)",
            ],
            raw,
        ),
        "port": first_match(
            [
                r"dest_port[=:]\s*(\d+)",
                r"dst_port[=:]\s*(\d+)",
                r"port\s+(\d+)",
                r"port[=:]\s*(\d+)",
            ],
            raw,
        ),
        "action": first_match(
            [
                r"action[=:]\s*([A-Za-z_-]+)",
                r"\b(blocked|denied|deny|allowed|allow|quarantined|detected)\b",
            ],
            raw,
        ),
    }


# =============================================================================
# End: Enterprise SOC entity extraction
# =============================================================================