"""
Feature Extractor for Plaid Transaction Data

Extracts financial features from Plaid transaction JSON to support
the auditor agent's analysis.
"""

from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime
import statistics


def extract_bank_features(plaid_json: dict) -> dict:
    """
    Extract bank features from Plaid transaction JSON.
    
    Computes features needed by auditor_node:
    - revenue_months: Count distinct months with positive inflows (income-like deposits)
    - avg_monthly_revenue: Average inflow per month
    - revenue_volatility: Coefficient of variation (std/mean) on monthly inflows, clamped 0..1
    - nsf_count: Count transactions containing keywords like "NSF", "Overdraft", "Returned"
    - debt_to_income: Simple ratio of outflows vs inflows (hackathon proxy)
    
    Args:
        plaid_json: Plaid transactions/get API response containing 'transactions' list
        
    Returns:
        Dict with extracted features matching what auditor_node expects:
        {
            "avg_monthly_revenue": float,
            "revenue_months": int,
            "volatility": float,  # 0-1 range
            "nsf_count": int,
            "debt_to_income": float
        }
    """
    transactions = plaid_json.get("transactions", [])
    
    if not transactions:
        # Return defaults if no transactions
        return {
            "avg_monthly_revenue": 0,
            "revenue_months": 0,
            "volatility": 1.0,
            "nsf_count": 0,
            "debt_to_income": 0.0
        }
    
    # Process transactions
    monthly_inflows: Dict[str, float] = defaultdict(float)  # YYYY-MM -> total inflow
    total_outflows = 0.0
    total_inflows = 0.0
    nsf_count = 0
    
    # Keywords to identify NSF/overdraft transactions
    nsf_keywords = ["nsf", "overdraft", "returned", "insufficient funds", 
                    "bounced", "non-sufficient", "fee"]
    
    for txn in transactions:
        amount = txn.get("amount", 0)
        date_str = txn.get("date", "")
        
        # Plaid: positive amounts are debits (outflows), negative are credits (inflows)
        # For business revenue, we want credits (negative amounts in Plaid)
        # So inflows = negative amounts, outflows = positive amounts
        if amount < 0:
            # This is an inflow (credit) - money coming in
            inflow_amount = abs(amount)
            total_inflows += inflow_amount
            
            # Group by month for monthly revenue calculation
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = date_obj.strftime("%Y-%m")
                    monthly_inflows[month_key] += inflow_amount
                except (ValueError, TypeError):
                    pass
        elif amount > 0:
            # This is an outflow (debit) - money going out
            total_outflows += abs(amount)
        
        # Check for NSF/overdraft transactions
        transaction_name = (txn.get("name", "") + " " + 
                           txn.get("merchant_name", "") + " " + 
                           txn.get("category", "")).lower()
        
        if any(keyword in transaction_name for keyword in nsf_keywords):
            nsf_count += 1
    
    # Calculate revenue_months (distinct months with positive inflows)
    revenue_months = len([m for m, amount in monthly_inflows.items() if amount > 0])
    
    # Calculate avg_monthly_revenue
    if monthly_inflows:
        total_revenue = sum(monthly_inflows.values())
        months_with_revenue = max(1, revenue_months)  # Avoid division by zero
        avg_monthly_revenue = total_revenue / months_with_revenue
    else:
        avg_monthly_revenue = 0
    
    # Calculate revenue_volatility (coefficient of variation: std/mean)
    # Clamped to 0..1 range
    if len(monthly_inflows) > 1 and avg_monthly_revenue > 0:
        monthly_values = list(monthly_inflows.values())
        std_dev = statistics.stdev(monthly_values) if len(monthly_values) > 1 else 0
        mean = statistics.mean(monthly_values)
        coefficient_of_variation = std_dev / mean if mean > 0 else 1.0
        # Clamp to 0..1
        volatility = min(1.0, max(0.0, coefficient_of_variation))
    elif len(monthly_inflows) == 1:
        # Only one month of data - low volatility
        volatility = 0.0
    else:
        # No data - high volatility (worst case)
        volatility = 1.0
    
    # Calculate debt_to_income ratio (outflows / inflows)
    # This is a simple hackathon proxy for actual DTI
    debt_to_income = total_outflows / total_inflows if total_inflows > 0 else 0.0
    
    return {
        "avg_monthly_revenue": round(avg_monthly_revenue, 2),
        "revenue_months": revenue_months,
        "volatility": round(volatility, 3),
        "nsf_count": nsf_count,
        "debt_to_income": round(debt_to_income, 3)
    }

