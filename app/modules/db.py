import sqlite3
from datetime import datetime

DB_PATH = "data/secops_cases.db"


def init_db():
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
        ai_output TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_case(module, severity, log_type, input_text, ai_output):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cases (
        created_at, module, severity, log_type, input_text, ai_output
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        module,
        severity,
        log_type,
        input_text,
        ai_output
    ))

    conn.commit()
    conn.close()


def get_recent_cases(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, created_at, module, severity, log_type, ai_output
    FROM cases
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows