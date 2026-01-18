from langchain.tools import Tool
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.services.plaid_service import PlaidService
from app.services.google_service import GoogleService
from app.services.financial_calculator import FinancialCalculator


def get_financial_data_tool(access_token: str) -> Dict[str, Any]:
    """
    Tool for retrieving and analyzing financial data from Plaid

    Args:
        access_token: Plaid access token

    Returns:
        Dictionary with financial metrics
    """
    plaid_service = PlaidService()
    calculator = FinancialCalculator()

    # Get data from Plaid
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    transactions = plaid_service.get_transactions(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )

    balance_data = plaid_service.get_balance(access_token)

    # Calculate metrics
    metrics = calculator.calculate_all_metrics(
        transactions=transactions.get('transactions', []),
        balance_data=balance_data
    )

    return metrics


def analyze_market_tool(
    lat: float,
    lng: float,
    business_type: str
) -> Dict[str, Any]:
    """
    Tool for analyzing market conditions and competition

    Args:
        lat: Latitude
        lng: Longitude
        business_type: Type of business

    Returns:
        Dictionary with market analysis
    """
    google_service = GoogleService()

    # Get nearby businesses
    nearby = google_service.get_nearby_businesses(
        lat=lat,
        lng=lng,
        business_type=business_type,
        radius=3200  # 2 miles in meters
    )

    # Analyze density
    density = google_service.analyze_market_density(
        nearby_businesses=nearby,
        radius_miles=2.0
    )

    # Calculate viability score
    competitor_count = len(nearby)

    # Simple viability scoring
    if density == "low":
        viability = 85.0
    elif density == "medium":
        viability = 65.0
    else:
        viability = 40.0

    return {
        'competitor_count': competitor_count,
        'market_density': density,
        'viability_score': viability,
        'nearby_businesses': nearby[:10],  # Top 10
        'market_insights': f"Found {competitor_count} competitors in 2-mile radius. Market density is {density}."
    }


def create_tools() -> List[Tool]:
    """
    Create LangChain tools for agent use

    Returns:
        List of configured tools
    """
    # Note: These tools will be wrapped with partial application of parameters
    # when used in the actual agent workflow

    financial_tool = Tool(
        name="get_financial_data",
        description=(
            "Retrieves and analyzes financial data from Plaid API. "
            "Returns metrics like income, expenses, debt-to-income ratio, "
            "savings rate, and income stability. "
            "Input should be a Plaid access token."
        ),
        func=lambda x: get_financial_data_tool(x)
    )

    market_tool = Tool(
        name="analyze_market",
        description=(
            "Analyzes market conditions for a business location. "
            "Returns competitor count, market density, viability score, "
            "and nearby businesses. "
            "Input should be a JSON string with keys: lat, lng, business_type."
        ),
        func=lambda x: analyze_market_tool(**eval(x))
    )

    return [financial_tool, market_tool]
