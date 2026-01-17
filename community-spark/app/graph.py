"""
LangGraph Workflow Definition

This module defines the LangGraph workflow that orchestrates the various
agents (auditor, impact_analyst, compliance_sentry) to process community
loan applications.

Workflow:
1. Auditor analyzes bank data and calculates audit score
2. Conditional routing based on auditor_score:
   - If auditor_score < 60: Route to impact_analyst for community assessment
   - If auditor_score >= 60: Route directly to compliance for faster processing
3. Impact analyst (if routed) calculates community multiplier
4. Compliance makes final decision (APPROVE/DENY/REFER)
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from app.state import CommunitySparkState
from app.agents.auditor import auditor_node
from app.agents.impact_analyst import impact_node
from app.agents.compliance_sentry import compliance_node


def route_after_auditor(state: CommunitySparkState) -> Literal["impact", "compliance"]:
    """
    Conditional routing function after auditor node.
    
    If auditor_score < 60, route to impact analyst for community multiplier.
    Otherwise, route directly to compliance for faster processing.
    
    Args:
        state: Current workflow state containing auditor_score
        
    Returns:
        Next node name: "impact" or "compliance"
    """
    auditor_score = state.get("auditor_score", 0)
    
    if auditor_score < 60:
        # Low score - need community multiplier to potentially improve adjusted score
        return "impact"
    else:
        # Good score - skip impact analysis and go directly to compliance
        return "compliance"


def build_graph():
    """
    Build and compile the LangGraph workflow.
    
    Returns:
        Compiled graph ready for execution
    """
    # Initialize the graph with the state schema
    workflow = StateGraph(CommunitySparkState)
    
    # Add agent nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("impact", impact_node)
    workflow.add_node("compliance", compliance_node)
    
    # Set entry point
    workflow.set_entry_point("auditor")
    
    # Add conditional edge from auditor
    workflow.add_conditional_edges(
        "auditor",
        route_after_auditor,
        {
            "impact": "impact",
            "compliance": "compliance"
        }
    )
    
    # Impact always goes to compliance
    workflow.add_edge("impact", "compliance")
    
    # Compliance is the end node
    workflow.add_edge("compliance", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

