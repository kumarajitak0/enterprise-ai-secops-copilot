from app.modules.ollama_client import ask_llm


def map_grc(data: str) -> str:
    prompt = f"""
You are a GRC analyst.

Map the following security evidence to compliance controls.

Evidence:
{data}

Return concise audit-ready output:

1. Evidence Summary:
2. Control Area:
3. NIST CSF Mapping:
4. PCI DSS Mapping:
5. SOC 2 Mapping:
6. Evidence Type:
7. Risk Reduced:
8. Control Owner:
9. Audit-Ready Explanation:
"""

    return ask_llm(prompt)