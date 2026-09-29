"""Summary Agent: Synthesizes findings across all upstream agents into
a structured crisis intelligence briefing.
"""
from typing import Dict, Any
from services.gemini import get_model

def run_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = state.get("input_text", "")
    extracted = state.get("extracted_data", {})
    verification = state.get("verification_result", {})
    risk = state.get("risk_result", {})
    action = state.get("action_result", {})
    
    event = extracted.get("event") or "Unclassified Incident"
    location = extracted.get("location") or "Unknown Location"
    verdict = verification.get("verdict", "UNVERIFIED")
    credibility = verification.get("credibility", 50)
    physical_severity = risk.get("physical_severity", 50)
    misinfo_risk = risk.get("misinformation_risk", 50)
    evidence = verification.get("evidence", "No evidence analyzed.")
    
    model = get_model()
    executive_summary = None
    if model:
        try:
            prompt = (
                f"Write a 2-sentence executive crisis intelligence summary for authorities:\n"
                f"Incident: {event} in {location}\n"
                f"Claim: '{raw_text}'\n"
                f"Verification Verdict: {verdict} (Credibility: {credibility}%)\n"
                f"Physical Severity: {physical_severity}/100, Misinformation Harm Risk: {misinfo_risk}/100\n"
                f"Evidence: {evidence}"
            )
            response = model.generate_content(prompt)
            if response and response.text:
                executive_summary = response.text.strip()
        except Exception:
            pass

    if not executive_summary:
        executive_summary = (
            f"Assessment of {event} report in {location}: Status is {verdict} (Credibility: {credibility}%). "
            f"Physical severity evaluated at {physical_severity}/100, with misinformation harm potential of {misinfo_risk}/100. "
            f"{evidence}"
        )

    state["summary_result"] = {
        "status": "completed",
        "summary": executive_summary,
        "executive_summary": executive_summary,
        "event": event,
        "location": location,
        "verdict": verdict,
        "credibility": credibility,
        "physical_severity": physical_severity,
        "misinformation_risk": misinfo_risk
    }
    return state
