"""
Plaid API Client for Sandbox Integration

This module provides async functions to interact with Plaid's sandbox environment
for fetching bank transaction data.
"""

import os
import asyncio
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "")
PLAID_SECRET = os.getenv("PLAID_SECRET", "")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

# Plaid API base URLs
PLAID_URLS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com"
}

BASE_URL = PLAID_URLS.get(PLAID_ENV, PLAID_URLS["sandbox"])


async def plaid_sandbox_create_public_token(
    institution_id: str = "ins_109509",
    initial_products: list = None
) -> Dict[str, Any]:
    """
    Create a sandbox public token for testing.
    
    Args:
        institution_id: Plaid institution ID
            - ins_109508: First Platypus Bank (minimal transactions)
            - ins_109509: Tartan Bank (MORE transactions - default)
            - ins_109510: Houndstooth Bank (different patterns)
        initial_products: List of products to enable (default: ["transactions"])
        
    Returns:
        Dict with public_token
    """
    if initial_products is None:
        initial_products = ["transactions"]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/sandbox/public_token/create",
            json={
                "client_id": PLAID_CLIENT_ID,
                "secret": PLAID_SECRET,
                "institution_id": institution_id,
                "initial_products": initial_products
            },
            timeout=30.0
        )
        if response.status_code != 200:
            # Get detailed error from Plaid
            try:
                error_data = response.json()
                error_message = error_data.get("error_message", "Unknown error")
                error_code = error_data.get("error_code", "")
                raise Exception(f"Plaid API error ({response.status_code}): {error_code} - {error_message}")
            except Exception as e:
                if "Plaid API error" in str(e):
                    raise
                raise Exception(f"Plaid API error ({response.status_code}): {response.text}")
        return response.json()


async def plaid_exchange_public_token(public_token: str) -> Dict[str, Any]:
    """
    Exchange a public token for an access token.
    
    Args:
        public_token: Public token from Link or sandbox
        
    Returns:
        Dict with access_token and item_id
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/item/public_token/exchange",
            json={
                "client_id": PLAID_CLIENT_ID,
                "secret": PLAID_SECRET,
                "public_token": public_token
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def plaid_get_transactions(
    access_token: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Dict[str, Any]:
    """
    Fetch transactions for an access token.
    
    Handles PRODUCT_NOT_READY by retrying with delays, as Plaid needs time
    to process initial transaction data in sandbox.
    
    Args:
        access_token: Plaid access token
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
        
    Returns:
        Dict with transactions list and account info
    """
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            response = await client.post(
                f"{BASE_URL}/transactions/get",
                json={
                    "client_id": PLAID_CLIENT_ID,
                    "secret": PLAID_SECRET,
                    "access_token": access_token,
                    "start_date": start_date,
                    "end_date": end_date
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Check if it's a PRODUCT_NOT_READY error
            try:
                error_data = response.json()
                error_code = error_data.get("error_code", "")
                
                if error_code == "PRODUCT_NOT_READY" and attempt < max_retries - 1:
                    # Wait and retry
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
            except:
                pass
            
            # If not PRODUCT_NOT_READY or out of retries, raise the error
            response.raise_for_status()
        
        # Should not reach here, but just in case
        response.raise_for_status()
        return response.json()


async def plaid_sandbox_get_transactions(
    access_token: Optional[str] = None,
    start_date: str = "2023-01-01",
    end_date: str = "2024-01-01"
) -> Dict[str, Any]:
    """
    Complete sandbox flow: create public token, exchange it, and fetch transactions.
    
    If access_token is provided, uses it directly. Otherwise, creates a new
    sandbox token for testing.
    
    Args:
        access_token: Optional access token to use directly
        start_date: Start date for transactions (YYYY-MM-DD)
        end_date: End date for transactions (YYYY-MM-DD)
        
    Returns:
        Dict with transactions list and account data
    """
    # If no access token provided, create one via sandbox flow
    if not access_token:
        # Step 1: Create sandbox public token
        public_token_response = await plaid_sandbox_create_public_token()
        public_token = public_token_response["public_token"]
        
        # Step 2: Exchange for access token
        exchange_response = await plaid_exchange_public_token(public_token)
        access_token = exchange_response["access_token"]
        
        # Step 2.5: Wait a moment for Plaid to initialize the item
        # (Transactions product needs time to be ready in sandbox)
        await asyncio.sleep(1.0)
    
    # Step 3: Fetch transactions (with retry logic for PRODUCT_NOT_READY)
    transactions_data = await plaid_get_transactions(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    
    return transactions_data

