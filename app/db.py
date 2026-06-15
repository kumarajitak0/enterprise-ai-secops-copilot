# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/db.py
# Date Updated: 2026-06-14
# Purpose:
#   Single source of truth for SQLite case database.
#   Handles table creation, safe migration, case save, case read, and dashboard stats.
# =============================================================================

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/secops_cases.db")


# =============================================================================
# 1. DATABASE CONNECTION
# =============================================================================

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# 2. INITIALIZE / MIGRATE CASE TABLE
# =============================================================================

def init_case_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            module TEXT,
            severity TEXT,
            type TEXT,
            status TEXT,
            input_text TEXT,
            output_text TEXT
        )
        """
    )

    cursor.execute("PRAGMA table_info(cases)")
    existing_columns = [row["name"] for row in cursor.fetchall()]

    required_columns = {
        "timestamp": "TEXT",
        "module": "TEXT",
        "severity": "TEXT",
        "type": "TEXT",
        "status": "TEXT",
        "input_text": "TEXT",
        "output_text": "TEXT",
    }

    for column, column_type in required_columns.items():
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE cases ADD COLUMN {column} {column_type}"
            )

    conn.commit()
    conn.close()


# =============================================================================
# 3. DATABASE HEALTH
# =============================================================================

def case_db_health() -> str:
    try:
        init_case_db()
        return "connected"
    except Exception as error:
        return f"error: {error}"


# =============================================================================
# 4. SAVE CASE
# =============================================================================

def save_case(
    module: str,
    severity: str,
    case_type: str,
    status: str,
    input_text: str,
    output_text: str,
) -> dict:
    init_case_db()

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO cases (
            timestamp,
            module,
            severity,
            type,
            status,
            input_text,
            output_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            module,
            severity,
            case_type,
            status,
            input_text,
            output_text,
        ),
    )

    conn.commit()
    case_id = cursor.lastrowid
    conn.close()

    return {
        "success": True,
        "case_id": case_id,
        "message": "Case saved successfully",
    }


# =============================================================================
# 5. GET ALL CASES
# =============================================================================

def get_all_cases() -> list[dict]:
    init_case_db()

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            timestamp,
            module,
            severity,
            type,
            status,
            input_text,
            output_text
        FROM cases
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =============================================================================
# 6. DASHBOARD STATS
# =============================================================================

def get_dashboard_stats() -> dict:
    cases = get_all_cases()

    total = len(cases)
    high = len([c for c in cases if c.get("severity") == "High"])
    medium = len([c for c in cases if c.get("severity") == "Medium"])
    compliance = len([c for c in cases if c.get("severity") == "Compliance"])

    return {
        "total_cases": total,
        "high_severity": high,
        "medium_severity": medium,
        "grc_evidence": compliance,
        "recent_cases": cases[:5],
    }