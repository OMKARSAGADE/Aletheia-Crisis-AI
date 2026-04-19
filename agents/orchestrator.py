from .graph import graph
import os
import time
from services.langfuse_client import is_available, flush

_last_trace_metadata = {}

def get_last_trace_metadata():
    return _last_trace_metadata

def run_pipeline(user_input: str):
    global _last_trace_metadata
    
    start_time = time.time()
    
    initial_state = {
        "input_text": user_input,
        "extracted_data": {},
        "verification_result": {},
        "risk_result": {},
        "action_result": {},
        "summary_result": {}
    }
    
    # Langfuse Native Callback setup
    config = {}
    if is_available():
        try:
            from langfuse.langchain import CallbackHandler
            handler = CallbackHandler()
            config = {"callbacks": [handler]}
        except Exception as e:
            print(f"Langfuse callback init error: {e}")
            
    # Run graph natively (Langfuse will trace every node automatically if config is passed)
    result = graph.invoke(initial_state, config=config)
    
    # Process results for the UI
    extracted = result.get("extracted_data", {})
    verification = result.get("verification_result", {})
    
    result["final_verdict"] = verification.get("verdict", "UNVERIFIED")
    result["final_credibility"] = verification.get("credibility", 50)
    result["trusted_sources"] = verification.get("trusted_sources", [])
    result["evidence_found"] = verification.get("evidence", "No evidence analyzed.")
    result["final_location"] = extracted.get("location", "Unknown")
    
    if result["final_verdict"] == "Likely Real" or result["final_verdict"] == "REAL":
        result["final_risk"] = 85
    elif result["final_verdict"] == "FAKE":
        result["final_risk"] = 90
    else:
        result["final_risk"] = 50
        
    elapsed = round(time.time() - start_time, 2)
    
    # Get trace ID from the handler to display in the UI
    trace_id = "N/A"
    try:
        if config and "callbacks" in config:
            trace_id = config["callbacks"][0].get_trace_id()
    except Exception:
        pass
        
    if is_available():
        flush()
    
    # Mock status for UI (actual proof is inside Langfuse waterfall diagram now)
    agent_statuses = {a: "completed" for a in ["ExtractionAgent", "VerificationAgent", "RiskAgent", "ActionAgent", "SummaryAgent"]}
    
    _last_trace_metadata = {
        "query": user_input,
        "agents": agent_statuses,
        "verdict": result.get("final_verdict", "UNVERIFIED"),
        "credibility": result.get("final_credibility", 50),
        "risk": result.get("final_risk", 50),
        "location": result.get("final_location", "Unknown"),
        "response_time": f"{elapsed}s",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trace_id": trace_id
    }
        
    return result
