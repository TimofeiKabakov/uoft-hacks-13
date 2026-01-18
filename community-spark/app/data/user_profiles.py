"""
User Profile Data for Demo/Testing

Contains predefined financial profiles that can be used instead of Plaid sandbox data.
"""

BAD_HABIT_USER = {
    "version": "2",
    "seed": "community-spark-bad-habits-v1",
    "mfa": {
        "type": "device"
    },
    "override_accounts": [
        {
            "type": "depository",
            "subtype": "checking",
            "starting_balance": 420.15,
            "currency": "USD",
            "meta": {
                "name": "Everyday Checking",
                "official_name": "First Platypus Bank Checking",
                "mask": "1049"
            },
            "identity": {
                "names": ["Jordan Example"],
                "phone_numbers": [
                    {"primary": True, "type": "mobile", "data": "4165550199"}
                ],
                "emails": [
                    {"primary": True, "type": "primary", "data": "jordan.example@demo-mail.com"}
                ],
                "addresses": [
                    {
                        "primary": True,
                        "data": {
                            "city": "Boston",
                            "region": "MA",
                            "street": "77 Demo Street, Unit 12",
                            "postal_code": "02118",
                            "country": "US"
                        }
                    }
                ]
            },
            "inflow_model": {
                "type": "monthly-income",
                "income_amount": 5200,
                "payment_day_of_month": 1,
                "transaction_name": "Payroll Deposit"
            },
            "transactions": [
                {"date_transacted": "2025-11-01", "date_posted": "2025-11-01", "currency": "USD", "amount": 1350.00, "description": "Rent Payment - ACH"},
                {"date_transacted": "2025-11-02", "date_posted": "2025-11-02", "currency": "USD", "amount": 86.42, "description": "GROCERIES - WHOLE MART"},
                {"date_transacted": "2025-11-02", "date_posted": "2025-11-02", "currency": "USD", "amount": 64.18, "description": "RESTAURANT - URBAN TACOS"},
                {"date_transacted": "2025-11-03", "date_posted": "2025-11-03", "currency": "USD", "amount": 38.77, "description": "UBER TRIP"},
                {"date_transacted": "2025-11-03", "date_posted": "2025-11-03", "currency": "USD", "amount": 55.90, "description": "DOORDASH"},
                {"date_transacted": "2025-11-04", "date_posted": "2025-11-04", "currency": "USD", "amount": 17.99, "description": "SUBSCRIPTION - NETFLIX"},
                {"date_transacted": "2025-11-04", "date_posted": "2025-11-04", "currency": "USD", "amount": 19.99, "description": "SUBSCRIPTION - SPOTIFY"},
                {"date_transacted": "2025-11-04", "date_posted": "2025-11-04", "currency": "USD", "amount": 14.99, "description": "SUBSCRIPTION - DISNEY PLUS"},
                {"date_transacted": "2025-11-05", "date_posted": "2025-11-05", "currency": "USD", "amount": 24.99, "description": "SUBSCRIPTION - CLOUD STORAGE"},
                {"date_transacted": "2025-11-05", "date_posted": "2025-11-05", "currency": "USD", "amount": 12.99, "description": "SUBSCRIPTION - PREMIUM FITNESS APP"},
                {"date_transacted": "2025-11-06", "date_posted": "2025-11-06", "currency": "USD", "amount": 89.21, "description": "LIQUOR STORE - CITY SPIRITS"},
                {"date_transacted": "2025-11-06", "date_posted": "2025-11-06", "currency": "USD", "amount": 74.33, "description": "RESTAURANT - STEAKHOUSE"},
                {"date_transacted": "2025-11-07", "date_posted": "2025-11-07", "currency": "USD", "amount": 120.00, "description": "ATM CASH WITHDRAWAL"},
                {"date_transacted": "2025-11-07", "date_posted": "2025-11-07", "currency": "USD", "amount": 9.00, "description": "ATM FEE"},
                {"date_transacted": "2025-11-08", "date_posted": "2025-11-08", "currency": "USD", "amount": 42.18, "description": "GAMING - ONLINE STORE"},
                {"date_transacted": "2025-11-08", "date_posted": "2025-11-08", "currency": "USD", "amount": 59.99, "description": "GAMING - IN-APP PURCHASES"},
                {"date_transacted": "2025-11-09", "date_posted": "2025-11-09", "currency": "USD", "amount": 27.43, "description": "COFFEE SHOP"},
                {"date_transacted": "2025-11-09", "date_posted": "2025-11-09", "currency": "USD", "amount": 61.20, "description": "RESTAURANT - BRUNCH PLACE"},
                {"date_transacted": "2025-11-10", "date_posted": "2025-11-10", "currency": "USD", "amount": 210.00, "description": "PAYDAY LOAN REPAYMENT"},
                {"date_transacted": "2025-11-10", "date_posted": "2025-11-10", "currency": "USD", "amount": 35.00, "description": "OVERDRAFT FEE"},
                {"date_transacted": "2025-11-10", "date_posted": "2025-11-10", "currency": "USD", "amount": 35.00, "description": "NSF FEE - RETURNED PAYMENT"},
                {"date_transacted": "2025-11-11", "date_posted": "2025-11-11", "currency": "USD", "amount": 128.64, "description": "ELECTRONICS - ONLINE MARKET"},
                {"date_transacted": "2025-11-11", "date_posted": "2025-11-11", "currency": "USD", "amount": 16.45, "description": "FAST FOOD"},
                {"date_transacted": "2025-11-12", "date_posted": "2025-11-12", "currency": "USD", "amount": 145.00, "description": "TRANSFER TO SAVINGS"},
                {"date_transacted": "2025-11-12", "date_posted": "2025-11-12", "currency": "USD", "amount": 145.00, "description": "TRANSFER OUT - SAVINGS FUND"},
                {"date_transacted": "2025-11-13", "date_posted": "2025-11-13", "currency": "USD", "amount": 79.99, "description": "SUBSCRIPTION - ONLINE LEARNING"},
                {"date_transacted": "2025-11-13", "date_posted": "2025-11-13", "currency": "USD", "amount": 22.99, "description": "SUBSCRIPTION - MUSIC ADD-ON"},
                {"date_transacted": "2025-11-14", "date_posted": "2025-11-14", "currency": "USD", "amount": 49.95, "description": "MOBILE BILL"},
                {"date_transacted": "2025-11-15", "date_posted": "2025-11-15", "currency": "USD", "amount": 96.10, "description": "GROCERIES - QUICK MART"},
                {"date_transacted": "2025-11-15", "date_posted": "2025-11-15", "currency": "USD", "amount": 68.52, "description": "DOORDASH"},
                {"date_transacted": "2025-11-18", "date_posted": "2025-11-18", "currency": "USD", "amount": 39.99, "description": "SUBSCRIPTION - VIDEO EDITOR"},
                {"date_transacted": "2025-11-19", "date_posted": "2025-11-19", "currency": "USD", "amount": 27.99, "description": "SUBSCRIPTION - EXTRA STORAGE"},
                {"date_transacted": "2025-11-20", "date_posted": "2025-11-20", "currency": "USD", "amount": 112.49, "description": "RESTAURANT - DELIVERY"},
                {"date_transacted": "2025-11-22", "date_posted": "2025-11-22", "currency": "USD", "amount": 250.00, "description": "ATM CASH WITHDRAWAL"},
                {"date_transacted": "2025-11-22", "date_posted": "2025-11-22", "currency": "USD", "amount": 9.00, "description": "ATM FEE"},
                {"date_transacted": "2025-11-25", "date_posted": "2025-11-25", "currency": "USD", "amount": 60.00, "description": "GAMBLING - SPORTSBOOK"},
                {"date_transacted": "2025-11-25", "date_posted": "2025-11-25", "currency": "USD", "amount": 85.00, "description": "GAMBLING - ONLINE CASINO"},
                {"date_transacted": "2025-11-28", "date_posted": "2025-11-28", "currency": "USD", "amount": 35.00, "description": "OVERDRAFT FEE"},
                {"date_transacted": "2025-12-01", "date_posted": "2025-12-01", "currency": "USD", "amount": 1320.00, "description": "Rent Payment - ACH"},
                {"date_transacted": "2025-12-02", "date_posted": "2025-12-02", "currency": "USD", "amount": 79.50, "description": "GROCERIES - WHOLE MART"},
                {"date_transacted": "2025-12-03", "date_posted": "2025-12-03", "currency": "USD", "amount": 72.40, "description": "RESTAURANT - TAKEOUT"},
                {"date_transacted": "2025-12-04", "date_posted": "2025-12-04", "currency": "USD", "amount": 55.90, "description": "DOORDASH"},
                {"date_transacted": "2025-12-05", "date_posted": "2025-12-05", "currency": "USD", "amount": 35.00, "description": "NSF FEE - RETURNED PAYMENT"},
                {"date_transacted": "2025-12-06", "date_posted": "2025-12-06", "currency": "USD", "amount": 44.18, "description": "COFFEE SHOP"},
                {"date_transacted": "2025-12-07", "date_posted": "2025-12-07", "currency": "USD", "amount": 119.99, "description": "ELECTRONICS - GADGET SHOP"},
                {"date_transacted": "2025-12-10", "date_posted": "2025-12-10", "currency": "USD", "amount": 210.00, "description": "PAYDAY LOAN REPAYMENT"},
                {"date_transacted": "2025-12-12", "date_posted": "2025-12-12", "currency": "USD", "amount": 99.99, "description": "LIQUOR STORE - CITY SPIRITS"},
                {"date_transacted": "2025-12-15", "date_posted": "2025-12-15", "currency": "USD", "amount": 225.00, "description": "ATM CASH WITHDRAWAL"},
                {"date_transacted": "2025-12-15", "date_posted": "2025-12-15", "currency": "USD", "amount": 9.00, "description": "ATM FEE"},
                {"date_transacted": "2025-12-18", "date_posted": "2025-12-18", "currency": "USD", "amount": 85.00, "description": "GAMBLING - SPORTSBOOK"},
                {"date_transacted": "2025-12-20", "date_posted": "2025-12-20", "currency": "USD", "amount": 62.40, "description": "RESTAURANT - TAKEOUT"},
                {"date_transacted": "2025-12-22", "date_posted": "2025-12-22", "currency": "USD", "amount": 35.00, "description": "OVERDRAFT FEE"},
                {"date_transacted": "2025-12-28", "date_posted": "2025-12-28", "currency": "USD", "amount": 19.99, "description": "SUBSCRIPTION - SPOTIFY"},
                {"date_transacted": "2025-12-28", "date_posted": "2025-12-28", "currency": "USD", "amount": 17.99, "description": "SUBSCRIPTION - NETFLIX"}
            ]
        },
        {
            "type": "depository",
            "subtype": "savings",
            "starting_balance": 110.00,
            "currency": "USD",
            "meta": {
                "name": "Emergency Savings",
                "official_name": "First Platypus Bank Savings",
                "mask": "7712"
            },
            "transactions": [
                {"date_transacted": "2025-11-12", "date_posted": "2025-11-12", "currency": "USD", "amount": -145.00, "description": "TRANSFER IN - FROM CHECKING"},
                {"date_transacted": "2025-11-26", "date_posted": "2025-11-26", "currency": "USD", "amount": 45.00, "description": "TRANSFER OUT - BACK TO CHECKING"},
                {"date_transacted": "2025-12-12", "date_posted": "2025-12-12", "currency": "USD", "amount": 25.00, "description": "TRANSFER OUT - BACK TO CHECKING"}
            ]
        },
        {
            "type": "credit",
            "subtype": "credit card",
            "starting_balance": 4875.22,
            "currency": "USD",
            "meta": {
                "name": "Rewards Credit Card",
                "official_name": "First Platypus Rewards Visa",
                "limit": 5000,
                "mask": "3321"
            },
            "liability": {
                "type": "credit",
                "purchase_apr": 24.99,
                "cash_apr": 29.99,
                "balance_transfer_apr": 27.50,
                "special_apr": 0,
                "last_payment_amount": 35,
                "minimum_payment_amount": 35,
                "is_overdue": True
            },
            "transactions": [
                {"date_transacted": "2025-11-05", "date_posted": "2025-11-06", "currency": "USD", "amount": 189.90, "description": "ELECTRONICS - ONLINE MARKET (CARD)"},
                {"date_transacted": "2025-11-08", "date_posted": "2025-11-09", "currency": "USD", "amount": 76.55, "description": "RESTAURANT - DELIVERY (CARD)"},
                {"date_transacted": "2025-11-12", "date_posted": "2025-11-12", "currency": "USD", "amount": 35.00, "description": "CREDIT CARD LATE FEE"},
                {"date_transacted": "2025-11-12", "date_posted": "2025-11-12", "currency": "USD", "amount": 12.00, "description": "INTEREST CHARGE"},
                {"date_transacted": "2025-11-15", "date_posted": "2025-11-15", "currency": "USD", "amount": 250.00, "description": "CASH ADVANCE"},
                {"date_transacted": "2025-11-15", "date_posted": "2025-11-15", "currency": "USD", "amount": 10.00, "description": "CASH ADVANCE FEE"},
                {"date_transacted": "2025-12-12", "date_posted": "2025-12-12", "currency": "USD", "amount": 35.00, "description": "CREDIT CARD LATE FEE"},
                {"date_transacted": "2025-12-12", "date_posted": "2025-12-12", "currency": "USD", "amount": 14.50, "description": "INTEREST CHARGE"}
            ]
        },
        {
            "type": "loan",
            "subtype": "student",
            "currency": "USD",
            "meta": {
                "name": "Student Loan",
                "official_name": "Plaid Student Loan",
                "mask": "2208"
            },
            "liability": {
                "type": "student",
                "origination_date": "2021-09-01",
                "principal": 18000,
                "nominal_apr": 6.25,
                "loan_name": "Student Loan - Standard Plan",
                "repayment_model": {
                    "type": "standard",
                    "non_repayment_months": 6,
                    "repayment_months": 120
                }
            }
        }
    ]
}


