import pytest
from datetime import datetime
from app.database.models import Application, FinancialMetrics, MarketAnalysis, Assessment


def test_application_model_creation():
    """Test Application model can be instantiated"""
    app = Application(
        id="test-123",
        user_job="Coffee shop owner",
        user_age=32,
        location_lat=43.6532,
        location_lng=-79.3832,
        location_address="123 Main St",
        loan_amount=50000.0,
        loan_purpose="Equipment",
        status="pending_plaid"
    )

    assert app.user_job == "Coffee shop owner"
    assert app.user_age == 32
    assert app.status == "pending_plaid"


def test_financial_metrics_model_creation():
    """Test FinancialMetrics model can be instantiated"""
    metrics = FinancialMetrics(
        id="metrics-123",
        application_id="app-123",
        debt_to_income_ratio=28.5,
        savings_rate=22.3,
        monthly_income=5000.0
    )

    assert metrics.debt_to_income_ratio == 28.5
    assert metrics.application_id == "app-123"
