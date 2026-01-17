"""Quick script to check if environment variables are being read correctly"""

import os

client_id = os.getenv("PLAID_CLIENT_ID", "")
secret = os.getenv("PLAID_SECRET", "")

print("=" * 60)
print("Environment Variable Check")
print("=" * 60)
print(f"\nPLAID_CLIENT_ID value: '{client_id}'")
print(f"PLAID_CLIENT_ID length: {len(client_id)}")
print(f"PLAID_CLIENT_ID type: {type(client_id)}")
print(f"\nPLAID_SECRET value: '{secret[:20]}...' (first 20 chars)")
print(f"PLAID_SECRET length: {len(secret)}")
print(f"PLAID_SECRET type: {type(secret)}")
print("\n" + "=" * 60)

if not client_id or client_id.strip() == "":
    print("✗ PLAID_CLIENT_ID is empty or whitespace!")
elif len(client_id) < 10:
    print("⚠ PLAID_CLIENT_ID looks too short. Should be a long string.")
    print("  Example format: '64a1b2c3d4e5f6g7h8i9j0'")
else:
    print("✓ PLAID_CLIENT_ID looks OK")

if not secret or secret.strip() == "":
    print("✗ PLAID_SECRET is empty or whitespace!")
elif len(secret) < 20:
    print("⚠ PLAID_SECRET looks too short. Should be a long string.")
    print("  Example format: 'secret-sandbox-1234567890abcdef...'")
elif not secret.startswith("secret-"):
    print("⚠ PLAID_SECRET should start with 'secret-sandbox-' for sandbox")
else:
    print("✓ PLAID_SECRET looks OK")

