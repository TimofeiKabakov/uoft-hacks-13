"""
Setup Plaid Sandbox with Mock Transaction Data

This script uses Plaid's sandbox endpoints to add realistic mock transactions
to a test account, so the feature extractor has actual data to work with.
"""

import asyncio
import os
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "")
PLAID_SECRET = os.getenv("PLAID_SECRET", "")
BASE_URL = "https://sandbox.plaid.com"


async def create_sandbox_item_with_transactions():
    """
    Create a sandbox item with custom transaction data.
    
    Plaid's sandbox allows you to use specific institution IDs that come
    with pre-populated transaction data:
    
    - ins_109508 (First Platypus Bank) - Default, minimal transactions
    - ins_109509 (Tartan Bank) - More transactions
    - ins_109510 (Houndstooth Bank) - Different patterns
    
    You can also use /sandbox/item/fire_webhook to trigger transaction updates.
    """
    
    print("=" * 60)
    print("Setting up Plaid Sandbox with Mock Transaction Data")
    print("=" * 60)
    
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        print("❌ Error: PLAID_CLIENT_ID and PLAID_SECRET must be set")
        print("   Set them in your .env file or via 1Password:")
        print("   op run -- python scripts/setup_plaid_mock_data.py")
        return
    
    async with httpx.AsyncClient() as client:
        # Create sandbox public token with Tartan Bank (has more transactions)
        print("\n1. Creating sandbox item with Tartan Bank (more transactions)...")
        response = await client.post(
            f"{BASE_URL}/sandbox/public_token/create",
            json={
                "client_id": PLAID_CLIENT_ID,
                "secret": PLAID_SECRET,
                "institution_id": "ins_109509",  # Tartan Bank - has more transactions
                "initial_products": ["transactions"],
                "options": {
                    "webhook": ""
                }
            },
            timeout=30.0
        )
        
        if response.status_code != 200:
            print(f"❌ Error creating sandbox token: {response.text}")
            return
        
        public_token = response.json()["public_token"]
        print(f"✓ Public token created: {public_token[:20]}...")
        
        # Exchange for access token
        print("\n2. Exchanging for access token...")
        response = await client.post(
            f"{BASE_URL}/item/public_token/exchange",
            json={
                "client_id": PLAID_CLIENT_ID,
                "secret": PLAID_SECRET,
                "public_token": public_token
            },
            timeout=30.0
        )
        
        if response.status_code != 200:
            print(f"❌ Error exchanging token: {response.text}")
            return
        
        exchange_data = response.json()
        access_token = exchange_data["access_token"]
        item_id = exchange_data["item_id"]
        print(f"✓ Access token: {access_token[:20]}...")
        print(f"✓ Item ID: {item_id}")
        
        # Wait for transactions to be ready
        print("\n3. Waiting for transactions to be ready...")
        await asyncio.sleep(2)
        
        # Fetch transactions
        print("\n4. Fetching transactions...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
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
        
        if response.status_code != 200:
            print(f"❌ Error fetching transactions: {response.text}")
            return
        
        transactions_data = response.json()
        transactions = transactions_data.get("transactions", [])
        accounts = transactions_data.get("accounts", [])
        
        print(f"\n✓ Success! Retrieved {len(transactions)} transactions")
        print(f"✓ Accounts: {len(accounts)}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("Transaction Summary")
        print("=" * 60)
        
        for account in accounts[:3]:  # Show first 3 accounts
            print(f"\nAccount: {account['name']}")
            print(f"  Type: {account['type']} - {account['subtype']}")
            print(f"  Balance: ${account['balances']['current']}")
        
        if transactions:
            print(f"\nSample Transactions:")
            for txn in transactions[:5]:  # Show first 5 transactions
                print(f"  {txn['date']}: {txn['name']} - ${txn['amount']}")
        
        print("\n" + "=" * 60)
        print("How to use this data:")
        print("=" * 60)
        print("\n1. The /evaluate/plaid endpoint will automatically create")
        print("   a new sandbox item with transactions each time.")
        print("\n2. To use this specific access token, you can modify")
        print("   plaid_client.py to use it directly (for testing).")
        print(f"\n3. Access token: {access_token}")
        print("\nNote: Sandbox tokens expire after a while. Just run this")
        print("script again to create a new one.")
        
        return access_token


if __name__ == "__main__":
    asyncio.run(create_sandbox_item_with_transactions())

