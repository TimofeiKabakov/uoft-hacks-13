"""
Unit tests for Orchestrator
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os

# Set test environment variables before importing app modules
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'
os.environ['PLAID_CLIENT_ID'] = 'test-plaid-client'
os.environ['PLAID_SECRET'] = 'test-plaid-secret'
os.environ['GOOGLE_MAPS_API_KEY'] = 'test-maps-key'
os.environ['GOOGLE_PLACES_API_KEY'] = 'test-places-key'
os.environ['ENCRYPTION_KEY'] = 'test-encryption-key-32bytes!!'
os.environ['PLAID_ENV'] = 'sandbox'

from app.agents.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initializes with all agents"""
    orchestrator = Orchestrator()

    assert orchestrator.financial_analyst is not None
    assert orchestrator.market_researcher is not None
    assert orchestrator.risk_assessor is not None


@pytest.mark.asyncio
async def test_orchestrator_run_assessment_success():
    """Test successful orchestrator execution"""
    orchestrator = Orchestrator()

    # Mock agent responses
    mock_financial = {
        'success': True,
        'monthly_income': 5000.0,
        'monthly_expenses': 3000.0,
        'debt_to_income_ratio': 25.0,
        'savings_rate': 15.0,
        'financial_health_score': 75.0,
        'key_findings': ['Good income'],
        'concerns': [],
        'strengths': ['Strong savings']
    }

    mock_market = {
        'success': True,
        'competitor_count': 5,
        'market_density': 'medium',
        'viability_score': 70.0,
        'market_insights': 'Balanced market',
        'opportunities': ['Room for growth'],
        'risks': [],
        'recommendations': []
    }

    mock_risk = {
        'success': True,
        'eligibility': 'approved',
        'confidence_score': 85.0,
        'risk_level': 'low',
        'reasoning': 'Strong financials and good market',
        'recommendations': ['Proceed with loan'],
        'key_factors': {
            'financial_score': 75.0,
            'market_score': 70.0,
            'overall_score': 72.5
        }
    }

    # Patch the agent methods
    orchestrator.financial_analyst.analyze = AsyncMock(return_value=mock_financial)
    orchestrator.market_researcher.analyze = AsyncMock(return_value=mock_market)
    orchestrator.risk_assessor.assess = AsyncMock(return_value=mock_risk)

    # Run assessment
    result = await orchestrator.run_assessment(
        application_id='test-123',
        access_token='fake-token',
        user_job='Coffee shop owner',
        user_age=35,
        location_lat=43.6532,
        location_lng=-79.3832,
        loan_amount=50000.0,
        loan_purpose='Equipment'
    )

    # Verify results
    assert result['success'] is True
    assert result['application_id'] == 'test-123'
    assert result['financial_metrics'] == mock_financial
    assert result['market_analysis'] == mock_market
    assert result['final_assessment'] == mock_risk
    assert 'metadata' in result
    assert result['metadata']['parallel_execution'] is True
    assert result['metadata']['processing_time_seconds'] >= 0


@pytest.mark.asyncio
async def test_orchestrator_handles_financial_analyst_error():
    """Test orchestrator handles financial analyst errors gracefully"""
    orchestrator = Orchestrator()

    mock_market = {
        'success': True,
        'competitor_count': 5,
        'market_density': 'medium',
        'viability_score': 70.0
    }

    mock_risk = {
        'success': True,
        'eligibility': 'review',
        'confidence_score': 50.0,
        'risk_level': 'medium',
        'reasoning': 'Needs review',
        'recommendations': []
    }

    # Financial analyst raises exception
    orchestrator.financial_analyst.analyze = AsyncMock(side_effect=Exception("Plaid error"))
    orchestrator.market_researcher.analyze = AsyncMock(return_value=mock_market)
    orchestrator.risk_assessor.assess = AsyncMock(return_value=mock_risk)

    # Run assessment
    result = await orchestrator.run_assessment(
        application_id='test-123',
        access_token='fake-token',
        user_job='Coffee shop owner',
        user_age=35,
        location_lat=43.6532,
        location_lng=-79.3832,
        loan_amount=50000.0,
        loan_purpose='Equipment'
    )

    # Should still succeed with default financial metrics
    assert result['success'] is True
    assert result['financial_metrics']['success'] is False
    assert 'error' in result['financial_metrics']
    assert 'Plaid error' in result['financial_metrics']['error']


@pytest.mark.asyncio
async def test_orchestrator_parallel_execution():
    """Test that financial and market agents run in parallel"""
    orchestrator = Orchestrator()

    # Track execution order
    execution_order = []

    async def mock_financial(*args, **kwargs):
        execution_order.append('financial_start')
        # Simulate some work
        import asyncio
        await asyncio.sleep(0.01)
        execution_order.append('financial_end')
        return {'success': True, 'monthly_income': 5000.0}

    async def mock_market(*args, **kwargs):
        execution_order.append('market_start')
        # Simulate some work
        import asyncio
        await asyncio.sleep(0.01)
        execution_order.append('market_end')
        return {'success': True, 'competitor_count': 5}

    async def mock_risk(*args, **kwargs):
        execution_order.append('risk')
        return {'success': True, 'eligibility': 'approved'}

    orchestrator.financial_analyst.analyze = mock_financial
    orchestrator.market_researcher.analyze = mock_market
    orchestrator.risk_assessor.assess = mock_risk

    # Run assessment
    await orchestrator.run_assessment(
        application_id='test-123',
        access_token='fake-token',
        user_job='Coffee shop owner',
        user_age=35,
        location_lat=43.6532,
        location_lng=-79.3832,
        loan_amount=50000.0,
        loan_purpose='Equipment'
    )

    # Both should start before either ends (parallel execution)
    financial_start_idx = execution_order.index('financial_start')
    market_start_idx = execution_order.index('market_start')
    financial_end_idx = execution_order.index('financial_end')
    market_end_idx = execution_order.index('market_end')
    risk_idx = execution_order.index('risk')

    # Both should start before either completes
    assert min(financial_start_idx, market_start_idx) < max(financial_end_idx, market_end_idx)

    # Risk should run after both complete
    assert risk_idx > max(financial_end_idx, market_end_idx)
