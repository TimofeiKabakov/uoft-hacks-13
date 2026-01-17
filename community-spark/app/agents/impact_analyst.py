"""
Impact Analysis Agent

This agent evaluates the community impact potential of businesses.
Calculates a community multiplier (1.0-1.6) based on business characteristics
and community metrics that indicate positive community contribution.
"""

from typing import Dict, Any
import logging
from app.state import CommunitySparkState
from app.data.community_data import lookup_community_metrics
from app.maps.google_maps import geocode_address

logger = logging.getLogger(__name__)


def impact_node(state: CommunitySparkState) -> Dict[str, Any]:
    """
    Impact analysis node function for LangGraph.
    
    Analyzes business_profile to calculate community multiplier and impact summary.
    Expects business_profile to contain:
    - type: Business type/category
    - low_income_area: Boolean indicating if located in low-income area
    - nearest_competitor_miles: Distance to nearest competitor
    - hires_locally: Boolean indicating if business hires from local community
    - latitude/longitude (optional): Coordinates for location
    - address (optional): Address to geocode if coordinates not provided
    
    Args:
        state: Current workflow state containing business_profile
        
    Returns:
        Dict with updated state containing community_multiplier, impact_summary, and log entry
    """
    business_profile = state.get("business_profile", {})
    log = state.get("log", [])
    
    # Resolve coordinates: prefer user-selected, fallback to geocoding
    latitude = business_profile.get("latitude") or business_profile.get("lat")
    longitude = business_profile.get("longitude") or business_profile.get("lng") or business_profile.get("lon")
    coordinate_source = "unknown"
    
    if latitude is not None and longitude is not None:
        # Coordinates provided by user (from map selection)
        coordinate_source = "user_selection"
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            log.append({
                "agent": "impact_analyst",
                "message": f"Using user-selected coordinates: ({latitude:.6f}, {longitude:.6f})",
                "step": "coordinate_resolution"
            })
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid user-provided coordinates: {e}")
            latitude = None
            longitude = None
    
    # If no coordinates, try geocoding the address
    if latitude is None or longitude is None:
        address = business_profile.get("address")
        if address:
            try:
                coordinate_source = "geocoding"
                geocode_result = geocode_address(address)
                latitude = geocode_result["lat"]
                longitude = geocode_result["lng"]
                formatted_address = geocode_result["formatted_address"]
                
                # Update business_profile with geocoded coordinates
                business_profile["latitude"] = latitude
                business_profile["longitude"] = longitude
                business_profile["formatted_address"] = formatted_address
                
                log.append({
                    "agent": "impact_analyst",
                    "message": f"Geocoded address '{address}' to coordinates: ({latitude:.6f}, {longitude:.6f})",
                    "step": "coordinate_resolution"
                })
                logger.info(f"Geocoded address: {address} -> ({latitude}, {longitude})")
            except Exception as e:
                coordinate_source = "geocoding_failed"
                logger.warning(f"Failed to geocode address '{address}': {e}")
                log.append({
                    "agent": "impact_analyst",
                    "message": f"Warning: Failed to geocode address '{address}'. Using default community metrics.",
                    "step": "coordinate_resolution"
                })
        else:
            log.append({
                "agent": "impact_analyst",
                "message": "No coordinates or address provided. Using default community metrics based on zip code only.",
                "step": "coordinate_resolution"
            })
    
    # Extract profile fields
    business_type = business_profile.get("type", "unknown")
    nearest_competitor_miles = business_profile.get("nearest_competitor_miles", 999)
    hires_locally = business_profile.get("hires_locally", False)
    
    # Lookup community metrics from zip code or location
    community_metrics = lookup_community_metrics(business_profile)
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
    
    # Generate impact summary
    summary_parts = [f"Community multiplier: {community_multiplier}x"]
    
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
    
    # Build log message mentioning community metrics used and coordinate source
    metrics_used = ", ".join(applied_metrics) if applied_metrics else "standard metrics"
    log.append({
        "agent": "impact_analyst",
        "message": f"Completed impact analysis. Community multiplier: {community_multiplier}x. Metrics used: {metrics_used}. Coordinates from: {coordinate_source}",
        "step": "impact_analysis_complete"
    })
    
    return {
        "community_multiplier": community_multiplier,
        "impact_summary": impact_summary,
        "business_profile": business_profile,  # Include updated profile with geocoded coords if applicable
        "log": log
    }

