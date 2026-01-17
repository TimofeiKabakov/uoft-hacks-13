"""
Audit Agent (LLM-powered)

This agent analyzes bank data to assess financial health using AI reasoning.
Falls back to rule-based scoring if OpenAI is unavailable.
"""

from typing import Dict, Any, List
from app.state import CommunitySparkState
from app.utils.gemini_helper import llm_audit_decision


def auditor_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Auditor node function for LangGraph.
    
    Uses LLM to analyze bank_data and make scoring decisions.
    Falls back to rule-based logic if LLM is unavailable.
    
    Args:
        state: Current workflow state containing bank_data
        
    Returns:
        Dict with updated state containing auditor_score, auditor_flags, auditor_summary, and log entry
    """
    bank_data = state.get("bank_data", {})
    
    # Try LLM-powered decision first
    llm_result = llm_audit_decision(bank_data)
    
    if llm_result:
        # Hybrid decision (deterministic bounds + LLM reasoning)
        auditor_score = llm_result["auditor_score"]
        flags = llm_result["flags"]
        auditor_summary = llm_result["reasoning"]
        method = llm_result.get("method", "llm")
        
        log = state.get("log", [])
        
        # Build detailed log message
        if method == "hybrid":
            bounds = llm_result.get("deterministic_bounds", [])
            message = f"Hybrid audit complete. Score: {auditor_score}/100 (bounds: {bounds[0]}-{bounds[1]}). Flags: {len(flags)}"
        else:
            message = f"LLM-powered audit complete. Score: {auditor_score}/100. Flags: {len(flags)}"
        
        log.append({
            "agent": "auditor",
            "message": message,
            "reasoning": auditor_summary,
            "decision": auditor_score,
            "flags": flags,
            "method": method,
            "step": "audit_complete"
        })
        
        return {
            "auditor_score": auditor_score,
            "auditor_flags": flags,
            "auditor_summary": auditor_summary,
            "log": log
        }
    
    # Fallback to rule-based logic if LLM unavailable
    else:
        # Extract preprocessed fields (with defaults)
        avg_monthly_revenue = bank_data.get("avg_monthly_revenue", 0)
        revenue_months = bank_data.get("revenue_months", 0)
        volatility = bank_data.get("volatility", 1.0)
        nsf_count = bank_data.get("nsf_count", 0)
        debt_to_income = bank_data.get("debt_to_income", 0.0)
        traditional_credit_score = bank_data.get("traditional_credit_score", 0)
        
        # Calculate auditor_score (1-100 scale)
        # For business loans, revenue is PRIMARY indicator
        
        # Severe penalty for no revenue data
        if avg_monthly_revenue == 0 or revenue_months == 0:
            # No business revenue = major risk, cap score at 35
            base_score = (traditional_credit_score / 850) * 35 if traditional_credit_score > 0 else 20
            revenue_score = 0
            volatility_score = 0
        else:
            # Base score from traditional credit score (scaled to 40% weight for business)
            base_score = (traditional_credit_score / 850) * 40 if traditional_credit_score > 0 else 20
            
            # Revenue stability factor (up to 30 points - more important for business)
            revenue_score = min(30, (revenue_months / 12) * 30) if revenue_months > 0 else 0
            
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
        if avg_monthly_revenue == 0 or revenue_months == 0:
            flags.append("no_revenue")
        elif avg_monthly_revenue < 1000:
            flags.append("low_revenue")
        if revenue_months < 6 and revenue_months > 0:
            flags.append("insufficient_revenue_history")
        if volatility > 0.5:
            flags.append("high_revenue_volatility")
        if nsf_count >= 1:
            flags.append("nsf_occurrences")
        if nsf_count >= 2:
            flags.append("multiple_nsf_occurrences")
        if debt_to_income > 0.5:
            flags.append("high_debt_to_income")
        if traditional_credit_score < 600:
            flags.append("low_traditional_credit_score")
        
        # Generate summary
        summary_parts = [f"Audit score: {auditor_score}/100 (rule-based fallback)"]
        if traditional_credit_score > 0:
            summary_parts.append(f"Traditional credit score: {traditional_credit_score}")
        if revenue_months > 0:
            summary_parts.append(f"Revenue history: {revenue_months} months")
        if flags:
            summary_parts.append(f"Flags: {', '.join(flags)}")
        else:
            summary_parts.append("No significant flags identified")
        
        auditor_summary = ". ".join(summary_parts) + "."
        
        # Get existing log or initialize empty list
        log = state.get("log", [])
        
        # Append log entry
        log.append({
            "agent": "auditor",
            "message": f"Rule-based audit complete. Score: {auditor_score}/100. Flags: {len(flags)}",
            "reasoning": auditor_summary,
            "decision": auditor_score,
            "flags": flags,
            "method": "rule-based",
            "step": "audit_complete"
        })
        
        return {
            "auditor_score": auditor_score,
            "auditor_flags": flags,
            "auditor_summary": auditor_summary,
            "log": log
        }

