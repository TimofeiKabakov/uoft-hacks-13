"""
LangGraph Workflow Definition

This module defines the LangGraph workflow that orchestrates the various
agents (auditor, impact_analyst, compliance_sentry, coach) to process community
loan applications.

Workflow:
1. Auditor analyzes bank data and calculates audit score (0-100)
2. Impact Analyst evaluates community benefit (1.0-1.6x multiplier)
3. Compliance Sentry makes final decision using weighted scoring
4. Coach (conditional): Provides improvement plan for DENY/REFER decisions

Key Change: ALL businesses get community assessment, not just low-scoring ones.
This ensures community-focused businesses get proper credit regardless of finances.

Coach runs ONLY for DENY/REFER to provide actionable recommendations.
"""

from langgraph.graph import StateGraph, END
from app.state import CommunitySparkState
from app.agents.auditor import auditor_node
from app.agents.impact_analyst import impact_node
from app.agents.compliance_sentry import compliance_node
from app.agents.coach import coach_node


def build_graph():
    """
    Build and compile the LangGraph workflow.
    
    Sequential flow: Auditor → Impact Analyst → Compliance Sentry
    All agents run for every application to ensure fair community assessment.
    
    Returns:
        Compiled graph ready for execution
    """
    workflow = StateGraph(CommunitySparkState)
    
    # Add all three agent nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("impact", impact_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("coach", coach_node)
    
    # Set entry point
    workflow.set_entry_point("auditor")
    
    # Sequential edges: auditor → impact → compliance
    workflow.add_edge("auditor", "impact")
    workflow.add_edge("impact", "compliance")
    
    # Conditional edge from compliance: route to coach if DENY/REFER, otherwise END
    def route_after_compliance(state):
        """Route to coach for DENY/REFER decisions, otherwise END"""
        decision = state.get("final_decision", "")
        if decision in ["DENY", "REFER"]:
            return "coach"
        return END
    
    workflow.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {
            "coach": "coach",
            END: END
        }
    )
    
    # Coach always goes to END
    workflow.add_edge("coach", END)
    
    # Compile and return
    app = workflow.compile()
    
    return app

