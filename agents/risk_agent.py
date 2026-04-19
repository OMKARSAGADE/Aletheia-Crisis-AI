def run_risk(state):
    verdict = state.get("verification_result", {}).get("verdict", "UNVERIFIED")
    
    if "REAL" in verdict.upper():
        score = 85
    elif "FAKE" in verdict.upper():
        score = 90 
    else:
        score = 50
        
    state["risk_result"] = {"status": "completed", "risk_score": score}
    return state
