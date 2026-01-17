"""
LangGraph Workflow Definition

This module defines the LangGraph workflow that orchestrates the various
agents (auditor, impact_analyst, compliance_sentry, coach) to process community
loan applications.

Workflow:
1. Auditor analyzes bank data and calculates audit score
2. Conditional routing based on auditor_score:
   - If auditor_score < 60: Route to impact_analyst for community assessment
   - If auditor_score >= 60: Route directly to compliance for faster processing
3. Impact analyst (if routed) calculates community multiplier
4. Compliance makes final decision (APPROVE/DENY/REFER)
5. Conditional routing based on final_decision:
   - If decision in ["DENY", "REFER"]: Route to coach for improvement plan
   - Else: End workflow
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from app.state import CommunitySparkState
from app.agents.auditor import auditor_node
from app.agents.impact_analyst import impact_node
from app.agents.compliance_sentry import compliance_node
from app.agents.coach import coach_node


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


def route_after_compliance(state: CommunitySparkState) -> Literal["coach", "__end__"]:
    """
    Conditional routing function after compliance node.
    
    If decision is DENY or REFER, route to coach for improvement plan.
    Otherwise, end the workflow.
    
    Args:
        state: Current workflow state containing final_decision
        
    Returns:
        Next node name: "coach" or "__end__"
    """
    final_decision = state.get("final_decision", "UNKNOWN")
    
    if final_decision in ["DENY", "REFER"]:
        # Provide improvement plan for denied or referred applications
        return "coach"
    else:
        # Approved - no coaching needed
        return "__end__"


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
    workflow.add_node("coach", coach_node)
    
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
    
    # Add conditional edge from compliance
    workflow.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {
            "coach": "coach",
            "__end__": END
        }
    )
    
    # Coach goes to end
    workflow.add_edge("coach", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