def get_user_profile(profile_name: str):
    """
    Get a user profile by name.
    
    Args:
        profile_name: Name of the profile to retrieve
        
    Returns:
        Dict with profile data, or None if not found
    """
    profiles = {
        "bad_habit_user": BAD_HABIT_USER,
        # Aliases for the same profile
        "badhabituser": BAD_HABIT_USER,
        "bad_habits": BAD_HABIT_USER,
        "demo": BAD_HABIT_USER,
        "test": BAD_HABIT_USER
    }
    return profiles.get(profile_name)


def convert_profile_to_plaid_format(profile_data: dict) -> dict:
    """
    Convert user profile data to Plaid API format.
    
    This transforms the profile structure to match what extract_bank_features expects.
    
    Args:
        profile_data: User profile dict
        
    Returns:
        Dict in Plaid format with accounts and transactions
    """
    accounts = []
    all_transactions = []
    
    for account in profile_data.get("override_accounts", []):
        # Extract account info
        account_info = {
            "account_id": f"account_{account['meta'].get('mask', 'unknown')}",
            "name": account["meta"].get("name", ""),
            "official_name": account["meta"].get("official_name", ""),
            "type": account["type"],
            "subtype": account.get("subtype"),
            "balances": {
                "available": account.get("starting_balance", 0),
                "current": account.get("starting_balance", 0),
                "limit": account.get("meta", {}).get("limit")
            },
            "mask": account["meta"].get("mask", "")
        }
        accounts.append(account_info)
        
        # Extract transactions
        for txn in account.get("transactions", []):
            transaction = {
                "account_id": account_info["account_id"],
                "transaction_id": f"txn_{txn['date_posted']}_{len(all_transactions)}",
                "amount": txn.get("amount", 0),
                "date": txn.get("date_posted", txn.get("date_transacted", "")),
                "name": txn.get("description", ""),
                "merchant_name": txn.get("description", "").split(" - ")[0] if " - " in txn.get("description", "") else txn.get("description", ""),
                "category": _infer_category(txn.get("description", "")),
                "primary_category": _infer_primary_category(txn.get("description", "")),
                "account_owner": None
            }
            all_transactions.append(transaction)
    
    return {
        "accounts": accounts,
        "transactions": all_transactions,
        "total_transactions": len(all_transactions)
    }


