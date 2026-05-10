import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Enterprise AI SecOps Copilot",
    layout="wide"
)

st.title("Enterprise AI SecOps Copilot")
st.caption("Local SOC triage, GRC evidence mapping, RCA generation, and blue-team troubleshooting assistant.")

with st.sidebar:
    st.header("System Status")
    st.write("Backend: FastAPI :8001")
    st.write("AI Engine: Ollama")
    st.write("Recommended Model: llama3.2:1b")
    st.divider()

    st.header("Suggested Log Sources")
    st.markdown("""
    **Windows Event Viewer**
    - Security logs
    - Firewall logs
    - Failed logons
    - Account changes

    **Splunk**
    - `index=firewall`
    - `WinEventLog:Security`
    - `WinEventLog:Firewall`
    - failed login events
    """)

    st.divider()
    st.header("Recent Cases")

    try:
        case_response = requests.get(f"{API_URL}/cases", timeout=10)
        if case_response.status_code == 200:
            cases = case_response.json().get("cases", [])
            if cases:
                for case in cases[:5]:
                    st.caption(
                        f"{case['created_at']} | {case['module']} | {case['severity']}"
                    )
            else:
                st.caption("No cases saved yet.")
        else:
            st.caption("Case history unavailable.")
    except Exception:
        st.caption("Case history unavailable.")

module = st.selectbox(
    "Select Analysis Module",
    ["SOC Alert Triage", "RCA Generator", "GRC Evidence Mapping"]
)

col1, col2 = st.columns([2, 1])

with col1:
    input_text = st.text_area(
        "Paste Windows Event Log, Splunk event, firewall event, or security alert:",
        height=320,
        placeholder="""Example:
Log Name: Security
Source: Microsoft-Windows-Security-Auditing
Event ID: 4798
Computer: suraj
Description: A user's local group membership was enumerated."""
    )

with col2:
    st.subheader("Which module should I use?")
    st.markdown("""
    **SOC Alert Triage**
    - Firewall events
    - Failed logins
    - Suspicious activity
    - IDS alerts

    **RCA Generator**
    - Errors
    - Outages
    - Timeouts
    - Service failures

    **GRC Evidence Mapping**
    - MFA evidence
    - Logging evidence
    - Access control
    - Audit proof
    """)

if st.button("Analyze", type="primary"):
    if not input_text.strip():
        st.warning("Please paste a log or alert first.")
    else:
        if module == "SOC Alert Triage":
            endpoint = "/soc"
        elif module == "GRC Evidence Mapping":
            endpoint = "/grc"
        else:
            endpoint = "/rca"

        start_time = time.time()

        with st.spinner("Analyzing with local Ollama model..."):
            try:
                response = requests.post(
                    f"{API_URL}{endpoint}",
                    json={"text": input_text},
                    timeout=240
                )

                elapsed = round(time.time() - start_time, 2)
                st.subheader("AI Output")
                st.caption(f"Generated in {elapsed} seconds")

                if response.status_code == 200:
                    try:
                        data = response.json()

                        if "severity" in data:
                            st.info(f"Severity: {data.get('severity')}")

                        if "log_type" in data:
                            st.info(f"Detected Log Type: {data.get('log_type')}")

                        result = data.get("result", "No result returned.")
                        st.markdown(result)

                    except Exception as e:
                        st.error(f"JSON parsing error: {e}")
                        st.code(response.text)
                else:
                    st.error(f"API returned status code {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to FastAPI backend: {e}")