"""
LangGraph State Management

This module defines the state schema for the LangGraph workflow.
The state serves as shared memory between agents, accumulating data
as it flows through the audit -> impact analysis -> compliance pipeline.
"""

from typing import TypedDict, List, Dict, Literal


class CommunitySparkState(TypedDict, total=False):
    """
    Main state class for the LangGraph workflow.
    
    This state is passed between nodes in the graph and accumulates
    information as the workflow progresses through the agent pipeline.
    All fields are optional (total=False) to allow incremental population.
    """
    
    # ========== INPUT DATA ==========
    bank_data: Dict
    """
    Bank transaction and account data from Plaid.
    Contains transaction history, account balances, and financial patterns.
    """
    
    business_profile: Dict
    """
    Business profile information including:
    - Business name, type, and industry
    - Years in operation
    - Employee count
    - Business model and operations
    """
    
    # ========== AUDITOR AGENT OUTPUTS ==========
    auditor_score: int
    """
    Overall audit score from 1-100 (Plaid-based scoring).
    Higher scores indicate better financial health and reliability.
    """
    
    auditor_flags: List[str]
    """
    List of flags or issues identified during the audit process.
    Examples: "insufficient_history", "high_volatility", "low_balance"
    """
    
    auditor_summary: str
    """
    Human-readable summary of the audit findings and assessment.
    Provides context for the auditor_score and flags.
    """
    
    # ========== IMPACT ANALYST AGENT OUTPUTS ==========
    community_multiplier: float
    """
    Multiplier factor indicating the community impact potential.
    Values > 1.0 suggest positive community impact.
    Used to weight loan decisions based on social value.
    """
    
    impact_summary: str
    """
    Narrative description of the business's community impact.
    Details how the business contributes to local economy, employment, etc.
    """
    
    # ========== COMPLIANCE SENTRY AGENT OUTPUTS ==========
    final_decision: Literal["APPROVE", "DENY", "REFER"]
    """
    Final decision on the loan application.
    - APPROVE: Application meets all criteria
    - DENY: Application does not meet criteria
    - REFER: Requires manual review or additional information
    """
    
    decision_rationale: str
    """
    Detailed explanation of the final_decision.
    References auditor_score, community_multiplier, and compliance factors.
    """
    
    loan_terms: Dict | None
    """
    Proposed loan terms if approved, including:
    - Loan amount
    - Interest rate
    - Term length
    - Repayment schedule
    None if application is denied.
    """
    
    # ========== WORKFLOW LOG ==========
    log: List[Dict]
    """
    Sequential log of agent activities and workflow steps.
    Each entry contains:
    - agent: Name of the agent that performed the action
    - message: Description of what happened
    - step: Current workflow step identifier
    """