def _infer_category(description: str) -> list:
    """Infer transaction category from description."""
    desc_lower = description.lower()
    
    if "groceries" in desc_lower or "whole mart" in desc_lower or "quick mart" in desc_lower:
        return ["Food and Drink", "Groceries"]
    elif "restaurant" in desc_lower or "fast food" in desc_lower or "coffee shop" in desc_lower or "doordash" in desc_lower or "uber" in desc_lower or "brunch" in desc_lower or "tacos" in desc_lower or "takeout" in desc_lower or "delivery" in desc_lower:
        return ["Food and Drink", "Restaurants"]
    elif "rent" in desc_lower:
        return ["General Merchandise", "Housing"]
    elif "subscription" in desc_lower or "netflix" in desc_lower or "spotify" in desc_lower or "disney" in desc_lower:
        return ["General Services", "Entertainment"]
    elif "gambling" in desc_lower or "casino" in desc_lower or "sportsbook" in desc_lower:
        return ["Entertainment", "Gambling"]
    elif "liquor" in desc_lower or "spirits" in desc_lower:
        return ["Food and Drink", "Alcohol"]
    elif "atm" in desc_lower or "cash withdrawal" in desc_lower:
        return ["General", "Cash"]
    elif "fee" in desc_lower or "overdraft" in desc_lower or "nsf" in desc_lower:
        return ["Bank Fees", "ATM Fees"]
    elif "gaming" in desc_lower:
        return ["Entertainment", "Games"]
    elif "electronics" in desc_lower or "gadget" in desc_lower:
        return ["General Merchandise", "Electronics"]
    elif "loan" in desc_lower or "payday" in desc_lower:
        return ["Loan Payments", "Payday Loans"]
    elif "transfer" in desc_lower:
        return ["Transfer", "Internal Transfer"]
    elif "mobile" in desc_lower or "bill" in desc_lower:
        return ["General Services", "Utilities"]
    else:
        return ["General", "Other"]


def _infer_primary_category(description: str) -> str:
    """Infer primary category from description."""
    desc_lower = description.lower()
    
    if "groceries" in desc_lower or "whole mart" in desc_lower or "quick mart" in desc_lower:
        return "Food and Drink"
    elif "restaurant" in desc_lower or "fast food" in desc_lower or "coffee" in desc_lower or "doordash" in desc_lower or "uber" in desc_lower:
        return "Food and Drink"
    elif "rent" in desc_lower:
        return "General Merchandise"
    elif "subscription" in desc_lower or "netflix" in desc_lower or "spotify" in desc_lower:
        return "General Services"
    elif "gambling" in desc_lower or "casino" in desc_lower:
        return "Entertainment"
    elif "liquor" in desc_lower or "spirits" in desc_lower:
        return "Food and Drink"
    elif "atm" in desc_lower or "cash" in desc_lower:
        return "General"
    elif "fee" in desc_lower:
        return "Bank Fees"
    elif "gaming" in desc_lower:
        return "Entertainment"
    elif "electronics" in desc_lower:
        return "General Merchandise"
    elif "loan" in desc_lower or "payday" in desc_lower:
        return "Loan Payments"
    elif "transfer" in desc_lower:
        return "Transfer"
    else:
        return "General"

