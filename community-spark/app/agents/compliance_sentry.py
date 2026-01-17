"""
Compliance Sentry Agent

This agent makes the final loan decision by combining audit scores
with community multipliers and applying risk guardrails.
"""

from typing import Dict, Any
from app.state import CommunitySparkState


def compliance_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Compliance node function for LangGraph.
    
    Combines auditor_score and community_multiplier into adjusted_score,
    then applies guardrails to determine final_decision (APPROVE/DENY/REFER).
    
    Guardrails:
    - If auditor_score < 40 or nsf_count >= 2 => DENY
    - Else if adjusted_score >= 75 => APPROVE
    - Else => REFER
    
    Args:
        state: Current workflow state containing auditor_score, community_multiplier, and bank_data
        
    Returns:
        Dict with updated state containing final_decision, decision_rationale, loan_terms, and log entry
    """
    # Get scores from state
    auditor_score = state.get("auditor_score", 0)
    community_multiplier = state.get("community_multiplier", 1.0)
    bank_data = state.get("bank_data", {})
    nsf_count = bank_data.get("nsf_count", 0)
    
    # Determine decision path by checking if impact node ran
    # If community_multiplier is exactly 1.0 and wasn't explicitly set, impact node likely didn't run
    # Check log to see if impact_analyst ran
    log = state.get("log", [])
    impact_ran = any(entry.get("agent") == "impact_analyst" for entry in log)
    decision_path = "auditor->impact->compliance" if impact_ran else "auditor->compliance"
    
    # Baseline score is the auditor_score
    baseline_score = auditor_score
    
    # Calculate adjusted score
    adjusted_score = baseline_score * community_multiplier
    
    # Track policy floor checks
    policy_floor_checks = []
    
    # Apply guardrails to determine final_decision
    final_decision: str
    decision_rationale: str
    loan_terms: Dict | None = None
    
    # Guardrail 1: Hard denial conditions
    if auditor_score < 40 or nsf_count >= 2:
        final_decision = "DENY"
        reasons = []
        if auditor_score < 40:
            reasons.append(f"auditor score too low ({auditor_score}/100)")
            policy_floor_checks.append({
                "check": "auditor_score_floor",
                "threshold": 40,
                "value": auditor_score,
                "passed": False,
                "reason": f"Score {auditor_score} below minimum threshold of 40"
            })
        else:
            policy_floor_checks.append({
                "check": "auditor_score_floor",
                "threshold": 40,
                "value": auditor_score,
                "passed": True
            })
        
        if nsf_count >= 2:
            reasons.append(f"multiple NSF occurrences ({nsf_count})")
            policy_floor_checks.append({
                "check": "nsf_count_limit",
                "threshold": 2,
                "value": nsf_count,
                "passed": False,
                "reason": f"NSF count {nsf_count} exceeds maximum allowed (2)"
            })
        else:
            policy_floor_checks.append({
                "check": "nsf_count_limit",
                "threshold": 2,
                "value": nsf_count,
                "passed": True
            })
        
        decision_rationale = f"Application denied due to: {', '.join(reasons)}. "
        decision_rationale += f"Adjusted score: {adjusted_score:.1f} (auditor: {auditor_score}, multiplier: {community_multiplier}x)."
        loan_terms = None
    
    # Guardrail 2: Auto-approval for high adjusted scores
    elif adjusted_score >= 75:
        # Check policy floors first
        if auditor_score < 40:
            policy_floor_checks.append({
                "check": "auditor_score_floor",
                "threshold": 40,
                "value": auditor_score,
                "passed": False,
                "reason": f"Score {auditor_score} below minimum threshold of 40"
            })
        else:
            policy_floor_checks.append({
                "check": "auditor_score_floor",
                "threshold": 40,
                "value": auditor_score,
                "passed": True
            })
        
        if nsf_count >= 2:
            policy_floor_checks.append({
                "check": "nsf_count_limit",
                "threshold": 2,
                "value": nsf_count,
                "passed": False,
                "reason": f"NSF count {nsf_count} exceeds maximum allowed (2)"
            })
        else:
            policy_floor_checks.append({
                "check": "nsf_count_limit",
                "threshold": 2,
                "value": nsf_count,
                "passed": True
            })
        
        policy_floor_checks.append({
            "check": "adjusted_score_threshold",
            "threshold": 75,
            "value": adjusted_score,
            "passed": True,
            "reason": f"Adjusted score {adjusted_score:.1f} meets approval threshold"
        })
        
        final_decision = "APPROVE"
        decision_rationale = (
            f"Application approved. Adjusted score: {adjusted_score:.1f} "
            f"(auditor: {auditor_score}, community multiplier: {community_multiplier}x). "
            f"Meets approval threshold of 75."
        )
        
        # Generate loan terms based on score
        # Higher scores get better terms
        if adjusted_score >= 90:
            interest_rate = 6.5
            loan_amount_mult = 1.2
        elif adjusted_score >= 85:
            interest_rate = 7.0
            loan_amount_mult = 1.1
        else:
            interest_rate = 7.5
            loan_amount_mult = 1.0
        
        # Estimate loan amount based on revenue (if available)
        avg_monthly_revenue = bank_data.get("avg_monthly_revenue", 0)
        base_loan_amount = max(10000, min(100000, avg_monthly_revenue * 3 * loan_amount_mult)) if avg_monthly_revenue > 0 else 50000
        
        loan_terms = {
            "loan_amount": int(base_loan_amount),
            "interest_rate": interest_rate,
            "term_months": 36,
            "monthly_payment": int((base_loan_amount * (interest_rate / 100 / 12) * (1 + (interest_rate / 100 / 12)) ** 36) / (((1 + (interest_rate / 100 / 12)) ** 36) - 1))
        }
    
    # Guardrail 3: Refer for manual review
    else:
        # Check policy floors
        if auditor_score < 40:
            policy_floor_checks.append({
                "check": "auditor_score_floor",
                "threshold": 40,
                "value": auditor_score,
                "passed": False,
                "reason": f"Score {auditor_score} below minimum threshold of 40"
            })
        else:
            policy_floor_checks.append({
                "check": "auditor_score_floor",
                "threshold": 40,
                "value": auditor_score,
                "passed": True
            })
        
        if nsf_count >= 2:
            policy_floor_checks.append({
                "check": "nsf_count_limit",
                "threshold": 2,
                "value": nsf_count,
                "passed": False,
                "reason": f"NSF count {nsf_count} exceeds maximum allowed (2)"
            })
        else:
            policy_floor_checks.append({
                "check": "nsf_count_limit",
                "threshold": 2,
                "value": nsf_count,
                "passed": True
            })
        
        policy_floor_checks.append({
            "check": "adjusted_score_threshold",
            "threshold": 75,
            "value": adjusted_score,
            "passed": False,
            "reason": f"Adjusted score {adjusted_score:.1f} below approval threshold of 75"
        })
        
        final_decision = "REFER"
        decision_rationale = (
            f"Application requires manual review. Adjusted score: {adjusted_score:.1f} "
            f"(auditor: {auditor_score}, community multiplier: {community_multiplier}x). "
            f"Below auto-approval threshold of 75 but meets minimum criteria."
        )
        loan_terms = None
    
    # Append log entry
    log.append({
        "agent": "compliance_sentry",
        "message": f"Final decision: {final_decision}. Adjusted score: {adjusted_score:.1f}",
        "step": "compliance_check_complete"
    })
    
    # Build explain object
    explain = {
        "baseline_score": baseline_score,
        "community_multiplier": community_multiplier,
        "adjusted_score": round(adjusted_score, 2),
        "policy_floor_checks": policy_floor_checks,
        "decision_path": decision_path
    }
    
    return {
        "final_decision": final_decision,
        "decision_rationale": decision_rationale,
        "loan_terms": loan_terms,
        "explain": explain,
        "log": log
    }

