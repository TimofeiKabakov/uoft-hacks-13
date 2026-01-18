"""
Financial Analyst Agent

Analyzes financial health using Plaid data and financial metrics
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.plaid_service import PlaidService
from app.services.financial_calculator import FinancialCalculator


class FinancialAnalyst:
    """
    Agent responsible for financial analysis

    Analyzes transaction history, account balances, and calculates
    comprehensive financial health metrics for loan assessment.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize Financial Analyst agent

        Args:
            llm: Shared LLM instance
        """
        self.llm = llm
        self.plaid_service = PlaidService()
        self.calculator = FinancialCalculator()

    async def analyze(
        self,
        access_token: str,
        user_job: str,
        user_age: int,
        loan_amount: float,
        loan_purpose: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis

        Args:
            access_token: Decrypted Plaid access token
            user_job: Applicant's job/occupation
            user_age: Applicant's age
            loan_amount: Requested loan amount
            loan_purpose: Purpose of the loan

        Returns:
            Dictionary with financial metrics and analysis
        """
        try:
            # Get financial data from Plaid
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)

            transactions_result = self.plaid_service.get_transactions(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date
            )

            balance_data = self.plaid_service.get_balance(access_token)

            # Calculate metrics
            transactions = transactions_result.get('transactions', [])
            metrics = self.calculator.calculate_all_metrics(
                transactions=transactions,
                balance_data=balance_data
            )

            # Analyze the metrics
            analysis = self._analyze_metrics(
                metrics=metrics,
                user_job=user_job,
                user_age=user_age,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose
            )

            return {
                'success': True,
                **metrics,
                **analysis
            }

        except Exception as e:
            # Return default metrics on error
            return {
                'success': False,
                'error': str(e),
                'monthly_income': 0.0,
                'monthly_expenses': 0.0,
                'debt_to_income_ratio': 0.0,
                'savings_rate': 0.0,
                'avg_monthly_balance': 0.0,
                'min_balance_6mo': 0.0,
                'overdraft_count': 0,
                'income_stability_score': 0.0,
                'financial_health_score': 0.0,
                'key_findings': [f'Error analyzing financial data: {str(e)}'],
                'concerns': ['Unable to retrieve financial data'],
                'strengths': []
            }

    def _analyze_metrics(
        self,
        metrics: Dict[str, Any],
        user_job: str,
        user_age: int,
        loan_amount: float,
        loan_purpose: str
    ) -> Dict[str, Any]:
        """
        Analyze calculated metrics and generate insights

        Args:
            metrics: Calculated financial metrics
            user_job: Applicant's job
            user_age: Applicant's age
            loan_amount: Requested loan amount
            loan_purpose: Purpose of loan

        Returns:
            Dictionary with analysis results
        """
        key_findings = []
        concerns = []
        strengths = []

        # Income analysis
        monthly_income = metrics.get('monthly_income', 0)
        if monthly_income > 0:
            key_findings.append(f"Average monthly income: ${monthly_income:,.2f}")
            if monthly_income >= 5000:
                strengths.append("Strong monthly income")
            elif monthly_income < 2000:
                concerns.append("Low monthly income relative to typical loan requirements")

        # Expense analysis
        monthly_expenses = metrics.get('monthly_expenses', 0)
        if monthly_expenses > 0:
            key_findings.append(f"Average monthly expenses: ${monthly_expenses:,.2f}")

        # Debt-to-income ratio
        dti_ratio = metrics.get('debt_to_income_ratio', 0)
        key_findings.append(f"Debt-to-income ratio: {dti_ratio:.1f}%")
        if dti_ratio < 30:
            strengths.append("Excellent debt-to-income ratio (< 30%)")
        elif dti_ratio < 43:
            key_findings.append("Acceptable debt-to-income ratio")
        else:
            concerns.append(f"High debt-to-income ratio ({dti_ratio:.1f}%) - exceeds recommended 43%")

        # Savings rate
        savings_rate = metrics.get('savings_rate', 0)
        key_findings.append(f"Savings rate: {savings_rate:.1f}%")
        if savings_rate > 20:
            strengths.append("Strong savings rate (> 20%)")
        elif savings_rate < 5:
            concerns.append("Low savings rate indicates limited financial cushion")

        # Balance analysis
        avg_balance = metrics.get('avg_monthly_balance', 0)
        min_balance = metrics.get('min_balance_6mo', 0)
        if avg_balance > 0:
            key_findings.append(f"Average balance: ${avg_balance:,.2f}")
            if avg_balance >= 10000:
                strengths.append("Healthy average account balance")

        if min_balance < 0:
            concerns.append(f"Minimum balance dipped to ${min_balance:,.2f}")

        # Overdrafts
        overdraft_count = metrics.get('overdraft_count', 0)
        if overdraft_count > 0:
            concerns.append(f"{overdraft_count} overdraft(s) in past 6 months")
        else:
            strengths.append("No overdrafts in past 6 months")

        # Income stability
        stability_score = metrics.get('income_stability_score', 0)
        key_findings.append(f"Income stability score: {stability_score:.1f}/100")
        if stability_score >= 80:
            strengths.append("Very stable income pattern")
        elif stability_score < 50:
            concerns.append("Irregular income pattern detected")

        # Loan amount relative to income
        if monthly_income > 0:
            loan_to_income_months = loan_amount / monthly_income
            key_findings.append(f"Loan amount is {loan_to_income_months:.1f}x monthly income")
            if loan_to_income_months > 12:
                concerns.append("Loan amount is high relative to monthly income")

        # Calculate overall financial health score
        financial_health_score = self._calculate_health_score(metrics)

        return {
            'financial_health_score': financial_health_score,
            'key_findings': key_findings,
            'concerns': concerns,
            'strengths': strengths
        }

    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate overall financial health score (0-100)

        Args:
            metrics: Calculated financial metrics

        Returns:
            Score from 0-100
        """
        score = 0.0

        # Income stability (30 points)
        stability = metrics.get('income_stability_score', 0)
        score += (stability / 100) * 30

        # DTI ratio (25 points)
        dti = metrics.get('debt_to_income_ratio', 100)
        if dti < 30:
            score += 25
        elif dti < 43:
            score += 15
        elif dti < 50:
            score += 5

        # Savings rate (20 points)
        savings = metrics.get('savings_rate', 0)
        if savings > 20:
            score += 20
        elif savings > 10:
            score += 15
        elif savings > 5:
            score += 10
        else:
            score += max(0, savings)

        # Balance health (15 points)
        avg_balance = metrics.get('avg_monthly_balance', 0)
        if avg_balance > 10000:
            score += 15
        elif avg_balance > 5000:
            score += 10
        elif avg_balance > 1000:
            score += 5

        # Overdrafts (10 points)
        overdrafts = metrics.get('overdraft_count', 0)
        if overdrafts == 0:
            score += 10
        elif overdrafts <= 2:
            score += 5

        return min(100.0, max(0.0, score))
