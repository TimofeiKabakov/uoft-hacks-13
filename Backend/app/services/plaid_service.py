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

    def _get_plaid_environment(self):
        """Map PLAID_ENV string to Plaid Environment enum"""
        import plaid
        env_map = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production,
        }
        return env_map.get(self.environment.lower(), plaid.Environment.Sandbox)

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
            host=self._get_plaid_environment(),
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
            host=self._get_plaid_environment(),
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
        # In Sandbox it's common for transactions to be briefly unavailable right after link/exchange.
        # Plaid returns ITEM_ERROR/PRODUCT_NOT_READY; the recommended action is to retry later.
        import time
        import logging
        try:
            from plaid.exceptions import ApiException  # type: ignore
        except Exception:  # pragma: no cover
            ApiException = Exception  # type: ignore

        response = None
        last_err: Exception | None = None
        for attempt in range(1, 6):  # up to 5 attempts
            try:
                response = client.transactions_get(request)
                last_err = None
                break
            except ApiException as e:  # Plaid API errors
                last_err = e
                body = getattr(e, "body", "") or ""
                is_not_ready = "PRODUCT_NOT_READY" in str(body)
                if is_not_ready and attempt < 5:
                    logging.getLogger(__name__).warning(
                        f"Plaid transactions not ready (PRODUCT_NOT_READY). Retrying in {attempt}s (attempt {attempt}/5)."
                    )
                    time.sleep(attempt)  # 1s,2s,3s,4s backoff
                    continue
                error_msg = f"Plaid transactions_get failed: {type(e).__name__}: {str(e)}"
                logging.getLogger(__name__).error(error_msg, exc_info=True)
                raise ValueError(error_msg) from e
            except Exception as e:
                last_err = e
                error_msg = f"Plaid transactions_get failed: {type(e).__name__}: {str(e)}"
                logging.getLogger(__name__).error(error_msg, exc_info=True)
                raise ValueError(error_msg) from e

        if response is None and last_err is not None:
            error_msg = f"Plaid transactions_get failed after retries: {type(last_err).__name__}: {str(last_err)}"
            logging.getLogger(__name__).error(error_msg, exc_info=True)
            raise ValueError(error_msg) from last_err
        # SDK returns an object; normalize to dict with list of plain dicts for our calculator/routes
        raw = getattr(response, 'transactions', None) or []
        total = getattr(response, 'total_transactions', None)
        transactions = []
        for t in raw:
            amount = getattr(t, 'amount', 0)
            date_val = getattr(t, 'date', None)
            category = getattr(t, 'category', None) or []
            name = getattr(t, 'name', None) or getattr(t, 'merchant_name', None) or ''
            transactions.append({
                'amount': float(amount) if amount is not None else 0,
                'date': str(date_val) if date_val is not None else '',
                'category': list(category) if isinstance(category, (list, tuple)) else [],
                'name': str(name) if name else '',
            })
        return {'transactions': transactions, 'total_transactions': total}

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
            host=self._get_plaid_environment(),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        request = {'access_token': access_token}
        try:
            response = client.accounts_balance_get(request)
        except Exception as e:
            error_msg = f"Plaid accounts_balance_get failed: {type(e).__name__}: {str(e)}"
            import logging
            logging.getLogger(__name__).error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        # SDK returns an object; normalize to dict for our calculator
        raw_accounts = getattr(response, 'accounts', None) or []
        accounts = []
        for acc in raw_accounts:
            balances = getattr(acc, 'balances', None)
            current = getattr(balances, 'current', None) if balances else None
            accounts.append({
                'account_id': getattr(acc, 'account_id', ''),
                'balances': {'current': float(current) if current is not None else 0.0},
            })
        return {'accounts': accounts}

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
            host=self._get_plaid_environment(),
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
            host=self._get_plaid_environment(),
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

    def create_sandbox_public_token(self, institution_id: str = 'ins_109508') -> str:
        """
        Create a sandbox public token for testing (no real Link flow).

        Args:
            institution_id: Plaid sandbox institution ID (default ins_109508)

        Returns:
            Public token that can be exchanged for access token
        """
        import plaid
        from plaid.api import plaid_api

        configuration = plaid.Configuration(
            host=self._get_plaid_environment(),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)

        request = {
            'institution_id': institution_id,
            'initial_products': ['transactions', 'auth'],
        }
        response = client.sandbox_public_token_create(request)
        return response['public_token']
