# Enterprise AI SecOps Copilot

Local AI-powered SecOps Copilot using FastAPI, Streamlit, Ollama, SQLite, and Splunk-style logs.

## Features

- SOC alert triage
- RCA generation
- GRC evidence mapping
- Log type detection
- Severity classification
- SQLite case history
- Supports Windows Event Logs, Splunk logs, firewall logs, and security alerts

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt



Start Ollama

Install Ollama from:

https://ollama.com

Then run:

ollama pull llama3.2:1b
ollama serve
Start Backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

Open:

http://127.0.0.1:8001
Start UI

Open second terminal:

source venv/bin/activate
streamlit run app/ui.py

Open:

http://localhost:8501


Log Name: Security
Source: Microsoft-Windows-Security-Auditing
Event ID: ####
Computer: name of your computer
Description: A user's local group membership was enumerated.

Disclaimer

This project uses sanitized/sample logs only. Do not upload real logs, credentials, tokens, or sensitive data.


---

## Future changes

GitHub will **not update automatically**.

After every change:

```bash
git status
git add .
git commit -m "Updated project"
git push