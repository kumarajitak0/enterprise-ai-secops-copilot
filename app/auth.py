# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/auth.py
# Date Updated: 2026-06-14
# Purpose:
#   SQLite authentication with bcrypt password hashing.
# =============================================================================

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

import bcrypt

DATA_DIR = Path("data")
AUTH_DB_PATH = DATA_DIR / "auth_users.db"


def get_auth_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db() -> None:
    with get_auth_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def register_user(username: str, password: str, role: str = "SOC Analyst") -> dict:
    init_auth_db()

    username = username.strip()

    if not username or not password:
        return {"success": False, "message": "Username and password are required."}

    if len(password) < 8:
        return {"success": False, "message": "Password must be at least 8 characters."}

    try:
        with get_auth_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    username,
                    hash_password(password),
                    role,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()

        return {"success": True, "message": "User registered successfully."}

    except sqlite3.IntegrityError:
        return {"success": False, "message": "Username already exists."}


def login_user(username: str, password: str) -> dict:
    init_auth_db()

    with get_auth_connection() as conn:
        row = conn.execute(
            """
            SELECT username, password_hash, role
            FROM users
            WHERE username = ?
            """,
            (username.strip(),),
        ).fetchone()

    if not row:
        return {"success": False, "message": "Invalid username or password."}

    if not verify_password(password, row["password_hash"]):
        return {"success": False, "message": "Invalid username or password."}

    return {
        "success": True,
        "message": "Login successful.",
        "username": row["username"],
        "role": row["role"],
    }


def auth_health() -> str:
    try:
        init_auth_db()
        return "enabled"
    except Exception:
        return "unavailable"