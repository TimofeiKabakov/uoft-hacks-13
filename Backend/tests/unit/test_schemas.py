import pytest
from pydantic import ValidationError
from app.models.schemas import (
    ApplicationCreate,
    PlaidConnect,
    LocationData,
    FinancialMetricsResponse,
    AssessmentResponse
)


def test_application_create_valid():
    """Test ApplicationCreate schema with valid data"""
    data = ApplicationCreate(
        job="Coffee shop owner",
        age=32,
        location=LocationData(
            lat=43.6532,
            lng=-79.3832,
            address="123 Main St"
        ),
        loan_amount=50000.0,
        loan_purpose="Equipment purchase"
    )

    assert data.job == "Coffee shop owner"
    assert data.age == 32
    assert data.loan_amount == 50000.0


def test_application_create_invalid_age():
    """Test ApplicationCreate rejects invalid age"""
    with pytest.raises(ValidationError):
        ApplicationCreate(
            job="Business",
            age=15,  # Too young
            location=LocationData(lat=43.0, lng=-79.0, address="Test"),
            loan_amount=10000.0,
            loan_purpose="Test"
        )


def test_plaid_connect_schema():
    """Test PlaidConnect schema"""
    data = PlaidConnect(plaid_public_token="public-sandbox-123")
    assert data.plaid_public_token == "public-sandbox-123"
