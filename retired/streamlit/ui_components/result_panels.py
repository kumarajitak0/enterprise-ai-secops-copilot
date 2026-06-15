# =============================================================================
# Project: Enterprise AI SecOps Copilot
# File: app/ui_components/result_panels.py
# Date Created: 2026-05-27
# Date Updated: 2026-05-27
# Purpose:
#   Reusable Streamlit result panels for AI guardrails, MITRE mapping,
#   normalized pipeline details, dynamic playbooks, and command references.
# =============================================================================

import streamlit as st

from app.modules.playbook_engine import get_playbook


# =============================================================================
# 1. HELPER FUNCTION
# Purpose:
#   Extract Event ID from normalized backend response.
# =============================================================================

def get_event_id_from_data(data: dict) -> str:
    normalized_event = data.get("normalized_event", {})
    detection_result = data.get("detection_result", {})

    event_id = normalized_event.get("event_id")

    if event_id:
        return str(event_id)

    evidence = detection_result.get("evidence", {})
    event_id = evidence.get("event_id")

    if event_id:
        return str(event_id)

    return "unknown"


# =============================================================================
# 2. AI GUARDRAIL WARNING PANEL
# Purpose:
#   Show warning if prompt injection or unsafe AI input pattern is detected.
# =============================================================================

def render_guardrail_warning(data: dict) -> None:
    guardrail = data.get("ai_guardrail", {})

    if not guardrail.get("is_suspicious"):
        return

    st.error("AI Defense Warning: Possible prompt injection detected.")
    st.write("Detected patterns:")

    for finding in guardrail.get("findings", []):
        st.code(finding)


# =============================================================================
# 3. RULE-BASED MITRE PANEL
# Purpose:
#   Display deterministic MITRE mapping returned by backend.
# =============================================================================

def render_mitre_mapping(data: dict) -> None:
    mitre_matches = data.get("mitre_matches", [])

    with st.expander("Rule-Based MITRE ATT&CK Mapping", expanded=bool(mitre_matches)):
        if not mitre_matches:
            st.warning("No rule-based MITRE mapping found for this log.")
            return

        for match in mitre_matches:
            st.success(
                f"Event ID {match.get('event_id')} → "
                f"{match.get('technique_id')} "
                f"{match.get('technique_name')} "
                f"({match.get('tactic')})"
            )


# =============================================================================
# 4. PIPELINE DETAILS PANEL
# Purpose:
#   Show normalized event and deterministic detection rule output.
# =============================================================================

def render_pipeline_details(data: dict) -> None:
    normalized_event = data.get("normalized_event", {})
    detection_result = data.get("detection_result", {})

    with st.expander("Normalized Event"):
        st.json(normalized_event)

    with st.expander("Rule-Based Detection Result", expanded=True):
        if detection_result.get("matched"):
            st.success(f"Matched Rule: {detection_result.get('name')}")
        else:
            st.warning("No deterministic detection rule matched.")

        st.write(f"Rule ID: `{detection_result.get('rule_id', 'N/A')}`")
        st.write(f"Alert Type: `{detection_result.get('alert_type', 'N/A')}`")
        st.write(f"Severity: `{detection_result.get('severity', 'N/A')}`")
        st.write(
            f"MITRE: `{detection_result.get('mitre_id', 'N/A')} "
            f"{detection_result.get('mitre_name', '')}`"
        )
        st.write(f"Tactic: `{detection_result.get('tactic', 'N/A')}`")

        st.write("Recommended Action:")
        st.info(detection_result.get("recommended_action", "N/A"))


# =============================================================================
# 5. DYNAMIC SOC PLAYBOOK PANEL
# Purpose:
#   Render event-specific playbook content from knowledge_base/playbooks.json.
# =============================================================================

def render_dynamic_playbook(data: dict) -> None:
    playbook = data.get("playbook", {})

    if not playbook:
        st.warning("No dynamic playbook found for this event.")
        return

    with st.expander("Dynamic SOC Playbook", expanded=True):
        st.subheader(playbook.get("title", "SOC Playbook"))

        st.write(f"Category: `{playbook.get('category', 'N/A')}`")
        st.write(f"MITRE: `{playbook.get('mitre', 'N/A')}`")
        st.write(f"Severity: `{playbook.get('severity', 'N/A')}`")

        if playbook.get("splunk_queries"):
            st.markdown("#### Splunk Queries")
            for query in playbook.get("splunk_queries", []):
                st.code(query, language="spl")

        if playbook.get("windows_commands"):
            st.markdown("#### Windows Commands")
            for command in playbook.get("windows_commands", []):
                st.code(command, language="powershell")

        if playbook.get("linux_commands"):
            st.markdown("#### Linux Commands")
            for command in playbook.get("linux_commands", []):
                st.code(command, language="bash")

        if playbook.get("network_commands"):
            st.markdown("#### Network Commands")
            for command in playbook.get("network_commands", []):
                st.code(command, language="bash")

        if playbook.get("containment"):
            st.markdown("#### Containment / Response")
            for action in playbook.get("containment", []):
                st.checkbox(action)

        if playbook.get("severity_actions"):
            st.markdown("#### Severity-Based Actions")
            for action in playbook.get("severity_actions", []):
                st.warning(action)
# =============================================================================
# 6. ANALYST NOTES PANEL
# Purpose:
#   Show guidance for how analysts should write investigation notes.
#   Actual note saving happens from pages.py.
# =============================================================================

def render_analyst_notes_guidance() -> None:
    with st.expander("How to Write Analyst Notes"):
        st.markdown(
            """
            Use analyst notes to document **what you manually verified**.

            Good analyst notes include:
            - What log source was checked
            - What user/host/IP was reviewed
            - Whether activity was expected or suspicious
            - What containment or escalation action was taken
            - Final analyst decision
            """
        )

        st.code(
            """Example:
Reviewed Event ID 4625 from DC-PROD-01.
Target account: administrator.
Source workstation: WS-102.
No successful login observed after failed attempts.
Recommended monitoring and account lockout review.
Decision: Needs further review.""",
            language="text"
        )


# =============================================================================
# 7. STATIC FALLBACK COMMAND REFERENCE
# Purpose:
#   Provide generic commands when no dynamic playbook exists.
# =============================================================================

def render_command_reference() -> None:
    with st.expander("Static Fallback Command Reference"):
        st.markdown("#### Windows Security Checks")
        st.code(
            """Get-WinEvent -FilterHashtable @{LogName="Security"; Id=<EventID>} -MaxEvents 20
Get-LocalUser
Get-LocalGroupMember Administrators
whoami /groups
net user <username>
tasklist /FI "PID eq <PID>" """,
            language="powershell"
        )

        st.markdown("#### Linux Service Checks")
        st.code(
            """systemctl status <service-name>
journalctl -u <service-name> --since "30 minutes ago" """,
            language="bash"
        )

        st.markdown("#### Network Checks")
        st.code(
            """ss -antp | grep <port>
curl -v http://<host>:<port>/health
ping <target-host>""",
            language="bash"
        )

        st.markdown("#### Splunk / SIEM Examples")
        st.code(
            """index=* ("error" OR "failed" OR "timeout" OR "denied") earliest=-30m
index=* host=<host> earliest=-30m""",
            language="text"
        )