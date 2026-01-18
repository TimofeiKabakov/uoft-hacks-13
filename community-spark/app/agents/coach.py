"""
Coach Agent

This agent provides improvement plans for DENY/REFER decisions.
Analyzes the reasons for denial/referral and provides actionable recommendations.
Uses Gemini AI to provide personalized spending habit analysis.
"""

from typing import Dict, Any, List
import logging
from app.state import CommunitySparkState
from app.utils.gemini_helper import llm_generate_improvement_plan

logger = logging.getLogger(__name__)


def coach_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Coach node function for LangGraph.
    
    Generates improvement plans for denied or referred loan applications.
    Uses Gemini AI to analyze spending habits and provide personalized recommendations.
    
    Args:
        state: Current workflow state containing auditor_flags, auditor_summary, 
               decision_rationale, business_profile, bank_data, and final_decision
        
    Returns:
        Dict with updated state containing improvement_plan and log entry
    """
    # Get relevant data from state
    auditor_flags = state.get("auditor_flags", [])
    auditor_summary = state.get("auditor_summary", "")
    decision_rationale = state.get("decision_rationale", "")
    business_profile = state.get("business_profile", {})
    final_decision = state.get("final_decision", "UNKNOWN")
    auditor_score = state.get("auditor_score", 0)
    bank_data = state.get("bank_data", {})
    
    # Try to use Gemini for personalized improvement plan
    llm_plan = llm_generate_improvement_plan(
        auditor_flags=auditor_flags,
        auditor_score=auditor_score,
        bank_data=bank_data,
        business_profile=business_profile,
        decision_rationale=decision_rationale,
        final_decision=final_decision
    )
    
    if llm_plan:
        # Use Gemini-generated plan
        improvement_plan = llm_plan
        method = "gemini_ai"
    else:
        # Fallback to rule-based plan
        improvement_plan = _generate_fallback_plan(
            auditor_flags, auditor_score, business_profile, 
            final_decision, bank_data
        )
        method = "rule_based"
    
    # Add log entry
    log = state.get("log", [])
    log.append({
        "agent": "coach",
        "message": f"Generated improvement plan using {method} with {len(improvement_plan.get('recommendations', []))} recommendations",
        "reasoning": f"Analyzed {len(auditor_flags)} flags and provided actionable guidance for {final_decision} decision",
        "step": "coaching_complete"
    })
    
    return {
        "improvement_plan": improvement_plan,
        "log": log
    }


def _generate_fallback_plan(
    auditor_flags: List[str],
    auditor_score: int,
    business_profile: Dict[str, Any],
    final_decision: str,
    bank_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a rule-based improvement plan if Gemini is unavailable.
    
    Args:
        auditor_flags: List of risk flags
        auditor_score: Current score
        business_profile: Business information
        final_decision: DENY or REFER
        bank_data: Financial metrics
        
    Returns:
        Dict with improvement plan
    """
    
    # Build improvement plan based on flags and decision
    improvement_plan = {
        "decision": final_decision,
        "business_name": business_profile.get("name", "Unknown"),
        "current_score": auditor_score,
        "target_score": 75,  # Minimum for approval
        "recommendations": [],
        "timeline": "",
        "resources": [],
        "spending_analysis": "",
        "critical_issues": []
    }
    
    # Analyze spending patterns
    nsf_count = bank_data.get("nsf_count", 0)
    debt_to_income = bank_data.get("debt_to_income", 0)
    
    spending_issues = []
    if nsf_count > 0:
        spending_issues.append(f"{nsf_count} NSF/overdraft fees indicating poor cash management")
    if debt_to_income > 0.6:
        spending_issues.append("high debt-to-income ratio suggesting overspending")
    
    if spending_issues:
        improvement_plan["spending_analysis"] = f"Financial analysis reveals concerning patterns: {', '.join(spending_issues)}. These habits significantly impact creditworthiness."
    else:
        improvement_plan["spending_analysis"] = "Financial patterns show room for improvement in revenue stability and cash flow management."
    
    # Analyze flags and provide specific recommendations
    recommendations = []
    critical_issues = []
    
    if "nsf_occurrences" in auditor_flags:
        critical_issues.append("Multiple NSF/overdraft fees")
        recommendations.append({
            "issue": "NSF (Non-Sufficient Funds) Occurrences",
            "action": "Maintain minimum buffer balance of $500-1000 and set up overdraft alerts. This is a critical red flag for lenders.",
            "priority": "Critical",
            "expected_impact": "+10-20 points",
            "timeframe": "Immediate - 1 month"
        })
        if not improvement_plan["timeline"]:
            improvement_plan["timeline"] = "1-3 months"
    
    if "insufficient_revenue_history" in auditor_flags or "no_revenue_data" in auditor_flags:
        critical_issues.append("Insufficient revenue history")
        recommendations.append({
            "issue": "Insufficient Revenue History",
            "action": "Build a stronger transaction history by operating for at least 6-12 months with consistent revenue before reapplying",
            "priority": "High",
            "expected_impact": "+15-25 points",
            "timeframe": "6-12 months"
        })
        improvement_plan["timeline"] = "6-12 months"
    
    if "high_volatility" in auditor_flags:
        critical_issues.append("High revenue volatility")
        recommendations.append({
            "issue": "High Revenue Volatility",
            "action": "Stabilize cash flow by diversifying income streams, improving inventory management, and securing recurring revenue contracts",
            "priority": "High",
            "expected_impact": "+10-15 points",
            "timeframe": "3-6 months"
        })
        if not improvement_plan["timeline"]:
            improvement_plan["timeline"] = "3-6 months"
    
    if "high_debt_to_income" in auditor_flags:
        critical_issues.append("Excessive debt burden")
        recommendations.append({
            "issue": "High Debt-to-Income Ratio",
            "action": "Reduce existing debt obligations or significantly increase revenue to improve debt-to-income ratio below 0.5. Cut unnecessary expenses.",
            "priority": "High",
            "expected_impact": "+5-10 points",
            "timeframe": "3-6 months"
        })
    
    if "low_credit_score" in auditor_flags or auditor_score < 40:
        critical_issues.append("Poor financial health score")
        recommendations.append({
            "issue": "Low Financial Health Score",
            "action": "Focus on improving credit score, maintaining positive account balances, avoiding late payments, and eliminating overdraft fees",
            "priority": "Critical",
            "expected_impact": "+20-30 points",
            "timeframe": "6-12 months"
        })
        if not improvement_plan["timeline"]:
            improvement_plan["timeline"] = "6-12 months"
    
    # Add general recommendations if no specific flags
    if not recommendations:
        if auditor_score < 60:
            critical_issues.append("Below approval threshold")
            recommendations.append({
                "issue": "Below Approval Threshold",
                "action": "Improve overall financial health by increasing revenue, reducing expenses, and maintaining positive cash flow for 3-6 months",
                "priority": "Medium",
                "expected_impact": "+15-20 points",
                "timeframe": "3-6 months"
            })
            improvement_plan["timeline"] = "3-6 months"
        else:
            critical_issues.append("Borderline approval")
            recommendations.append({
                "issue": "Borderline Approval",
                "action": "Continue maintaining current financial performance and consider building additional revenue streams",
                "priority": "Low",
                "expected_impact": "+5-10 points",
                "timeframe": "1-3 months"
            })
            improvement_plan["timeline"] = "1-3 months"
    
    improvement_plan["recommendations"] = recommendations
    improvement_plan["critical_issues"] = critical_issues
    
    # Add resources based on business type and issues
    resources = [
        {
            "name": "Small Business Financial Management Guide",
            "type": "Guide",
            "description": "Comprehensive guide to managing business finances"
        },
        {
            "name": "Free Business Banking Consultation",
            "type": "Consultation",
            "description": "One-on-one financial coaching session"
        }
    ]
    
    if nsf_count > 0:
        resources.append({
            "name": "Cash Flow Management Tool",
            "type": "Tool",
            "description": "Helps track and predict cash flow to avoid overdrafts"
        })
    
    business_type = business_profile.get("type", "")
    if business_type in ["grocery", "pharmacy", "retail"]:
        resources.append({
            "name": "Inventory Management Best Practices",
            "type": "Course",
            "description": "Learn to optimize inventory and reduce costs"
        })
    
    if business_type in ["clinic", "childcare"]:
        resources.append({
            "name": "Service Business Cash Flow Management",
            "type": "Course",
            "description": "Specialized training for service-based businesses"
        })
    
    improvement_plan["resources"] = resources
    
    # Add summary
    if final_decision == "DENY":
        improvement_plan["summary"] = (
            f"{improvement_plan['spending_analysis']} "
            f"Key issues that led to denial: {', '.join(critical_issues[:2])}. "
            f"By following these recommendations over {improvement_plan['timeline']}, you could improve your score "
            f"from {auditor_score} to approximately {min(100, auditor_score + 30)}, increasing your chances of approval."
        )
    else:  # REFER
        improvement_plan["summary"] = (
            f"{improvement_plan['spending_analysis']} "
            f"Your application requires manual review due to: {', '.join(critical_issues[:2])}. "
            f"Addressing these items within {improvement_plan['timeline']} will strengthen your approval odds significantly."
        )
    
    return improvement_plan


