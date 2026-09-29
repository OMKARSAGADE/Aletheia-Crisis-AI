"""LangGraph Multi-Agent Orchestrator.
Executes the pipeline across Extraction, Verification, Risk, Action,
and Summary agents with Langfuse tracing and comprehensive metadata capture.
"""
from .graph import graph
import os
import time
from typing import Dict, Any
from services.langfuse_client import is_available, flush

_last_trace_metadata = {}

def get_last_trace_metadata() -> Dict[str, Any]:
    return _last_trace_metadata

def run_pipeline(user_input: str) -> Dict[str, Any]:
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
            
    # Run graph natively
    result = graph.invoke(initial_state, config=config)
    
    # Process structured outputs
    extracted = result.get("extracted_data", {})
    verification = result.get("verification_result", {})
    risk = result.get("risk_result", {})
    action = result.get("action_result", {})
    summary = result.get("summary_result", {})
    
    verdict = verification.get("verdict", "UNVERIFIED")
    credibility = verification.get("credibility", 50)
    composite_risk = risk.get("composite_risk", 50)
    physical_severity = risk.get("physical_severity", 50)
    misinfo_risk = risk.get("misinformation_risk", 50)
    location = extracted.get("location") or "Unknown"
    
    result["final_verdict"] = verdict
    result["final_credibility"] = credibility
    result["trusted_sources"] = verification.get("trusted_sources", [])
    result["evidence_found"] = verification.get("evidence", "No evidence analyzed.")
    result["final_location"] = location
    result["final_risk"] = composite_risk
    result["physical_severity"] = physical_severity
    result["misinformation_risk"] = misinfo_risk
    result["risk_explanation"] = risk.get("explanation", "")
    result["executive_summary"] = summary.get("executive_summary", "")
    result["citizen_action"] = action.get("citizen_action", "")
    result["authority_action"] = action.get("authority_action", "")
    result["has_simulated_sources"] = verification.get("has_simulated_sources", False)
    
    elapsed = round(time.time() - start_time, 2)
    
    # Extract trace ID if available
    trace_id = "N/A"
    try:
        if config and "callbacks" in config:
            trace_id = config["callbacks"][0].get_trace_id()
    except Exception:
        pass
        
    if is_available():
        flush()
    
    agent_statuses = {a: "completed" for a in ["ExtractionAgent", "VerificationAgent", "RiskAgent", "ActionAgent", "SummaryAgent"]}
    
    _last_trace_metadata = {
        "query": user_input,
        "agents": agent_statuses,
        "verdict": verdict,
        "credibility": credibility,
        "risk": composite_risk,
        "physical_severity": physical_severity,
        "misinformation_risk": misinfo_risk,
        "location": location,
        "response_time": f"{elapsed}s",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trace_id": trace_id
    }
        
    return result
