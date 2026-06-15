# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/modules/ollama_client.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   Safely call local Ollama only for narrative/readability tasks.
# =============================================================================

from __future__ import annotations

import os
from typing import Any

import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://172.30.32.1:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Local LLM request wrapper.
# =============================================================================

def ask_llm(prompt: str, num_predict: int = 350) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": num_predict,
                },
            },
            timeout=180,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data.get("response", "No response returned from Ollama.")
    except Exception as exc:
        return f"LLM unavailable. Deterministic analysis was used. Error: {exc}"


# =============================================================================
# End: Local LLM request wrapper
# =============================================================================