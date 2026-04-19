def run_action(state):
    verdict = state.get("verification_result", {}).get("verdict", "UNVERIFIED")
    
    if "REAL" in verdict.upper():
        action = "Escalate local verification teams immediately."
    elif "FAKE" in verdict.upper():
        action = "Issue public denial. Monitor for organized disinformation."
    else:
        action = "Queue for manual analyst review."
        
    state["action_result"] = {"status": "completed", "recommended_action": action}
    return state
