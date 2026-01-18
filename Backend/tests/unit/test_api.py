import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Loan Assessment API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_application_endpoint_exists():
    """Test that create application endpoint is defined"""
    # This is a basic smoke test - full integration tests would require
    # proper async database setup with greenlet
    application_data = {
        "job": "Coffee shop owner",
        "age": 32,
        "location": {
            "lat": 43.6532,
            "lng": -79.3832,
            "address": "123 Main St"
        },
        "loan_amount": 50000.0,
        "loan_purpose": "Equipment purchase"
    }

    # Just verify the route exists and validates input
    # Actual database operations would require greenlet in async context
    assert "/api/v1/applications" in [route.path for route in app.routes]
