import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.graph import (
    AgentState,
    create_assessment_graph,
    financial_agent,
    market_agent,
    decision_agent
)


def test_agent_state_creation():
    """Test AgentState creation"""
    state = AgentState(
        application_id="test-123",
        access_token="token-123",
        user_job="cafe owner",
        location_lat=43.6532,
        location_lng=-79.3832,
        loan_amount=50000.0,
        financial_metrics={},
        market_analysis={},
        final_assessment=None,
        messages=[]
    )

    assert state['application_id'] == "test-123"
    assert state['user_job'] == "cafe owner"


@patch('app.agents.graph.PlaidService')
@patch('app.agents.graph.FinancialCalculator')
def test_financial_agent(mock_calculator_class, mock_plaid_class):
    """Test financial agent node"""
    # Setup mocks
    mock_plaid = MagicMock()
    mock_calculator = MagicMock()

    mock_plaid_class.return_value = mock_plaid
    mock_calculator_class.return_value = mock_calculator

    mock_plaid.get_transactions.return_value = {
        'transactions': []
    }
    mock_plaid.get_balance.return_value = {
        'accounts': []
    }

    mock_calculator.calculate_all_metrics.return_value = {
        'monthly_income': 5000.0,
        'monthly_expenses': 3000.0,
        'debt_to_income_ratio': 20.0,
        'savings_rate': 40.0,
        'avg_monthly_balance': 2000.0,
        'min_balance_6mo': 1000.0,
        'overdraft_count': 0,
        'income_stability_score': 85.0
    }

    # Create state
    state = AgentState(
        application_id="test-123",
        access_token="token-123",
        user_job="cafe owner",
        location_lat=43.6532,
        location_lng=-79.3832,
        loan_amount=50000.0,
        financial_metrics={},
        market_analysis={},
        final_assessment=None,
        messages=[]
    )

    # Execute agent
    result = financial_agent(state)

    # Verify financial_metrics was populated
    assert 'financial_metrics' in result
    assert result['financial_metrics']['monthly_income'] == 5000.0


@patch('app.agents.graph.GoogleService')
def test_market_agent(mock_google_class):
    """Test market agent node"""
    # Setup mock
    mock_google = MagicMock()
    mock_google_class.return_value = mock_google

    mock_google.get_nearby_businesses.return_value = [
        {'name': 'Competitor 1', 'rating': 4.5, 'distance_miles': 0.5, 'type': 'cafe'},
        {'name': 'Competitor 2', 'rating': 4.0, 'distance_miles': 1.0, 'type': 'cafe'}
    ]

    mock_google.analyze_market_density.return_value = "medium"

    # Create state
    state = AgentState(
        application_id="test-123",
        access_token="token-123",
        user_job="cafe owner",
        location_lat=43.6532,
        location_lng=-79.3832,
        loan_amount=50000.0,
        financial_metrics={},
        market_analysis={},
        final_assessment=None,
        messages=[]
    )

    # Execute agent
    result = market_agent(state)

    # Verify market_analysis was populated
    assert 'market_analysis' in result
    assert result['market_analysis']['competitor_count'] == 2


def test_create_assessment_graph():
    """Test graph creation"""
    graph = create_assessment_graph()

    # Graph should be created successfully
    assert graph is not None
