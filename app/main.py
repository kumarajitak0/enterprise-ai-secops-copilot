from fastapi import FastAPI
from pydantic import BaseModel

from app.modules.soc_triage import analyze_alert
from app.modules.grc_mapper import map_grc
from app.modules.rca_generator import generate_rca
from app.modules.classifier import detect_log_type, estimate_severity
from app.modules.db import init_db, save_case, get_recent_cases

app = FastAPI(title="Enterprise AI SecOps Copilot")

init_db()


class InputData(BaseModel):
    text: str


@app.get("/")
def home():
    return {
        "status": "Enterprise AI SecOps Copilot is running",
        "modules": ["soc", "grc", "rca", "cases"]
    }


@app.post("/soc")
def soc_triage(input_data: InputData):
    log_type = detect_log_type(input_data.text)
    severity = estimate_severity(input_data.text)

    result = analyze_alert(input_data.text)

    save_case(
        module="SOC Alert Triage",
        severity=severity,
        log_type=log_type,
        input_text=input_data.text,
        ai_output=result
    )

    return {
        "module": "SOC Alert Triage",
        "severity": severity,
        "log_type": log_type,
        "result": result
    }


@app.post("/grc")
def grc_mapping(input_data: InputData):
    log_type = detect_log_type(input_data.text)
    severity = "Compliance"

    result = map_grc(input_data.text)

    save_case(
        module="GRC Evidence Mapping",
        severity=severity,
        log_type=log_type,
        input_text=input_data.text,
        ai_output=result
    )

    return {
        "module": "GRC Evidence Mapping",
        "severity": severity,
        "log_type": log_type,
        "result": result
    }


@app.post("/rca")
def rca(input_data: InputData):
    log_type = detect_log_type(input_data.text)
    severity = estimate_severity(input_data.text)

    result = generate_rca(input_data.text)

    save_case(
        module="RCA Generator",
        severity=severity,
        log_type=log_type,
        input_text=input_data.text,
        ai_output=result
    )

    return {
        "module": "RCA Generator",
        "severity": severity,
        "log_type": log_type,
        "result": result
    }


@app.get("/cases")
def cases():
    rows = get_recent_cases()
    return {
        "cases": [
            {
                "id": row[0],
                "created_at": row[1],
                "module": row[2],
                "severity": row[3],
                "log_type": row[4],
                "ai_output": row[5]
            }
            for row in rows
        ]
    }