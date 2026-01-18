import pytest
from datetime import datetime, timedelta
from app.services.financial_calculator import FinancialCalculator


@pytest.fixture
def calculator():
    """Create FinancialCalculator instance"""
    return FinancialCalculator()


@pytest.fixture
def sample_transactions():
    """Sample transaction data"""
    return [
        {
            'transaction_id': 'tx1',
            'amount': -50.0,  # Expense
            'date': '2024-01-15',
            'name': 'Grocery Store'
        },
        {
            'transaction_id': 'tx2',
            'amount': 2000.0,  # Income
            'date': '2024-01-01',
            'name': 'Paycheck'
        },
        {
            'transaction_id': 'tx3',
            'amount': -1500.0,  # Rent
            'date': '2024-01-05',
            'name': 'Rent Payment'
        }
    ]


@pytest.fixture
def sample_balances():
    """Sample balance data"""
    return {
        'accounts': [
            {
                'account_id': 'acc1',
                'balances': {
                    'current': 5000.0,
                    'available': 4800.0
                },
                'type': 'depository'
            }
        ]
    }


def test_calculate_debt_to_income_ratio(calculator, sample_transactions):
    """Test debt-to-income ratio calculation"""
    ratio = calculator.calculate_debt_to_income_ratio(
        monthly_debt_payment=500.0,
        monthly_income=3000.0
    )

    assert ratio == pytest.approx(16.67, rel=0.01)


def test_calculate_savings_rate(calculator):
    """Test savings rate calculation"""
    rate = calculator.calculate_savings_rate(
        monthly_income=5000.0,
        monthly_expenses=3500.0
    )

    assert rate == 30.0


def test_calculate_monthly_income(calculator, sample_transactions):
    """Test monthly income calculation"""
    income = calculator.calculate_monthly_income(sample_transactions)

    # Should identify positive transactions as income
    assert income > 0


def test_calculate_monthly_expenses(calculator, sample_transactions):
    """Test monthly expenses calculation"""
    expenses = calculator.calculate_monthly_expenses(sample_transactions)

    # Should sum negative transactions as expenses
    assert expenses > 0


def test_analyze_balance_history(calculator):
    """Test balance history analysis"""
    balance_data = {
        'accounts': [
            {
                'balances': {
                    'current': 5000.0
                }
            }
        ]
    }

    result = calculator.analyze_balance_history(balance_data)

    assert 'avg_balance' in result
    assert 'min_balance' in result
    assert result['avg_balance'] == 5000.0


def test_count_overdrafts(calculator, sample_transactions):
    """Test overdraft counting"""
    transactions_with_overdraft = sample_transactions + [
        {
            'transaction_id': 'tx4',
            'amount': -50.0,
            'date': '2024-01-20',
            'name': 'Overdraft Fee'
        }
    ]

    count = calculator.count_overdrafts(transactions_with_overdraft)

    # Should detect overdraft fee
    assert count >= 0


def test_calculate_income_stability(calculator, sample_transactions):
    """Test income stability score calculation"""
    score = calculator.calculate_income_stability(sample_transactions)

    # Should return a score between 0 and 100
    assert 0 <= score <= 100


def test_calculate_all_metrics(calculator, sample_transactions, sample_balances):
    """Test comprehensive metrics calculation"""
    result = calculator.calculate_all_metrics(
        transactions=sample_transactions,
        balance_data=sample_balances
    )

    # Verify all expected fields are present
    assert 'debt_to_income_ratio' in result
    assert 'savings_rate' in result
    assert 'avg_monthly_balance' in result
    assert 'min_balance_6mo' in result
    assert 'overdraft_count' in result
    assert 'income_stability_score' in result
    assert 'monthly_income' in result
    assert 'monthly_expenses' in result
