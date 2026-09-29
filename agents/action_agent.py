"""Action Agent: Generates tailored, actionable protocols for both
citizens and crisis management authorities based on verified risk and status.
"""
from typing import Dict, Any

def run_action(state: Dict[str, Any]) -> Dict[str, Any]:
    verification = state.get("verification_result", {})
    risk = state.get("risk_result", {})
    extracted = state.get("extracted_data", {})
    
    verdict = verification.get("verdict", "UNVERIFIED").upper()
    event = extracted.get("event", "incident")
    location = extracted.get("location", "the area")
    physical_severity = risk.get("physical_severity", 50)
    misinfo_risk = risk.get("misinformation_risk", 50)
    
    if "SUPPORTED" in verdict or "REAL" in verdict:
        authority_action = (
            f"Dispatch frontline disaster response for {event} in {location}. "
            f"Coordinate emergency relief, establish traffic diversions, and activate municipal shelters if required."
        )
        citizen_action = (
            f"Heed official evacuation and safety advisories from local authorities in {location}. "
            f"Keep phone lines clear for emergencies and check verified civic handles."
        )
    elif "CONTRADICTED" in verdict or "FAKE" in verdict:
        authority_action = (
            f"Issue immediate public clarification and social debunking bulletin regarding false {event} reports in {location}. "
            f"Flag viral accounts spreading panic and monitor community messaging channels."
        )
        citizen_action = (
            f"Do not forward or amplify this message. "
            f"Verify breaking claims directly on official municipal disaster management dashboards."
        )
    elif "CONFLICTING" in verdict:
        authority_action = (
            f"Deploy dedicated civil information officer to reconcile conflicting reports regarding {event} in {location}. "
            f"Awaited ground-truth confirmation before issuing major advisories."
        )
        citizen_action = (
            f"Conflicting reports detected. Exercise caution and refrain from sharing unconfirmed situation updates."
        )
    else: # UNVERIFIED
        if physical_severity > 70 or misinfo_risk > 70:
            authority_action = (
                f"High-priority triage: Send rapid ground scout or contact local police station in {location} to verify {event}. "
                f"Prepare standby response."
            )
            citizen_action = (
                f"This claim is currently unverified. Maintain heightened situational awareness without taking unguided emergency actions."
            )
        else:
            authority_action = f"Queue claim for analyst review. Monitor news feeds for corroboration regarding {event} in {location}."
            citizen_action = "Unverified report. Rely exclusively on official alerts before taking action."

    state["action_result"] = {
        "status": "completed",
        "recommended_action": authority_action,
        "authority_action": authority_action,
        "citizen_action": citizen_action
    }
    return state
