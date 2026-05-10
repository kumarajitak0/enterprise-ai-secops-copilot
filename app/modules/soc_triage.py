from app.modules.ollama_client import ask_llm


def detect_log_type(text: str) -> str:
    lower = text.lower()

    if "event id" in lower or "eventid" in lower or "microsoft-windows-security-auditing" in lower:
        return "Windows Event Log"

    if "wineventlog:firewall" in lower or "firewall" in lower:
        return "Windows Firewall Log"

    if "failed logon" in lower or "4625" in lower:
        return "Windows Failed Login Event"

    if "sudo" in lower or "auth.log" in lower or "ssh" in lower:
        return "Linux Authentication Log"

    if "splunk" in lower or "index=" in lower or "sourcetype=" in lower:
        return "Splunk Event"

    return "Generic Security Log"


def analyze_alert(log_text: str) -> str:
    log_type = detect_log_type(log_text)

    prompt = f"""
You are an enterprise SOC analyst.

Analyze the following log.

Detected Log Type: {log_type}

IMPORTANT RULES:
- If this is a Windows log, do NOT provide Linux commands.
- If this is informational only, clearly say it is low risk.
- Be concise.
- Use professional SOC language.

Log:
{log_text}

Return ONLY this format:

1. Alert Summary:
2. Log Type:
3. Severity: Low/Medium/High
4. Why This Matters:
5. Possible Root Cause:
6. MITRE ATT&CK Mapping:
7. Splunk Search Query:
8. Windows Checks or Linux Checks:
9. Recommended SOC Action:
10. Short RCA:
"""

    return ask_llm(prompt)