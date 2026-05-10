def detect_log_type(text: str) -> str:
    lower = text.lower()

    if "event id" in lower or "eventid" in lower or "microsoft-windows-security-auditing" in lower:
        return "Windows Security Event"

    if "firewall" in lower or "wineventlog:firewall" in lower:
        return "Windows Firewall Event"

    if "4625" in lower or "failed logon" in lower:
        return "Windows Failed Login"

    if "4798" in lower or "group membership was enumerated" in lower:
        return "Account Discovery Event"

    if "ssh" in lower or "sudo" in lower or "auth.log" in lower:
        return "Linux Authentication Log"

    if "timeout" in lower or "service unavailable" in lower or "500 error" in lower:
        return "Service / Application Error"

    if "index=" in lower or "sourcetype=" in lower:
        return "Splunk Event"

    return "Generic Security Event"


def estimate_severity(text: str) -> str:
    lower = text.lower()

    high_keywords = [
        "malware", "ransomware", "privilege escalation",
        "admin login", "persistence", "credential dump",
        "mimikatz", "powershell encoded"
    ]

    medium_keywords = [
        "failed logon", "4625", "brute force", "blocked",
        "port scan", "suspicious", "unauthorized",
        "account discovery", "4798"
    ]

    if any(word in lower for word in high_keywords):
        return "High"

    if any(word in lower for word in medium_keywords):
        return "Medium"

    return "Low"