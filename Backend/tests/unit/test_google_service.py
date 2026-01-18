import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.google_service import GoogleService


@pytest.fixture
def google_service():
    """Create GoogleService instance"""
    return GoogleService()


def test_get_nearby_businesses_success(google_service):
    """Test successful nearby business retrieval"""
    with patch('googlemaps.Client') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.places_nearby.return_value = {
            'results': [
                {
                    'name': 'Starbucks',
                    'types': ['cafe', 'food'],
                    'rating': 4.5,
                    'geometry': {
                        'location': {
                            'lat': 43.6532,
                            'lng': -79.3832
                        }
                    }
                },
                {
                    'name': 'Second Cup',
                    'types': ['cafe'],
                    'rating': 4.2,
                    'geometry': {
                        'location': {
                            'lat': 43.6540,
                            'lng': -79.3840
                        }
                    }
                }
            ]
        }

        # Execute
        result = google_service.get_nearby_businesses(
            lat=43.6532,
            lng=-79.3832,
            business_type="cafe",
            radius=2000
        )

        # Verify
        assert len(result) == 2
        assert result[0]['name'] == 'Starbucks'
        assert result[0]['rating'] == 4.5


def test_analyze_market_density(google_service):
    """Test market density analysis"""
    businesses = [
        {'name': f'Business {i}'} for i in range(15)
    ]

    density = google_service.analyze_market_density(
        nearby_businesses=businesses,
        radius_miles=1.0
    )

    assert density == "high"


def test_calculate_distance_miles(google_service):
    """Test distance calculation"""
    # Toronto coordinates (approx 1 km apart)
    distance = google_service.calculate_distance_miles(
        lat1=43.6532,
        lng1=-79.3832,
        lat2=43.6620,
        lng2=-79.3950
    )

    # Should be approximately 0.6-0.7 miles
    assert 0.5 < distance < 1.0


def test_geocode_address_success(google_service):
    """Test successful address geocoding"""
    with patch('googlemaps.Client') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.geocode.return_value = [
            {
                'geometry': {
                    'location': {
                        'lat': 43.6532,
                        'lng': -79.3832
                    }
                }
            }
        ]

        # Execute
        result = google_service.geocode_address("123 Main St, Toronto")

        # Verify
        assert result['lat'] == 43.6532
        assert result['lng'] == -79.3832
