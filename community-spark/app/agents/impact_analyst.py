"""
Impact Analysis Agent (Hybrid)

This agent evaluates the community impact potential of businesses.
Uses hybrid approach: deterministic community metrics + LLM reasoning.
"""

from typing import Dict, Any
from app.state import CommunitySparkState
from app.data.community_data import lookup_community_metrics
from app.utils.openai_helper import llm_impact_decision


def impact_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Impact analysis node function for LangGraph.
    
    Uses hybrid approach: deterministic community metrics + LLM reasoning.
    Falls back to rule-based if LLM unavailable.
    
    Args:
        state: Current workflow state containing business_profile and auditor_score
        
    Returns:
        Dict with updated state containing community_multiplier, impact_summary, and log entry
    """
    business_profile = state.get("business_profile", {})
    auditor_score = state.get("auditor_score", 50)
    
    # Lookup community metrics from zip code or location
    community_metrics = lookup_community_metrics(business_profile)
    
    # Try hybrid LLM-powered decision first
    llm_result = llm_impact_decision(business_profile, community_metrics, auditor_score)
    
    if llm_result:
        # Hybrid decision (deterministic base + LLM reasoning)
        community_multiplier = llm_result["community_multiplier"]
        impact_summary = llm_result["reasoning"]
        applied_factors = llm_result["applied_factors"]
        method = llm_result.get("method", "hybrid")
        
        log = state.get("log", [])
        
        # Build detailed log message
        if method == "hybrid":
            base = llm_result.get("deterministic_base", 1.0)
            message = f"Hybrid impact analysis complete. Multiplier: {community_multiplier:.2f}x (base: {base:.2f}x). Factors: {len(applied_factors)}"
        else:
            message = f"Impact analysis complete. Multiplier: {community_multiplier:.2f}x"
        
        log.append({
            "agent": "impact_analyst",
            "message": message,
            "reasoning": impact_summary,
            "decision": community_multiplier,
            "applied_factors": applied_factors,
            "method": method,
            "step": "impact_analysis_complete"
        })
        
        return {
            "community_multiplier": community_multiplier,
            "impact_summary": impact_summary,
            "log": log
        }
    
    # Fallback to rule-based logic if LLM unavailable
    else:
        # Extract profile fields
        business_type = business_profile.get("type", "unknown")
        nearest_competitor_miles = business_profile.get("nearest_competitor_miles", 999)
        hires_locally = business_profile.get("hires_locally", False)
        
        low_income_area = community_metrics.get("low_income_area", False)
        food_desert = community_metrics.get("food_desert", False)
        local_hiring_rate = community_metrics.get("local_hiring_rate", 0.5)
        nearest_grocery_miles = community_metrics.get("nearest_grocery_miles", 1.0)
        nearest_pharmacy_miles = community_metrics.get("nearest_pharmacy_miles", 0.8)
        
        # Calculate community_multiplier (starts at 1.0, max 1.6)
        multiplier = 1.0
        applied_metrics = []
        
        # Low-income area bonus (+0.2)
        if low_income_area:
            multiplier += 0.2
            applied_metrics.append("low_income_area")
        
        # Food desert bonus (+0.20)
        if food_desert:
            multiplier += 0.20
            applied_metrics.append("food_desert")
        
        # Grocery distance bonus for grocery-type businesses (+0.10 if >= 5 miles)
        grocery_types = ["grocery", "supermarket", "food", "market", "retail"]
        if any(grocery_type in business_type.lower() for grocery_type in grocery_types):
            if nearest_grocery_miles >= 5:
                multiplier += 0.10
                applied_metrics.append("high_grocery_distance")
        
        # Pharmacy distance bonus for pharmacy-type businesses (+0.10 if >= 5 miles)
        pharmacy_types = ["pharmacy", "drugstore", "health"]
        if any(pharmacy_type in business_type.lower() for pharmacy_type in pharmacy_types):
            if nearest_pharmacy_miles >= 5:
                multiplier += 0.10
                applied_metrics.append("high_pharmacy_distance")
        
        # Local hiring rate bonus (+0.05 if >= 0.6)
        if local_hiring_rate >= 0.6:
            multiplier += 0.05
            applied_metrics.append("high_local_hiring_rate")
        
        # Local hiring bonus from profile (+0.15) - keep existing logic
        if hires_locally:
            multiplier += 0.15
            applied_metrics.append("hires_locally")
        
        # Market need bonus (less competition = more need, up to +0.15)
        if nearest_competitor_miles > 10:
            multiplier += 0.15
            applied_metrics.append("low_competition")
        elif nearest_competitor_miles > 5:
            multiplier += 0.1
            applied_metrics.append("moderate_competition")
        elif nearest_competitor_miles > 2:
            multiplier += 0.05
        
        # Business type bonus for community-focused types (+0.1)
        community_types = ["nonprofit", "cooperative", "social_enterprise", "community_center", "food_bank"]
        if business_type.lower() in community_types:
            multiplier += 0.1
            applied_metrics.append("community_focused_type")
        
        # Clamp to 1.0-1.6 range
        community_multiplier = round(max(1.0, min(1.6, multiplier)), 2)
        
        # Generate impact summary (rule-based fallback)
        summary_parts = [f"Community multiplier: {community_multiplier}x (rule-based fallback)"]
        
        if low_income_area:
            summary_parts.append("Located in low-income area - supports underserved community")
        
        if food_desert:
            summary_parts.append("Located in food desert - addresses critical community need")
        
        if any(grocery_type in business_type.lower() for grocery_type in grocery_types) and nearest_grocery_miles >= 5:
            summary_parts.append(f"Grocery business in area with limited access (nearest: {nearest_grocery_miles} miles)")
        
        if any(pharmacy_type in business_type.lower() for pharmacy_type in pharmacy_types) and nearest_pharmacy_miles >= 5:
            summary_parts.append(f"Pharmacy business in area with limited access (nearest: {nearest_pharmacy_miles} miles)")
        
        if local_hiring_rate >= 0.6:
            summary_parts.append(f"High local hiring rate ({local_hiring_rate:.0%}) - strengthens local employment")
        
        if hires_locally:
            summary_parts.append("Hires locally - strengthens local employment")
        
        if nearest_competitor_miles > 5:
            summary_parts.append("Serves area with limited competition - fills market gap")
        
        if business_type.lower() in community_types:
            summary_parts.append(f"Community-focused business type: {business_type}")
        
        if community_multiplier <= 1.1:
            summary_parts.append("Standard community impact expected")
        
        impact_summary = ". ".join(summary_parts) + "."
        
        # Get existing log or initialize empty list
        log = state.get("log", [])
        
        # Build log message mentioning community metrics used
        metrics_used = ", ".join(applied_metrics) if applied_metrics else "standard metrics"
        log.append({
            "agent": "impact_analyst",
            "message": f"Rule-based impact analysis complete. Community multiplier: {community_multiplier}x. Metrics used: {metrics_used}",
            "reasoning": impact_summary,
            "decision": community_multiplier,
            "method": "rule-based",
            "step": "impact_analysis_complete"
        })
        
        return {
            "community_multiplier": community_multiplier,
            "impact_summary": impact_summary,
            "log": log
        }

