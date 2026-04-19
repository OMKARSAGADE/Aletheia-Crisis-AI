from langgraph.graph import StateGraph, START, END
from .state import CrisisState
from .extraction_agent import run_extraction
from .verification_agent import run_verification
from .risk_agent import run_risk
from .action_agent import run_action
from .summary_agent import run_summary

def build_graph():
    builder = StateGraph(CrisisState)
    
    builder.add_node("extraction", run_extraction)
    builder.add_node("verification", run_verification)
    builder.add_node("risk", run_risk)
    builder.add_node("action", run_action)
    builder.add_node("summary", run_summary)
    
    builder.add_edge(START, "extraction")
    builder.add_edge("extraction", "verification")
    builder.add_edge("verification", "risk")
    builder.add_edge("risk", "action")
    builder.add_edge("action", "summary")
    builder.add_edge("summary", END)
    
    return builder.compile()

graph = build_graph()
