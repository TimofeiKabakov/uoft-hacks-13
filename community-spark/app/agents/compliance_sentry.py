"""
Compliance Sentry Agent (Hybrid-Explanation)

This agent makes the final loan decision by combining audit scores
with community multipliers and applying risk guardrails.

Decision logic is deterministic (rule-based), but rationale is LLM-enhanced.
"""

from typing import Dict, Any
from app.state import CommunitySparkState
from app.utils.openai_helper import llm_compliance_rationale


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
    auditor_score = state.get("auditor_score", 0)
    community_multiplier = state.get("community_multiplier", 1.0)
    bank_data = state.get("bank_data", {})
    nsf_count = bank_data.get("nsf_count", 0)
    auditor_summary = state.get("auditor_summary", "")
    impact_summary = state.get("impact_summary", "")
    
    log = state.get("log", [])
    impact_ran = any(entry.get("agent") == "impact_analyst" for entry in log)
    decision_path = "auditor->impact->compliance" if impact_ran else "auditor->compliance"
    
    baseline_score = auditor_score
    adjusted_score = baseline_score * community_multiplier
    policy_floor_checks = []
    
    final_decision: str
    decision_rationale: str
    loan_terms: Dict | None = None
    llm_rationale = None
    
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
        
        basic_rationale = f"Application denied due to: {', '.join(reasons)}. "
        basic_rationale += f"Adjusted score: {adjusted_score:.1f} (auditor: {auditor_score}, multiplier: {community_multiplier}x)."
        
        llm_rationale = llm_compliance_rationale(
            final_decision="DENY",
            auditor_score=auditor_score,
            community_multiplier=community_multiplier,
            adjusted_score=adjusted_score,
            policy_checks=policy_floor_checks,
            auditor_summary=auditor_summary,
            impact_summary=impact_summary
        )
        
        decision_rationale = llm_rationale if llm_rationale else basic_rationale
        loan_terms = None
    
    elif adjusted_score >= 75:
        policy_floor_checks.append({
            "check": "auditor_score_floor",
            "threshold": 40,
            "value": auditor_score,
            "passed": True
        })
        
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
        
        basic_rationale = (
            f"Application approved. Adjusted score: {adjusted_score:.1f} "
            f"(auditor: {auditor_score}, community multiplier: {community_multiplier}x). "
            f"Meets approval threshold of 75."
        )
        
        llm_rationale = llm_compliance_rationale(
            final_decision="APPROVE",
            auditor_score=auditor_score,
            community_multiplier=community_multiplier,
            adjusted_score=adjusted_score,
            policy_checks=policy_floor_checks,
            auditor_summary=auditor_summary,
            impact_summary=impact_summary
        )
        
        decision_rationale = llm_rationale if llm_rationale else basic_rationale
        
        if adjusted_score >= 90:
            interest_rate = 6.5
            loan_amount_mult = 1.2
        elif adjusted_score >= 85:
            interest_rate = 7.0
            loan_amount_mult = 1.1
        else:
            interest_rate = 7.5
            loan_amount_mult = 1.0
        
        avg_monthly_revenue = bank_data.get("avg_monthly_revenue", 0)
        base_loan_amount = max(10000, min(100000, avg_monthly_revenue * 3 * loan_amount_mult)) if avg_monthly_revenue > 0 else 50000
        
        loan_terms = {
            "loan_amount": int(base_loan_amount),
            "interest_rate": interest_rate,
            "term_months": 36,
            "monthly_payment": int((base_loan_amount * (interest_rate / 100 / 12) * (1 + (interest_rate / 100 / 12)) ** 36) / (((1 + (interest_rate / 100 / 12)) ** 36) - 1))
        }
    else:
        policy_floor_checks.append({
            "check": "auditor_score_floor",
            "threshold": 40,
            "value": auditor_score,
            "passed": True
        })
        
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
        
        basic_rationale = (
            f"Application requires manual review. Adjusted score: {adjusted_score:.1f} "
            f"(auditor: {auditor_score}, community multiplier: {community_multiplier}x). "
            f"Below auto-approval threshold of 75 but meets minimum criteria."
        )
        
        llm_rationale = llm_compliance_rationale(
            final_decision="REFER",
            auditor_score=auditor_score,
            community_multiplier=community_multiplier,
            adjusted_score=adjusted_score,
            policy_checks=policy_floor_checks,
            auditor_summary=auditor_summary,
            impact_summary=impact_summary
        )
        
        decision_rationale = llm_rationale if llm_rationale else basic_rationale
        loan_terms = None
    
    method = "hybrid-explanation" if llm_rationale else "rule-based"
    
    log.append({
        "agent": "compliance_sentry",
        "message": f"Compliance decision: {final_decision}. Adjusted score: {adjusted_score:.1f}",
        "reasoning": decision_rationale,
        "decision": final_decision,
        "method": method,
        "step": "compliance_check_complete"
    })
    
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

