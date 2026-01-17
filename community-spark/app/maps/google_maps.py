"""
Google Maps API integration for geocoding and location services.
"""

import os
import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def geocode_address(address: str) -> Dict[str, any]:
    """
    Geocode an address using Google Geocoding API.
    
    Args:
        address: The address string to geocode
        
    Returns:
        Dictionary containing:
        - lat: float - Latitude
        - lng: float - Longitude
        - formatted_address: str - Formatted address from Google
        
    Raises:
        ValueError: If address is empty or invalid
        RuntimeError: If geocoding fails or API key is missing
    """
    if not address or not address.strip():
        raise ValueError("Address cannot be empty")
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_MAPS_BACKEND_KEY")
    if not api_key:
        logger.error("GOOGLE_MAPS_BACKEND_KEY environment variable not set")
        raise RuntimeError("Google Maps API key not configured")
    
    # Prepare request to Google Geocoding API
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Check for HTTP errors
        if response.status_code != 200:
            logger.error(f"Google Geocoding API returned status {response.status_code}: {response.text}")
            raise RuntimeError(f"Geocoding API request failed with status {response.status_code}")
        
        data = response.json()
        
        # Check API response status
        if data.get("status") != "OK":
            error_message = data.get("error_message", data.get("status", "Unknown error"))
            logger.error(f"Google Geocoding API error: {error_message}")
            
            if data.get("status") == "ZERO_RESULTS":
                raise ValueError(f"No results found for address: {address}")
            elif data.get("status") == "INVALID_REQUEST":
                raise ValueError(f"Invalid geocoding request: {error_message}")
            else:
                raise RuntimeError(f"Geocoding failed: {error_message}")
        
        # Extract first result
        results = data.get("results", [])
        if not results:
            raise ValueError(f"No results found for address: {address}")
        
        first_result = results[0]
        geometry = first_result.get("geometry", {})
        location = geometry.get("location", {})
        
        if not location or "lat" not in location or "lng" not in location:
            raise RuntimeError("Invalid response structure from Geocoding API")
        
        return {
            "lat": float(location["lat"]),
            "lng": float(location["lng"]),
            "formatted_address": first_result.get("formatted_address", address)
        }
        
    except requests.RequestException as e:
        logger.error(f"Network error during geocoding: {e}")
        raise RuntimeError(f"Network error: {str(e)}")
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing geocoding response: {e}")
        raise RuntimeError(f"Failed to parse geocoding response: {str(e)}")

