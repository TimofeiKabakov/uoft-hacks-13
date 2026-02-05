"""
Prompts for Risk Assessor agent
"""
from typing import Dict, Any

SYSTEM_PROMPT = """You are a Risk Assessor AI agent specializing in loan application evaluation and risk analysis.

Your role is to:
1. Synthesize financial and market data into comprehensive risk assessment
2. Evaluate loan eligibility based on multiple factors
3. Determine appropriate risk levels
4. Provide clear reasoning for decisions
5. Generate actionable recommendations

You have access to:
- Financial analysis from the Financial Analyst
- Market analysis from the Market Researcher
- Applicant information

Guidelines:
- Be objective and thorough in your assessment
- Consider both financial health AND market viability
- Weigh multiple factors appropriately
- Provide clear, justified decisions
- Include specific reasoning for your conclusions
- Generate practical recommendations
- Consider the loan amount relative to income and market potential

Decision Criteria:
- APPROVED: Strong financial health + viable market conditions
- DENIED: Poor financial health OR high-risk market conditions
- REVIEW: Mixed signals requiring human judgment

Risk Levels:
- LOW: Minimal risk indicators, strong financial + market position
- MEDIUM: Some concerns but manageable risk profile
- HIGH: Multiple risk factors or critical issues

Do not:
- Make decisions without considering all available data
- Ignore important risk factors
- Provide vague or unjustified reasoning
"""


ASSESSMENT_PROMPT_TEMPLATE = """Evaluate this loan application and provide a final assessment.

APPLICANT INFORMATION:
- Job/Business: {user_job}
- Age: {user_age}
- Loan Amount: ${loan_amount:,.2f}
- Loan Purpose: {loan_purpose}

FINANCIAL ANALYSIS:
{financial_analysis}

MARKET ANALYSIS:
{market_analysis}

TASK:
Synthesize the financial and market data to make a final loan decision.

Consider:
1. Financial Health:
   - Income stability and level
   - Debt-to-income ratio
   - Savings rate and cushion
   - Banking behavior (overdrafts, balance history)

2. Market Viability:
   - Competition level
   - Market saturation
   - Location viability
   - Business type potential

3. Loan Factors:
   - Loan amount relative to income
   - Loan amount relative to business potential
   - Purpose alignment with business type

4. Overall Risk:
   - Probability of repayment
   - Market success probability
   - Combined risk factors

Provide your assessment with:
- eligibility: "approved", "denied", or "review"
- confidence_score: float between 0-100
- risk_level: "low", "medium", or "high"
- reasoning: detailed 2-3 sentence explanation of your decision
- recommendations: list of 3 specific actionable recommendations
- key_factors: financial_score (0-100), market_score (0-100), overall_score (0-100)

Be thorough and specific in your reasoning. The decision must be well-justified based on the data.
"""


def get_assessment_prompt(
    user_job: str,
    user_age: int,
    loan_amount: float,
    loan_purpose: str,
    financial_analysis: Dict,
    market_analysis: Dict
) -> str:
    """
    Generate assessment prompt with all data

    Args:
        user_job: Applicant's job
        user_age: Applicant's age
        loan_amount: Requested loan amount
        loan_purpose: Purpose of loan
        financial_analysis: Results from Financial Analyst
        market_analysis: Results from Market Researcher

    Returns:
        Formatted prompt string
    """
    import json

    # Format financial analysis
    financial_str = json.dumps(financial_analysis, indent=2)

    # Format market analysis
    market_str = json.dumps(market_analysis, indent=2)

    return ASSESSMENT_PROMPT_TEMPLATE.format(
        user_job=user_job,
        user_age=user_age,
        loan_amount=loan_amount,
        loan_purpose=loan_purpose,
        financial_analysis=financial_str,
        market_analysis=market_str
    )
