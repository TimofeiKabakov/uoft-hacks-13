"""
Community Data Lookup Module

Provides lookup functionality for community metrics based on zip code
or geographic coordinates.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


# Load community metrics data
def _load_community_metrics() -> Dict[str, Any]:
    """
    Load community metrics from JSON file.
    
    Returns:
        Dict mapping zip codes/region IDs to community metrics
    """
    # Get the path to the data directory (parent of app/)
    current_dir = Path(__file__).parent.parent.parent
    data_file = current_dir / "data" / "community_zip_metrics.json"
    
    if not data_file.exists():
        return {}
    
    with open(data_file, 'r') as f:
        return json.load(f)


# Cache the loaded data
_COMMUNITY_METRICS = _load_community_metrics()


def _create_lat_lon_bucket(lat: float, lon: float, precision: int = 1) -> str:
    """
    Create a bucket key from lat/lon coordinates.
    
    Rounds coordinates to specified decimal precision to create
    geographic buckets (e.g., "40.7,-73.9" for NYC area).
    
    Args:
        lat: Latitude
        lon: Longitude
        precision: Decimal places to round to (default: 1 = ~11km buckets)
        
    Returns:
        String key like "40.7,-73.9"
    """
    return f"{round(lat, precision)},{round(lon, precision)}"


def lookup_community_metrics(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lookup community metrics for a business profile.
    
    Uses zip_code if available, otherwise falls back to lat/lon bucket.
    Returns default values if no match is found.
    
    Args:
        profile: Business profile dict containing:
            - zip_code (str, optional): Zip code
            - latitude (float, optional): Business latitude
            - longitude (float, optional): Business longitude
    
    Returns:
        Dict with community metrics:
        {
            "low_income_area": bool,
            "food_desert": bool,
            "local_hiring_rate": float,
            "nearest_grocery_miles": float,
            "nearest_pharmacy_miles": float
        }
    """
    # Default values if no match found
    default_metrics = {
        "low_income_area": False,
        "food_desert": False,
        "local_hiring_rate": 0.5,
        "nearest_grocery_miles": 1.0,
        "nearest_pharmacy_miles": 0.8
    }
    
    # Try zip code first
    zip_code = profile.get("zip_code") or profile.get("zip")
    if zip_code:
        # Convert to string and try lookup
        zip_str = str(zip_code).strip()
        if zip_str in _COMMUNITY_METRICS:
            return _COMMUNITY_METRICS[zip_str]
    
    # Fallback to lat/lon bucket
    lat = profile.get("latitude") or profile.get("lat")
    lon = profile.get("longitude") or profile.get("lon") or profile.get("lng")
    
    if lat is not None and lon is not None:
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            bucket_key = _create_lat_lon_bucket(lat_float, lon_float)
            
            # Try to find matching bucket (may need to check nearby buckets)
            # For now, return default if exact match not found
            # In production, you'd implement nearest-neighbor lookup
            if bucket_key in _COMMUNITY_METRICS:
                return _COMMUNITY_METRICS[bucket_key]
        except (ValueError, TypeError):
            pass
    
    # No match found, return defaults
    return default_metrics

