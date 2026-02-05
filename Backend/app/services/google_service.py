import googlemaps
from typing import List, Dict, Any, Optional
from math import radians, sin, cos, sqrt, atan2
from app.core.config import get_settings

settings = get_settings()


class GoogleService:
    """Service for interacting with Google Maps/Places API"""

    def __init__(self):
        self.maps_client = None
        self.places_client = None
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    def _get_maps_client(self):
        """Lazy initialization of Google Maps client"""
        if not self.maps_client:
            self.maps_client = googlemaps.Client(key=self.api_key)
        return self.maps_client

    def _get_places_client(self):
        """Lazy initialization of Google Places client"""
        if not self.places_client:
            self.places_client = googlemaps.Client(key=settings.GOOGLE_PLACES_API_KEY)
        return self.places_client

    def get_nearby_businesses(
        self,
        lat: float,
        lng: float,
        business_type: str,
        radius: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Find nearby businesses of a specific type

        Args:
            lat: Latitude
            lng: Longitude
            business_type: Type of business (e.g., 'cafe', 'restaurant')
            radius: Search radius in meters (default 2000m)

        Returns:
            List of nearby businesses with details
        """
        client = self._get_places_client()

        response = client.places_nearby(
            location=(lat, lng),
            radius=radius,
            type=business_type
        )

        businesses = []
        for place in response.get('results', []):
            # Calculate distance from center point
            place_lat = place['geometry']['location']['lat']
            place_lng = place['geometry']['location']['lng']
            distance = self.calculate_distance_miles(lat, lng, place_lat, place_lng)

            businesses.append({
                'name': place.get('name', 'Unknown'),
                'type': place.get('types', [business_type])[0] if place.get('types') else business_type,
                'rating': place.get('rating'),
                'distance_miles': round(distance, 2),
                'lat': place_lat,
                'lng': place_lng
            })

        return businesses

    def analyze_market_density(
        self,
        nearby_businesses: List[Dict],
        radius_miles: float
    ) -> str:
        """
        Analyze market density based on number of competitors

        Args:
            nearby_businesses: List of nearby businesses
            radius_miles: Search radius in miles

        Returns:
            Density level: 'low', 'medium', or 'high'
        """
        count = len(nearby_businesses)

        # Thresholds based on 1-mile radius
        # Adjust proportionally for different radii
        normalized_count = count * (1.0 / radius_miles)

        if normalized_count < 5:
            return "low"
        elif normalized_count < 12:
            return "medium"
        else:
            return "high"

    def calculate_distance_miles(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula

        Args:
            lat1, lng1: First coordinate
            lat2, lng2: Second coordinate

        Returns:
            Distance in miles
        """
        # Earth radius in miles
        R = 3959.0

        # Convert to radians
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    def places_autocomplete(
        self, input_text: str, session_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Place autocomplete predictions for address search.

        Args:
            input_text: The text string on which to search.
            session_token: Optional session token for billing.

        Returns:
            List of predictions (place_id, description, structured_formatting, etc.)
        """
        client = self._get_places_client()
        return client.places_autocomplete(
            input_text,
            session_token=session_token,
            types="address",
        )

    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to address.

        Returns:
            First result with formatted_address and address_components, or None.
        """
        client = self._get_maps_client()
        results = client.reverse_geocode((lat, lng))
        if not results:
            return None
        return results[0]

    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Convert address to coordinates

        Args:
            address: Street address

        Returns:
            Dictionary with 'lat' and 'lng' keys, or None if not found
        """
        client = self._get_maps_client()

        result = client.geocode(address)

        if result:
            location = result[0]['geometry']['location']
            return {
                'lat': location['lat'],
                'lng': location['lng']
            }

        return None

    def get_place_details(
        self, place_id: str, session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a place (formatted_address, geometry, address_components).

        Args:
            place_id: Google Places ID
            session_token: Optional session token (use same as autocomplete for billing)

        Returns:
            Place details (result dict from API)
        """
        client = self._get_places_client()
        result = client.place(
            place_id,
            session_token=session_token,
            fields=["formatted_address", "geometry", "address_component"],
        )
        data = result.get("result", {})
        # API/library may return address_component (singular); frontend expects address_components
        if "address_components" not in data and "address_component" in data:
            data = dict(data)
            data["address_components"] = data.pop("address_component", [])
        return data
