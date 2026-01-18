from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.plaid_service import PlaidService
from app.services.google_service import GoogleService
from app.services.financial_calculator import FinancialCalculator
from app.core.config import get_settings

settings = get_settings()


class AgentState(TypedDict):
    """State for multi-agent workflow"""
    application_id: str
    access_token: str
    user_job: str
    user_age: int
    location_lat: float
    location_lng: float
    loan_amount: float
    loan_purpose: str
    financial_metrics: Dict[str, Any]
    market_analysis: Dict[str, Any]
    final_assessment: Optional[Dict[str, Any]]
    messages: List[str]


def financial_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for financial analysis

    Retrieves Plaid data and calculates financial metrics
    """
    plaid_service = PlaidService()
    calculator = FinancialCalculator()

    # Get financial data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    try:
        transactions = plaid_service.get_transactions(
            access_token=state['access_token'],
            start_date=start_date,
            end_date=end_date
        )

        balance_data = plaid_service.get_balance(state['access_token'])

        # Calculate metrics
        metrics = calculator.calculate_all_metrics(
            transactions=transactions.get('transactions', []),
            balance_data=balance_data
        )

        state['financial_metrics'] = metrics
        state['messages'].append("Financial analysis completed")

    except Exception as e:
        state['messages'].append(f"Financial analysis failed: {str(e)}")
        # Provide default metrics
        state['financial_metrics'] = {
            'monthly_income': 0.0,
            'monthly_expenses': 0.0,
            'debt_to_income_ratio': 0.0,
            'savings_rate': 0.0,
            'avg_monthly_balance': 0.0,
            'min_balance_6mo': 0.0,
            'overdraft_count': 0,
            'income_stability_score': 0.0
        }

    return state


def market_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for market analysis

    Analyzes location and competition using Google Maps/Places
    """
    google_service = GoogleService()

    try:
        # Extract business type from job description
        job_lower = state['user_job'].lower()

        # Simple keyword matching for business type
        if 'cafe' in job_lower or 'coffee' in job_lower:
            business_type = 'cafe'
        elif 'restaurant' in job_lower or 'food' in job_lower:
            business_type = 'restaurant'
        elif 'retail' in job_lower or 'store' in job_lower or 'shop' in job_lower:
            business_type = 'store'
        else:
            business_type = 'establishment'

        # Get nearby businesses
        nearby = google_service.get_nearby_businesses(
            lat=state['location_lat'],
            lng=state['location_lng'],
            business_type=business_type,
            radius=3200  # 2 miles
        )

        # Analyze market density
        density = google_service.analyze_market_density(
            nearby_businesses=nearby,
            radius_miles=2.0
        )

        # Calculate viability score
        competitor_count = len(nearby)

        if density == "low":
            viability = 85.0
        elif density == "medium":
            viability = 65.0
        else:
            viability = 40.0

        state['market_analysis'] = {
            'competitor_count': competitor_count,
            'market_density': density,
            'viability_score': viability,
            'nearby_businesses': nearby[:10],
            'market_insights': f"Found {competitor_count} competitors in 2-mile radius. Market density is {density}."
        }

        state['messages'].append("Market analysis completed")

    except Exception as e:
        state['messages'].append(f"Market analysis failed: {str(e)}")
        # Provide default analysis
        state['market_analysis'] = {
            'competitor_count': 0,
            'market_density': 'unknown',
            'viability_score': 50.0,
            'nearby_businesses': [],
            'market_insights': 'Unable to analyze market'
        }

    return state


def decision_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for final decision making

    Uses LLM to synthesize financial and market data into final assessment
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

    # Build context for LLM
    financial = state['financial_metrics']
    market = state['market_analysis']

    context = f"""
    You are a loan assessment expert. Analyze the following data and provide a decision.

    APPLICANT INFORMATION:
    - Job: {state['user_job']}
    - Age: {state.get('user_age', 'N/A')}
    - Loan Amount: ${state['loan_amount']:,.2f}
    - Loan Purpose: {state.get('loan_purpose', 'N/A')}

    FINANCIAL METRICS:
    - Monthly Income: ${financial.get('monthly_income', 0):,.2f}
    - Monthly Expenses: ${financial.get('monthly_expenses', 0):,.2f}
    - Debt-to-Income Ratio: {financial.get('debt_to_income_ratio', 0):.1f}%
    - Savings Rate: {financial.get('savings_rate', 0):.1f}%
    - Average Balance: ${financial.get('avg_monthly_balance', 0):,.2f}
    - Minimum Balance (6mo): ${financial.get('min_balance_6mo', 0):,.2f}
    - Overdrafts: {financial.get('overdraft_count', 0)}
    - Income Stability Score: {financial.get('income_stability_score', 0):.1f}/100

    MARKET ANALYSIS:
    - Competitors in Area: {market.get('competitor_count', 0)}
    - Market Density: {market.get('market_density', 'unknown')}
    - Market Viability Score: {market.get('viability_score', 0):.1f}/100
    - Market Insights: {market.get('market_insights', 'N/A')}

    Provide your assessment in the following JSON format:
    {{
        "eligibility": "approved" | "denied" | "review",
        "confidence_score": <0-100>,
        "risk_level": "low" | "medium" | "high",
        "reasoning": "<detailed explanation>",
        "recommendations": ["<recommendation 1>", "<recommendation 2>", ...]
    }}

    Base your decision on:
    1. Financial health (income, expenses, debt ratio, savings)
    2. Market viability (competition, location, business type)
    3. Loan amount relative to income and business potential
    4. Overall risk assessment
    """

    try:
        response = llm.invoke(context)
        content = response.content

        # Parse LLM response (simplified - in production use structured output)
        import json
        import re

        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            assessment = json.loads(json_match.group())
        else:
            # Fallback assessment
            assessment = {
                'eligibility': 'review',
                'confidence_score': 50.0,
                'risk_level': 'medium',
                'reasoning': 'Unable to parse LLM response',
                'recommendations': ['Manual review required']
            }

        state['final_assessment'] = assessment
        state['messages'].append("Decision completed")

    except Exception as e:
        state['messages'].append(f"Decision making failed: {str(e)}")
        # Provide default assessment
        state['final_assessment'] = {
            'eligibility': 'review',
            'confidence_score': 0.0,
            'risk_level': 'high',
            'reasoning': f'Error during assessment: {str(e)}',
            'recommendations': ['Manual review required due to system error']
        }

    return state


def create_assessment_graph():
    """
    Create the multi-agent assessment workflow graph

    Returns:
        Compiled StateGraph
    """
    workflow = StateGraph(AgentState)

    # Add nodes (use different names than state attributes)
    workflow.add_node("analyze_finances", financial_agent)
    workflow.add_node("analyze_market", market_agent)
    workflow.add_node("make_decision", decision_agent)

    # Define edges
    workflow.set_entry_point("analyze_finances")
    workflow.add_edge("analyze_finances", "analyze_market")
    workflow.add_edge("analyze_market", "make_decision")
    workflow.add_edge("make_decision", END)

    # Compile graph
    app = workflow.compile()

    return app
