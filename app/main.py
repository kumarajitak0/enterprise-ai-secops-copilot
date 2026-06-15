# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/main.py
# Date Updated: 2026-06-15 14:30
# Purpose:
#   FastAPI backend for React + Vite frontend, auth, SOC triage, RCA, GRC,
#   case storage, dashboard stats, health, CORS, and API compatibility.
# =============================================================================

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.modules.case_enricher import enrich_cases

from app.auth import register_user, login_user, auth_health
from app.db import (
    init_case_db,
    save_case,
    get_all_cases,
    get_dashboard_stats,
    case_db_health,
)

from app.modules.soc_triage import analyze_alert_case
from app.modules.rca_generator import generate_rca_case
from app.modules.grc_mapper import map_grc_case


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# FastAPI app setup for React frontend and backend services.
# =============================================================================

app = FastAPI(
    title="Enterprise AI SecOps Copilot API",
    version="1.0.0",
)

# =============================================================================
# End: FastAPI app setup
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# CORS configuration for React + Vite frontend.
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# End: CORS configuration
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Request models used by auth, SOC, RCA, GRC, and case endpoints.
# =============================================================================

class AuthRequest(BaseModel):
    username: str
    password: str
    role: str | None = "SOC Analyst"


class TextRequest(BaseModel):
    text: str | None = None
    input_text: str | None = None
    log_text: str | None = None
    alert_text: str | None = None

    def resolved_text(self) -> str:
        return (
            self.text
            or self.input_text
            or self.log_text
            or self.alert_text
            or ""
        )


class CaseRequest(BaseModel):
    module: str
    severity: str
    type: str
    status: str = "New"
    input_text: str
    output_text: str

# =============================================================================
# End: Request models
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Startup initialization.
# =============================================================================

@app.on_event("startup")
def startup_event() -> None:
    init_case_db()

# =============================================================================
# End: Startup initialization
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Root and health endpoints.
# =============================================================================

@app.get("/")
def root() -> dict:
    return {
        "status": "ready",
        "service": "Enterprise AI SecOps Copilot API",
        "version": "1.0.0",
    }


@app.get("/health")
def health() -> dict:
    return {
        "backend": "ready",
        "database": case_db_health(),
        "auth": auth_health(),
        "soc_engine": "ready",
        "rca_engine": "ready",
        "grc_engine": "ready",
        "ollama": "local_optional",
        "splunk_connector": "planned",
        "grafana_webhook": "planned",
        "pdf_export": "planned",
    }

# =============================================================================
# End: Root and health endpoints
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Authentication endpoints.
# =============================================================================

@app.post("/auth/register")
def register(payload: AuthRequest) -> dict:
    result = register_user(
        username=payload.username,
        password=payload.password,
        role=payload.role or "SOC Analyst",
    )

    if isinstance(result, dict):
        result.setdefault("success", True)
        result.setdefault("username", payload.username)
        result.setdefault("role", payload.role or "SOC Analyst")

    return result


@app.post("/auth/login")
def login(payload: AuthRequest) -> dict:
    result = login_user(
        username=payload.username,
        password=payload.password,
    )

    if isinstance(result, dict):
        login_ok = (
            result.get("success") is True
            or result.get("authenticated") is True
            or str(result.get("status", "")).lower() == "success"
        )

        if login_ok:
            result.setdefault("success", True)
            result.setdefault("authenticated", True)
            result.setdefault("username", payload.username)
            result.setdefault("role", result.get("role", "Administrator"))

    return result

# =============================================================================
# End: Authentication endpoints
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# Case and dashboard endpoints.
# =============================================================================

@app.get("/cases")
def cases() -> dict:
    raw_cases = get_all_cases()
    return {
        "cases":enrich_cases(raw_cases),
    }


@app.post("/cases")
def create_case(payload: CaseRequest) -> dict:
    return save_case(
        module=payload.module,
        severity=payload.severity,
        case_type=payload.type,
        status=payload.status,
        input_text=payload.input_text,
        output_text=payload.output_text,
    )


@app.get("/dashboard/stats")
def dashboard_stats() -> dict:
    return get_dashboard_stats()

# =============================================================================
# End: Case and dashboard endpoints
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# SOC analysis endpoint using enterprise deterministic SOC engine.
# =============================================================================

@app.post("/soc/analyze")
def soc_analyze(payload: TextRequest) -> dict:
    text = payload.resolved_text()

    result = analyze_alert_case(text)

    save_case(
        module=result["module"],
        severity=result["severity"],
        case_type=result["type"],
        status=result["status"],
        input_text=text,
        output_text=result["output"],
    )

    return result

# =============================================================================
# End: SOC analysis endpoint
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# RCA generation endpoint using evidence-first RCA engine.
# =============================================================================

@app.post("/rca/generate")
def rca_generate(payload: TextRequest) -> dict:
    text = payload.resolved_text()

    result = generate_rca_case(text)

    save_case(
        module=result["module"],
        severity=result["severity"],
        case_type=result["type"],
        status=result["status"],
        input_text=text,
        output_text=result["output"],
    )

    return result

# =============================================================================
# End: RCA generation endpoint
# =============================================================================


# =============================================================================
# 2026-06-15 14:30 - Added/Updated:
# GRC mapping endpoint using deterministic control mapping first.
# =============================================================================

@app.post("/grc/map")
def grc_map(payload: TextRequest) -> dict:
    text = payload.resolved_text()

    result = map_grc_case(text)

    save_case(
        module=result["module"],
        severity=result["severity"],
        case_type=result["type"],
        status=result["status"],
        input_text=text,
        output_text=result["output"],
    )

    return result

# =============================================================================
# End: GRC mapping endpoint
# =============================================================================