"""
Coach Agent

This agent provides improvement plans for DENY/REFER decisions.
Analyzes the reasons for denial/referral and provides actionable recommendations.
"""

from typing import Dict, Any
from app.state import CommunitySparkState


def coach_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Coach node function for LangGraph.
    
    Generates improvement plans for denied or referred loan applications.
    Analyzes auditor flags, auditor summary, decision rationale, and business profile
    to provide actionable recommendations.
    
    Args:
        state: Current workflow state containing auditor_flags, auditor_summary, 
               decision_rationale, business_profile, and final_decision
        
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
    
    # Build improvement plan based on flags and decision
    improvement_plan = {
        "decision": final_decision,
        "business_name": business_profile.get("name", "Unknown"),
        "current_score": auditor_score,
        "target_score": 75,  # Minimum for approval
        "recommendations": [],
        "timeline": "",
        "resources": []
    }
    
    # Analyze flags and provide specific recommendations
    recommendations = []
    
    if "insufficient_revenue_history" in auditor_flags or "no_revenue_data" in auditor_flags:
        recommendations.append({
            "issue": "Insufficient Revenue History",
            "action": "Build a stronger transaction history by operating for at least 6-12 months with consistent revenue",
            "priority": "High",
            "expected_impact": "+15-25 points"
        })
        improvement_plan["timeline"] = "6-12 months"
    
    if "high_volatility" in auditor_flags:
        recommendations.append({
            "issue": "High Revenue Volatility",
            "action": "Stabilize cash flow by diversifying income streams and improving inventory management",
            "priority": "High",
            "expected_impact": "+10-15 points"
        })
        if not improvement_plan["timeline"]:
            improvement_plan["timeline"] = "3-6 months"
    
    if "nsf_occurrences" in auditor_flags:
        recommendations.append({
            "issue": "NSF (Non-Sufficient Funds) Occurrences",
            "action": "Maintain minimum buffer balance and set up overdraft alerts to prevent NSF incidents",
            "priority": "Critical",
            "expected_impact": "+10-20 points"
        })
        if not improvement_plan["timeline"]:
            improvement_plan["timeline"] = "1-3 months"
    
    if "high_debt_to_income" in auditor_flags:
        recommendations.append({
            "issue": "High Debt-to-Income Ratio",
            "action": "Reduce existing debt obligations or increase revenue to improve debt-to-income ratio below 0.5",
            "priority": "Medium",
            "expected_impact": "+5-10 points"
        })
    
    if "low_credit_score" in auditor_flags or auditor_score < 40:
        recommendations.append({
            "issue": "Low Financial Health Score",
            "action": "Focus on improving credit score, maintaining positive account balances, and avoiding late payments",
            "priority": "High",
            "expected_impact": "+20-30 points"
        })
        if not improvement_plan["timeline"]:
            improvement_plan["timeline"] = "6-12 months"
    
    # Add general recommendations if no specific flags
    if not recommendations:
        if auditor_score < 60:
            recommendations.append({
                "issue": "Below Approval Threshold",
                "action": "Improve overall financial health by increasing revenue, reducing expenses, and maintaining positive cash flow",
                "priority": "Medium",
                "expected_impact": "+15-20 points"
            })
            improvement_plan["timeline"] = "3-6 months"
        else:
            recommendations.append({
                "issue": "Borderline Approval",
                "action": "Continue maintaining current financial performance and consider building additional revenue streams",
                "priority": "Low",
                "expected_impact": "+5-10 points"
            })
            improvement_plan["timeline"] = "1-3 months"
    
    improvement_plan["recommendations"] = recommendations
    
    # Add resources based on business type
    resources = [
        {
            "name": "Small Business Financial Management Guide",
            "type": "PDF Guide",
            "url": "https://example.com/financial-guide"
        },
        {
            "name": "Free Business Banking Consultation",
            "type": "Consultation",
            "url": "https://example.com/consultation"
        }
    ]
    
    business_type = business_profile.get("type", "")
    if business_type in ["grocery", "pharmacy", "retail"]:
        resources.append({
            "name": "Inventory Management Best Practices",
            "type": "Webinar",
            "url": "https://example.com/inventory-webinar"
        })
    
    if business_type in ["clinic", "childcare"]:
        resources.append({
            "name": "Service Business Cash Flow Management",
            "type": "Course",
            "url": "https://example.com/cashflow-course"
        })
    
    improvement_plan["resources"] = resources
    
    # Add summary
    if final_decision == "DENY":
        improvement_plan["summary"] = (
            f"Your application was denied primarily due to: {', '.join([r['issue'] for r in recommendations[:2]])}. "
            f"By following these recommendations over the next {improvement_plan['timeline']}, you could improve your score "
            f"from {auditor_score} to approximately {min(100, auditor_score + 30)}, increasing your chances of approval."
        )
    else:  # REFER
        improvement_plan["summary"] = (
            f"Your application requires manual review. To strengthen your application: {', '.join([r['issue'] for r in recommendations[:2]])}. "
            f"Addressing these items within {improvement_plan['timeline']} will improve your approval odds."
        )
    
    # Add log entry
    log = state.get("log", [])
    log.append({
        "agent": "coach",
        "message": f"Generated improvement plan with {len(recommendations)} recommendations",
        "reasoning": f"Analyzed {len(auditor_flags)} flags and provided actionable guidance for {final_decision} decision",
        "step": "coaching_complete"
    })
    
    return {
        "improvement_plan": improvement_plan,
        "log": log
    }

