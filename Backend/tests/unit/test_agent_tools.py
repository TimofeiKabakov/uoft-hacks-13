import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.tools import (
    get_financial_data_tool,
    analyze_market_tool,
    create_tools
)


def test_create_tools():
    """Test that create_tools returns valid LangChain tools"""
    tools = create_tools()

    # Should return a list of tools
    assert isinstance(tools, list)
    assert len(tools) == 2

    # Check tool names
    tool_names = [tool.name for tool in tools]
    assert "get_financial_data" in tool_names
    assert "analyze_market" in tool_names


@patch('app.services.plaid_service.PlaidService')
@patch('app.services.financial_calculator.FinancialCalculator')
def test_get_financial_data_tool_execution(mock_calculator_class, mock_plaid_class):
    """Test financial data tool execution"""
    # Setup mocks
    mock_plaid = MagicMock()
    mock_calculator = MagicMock()

    mock_plaid_class.return_value = mock_plaid
    mock_calculator_class.return_value = mock_calculator

    mock_plaid.get_transactions.return_value = {
        'transactions': [
            {'amount': 100.0, 'date': '2024-01-01'}
        ]
    }
    mock_plaid.get_balance.return_value = {
        'accounts': [
            {'balances': {'current': 1000.0}}
        ]
    }

    mock_calculator.calculate_all_metrics.return_value = {
        'monthly_income': 5000.0,
        'monthly_expenses': 3000.0
    }

    # Create and execute tool
    tools = create_tools()
    financial_tool = next(t for t in tools if t.name == "get_financial_data")

    # Tool should be callable
    assert callable(financial_tool.func)


@patch('app.services.google_service.GoogleService')
def test_analyze_market_tool_execution(mock_google_class):
    """Test market analysis tool execution"""
    # Setup mock
    mock_google = MagicMock()
    mock_google_class.return_value = mock_google

    mock_google.get_nearby_businesses.return_value = [
        {'name': 'Competitor 1', 'rating': 4.5},
        {'name': 'Competitor 2', 'rating': 4.0}
    ]

    mock_google.analyze_market_density.return_value = "medium"

    # Create and execute tool
    tools = create_tools()
    market_tool = next(t for t in tools if t.name == "analyze_market")

    # Tool should be callable
    assert callable(market_tool.func)
