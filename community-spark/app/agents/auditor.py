"""
Audit Agent

This agent analyzes bank data to assess financial health and reliability.
Generates a Plaid-based audit score and identifies potential risk flags.
"""

from typing import Dict, Any, List
from app.state import CommunitySparkState
from app.utils.openai_helper import llm_enhance_audit_summary


def auditor_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Auditor node function for LangGraph.
    
    Analyzes bank_data to calculate an audit score (1-100) and generate flags.
    Expects bank_data to contain preprocessed fields:
    - avg_monthly_revenue
    - revenue_months
    - volatility
    - nsf_count
    - debt_to_income
    - traditional_credit_score
    
    Args:
        state: Current workflow state containing bank_data
        
    Returns:
        Dict with updated state containing auditor_score, auditor_flags, auditor_summary, and log entry
    """
    bank_data = state.get("bank_data", {})
    
    # Extract preprocessed fields (with defaults)
    avg_monthly_revenue = bank_data.get("avg_monthly_revenue", 0)
    revenue_months = bank_data.get("revenue_months", 0)
    volatility = bank_data.get("volatility", 1.0)
    nsf_count = bank_data.get("nsf_count", 0)
    debt_to_income = bank_data.get("debt_to_income", 0.0)
    traditional_credit_score = bank_data.get("traditional_credit_score", 0)
    
    # Calculate auditor_score (1-100 scale)
    # Base score from traditional credit score (scaled to 60% weight)
    base_score = (traditional_credit_score / 850) * 60 if traditional_credit_score > 0 else 30
    
    # Revenue stability factor (up to 20 points)
    revenue_score = min(20, (revenue_months / 12) * 20) if revenue_months > 0 else 0
    
    # Volatility penalty (lower volatility = higher score, up to 10 points)
    volatility_score = max(0, 10 - (volatility * 10)) if volatility > 0 else 5
    
    # NSF penalty (up to 10 points deduction)
    nsf_penalty = min(10, nsf_count * 5)
    
    # Debt-to-income penalty (if > 0.5, penalty increases)
    dti_penalty = min(10, max(0, (debt_to_income - 0.3) * 20)) if debt_to_income > 0.3 else 0
    
    # Calculate final score (clamped to 1-100)
    auditor_score = max(1, min(100, int(base_score + revenue_score + volatility_score - nsf_penalty - dti_penalty)))
    
    # Generate flags
    flags: List[str] = []
    if revenue_months < 6:
        flags.append("insufficient_revenue_history")
    if volatility > 0.5:
        flags.append("high_revenue_volatility")
    if nsf_count >= 1:
        flags.append("nsf_occurrences")
    if nsf_count >= 2:
        flags.append("multiple_nsf_occurrences")
    if debt_to_income > 0.5:
        flags.append("high_debt_to_income")
    if avg_monthly_revenue < 1000:
        flags.append("low_revenue")
    if traditional_credit_score < 600:
        flags.append("low_traditional_credit_score")
    
    # Generate summary
    summary_parts = [f"Audit score: {auditor_score}/100"]
    if traditional_credit_score > 0:
        summary_parts.append(f"Traditional credit score: {traditional_credit_score}")
    if revenue_months > 0:
        summary_parts.append(f"Revenue history: {revenue_months} months")
    if flags:
        summary_parts.append(f"Flags identified: {', '.join(flags)}")
    else:
        summary_parts.append("No significant flags identified")
    
    # Use LLM to enhance the summary if OpenAI API key is available
    auditor_summary = llm_enhance_audit_summary(bank_data, auditor_score, flags)
    
    # Fallback to basic summary if LLM fails or is not configured
    if not auditor_summary or len(auditor_summary) < 20:
        auditor_summary = ". ".join(summary_parts) + "."
    
    # Get existing log or initialize empty list
    log = state.get("log", [])
    
    # Append log entry
    log.append({
        "agent": "auditor",
        "message": f"Completed audit analysis. Score: {auditor_score}/100. Flags: {len(flags)}",
        "step": "audit_complete"
    })
    
    return {
        "auditor_score": auditor_score,
        "auditor_flags": flags,
        "auditor_summary": auditor_summary,
        "log": log
    }

