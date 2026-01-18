from datetime import datetime
from typing import Dict, Any, Optional
from app.core.config import get_settings

settings = get_settings()


class PlaidService:
    """Service for interacting with Plaid API"""

    def __init__(self):
        # Plaid client will be initialized when needed
        # This is a simplified version for testing
        self.client_id = settings.PLAID_CLIENT_ID
        self.secret = settings.PLAID_SECRET
        self.environment = settings.PLAID_ENV

    def exchange_public_token(self, public_token: str) -> str:
        """
        Exchange public token for access token

        Args:
            public_token: Public token from Plaid Link

        Returns:
            Access token for API calls
        """
        # Import here to avoid import errors
        import plaid
        from plaid.api import plaid_api

        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        # Create request using dict
        request = {'public_token': public_token}
        response = client.item_public_token_exchange(request)
        return response['access_token']

    def get_transactions(
        self,
        access_token: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Fetch transactions for a given date range

        Args:
            access_token: Plaid access token
            start_date: Start date for transactions
            end_date: End date for transactions

        Returns:
            Dictionary containing transactions
        """
        import plaid
        from plaid.api import plaid_api

        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        request = {
            'access_token': access_token,
            'start_date': start_date.date(),
            'end_date': end_date.date()
        }
        response = client.transactions_get(request)
        return response

    def get_balance(self, access_token: str) -> Dict[str, Any]:
        """
        Get account balances

        Args:
            access_token: Plaid access token

        Returns:
            Dictionary containing account balances
        """
        import plaid
        from plaid.api import plaid_api

        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        request = {'access_token': access_token}
        response = client.accounts_balance_get(request)
        return response

    def get_income(self, access_token: str) -> Dict[str, Any]:
        """
        Get income information

        Args:
            access_token: Plaid access token

        Returns:
            Dictionary containing income data
        """
        import plaid
        from plaid.api import plaid_api

        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        request = {'access_token': access_token}
        response = client.income_get(request)
        return response

    def create_link_token(self, user_id: str) -> str:
        """
        Create a Link token for frontend initialization

        Args:
            user_id: Unique identifier for the user

        Returns:
            Link token for Plaid Link
        """
        import plaid
        from plaid.api import plaid_api

        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        request = {
            'products': ['transactions', 'auth'],
            'client_name': 'Loan Assessment Platform',
            'country_codes': ['US'],
            'language': 'en',
            'user': {'client_user_id': user_id}
        }
        response = client.link_token_create(request)
        return response['link_token']
