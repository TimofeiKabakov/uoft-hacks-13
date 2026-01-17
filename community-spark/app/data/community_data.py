"""
Community Data Lookup Module - Canada Only

Provides lookup functionality for community metrics for Canadian locations.

API-First Approach:
1. Statistics Canada API (real-time, free)
2. Static postal code data (fallback only)
3. Default values (last resort)

Note: Static JSON data is now used only as a fallback if live API fails.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


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


_COMMUNITY_METRICS = _load_community_metrics()

try:
    from app.utils.statcan_api import get_community_metrics_from_statcan
    STATCAN_API_AVAILABLE = True
except ImportError:
    STATCAN_API_AVAILABLE = False
    print("[INFO] StatCan API module not available - using static data only")

_statcan_cache: Dict[str, Dict[str, Any]] = {}


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
    Lookup community metrics for a Canadian business profile.
    
    Priority:
    1. Statistics Canada API (real-time, for Canadian coordinates)
    2. Static postal code data (fallback if API fails)
    3. Default values (last resort)
    
    Args:
        profile: Business profile dict containing:
            - zip_code or postal_code (str, optional): Canadian postal code
            - latitude (float, optional): Business latitude
            - longitude (float, optional): Business longitude
    
    Returns:
        Dict with community metrics:
        {
            "low_income_area": bool,
            "food_desert": bool,
            "local_hiring_rate": float,
            "nearest_grocery_miles": float,
            "nearest_pharmacy_miles": float,
            "source": str  # "statcan_estimated", "static_postal_fallback", "default"
        }
    """
    default_metrics = {
        "low_income_area": False,
        "food_desert": False,
        "local_hiring_rate": 0.5,
        "nearest_grocery_miles": 1.0,
        "nearest_pharmacy_miles": 0.8,
        "source": "default"
    }
    
    postal_code = profile.get("zip_code") or profile.get("zip") or profile.get("postal_code")
    lat = profile.get("latitude") or profile.get("lat")
    lon = profile.get("longitude") or profile.get("lon") or profile.get("lng")
    
    if lat is not None and lon is not None and STATCAN_API_AVAILABLE:
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            cache_key = f"{round(lat_float, 2)},{round(lon_float, 2)}"
            
            if cache_key in _statcan_cache:
                print(f"[INFO] Using cached StatCan data for {cache_key}")
                return _statcan_cache[cache_key]
            
            print(f"[INFO] Fetching Statistics Canada data for ({lat_float}, {lon_float})...")
            api_metrics = get_community_metrics_from_statcan(lat_float, lon_float)
            
            if api_metrics:
                result = default_metrics.copy()
                result.update(api_metrics)
                
                _statcan_cache[cache_key] = result
                
                print(f"[INFO] StatCan API success: Low-income={result['low_income_area']}, Median income=${result.get('median_income', 'N/A')} CAD")
                return result
            else:
                print(f"[WARNING] StatCan API failed for ({lat_float}, {lon_float})")
                
        except (ValueError, TypeError) as e:
            print(f"[WARNING] Invalid lat/lon values: {e}")
    
    if postal_code:
        postal_str = str(postal_code).strip()
        if postal_str in _COMMUNITY_METRICS:
            result = _COMMUNITY_METRICS[postal_str].copy()
            result["source"] = "static_postal_fallback"
            print(f"[INFO] Using static postal code fallback for {postal_str}")
            return result
    
    if lat is not None and lon is not None:
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            bucket_key = _create_lat_lon_bucket(lat_float, lon_float)
            
            if bucket_key in _COMMUNITY_METRICS:
                result = _COMMUNITY_METRICS[bucket_key].copy()
                result["source"] = "static_bucket_fallback"
                print(f"[INFO] Using static bucket fallback for {bucket_key}")
                return result
        except (ValueError, TypeError):
            pass
    
    print(f"[INFO] No community data found, using defaults")
    return default_metrics

