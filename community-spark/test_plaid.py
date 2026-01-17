"""
Test script for Plaid sandbox integration

This script tests the Plaid client by:
1. Creating a sandbox public token
2. Exchanging it for an access token
3. Fetching transactions
"""

import os
import asyncio
import httpx
from app.data.plaid_client import plaid_sandbox_get_transactions


async def main():
    """Test the Plaid sandbox flow"""
    print("=" * 60)
    print("Testing Plaid Sandbox Integration")
    print("=" * 60)
    
    # Check if credentials are set
    client_id = os.getenv("PLAID_CLIENT_ID", "")
    secret = os.getenv("PLAID_SECRET", "")
    
    print(f"\nClient ID: {'✓ Set' if client_id else '✗ Missing'}")
    print(f"Secret: {'✓ Set' if secret else '✗ Missing'}")
    
    if not client_id or not secret:
        print("\n✗ Error: PLAID_CLIENT_ID or PLAID_SECRET not found!")
        print("\nSet them in PowerShell with:")
        print('  $env:PLAID_CLIENT_ID="your_client_id"')
        print('  $env:PLAID_SECRET="your_secret"')
        return
    
    try:
        print("\n1. Creating sandbox public token...")
        print("2. Exchanging for access token...")
        print("3. Fetching transactions...\n")
        
        # Call the complete sandbox flow
        data = await plaid_sandbox_get_transactions()
        
        # Display results
        print("✓ Success! Plaid API is working.\n")
        print(f"Accounts found: {len(data.get('accounts', []))}")
        print(f"Total transactions: {len(data.get('transactions', []))}")
        
        # Show first few transactions
        transactions = data.get('transactions', [])
        if transactions:
            print(f"\nFirst 3 transactions:")
            for i, txn in enumerate(transactions[:3], 1):
                print(f"  {i}. {txn.get('name', 'Unknown')} - ${txn.get('amount', 0)}")
        
        print("\n" + "=" * 60)
        print("Full response data:")
        print("=" * 60)
        print(data)
        
    except httpx.HTTPStatusError as e:
        print(f"\n✗ HTTP Error: {e}")
        try:
            error_detail = e.response.json()
            print(f"\nPlaid Error Details:")
            print(f"  Error Code: {error_detail.get('error_code', 'N/A')}")
            print(f"  Error Type: {error_detail.get('error_type', 'N/A')}")
            print(f"  Error Message: {error_detail.get('error_message', 'N/A')}")
        except:
            print(f"\nResponse text: {e.response.text}")
        print("\nTroubleshooting:")
        print("1. Make sure PLAID_CLIENT_ID and PLAID_SECRET are set correctly")
        print("2. Verify they're from Plaid Dashboard > Team Settings > Keys > Sandbox")
        print("3. Check that PLAID_SECRET is the 'Secret' key (not 'Secret key ID')")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PLAID_CLIENT_ID and PLAID_SECRET are set correctly")
        print("2. Verify they're from Plaid Dashboard > Team Settings > Keys > Sandbox")
        print("3. Check that PLAID_SECRET is the 'Secret' key (not 'Secret key ID')")


if __name__ == "__main__":
    asyncio.run(main())

