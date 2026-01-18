from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from statistics import mean, stdev
import re


class FinancialCalculator:
    """Service for calculating financial metrics from Plaid data"""

    def calculate_debt_to_income_ratio(
        self,
        monthly_debt_payment: float,
        monthly_income: float
    ) -> float:
        """
        Calculate debt-to-income ratio

        Args:
            monthly_debt_payment: Total monthly debt payments
            monthly_income: Total monthly income

        Returns:
            Debt-to-income ratio as percentage
        """
        if monthly_income == 0:
            return 0.0

        ratio = (monthly_debt_payment / monthly_income) * 100
        return round(ratio, 2)

    def calculate_savings_rate(
        self,
        monthly_income: float,
        monthly_expenses: float
    ) -> float:
        """
        Calculate savings rate

        Args:
            monthly_income: Total monthly income
            monthly_expenses: Total monthly expenses

        Returns:
            Savings rate as percentage
        """
        if monthly_income == 0:
            return 0.0

        savings = monthly_income - monthly_expenses
        rate = (savings / monthly_income) * 100
        return round(rate, 2)

    def calculate_monthly_income(self, transactions: List[Dict]) -> float:
        """
        Calculate average monthly income from transactions

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Average monthly income
        """
        # Filter for positive transactions (income)
        income_transactions = [
            t for t in transactions
            if t.get('amount', 0) > 0
        ]

        if not income_transactions:
            return 0.0

        total_income = sum(t['amount'] for t in income_transactions)

        # Get date range to calculate monthly average
        dates = [datetime.fromisoformat(t['date']) if isinstance(t['date'], str)
                else t['date'] for t in income_transactions]

        if not dates:
            return 0.0

        date_range_days = (max(dates) - min(dates)).days
        months = max(date_range_days / 30.0, 1.0)

        return round(total_income / months, 2)

    def calculate_monthly_expenses(self, transactions: List[Dict]) -> float:
        """
        Calculate average monthly expenses from transactions

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Average monthly expenses
        """
        # Filter for negative transactions (expenses)
        expense_transactions = [
            t for t in transactions
            if t.get('amount', 0) < 0
        ]

        if not expense_transactions:
            return 0.0

        total_expenses = sum(abs(t['amount']) for t in expense_transactions)

        # Get date range to calculate monthly average
        dates = [datetime.fromisoformat(t['date']) if isinstance(t['date'], str)
                else t['date'] for t in expense_transactions]

        if not dates:
            return 0.0

        date_range_days = (max(dates) - min(dates)).days
        months = max(date_range_days / 30.0, 1.0)

        return round(total_expenses / months, 2)

    def analyze_balance_history(self, balance_data: Dict) -> Dict[str, float]:
        """
        Analyze account balance history

        Args:
            balance_data: Balance data from Plaid

        Returns:
            Dictionary with balance statistics
        """
        accounts = balance_data.get('accounts', [])

        if not accounts:
            return {
                'avg_balance': 0.0,
                'min_balance': 0.0,
                'max_balance': 0.0
            }

        balances = [
            acc['balances']['current']
            for acc in accounts
            if 'balances' in acc and 'current' in acc['balances']
        ]

        if not balances:
            return {
                'avg_balance': 0.0,
                'min_balance': 0.0,
                'max_balance': 0.0
            }

        return {
            'avg_balance': round(mean(balances), 2),
            'min_balance': round(min(balances), 2),
            'max_balance': round(max(balances), 2)
        }

    def count_overdrafts(self, transactions: List[Dict]) -> int:
        """
        Count overdraft occurrences in transactions

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Number of overdraft incidents
        """
        overdraft_keywords = ['overdraft', 'nsf', 'insufficient funds']

        count = 0
        for transaction in transactions:
            name = transaction.get('name', '').lower()
            if any(keyword in name for keyword in overdraft_keywords):
                count += 1

        return count

    def calculate_income_stability(self, transactions: List[Dict]) -> float:
        """
        Calculate income stability score based on regularity

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Stability score from 0-100
        """
        # Filter for positive transactions (income)
        income_transactions = [
            t for t in transactions
            if t.get('amount', 0) > 0 and t.get('amount', 0) > 500  # Filter small transfers
        ]

        if len(income_transactions) < 2:
            return 50.0  # Neutral score for insufficient data

        # Calculate coefficient of variation (lower is more stable)
        amounts = [t['amount'] for t in income_transactions]

        avg_amount = mean(amounts)
        if avg_amount == 0:
            return 50.0

        std_amount = stdev(amounts) if len(amounts) > 1 else 0
        cv = (std_amount / avg_amount) * 100

        # Convert CV to stability score (0-100)
        # Lower CV = higher stability
        stability_score = max(0, min(100, 100 - cv))

        return round(stability_score, 2)

    def calculate_all_metrics(
        self,
        transactions: List[Dict],
        balance_data: Dict,
        income_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calculate all financial metrics

        Args:
            transactions: Transaction history
            balance_data: Account balance data
            income_data: Optional income data from Plaid

        Returns:
            Dictionary with all calculated metrics
        """
        monthly_income = self.calculate_monthly_income(transactions)
        monthly_expenses = self.calculate_monthly_expenses(transactions)
        balance_stats = self.analyze_balance_history(balance_data)

        # Estimate monthly debt payment (look for recurring payments)
        # Simplified: use 30% of expenses as debt estimate
        estimated_debt = monthly_expenses * 0.3

        return {
            'debt_to_income_ratio': self.calculate_debt_to_income_ratio(
                estimated_debt, monthly_income
            ),
            'savings_rate': self.calculate_savings_rate(
                monthly_income, monthly_expenses
            ),
            'avg_monthly_balance': balance_stats['avg_balance'],
            'min_balance_6mo': balance_stats['min_balance'],
            'overdraft_count': self.count_overdrafts(transactions),
            'income_stability_score': self.calculate_income_stability(transactions),
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses
        }
