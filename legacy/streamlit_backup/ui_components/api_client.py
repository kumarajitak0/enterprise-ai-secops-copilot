# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_components/api_client.py
# Date Updated: 2026-06-14
# Purpose:
#   Central API client for Streamlit frontend to communicate with FastAPI backend.
# =============================================================================

from __future__ import annotations

import requests

API_URL = "http://127.0.0.1:8001"


# =============================================================================
# 1. GET REQUEST HELPER
# Use:
#   Calls FastAPI GET endpoints.
# Returns:
#   tuple[bool, dict]
# =============================================================================

def get_request(path: str, timeout: int = 10) -> tuple[bool, dict]:
    try:
        response = requests.get(
            f"{API_URL}{path}",
            timeout=timeout,
        )

        if response.status_code != 200:
            return False, {
                "error": f"Backend returned {response.status_code}: {response.text}"
            }

        return True, response.json()

    except requests.exceptions.ConnectionError:
        return False, {
            "error": "FastAPI backend is not running on http://127.0.0.1:8001"
        }

    except Exception as error:
        return False, {
            "error": str(error)
        }


# =============================================================================
# 2. POST REQUEST HELPER
# Use:
#   Calls FastAPI POST endpoints.
# Returns:
#   tuple[bool, dict]
# =============================================================================

def post_request(path: str, payload: dict, timeout: int = 60) -> tuple[bool, dict]:
    try:
        response = requests.post(
            f"{API_URL}{path}",
            json=payload,
            timeout=timeout,
        )

        if response.status_code != 200:
            return False, {
                "error": f"Backend returned {response.status_code}: {response.text}"
            }

        return True, response.json()

    except requests.exceptions.ConnectionError:
        return False, {
            "error": "FastAPI backend is not running on http://127.0.0.1:8001"
        }

    except Exception as error:
        return False, {
            "error": str(error)
        }


# =============================================================================
# 3. HEALTH / ADMIN
# =============================================================================

def health_check() -> tuple[bool, dict]:
    return get_request("/health")


# =============================================================================
# 4. AUTH API
# =============================================================================

def login(username: str, password: str) -> tuple[bool, dict]:
    return post_request(
        "/auth/login",
        {
            "username": username,
            "password": password,
        },
    )


def register(username: str, password: str, role: str) -> tuple[bool, dict]:
    return post_request(
        "/auth/register",
        {
            "username": username,
            "password": password,
            "role": role,
        },
    )


# =============================================================================
# 5. CASES / DASHBOARD
# =============================================================================

def get_cases() -> tuple[bool, dict]:
    return get_request("/cases")


def get_dashboard_stats() -> tuple[bool, dict]:
    return get_request("/dashboard/stats")


# =============================================================================
# 6. ANALYSIS API
# =============================================================================

def analyze_soc(text: str) -> tuple[bool, dict]:
    return post_request(
        "/soc/analyze",
        {"text": text},
        timeout=120,
    )


def generate_rca(text: str) -> tuple[bool, dict]:
    return post_request(
        "/rca/generate",
        {"text": text},
        timeout=120,
    )


def map_grc(text: str) -> tuple[bool, dict]:
    return post_request(
        "/grc/map",
        {"text": text},
        timeout=120,
    )