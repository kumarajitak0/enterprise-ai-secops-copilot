
# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/db.py
# Purpose:
#   SQLite case database for saved SOC/GRC/RCA investigations.
# =============================================================================

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/secops_cases.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        module TEXT,
        severity TEXT,
        log_type TEXT,
        input_text TEXT,
        analyst_note TEXT,
        ai_output TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_case(
    module: str,
    severity: str,
    log_type: str,
    input_text: str,
    analyst_note: str,
    ai_output: str,
) -> None:
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cases (
        created_at,
        module,
        severity,
        log_type,
        input_text,
        analyst_note,
        ai_output
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        module,
        severity,
        log_type,
        input_text,
        analyst_note,
        ai_output,
    ))

    conn.commit()
    conn.close()


def get_recent_cases(limit: int = 50) -> list[dict]:
    init_db()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        created_at,
        module,
        severity,
        log_type,
        input_text,
        analyst_note,
        ai_output
    FROM cases
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]