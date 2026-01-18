import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.plaid_service import PlaidService
from datetime import datetime, timedelta


@pytest.fixture
def plaid_service():
    """Create PlaidService instance"""
    return PlaidService()


@pytest.fixture
def mock_plaid_client():
    """Mock Plaid client"""
    return MagicMock()


def test_exchange_public_token_success(plaid_service):
    """Test successful public token exchange"""
    with patch('plaid.ApiClient') as mock_client, \
         patch('plaid.api.plaid_api.PlaidApi') as mock_plaid_api:

        # Setup mock
        mock_api_instance = MagicMock()
        mock_plaid_api.return_value = mock_api_instance

        mock_api_instance.item_public_token_exchange.return_value = {
            'access_token': 'access-sandbox-123',
            'item_id': 'item-123'
        }

        # Execute
        result = plaid_service.exchange_public_token("public-sandbox-123")

        # Verify
        assert result == "access-sandbox-123"


def test_get_transactions_success(plaid_service):
    """Test successful transaction retrieval"""
    with patch('plaid.ApiClient') as mock_client, \
         patch('plaid.api.plaid_api.PlaidApi') as mock_plaid_api:

        # Setup mock
        mock_api_instance = MagicMock()
        mock_plaid_api.return_value = mock_api_instance

        mock_api_instance.transactions_get.return_value = {
            'transactions': [
                {
                    'transaction_id': 'tx1',
                    'amount': 100.0,
                    'date': '2024-01-01',
                    'name': 'Test Transaction',
                    'category': ['Food']
                }
            ]
        }

        # Execute
        result = plaid_service.get_transactions(
            access_token="access-sandbox-123",
            start_date=datetime.now() - timedelta(days=180),
            end_date=datetime.now()
        )

        # Verify
        assert 'transactions' in result
        assert len(result['transactions']) == 1


def test_get_balance_success(plaid_service):
    """Test successful balance retrieval"""
    with patch('plaid.ApiClient') as mock_client, \
         patch('plaid.api.plaid_api.PlaidApi') as mock_plaid_api:

        # Setup mock
        mock_api_instance = MagicMock()
        mock_plaid_api.return_value = mock_api_instance

        mock_api_instance.accounts_balance_get.return_value = {
            'accounts': [
                {
                    'account_id': 'acc1',
                    'balances': {
                        'current': 1000.0,
                        'available': 950.0
                    },
                    'type': 'depository'
                }
            ]
        }

        # Execute
        result = plaid_service.get_balance("access-sandbox-123")

        # Verify
        assert 'accounts' in result
        assert len(result['accounts']) == 1


def test_get_income_success(plaid_service):
    """Test successful income retrieval"""
    with patch('plaid.ApiClient') as mock_client, \
         patch('plaid.api.plaid_api.PlaidApi') as mock_plaid_api:

        # Setup mock
        mock_api_instance = MagicMock()
        mock_plaid_api.return_value = mock_api_instance

        mock_api_instance.income_get.return_value = {
            'income': {
                'income_streams': [
                    {
                        'monthly_income': 5000.0,
                        'confidence': 0.95
                    }
                ]
            }
        }

        # Execute
        result = plaid_service.get_income("access-sandbox-123")

        # Verify
        assert 'income' in result
