"""Risk Agent: Computes explainable numerical risk scores, separating
physical incident severity from misinformation harm potential.
"""
from typing import Dict, Any

# Base physical danger ratings by crisis type (0 - 100)
PHYSICAL_SEVERITY_BASE = {
    "Earthquake": 80,
    "Blast": 90,
    "Leak": 85,
    "Cyclone": 80,
    "Tsunami": 90,
    "Collapse": 75,
    "Flood": 65,
    "Fire": 65,
    "Landslide": 65,
    "Accident": 50,
    "Riot": 60,
    "Incident": 40
}

# Words indicating imminent physical danger or human casualties
HIGH_URGENCY_KEYWORDS = [
    "evacuate", "evacuation", "casualties", "dead", "deaths", "killed",
    "injured", "trapped", "bodies", "explosion", "toxic", "massive",
    "catastrophic", "emergency", "urgent", "sos", "save us"
]

# Words indicating sensationalism or viral panic drivers
PANIC_INDUCING_KEYWORDS = [
    "run for your lives", "poisoned water", "do not drink", "city under attack",
    "spread this to everyone", "media hiding", "share before deleted",
    "flee immediately", "looting", "army deployed"
]

def run_risk(state: Dict[str, Any]) -> Dict[str, Any]:
    extracted = state.get("extracted_data", {})
    verification = state.get("verification_result", {})
    raw_text = state.get("input_text", "").lower()
    
    event = extracted.get("event")
    is_crisis = extracted.get("is_crisis", True)
    verdict = verification.get("verdict", "UNVERIFIED").upper()
    credibility = verification.get("credibility", 50)
    
    # Non-crisis text: zero out physical and misinformation risk
    if not is_crisis or not event:
        state["risk_result"] = {
            "status": "completed",
            "physical_severity": 10,
            "misinformation_risk": 10,
            "composite_risk": 10,
            "explanation": "No crisis or emergency claims identified. Standard low baseline risk."
        }
        return state

    # 1. Compute Physical Incident Severity
    base_severity = PHYSICAL_SEVERITY_BASE.get(event, 45)
    urgency_boost = 0
    matched_urgency = [w for w in HIGH_URGENCY_KEYWORDS if w in raw_text]
    if matched_urgency:
        urgency_boost = min(20, len(matched_urgency) * 8)
        
    physical_severity = min(100, base_severity + urgency_boost)

    # 2. Compute Misinformation Harm Potential
    # How damaging is this if it's false? (Inducing unneeded evacuation, stampedes, riots)
    panic_boost = 0
    matched_panic = [w for w in PANIC_INDUCING_KEYWORDS if w in raw_text]
    if matched_panic:
        panic_boost = min(25, len(matched_panic) * 12)
        
    if "evacuate" in raw_text or "evacuation" in raw_text:
        panic_boost = max(panic_boost, 15)

    if "CONTRADICTED" in verdict or "FAKE" in verdict:
        # False crisis claims causing panic have extremely high misinformation risk
        misinformation_risk = min(100, 70 + panic_boost + (15 if physical_severity > 60 else 5))
    elif "SUPPORTED" in verdict or "REAL" in verdict:
        # Corroborated claims carry low misinformation risk
        misinformation_risk = max(10, 25 - int(credibility * 0.15))
    else:  # UNVERIFIED
        # High unverified claims with high physical claims create high uncertainty/anxiety
        cred_deficit = max(0, 70 - credibility)
        misinformation_risk = min(100, 45 + int(cred_deficit * 0.4) + panic_boost)

    # 3. Compute Composite Operational Risk Score (for authorities prioritisation)
    if "SUPPORTED" in verdict or "REAL" in verdict:
        # Physical disaster management is the priority
        composite_risk = int(0.75 * physical_severity + 0.25 * misinformation_risk)
    elif "CONTRADICTED" in verdict or "FAKE" in verdict:
        # Countering false narrative / rumor control is the priority
        composite_risk = int(0.30 * physical_severity + 0.70 * misinformation_risk)
    else:
        # Balanced triage
        composite_risk = int(0.55 * physical_severity + 0.45 * misinformation_risk)

    composite_risk = max(10, min(100, composite_risk))

    # 4. Formulate Explainability Rationale
    urgency_desc = f" Urgency factors detected ({', '.join(matched_urgency)})." if matched_urgency else ""
    panic_desc = f" Panic/viral triggers detected ({', '.join(matched_panic)})." if matched_panic else ""
    
    explanation = (
        f"Physical Severity: {physical_severity}/100 (Based on {event} baseline of {base_severity}/100.{urgency_desc}) | "
        f"Misinformation Risk: {misinformation_risk}/100 (Status: {verdict}, Credibility: {credibility}%.{panic_desc}) | "
        f"Operational Priority: {composite_risk}/100."
    )

    state["risk_result"] = {
        "status": "completed",
        "physical_severity": physical_severity,
        "misinformation_risk": misinformation_risk,
        "composite_risk": composite_risk,
        "explanation": explanation
    }
    return state
