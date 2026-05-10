from app.modules.ollama_client import ask_llm


def generate_rca(data: str) -> str:
    prompt = f"""
You are an SRE/SOC RCA analyst.

Analyze this incident or log and produce a short RCA.

Rules:
- Keep output concise.
- If Windows log, use Windows investigation steps.
- If Splunk log, include Splunk search.
- Do not invent unsupported facts.

Input:
{data}

Return:

1. Incident Summary:
2. Impact:
3. Likely Root Cause:
4. Evidence Observed:
5. Validation Steps:
6. Fix / Remediation:
7. Prevention:
8. Final RCA Summary:
"""

    return ask_llm(prompt)