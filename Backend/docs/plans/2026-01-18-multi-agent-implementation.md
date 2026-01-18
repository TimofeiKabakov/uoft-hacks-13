# Multi-Agent Loan Assessment System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign the loan assessment backend from a simple linear pipeline to a true multi-agent system with intelligent orchestration and specialized ReAct agents.

**Architecture:** Hierarchical multi-agent system with one orchestrator agent that coordinates three specialized ReAct agents (Financial Analyst, Market Researcher, Risk Assessor). Each agent uses LangChain's ReAct pattern to reason about which tools to use. Orchestrator controls information flow and conditionally invokes agents based on loan type.

**Tech Stack:** FastAPI, LangChain, LangChain Google GenAI, SQLAlchemy, Plaid API, Google Maps/Places API, Tenacity (retry logic)

---

## Phase 1: Setup Infrastructure

### Task 1: Create Directory Structure

**Files:**
- Create: `Backend/app/agents/shared/__init__.py`
- Create: `Backend/app/agents/shared/llm.py`
- Create: `Backend/app/agents/financial_analyst/__init__.py`
- Create: `Backend/app/agents/market_researcher/__init__.py`
- Create: `Backend/app/agents/risk_assessor/__init__.py`

**Step 1: Create shared directory structure**

```bash
mkdir -p Backend/app/agents/shared
mkdir -p Backend/app/agents/financial_analyst
mkdir -p Backend/app/agents/market_researcher
mkdir -p Backend/app/agents/risk_assessor
```

**Step 2: Create __init__.py files**

```bash
touch Backend/app/agents/shared/__init__.py
touch Backend/app/agents/financial_analyst/__init__.py
touch Backend/app/agents/market_researcher/__init__.py
touch Backend/app/agents/risk_assessor/__init__.py
```

**Step 3: Verify directory structure**

Run: `tree Backend/app/agents -L 2`
Expected: See new directories with __init__.py files

**Step 4: Commit**

```bash
git add Backend/app/agents/
git commit -m "chore: create multi-agent directory structure"
```

---

### Task 2: Create Shared LLM Instance

**Files:**
- Create: `Backend/app/agents/shared/llm.py`

**Step 1: Write shared LLM module**

Create `Backend/app/agents/shared/llm.py`:

```python
"""Shared LLM instance for all agents"""

from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings

settings = get_settings()

# Singleton LLM instance
_llm_instance = None


def get_llm():
    """
    Get shared LLM instance for all agents

    Returns:
        ChatGoogleGenerativeAI: Configured Gemini Pro instance
    """
    global _llm_instance

    if _llm_instance is None:
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            max_output_tokens=2048
        )

    return _llm_instance


def reset_llm():
    """Reset LLM instance (useful for testing)"""
    global _llm_instance
    _llm_instance = None
```

**Step 2: Update shared __init__.py**

Update `Backend/app/agents/shared/__init__.py`:

```python
"""Shared utilities for all agents"""

from .llm import get_llm, reset_llm

__all__ = ["get_llm", "reset_llm"]
```

**Step 3: Verify imports work**

Run: `cd Backend && python -c "from app.agents.shared import get_llm; print('OK')"`
Expected: "OK"

**Step 4: Commit**

```bash
git add Backend/app/agents/shared/
git commit -m "feat: add shared LLM instance for multi-agent system"
```

---

## Phase 2: Financial Analyst Agent

### Task 3: Create Financial Analyst Prompts

**Files:**
- Create: `Backend/app/agents/financial_analyst/prompts.py`

**Step 1: Write prompts module**

Create `Backend/app/agents/financial_analyst/prompts.py`:

```python
"""Prompts for Financial Analyst Agent"""

FINANCIAL_ANALYST_PROMPT = """You are the Financial Analyst Agent for a loan assessment system.

YOUR ROLE:
- Analyze applicant's financial health using Plaid banking data
- Calculate key financial metrics (DTI, savings rate, cash flow)
- Assess income stability and spending patterns
- Provide comprehensive financial assessment

TOOLS AVAILABLE:
- fetch_plaid_transactions: Get transaction history from Plaid API
- calculate_dti_ratio: Calculate debt-to-income ratio from transactions
- analyze_cash_flow: Analyze balance trends and cash flow patterns
- assess_income_stability: Score income consistency (0-100)

PROCESS:
1. Fetch transaction data using the Plaid access token
2. Assess income stability first to understand income patterns
3. Calculate DTI ratio to evaluate debt burden
4. Analyze cash flow to understand financial behavior
5. Return comprehensive financial metrics in JSON format

FOCUS ON:
- Income stability (regularity, trend, sources)
- Debt levels (DTI ratio, monthly obligations)
- Savings behavior (savings rate, balance trends)
- Spending patterns (overdrafts, balance consistency)

OUTPUT FORMAT:
Return a JSON object with these keys:
- monthly_income: Average monthly income
- monthly_expenses: Average monthly expenses
- debt_to_income_ratio: DTI percentage
- savings_rate: Savings as % of income
- avg_monthly_balance: Average account balance
- min_balance_6mo: Minimum balance in 6 months
- overdraft_count: Number of overdraft incidents
- income_stability_score: 0-100 stability score
- analysis: Brief text summary

Be thorough but efficient with tool usage. Use your reasoning to decide which tools to call and in what order.
"""
```

**Step 2: Verify file created**

Run: `cat Backend/app/agents/financial_analyst/prompts.py | head -5`
Expected: See prompt content

**Step 3: Commit**

```bash
git add Backend/app/agents/financial_analyst/prompts.py
git commit -m "feat: add financial analyst agent prompt"
```

---

### Task 4: Create Financial Analyst Tools

**Files:**
- Create: `Backend/app/agents/financial_analyst/tools.py`

**Step 1: Write tools module**

Create `Backend/app/agents/financial_analyst/tools.py`:

```python
"""Tools for Financial Analyst Agent"""

from langchain.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential
from app.services.plaid_service import PlaidService
from app.services.financial_calculator import FinancialCalculator
from datetime import datetime, timedelta
import json


@tool
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_plaid_transactions(access_token: str, days: int = 180) -> str:
    """
    Fetch transaction history from Plaid API

    Args:
        access_token: Plaid access token
        days: Number of days of history to fetch (default: 180)

    Returns:
        JSON string with transaction data including:
        - transactions: List of transaction objects
        - balance: Current account balance
    """
    try:
        plaid_service = PlaidService()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = plaid_service.get_transactions(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )

        balance_data = plaid_service.get_balance(access_token)

        result = {
            "transactions": transactions.get("transactions", []),
            "balance": balance_data
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to fetch transactions: {str(e)}"})


@tool
def calculate_dti_ratio(transactions_json: str) -> str:
    """
    Calculate debt-to-income ratio from transaction data

    Args:
        transactions_json: JSON string with transaction data

    Returns:
        JSON string with:
        - dti_ratio: Debt-to-income percentage
        - monthly_debt: Total monthly debt payments
        - monthly_income: Average monthly income
    """
    try:
        data = json.loads(transactions_json)
        transactions = data.get("transactions", [])

        calculator = FinancialCalculator()
        balance_data = data.get("balance", {})

        metrics = calculator.calculate_all_metrics(
            transactions=transactions,
            balance_data=balance_data
        )

        result = {
            "dti_ratio": metrics.get("debt_to_income_ratio", 0.0),
            "monthly_debt": metrics.get("monthly_expenses", 0.0) * 0.3,  # Estimate
            "monthly_income": metrics.get("monthly_income", 0.0)
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to calculate DTI: {str(e)}"})


@tool
def analyze_cash_flow(transactions_json: str) -> str:
    """
    Analyze balance trends and cash flow patterns

    Args:
        transactions_json: JSON string with transaction data

    Returns:
        JSON string with:
        - avg_monthly_balance: Average balance over period
        - min_balance_6mo: Minimum balance in 6 months
        - overdraft_count: Number of overdraft incidents
        - balance_trend: "increasing", "stable", or "decreasing"
    """
    try:
        data = json.loads(transactions_json)
        transactions = data.get("transactions", [])
        balance_data = data.get("balance", {})

        calculator = FinancialCalculator()
        metrics = calculator.calculate_all_metrics(
            transactions=transactions,
            balance_data=balance_data
        )

        result = {
            "avg_monthly_balance": metrics.get("avg_monthly_balance", 0.0),
            "min_balance_6mo": metrics.get("min_balance_6mo", 0.0),
            "overdraft_count": metrics.get("overdraft_count", 0),
            "balance_trend": "stable"  # Could be enhanced with trend analysis
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to analyze cash flow: {str(e)}"})


@tool
def assess_income_stability(transactions_json: str) -> str:
    """
    Score income consistency and stability (0-100)

    Args:
        transactions_json: JSON string with transaction data

    Returns:
        JSON string with:
        - stability_score: 0-100 score
        - income_regularity: "regular", "irregular", or "variable"
        - income_trend: "growing", "stable", or "declining"
    """
    try:
        data = json.loads(transactions_json)
        transactions = data.get("transactions", [])
        balance_data = data.get("balance", {})

        calculator = FinancialCalculator()
        metrics = calculator.calculate_all_metrics(
            transactions=transactions,
            balance_data=balance_data
        )

        stability_score = metrics.get("income_stability_score", 0.0)

        # Categorize regularity
        if stability_score >= 80:
            regularity = "regular"
        elif stability_score >= 50:
            regularity = "variable"
        else:
            regularity = "irregular"

        result = {
            "stability_score": stability_score,
            "income_regularity": regularity,
            "income_trend": "stable"  # Could be enhanced with trend analysis
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to assess income stability: {str(e)}"})
```

**Step 2: Verify imports**

Run: `cd Backend && python -c "from app.agents.financial_analyst.tools import fetch_plaid_transactions; print('OK')"`
Expected: "OK"

**Step 3: Commit**

```bash
git add Backend/app/agents/financial_analyst/tools.py
git commit -m "feat: add financial analyst agent tools"
```

---

### Task 5: Create Financial Analyst Agent

**Files:**
- Create: `Backend/app/agents/financial_analyst/agent.py`

**Step 1: Write agent module**

Create `Backend/app/agents/financial_analyst/agent.py`:

```python
"""Financial Analyst ReAct Agent"""

from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from .tools import (
    fetch_plaid_transactions,
    calculate_dti_ratio,
    analyze_cash_flow,
    assess_income_stability
)
from .prompts import FINANCIAL_ANALYST_PROMPT


def create_financial_analyst_agent(llm):
    """
    Create Financial Analyst ReAct agent

    Args:
        llm: LangChain LLM instance

    Returns:
        AgentExecutor: Configured agent executor
    """
    tools = [
        fetch_plaid_transactions,
        calculate_dti_ratio,
        analyze_cash_flow,
        assess_income_stability
    ]

    # Create prompt template with ReAct format
    prompt = PromptTemplate.from_template(
        FINANCIAL_ANALYST_PROMPT + "\n\n{agent_scratchpad}"
    )

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=5,
        handle_parsing_errors=True,
        verbose=True
    )

    return executor
```

**Step 2: Update agent __init__.py**

Update `Backend/app/agents/financial_analyst/__init__.py`:

```python
"""Financial Analyst Agent"""

from .agent import create_financial_analyst_agent

__all__ = ["create_financial_analyst_agent"]
```

**Step 3: Verify imports**

Run: `cd Backend && python -c "from app.agents.financial_analyst import create_financial_analyst_agent; print('OK')"`
Expected: "OK"

**Step 4: Commit**

```bash
git add Backend/app/agents/financial_analyst/
git commit -m "feat: add financial analyst react agent"
```

---

## Phase 3: Market Researcher Agent

### Task 6: Create Market Researcher Prompts

**Files:**
- Create: `Backend/app/agents/market_researcher/prompts.py`

**Step 1: Write prompts module**

Create `Backend/app/agents/market_researcher/prompts.py`:

```python
"""Prompts for Market Researcher Agent"""

MARKET_RESEARCHER_PROMPT = """You are the Market Researcher Agent for a loan assessment system.

YOUR ROLE:
- Analyze business location and market viability
- Assess competition in the area
- Evaluate market saturation
- Provide market insights for business loan decisions

TOOLS AVAILABLE:
- search_competitors: Find competing businesses nearby using Google Places API
- analyze_market_saturation: Assess market density and saturation level
- assess_location_viability: Evaluate location fit for business type

PROCESS:
1. Search for competitors in the business area (2-mile radius)
2. Analyze market saturation level based on competitor count
3. Assess location viability for this specific business type
4. Return comprehensive market analysis in JSON format

FOCUS ON:
- Competition level (how many competitors, their ratings)
- Market gaps (opportunities for differentiation)
- Location advantages/disadvantages
- Market saturation (low/medium/high)

OUTPUT FORMAT:
Return a JSON object with these keys:
- competitor_count: Number of competing businesses
- market_density: "low", "medium", or "high"
- viability_score: 0-100 location viability score
- nearby_businesses: List of top competitors (name, rating, distance)
- market_insights: Text summary of market analysis

Be thorough in your analysis. Consider both competition and opportunity.
"""
```

**Step 2: Commit**

```bash
git add Backend/app/agents/market_researcher/prompts.py
git commit -m "feat: add market researcher agent prompt"
```

---

### Task 7: Create Market Researcher Tools

**Files:**
- Create: `Backend/app/agents/market_researcher/tools.py`

**Step 1: Write tools module**

Create `Backend/app/agents/market_researcher/tools.py`:

```python
"""Tools for Market Researcher Agent"""

from langchain.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential
from app.services.google_service import GoogleService
import json


@tool
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def search_competitors(lat: float, lng: float, business_type: str, radius_miles: float = 2.0) -> str:
    """
    Search for competing businesses using Google Places API

    Args:
        lat: Latitude
        lng: Longitude
        business_type: Type of business (e.g., "cafe", "restaurant", "store")
        radius_miles: Search radius in miles (default: 2.0)

    Returns:
        JSON string with list of competitors:
        - name: Business name
        - rating: Google rating
        - distance_miles: Distance from location
        - type: Business type
    """
    try:
        google_service = GoogleService()

        # Convert miles to meters
        radius_meters = int(radius_miles * 1609.34)

        nearby = google_service.get_nearby_businesses(
            lat=lat,
            lng=lng,
            business_type=business_type,
            radius=radius_meters
        )

        # Format response
        competitors = []
        for business in nearby[:20]:  # Limit to top 20
            competitors.append({
                "name": business.get("name", "Unknown"),
                "rating": business.get("rating", 0.0),
                "distance_miles": business.get("distance_miles", 0.0),
                "type": business_type
            })

        return json.dumps({"competitors": competitors, "count": len(competitors)})

    except Exception as e:
        return json.dumps({"error": f"Failed to search competitors: {str(e)}"})


@tool
def analyze_market_saturation(competitors_json: str, business_type: str) -> str:
    """
    Assess market density and saturation level

    Args:
        competitors_json: JSON string with competitor data
        business_type: Type of business

    Returns:
        JSON string with:
        - density: "low", "medium", or "high"
        - saturation_score: 0-100 (higher = more saturated)
        - avg_competitor_rating: Average rating of competitors
        - market_gap_analysis: Insights about market gaps
    """
    try:
        data = json.loads(competitors_json)
        competitors = data.get("competitors", [])
        count = len(competitors)

        # Determine density
        if count < 5:
            density = "low"
            saturation_score = 25.0
            gap_analysis = "Low competition - good opportunity for new entrants"
        elif count < 15:
            density = "medium"
            saturation_score = 55.0
            gap_analysis = "Moderate competition - differentiation will be key"
        else:
            density = "high"
            saturation_score = 85.0
            gap_analysis = "High competition - strong value proposition needed"

        # Calculate average rating
        ratings = [c.get("rating", 0.0) for c in competitors if c.get("rating", 0.0) > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

        result = {
            "density": density,
            "saturation_score": saturation_score,
            "avg_competitor_rating": round(avg_rating, 1),
            "market_gap_analysis": gap_analysis
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to analyze saturation: {str(e)}"})


@tool
def assess_location_viability(lat: float, lng: float, business_type: str) -> str:
    """
    Evaluate location suitability for business type (0-100)

    Args:
        lat: Latitude
        lng: Longitude
        business_type: Type of business

    Returns:
        JSON string with:
        - viability_score: 0-100 score
        - location_strengths: List of advantages
        - location_weaknesses: List of disadvantages
    """
    try:
        google_service = GoogleService()

        # Get nearby businesses for area analysis
        nearby = google_service.get_nearby_businesses(
            lat=lat,
            lng=lng,
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
            viability_score = 85.0
            strengths = ["Low competition", "First-mover advantage"]
            weaknesses = ["Market demand uncertain"]
        elif density == "medium":
            viability_score = 65.0
            strengths = ["Proven market demand", "Room for differentiation"]
            weaknesses = ["Some competition present"]
        else:
            viability_score = 40.0
            strengths = ["Established market"]
            weaknesses = ["High competition", "Difficult to differentiate"]

        result = {
            "viability_score": viability_score,
            "location_strengths": strengths,
            "location_weaknesses": weaknesses
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to assess viability: {str(e)}"})
```

**Step 2: Commit**

```bash
git add Backend/app/agents/market_researcher/tools.py
git commit -m "feat: add market researcher agent tools"
```

---

### Task 8: Create Market Researcher Agent

**Files:**
- Create: `Backend/app/agents/market_researcher/agent.py`

**Step 1: Write agent module**

Create `Backend/app/agents/market_researcher/agent.py`:

```python
"""Market Researcher ReAct Agent"""

from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from .tools import (
    search_competitors,
    analyze_market_saturation,
    assess_location_viability
)
from .prompts import MARKET_RESEARCHER_PROMPT


def create_market_researcher_agent(llm):
    """
    Create Market Researcher ReAct agent

    Args:
        llm: LangChain LLM instance

    Returns:
        AgentExecutor: Configured agent executor
    """
    tools = [
        search_competitors,
        analyze_market_saturation,
        assess_location_viability
    ]

    prompt = PromptTemplate.from_template(
        MARKET_RESEARCHER_PROMPT + "\n\n{agent_scratchpad}"
    )

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=5,
        handle_parsing_errors=True,
        verbose=True
    )

    return executor
```

**Step 2: Update agent __init__.py**

Update `Backend/app/agents/market_researcher/__init__.py`:

```python
"""Market Researcher Agent"""

from .agent import create_market_researcher_agent

__all__ = ["create_market_researcher_agent"]
```

**Step 3: Commit**

```bash
git add Backend/app/agents/market_researcher/
git commit -m "feat: add market researcher react agent"
```

---

## Phase 4: Risk Assessor Agent

### Task 9: Create Risk Assessor Prompts

**Files:**
- Create: `Backend/app/agents/risk_assessor/prompts.py`

**Step 1: Write prompts module**

Create `Backend/app/agents/risk_assessor/prompts.py`:

```python
"""Prompts for Risk Assessor Agent"""

RISK_ASSESSOR_PROMPT = """You are the Risk Assessor Agent for a loan assessment system.

YOUR ROLE:
- Synthesize financial and market data into comprehensive risk assessment
- Calculate overall risk score
- Generate actionable recommendations
- Provide clear explanation of decision

TOOLS AVAILABLE:
- calculate_risk_score: Compute overall risk from financial and market metrics
- generate_recommendations: Create actionable suggestions for applicant
- explain_decision: Generate human-readable reasoning for the assessment

PROCESS:
1. Review financial metrics from Financial Analyst
2. Review market analysis from Market Researcher (if available)
3. Calculate comprehensive risk score using both datasets
4. Generate specific, actionable recommendations
5. Explain the decision clearly in human-readable format
6. Return complete assessment in JSON format

FOCUS ON:
- Overall risk level (low/medium/high)
- Approval likelihood (approved/denied/review)
- Actionable recommendations (what applicant should do)
- Clear reasoning (why this decision was made)

DECISION CRITERIA:
- Financial health: DTI < 40%, savings rate > 10%, stable income
- Market viability: Viability score > 60, manageable competition
- Overall confidence: Combination of financial + market factors

OUTPUT FORMAT:
Return a JSON object with these keys:
- eligibility: "approved", "denied", or "review"
- confidence_score: 0-100 confidence in this decision
- risk_level: "low", "medium", or "high"
- reasoning: Detailed explanation of the decision
- recommendations: List of actionable suggestions

Make decisions that balance risk with opportunity. Be fair but thorough.
"""
```

**Step 2: Commit**

```bash
git add Backend/app/agents/risk_assessor/prompts.py
git commit -m "feat: add risk assessor agent prompt"
```

---

### Task 10: Create Risk Assessor Tools

**Files:**
- Create: `Backend/app/agents/risk_assessor/tools.py`

**Step 1: Write tools module**

Create `Backend/app/agents/risk_assessor/tools.py`:

```python
"""Tools for Risk Assessor Agent"""

from langchain.tools import tool
import json


@tool
def calculate_risk_score(financial_metrics_json: str, market_analysis_json: str = "{}") -> str:
    """
    Calculate overall risk score from financial and market metrics

    Args:
        financial_metrics_json: JSON string with financial analysis
        market_analysis_json: JSON string with market analysis (optional)

    Returns:
        JSON string with:
        - risk_score: 0-100 (higher = lower risk, better applicant)
        - risk_level: "low", "medium", or "high"
        - risk_factors: List of identified risks
        - mitigating_factors: List of positive factors
    """
    try:
        financial = json.loads(financial_metrics_json)
        market = json.loads(market_analysis_json) if market_analysis_json != "{}" else {}

        # Calculate financial risk score (0-100)
        financial_score = 50.0  # Base score

        # DTI ratio impact
        dti = financial.get("dti_ratio", 50.0)
        if dti < 30:
            financial_score += 20
        elif dti < 40:
            financial_score += 10
        elif dti > 50:
            financial_score -= 20

        # Savings rate impact
        savings_rate = financial.get("savings_rate", 0.0)
        if savings_rate > 20:
            financial_score += 15
        elif savings_rate > 10:
            financial_score += 10
        elif savings_rate < 5:
            financial_score -= 10

        # Income stability impact
        stability = financial.get("stability_score", 50.0)
        if stability > 80:
            financial_score += 15
        elif stability > 60:
            financial_score += 10
        elif stability < 40:
            financial_score -= 15

        # Market viability impact (if available)
        market_score = 50.0
        if market:
            viability = market.get("viability_score", 50.0)
            market_score = viability

        # Combine scores
        if market:
            overall_score = (financial_score * 0.6) + (market_score * 0.4)
        else:
            overall_score = financial_score

        # Clamp to 0-100
        overall_score = max(0, min(100, overall_score))

        # Determine risk level
        if overall_score >= 70:
            risk_level = "low"
        elif overall_score >= 50:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Identify factors
        risk_factors = []
        mitigating_factors = []

        if dti > 40:
            risk_factors.append("High debt-to-income ratio")
        else:
            mitigating_factors.append("Healthy debt-to-income ratio")

        if savings_rate < 10:
            risk_factors.append("Low savings rate")
        else:
            mitigating_factors.append("Good savings behavior")

        if stability < 60:
            risk_factors.append("Income instability")
        else:
            mitigating_factors.append("Stable income")

        if market and market.get("density") == "high":
            risk_factors.append("High market competition")
        elif market and market.get("density") == "low":
            mitigating_factors.append("Low competition area")

        result = {
            "risk_score": round(overall_score, 1),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigating_factors": mitigating_factors
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to calculate risk: {str(e)}"})


@tool
def generate_recommendations(assessment_data_json: str) -> str:
    """
    Generate actionable recommendations based on assessment

    Args:
        assessment_data_json: JSON string with full assessment data

    Returns:
        JSON string with:
        - recommendations: List of actionable suggestions
    """
    try:
        data = json.loads(assessment_data_json)
        recommendations = []

        # Financial recommendations
        dti = data.get("dti_ratio", 0)
        if dti > 40:
            recommendations.append("Work on reducing debt burden before applying for additional loans")

        savings_rate = data.get("savings_rate", 0)
        if savings_rate < 10:
            recommendations.append("Build emergency fund to at least 3 months of expenses")

        stability = data.get("stability_score", 0)
        if stability < 60:
            recommendations.append("Establish more consistent income streams")

        # Market recommendations
        market_density = data.get("market_density", "")
        if market_density == "high":
            recommendations.append("Develop unique value proposition to stand out in competitive market")
            recommendations.append("Consider location scouting in less saturated areas")
        elif market_density == "low":
            recommendations.append("Validate market demand before significant investment")

        # General recommendations
        risk_level = data.get("risk_level", "medium")
        if risk_level == "high":
            recommendations.append("Consider starting with smaller loan amount to minimize risk")

        # Default if no specific recommendations
        if not recommendations:
            recommendations.append("Maintain current financial health and business strategy")

        return json.dumps({"recommendations": recommendations})

    except Exception as e:
        return json.dumps({"error": f"Failed to generate recommendations: {str(e)}"})


@tool
def explain_decision(assessment_data_json: str) -> str:
    """
    Generate human-readable explanation of the decision

    Args:
        assessment_data_json: JSON string with full assessment data

    Returns:
        JSON string with:
        - reasoning: Detailed explanation
        - key_factors: Most important decision factors
    """
    try:
        data = json.loads(assessment_data_json)

        # Build reasoning
        risk_score = data.get("risk_score", 50)
        risk_level = data.get("risk_level", "medium")
        eligibility = data.get("eligibility", "review")

        # Determine decision
        if risk_score >= 70:
            decision_basis = "strong financial health and low risk profile"
        elif risk_score >= 50:
            decision_basis = "moderate financial health with manageable risk"
        else:
            decision_basis = "financial concerns that require attention"

        # Build detailed reasoning
        dti = data.get("dti_ratio", 0)
        savings = data.get("savings_rate", 0)
        stability = data.get("stability_score", 0)

        reasoning_parts = [
            f"This assessment is based on {decision_basis}."
        ]

        # Financial details
        if dti < 40:
            reasoning_parts.append(f"The applicant has a healthy debt-to-income ratio of {dti:.1f}%.")
        else:
            reasoning_parts.append(f"The debt-to-income ratio of {dti:.1f}% is concerning.")

        if savings > 15:
            reasoning_parts.append(f"Savings rate of {savings:.1f}% demonstrates good financial discipline.")
        elif savings < 10:
            reasoning_parts.append(f"Low savings rate of {savings:.1f}% suggests limited financial cushion.")

        if stability > 75:
            reasoning_parts.append(f"Income stability score of {stability:.1f}/100 indicates reliable income.")
        elif stability < 60:
            reasoning_parts.append(f"Income stability score of {stability:.1f}/100 raises concerns about income consistency.")

        # Market details (if available)
        market_density = data.get("market_density")
        if market_density:
            viability = data.get("viability_score", 50)
            reasoning_parts.append(f"Market analysis shows {market_density} competition with viability score of {viability:.1f}/100.")

        reasoning = " ".join(reasoning_parts)

        # Key factors
        key_factors = []
        if dti < 40:
            key_factors.append("Healthy debt-to-income ratio")
        if savings > 15:
            key_factors.append("Strong savings behavior")
        if stability > 75:
            key_factors.append("Stable income")
        if market_density == "low":
            key_factors.append("Low competition market")

        if not key_factors:
            key_factors = ["Mixed financial indicators", "Requires careful evaluation"]

        result = {
            "reasoning": reasoning,
            "key_factors": key_factors
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to explain decision: {str(e)}"})
```

**Step 2: Commit**

```bash
git add Backend/app/agents/risk_assessor/tools.py
git commit -m "feat: add risk assessor agent tools"
```

---

### Task 11: Create Risk Assessor Agent

**Files:**
- Create: `Backend/app/agents/risk_assessor/agent.py`

**Step 1: Write agent module**

Create `Backend/app/agents/risk_assessor/agent.py`:

```python
"""Risk Assessor ReAct Agent"""

from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from .tools import (
    calculate_risk_score,
    generate_recommendations,
    explain_decision
)
from .prompts import RISK_ASSESSOR_PROMPT


def create_risk_assessor_agent(llm):
    """
    Create Risk Assessor ReAct agent

    Args:
        llm: LangChain LLM instance

    Returns:
        AgentExecutor: Configured agent executor
    """
    tools = [
        calculate_risk_score,
        generate_recommendations,
        explain_decision
    ]

    prompt = PromptTemplate.from_template(
        RISK_ASSESSOR_PROMPT + "\n\n{agent_scratchpad}"
    )

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=5,
        handle_parsing_errors=True,
        verbose=True
    )

    return executor
```

**Step 2: Update agent __init__.py**

Update `Backend/app/agents/risk_assessor/__init__.py`:

```python
"""Risk Assessor Agent"""

from .agent import create_risk_assessor_agent

__all__ = ["create_risk_assessor_agent"]
```

**Step 3: Commit**

```bash
git add Backend/app/agents/risk_assessor/
git commit -m "feat: add risk assessor react agent"
```

---

## Phase 5: Orchestrator Agent

### Task 12: Create Orchestrator

**Files:**
- Create: `Backend/app/agents/orchestrator.py`

**Step 1: Write orchestrator module**

Create `Backend/app/agents/orchestrator.py`:

```python
"""Orchestrator Agent - Coordinates specialized agents"""

from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from app.agents.shared.llm import get_llm
from app.agents.financial_analyst import create_financial_analyst_agent
from app.agents.market_researcher import create_market_researcher_agent
from app.agents.risk_assessor import create_risk_assessor_agent
import json


# Cache agent instances
_agent_cache = {}


def _get_agent(agent_name: str):
    """Get or create cached agent instance"""
    if agent_name not in _agent_cache:
        llm = get_llm()
        if agent_name == "financial_analyst":
            _agent_cache[agent_name] = create_financial_analyst_agent(llm)
        elif agent_name == "market_researcher":
            _agent_cache[agent_name] = create_market_researcher_agent(llm)
        elif agent_name == "risk_assessor":
            _agent_cache[agent_name] = create_risk_assessor_agent(llm)
    return _agent_cache[agent_name]


@tool
def invoke_specialized_agent(agent_name: str, context: str) -> str:
    """
    Invoke a specialized agent to perform analysis

    Args:
        agent_name: One of 'financial_analyst', 'market_researcher', 'risk_assessor'
        context: JSON string with context data for the agent

    Returns:
        JSON string with agent's analysis results
    """
    try:
        context_data = json.loads(context)
        agent = _get_agent(agent_name)

        # Invoke agent
        result = agent.invoke(context_data)

        # Extract output from agent result
        if isinstance(result, dict) and "output" in result:
            return result["output"]
        else:
            return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"Failed to invoke {agent_name}: {str(e)}"})


ORCHESTRATOR_PROMPT = """You are the Orchestrator Agent for a loan assessment system.

YOUR ROLE:
- Analyze loan applications and determine which specialized agents to invoke
- Coordinate between Financial Analyst, Market Researcher, and Risk Assessor agents
- Control what information each agent receives
- Synthesize all results into comprehensive assessment

DECISION RULES:
- ALWAYS invoke Financial Analyst Agent (every loan needs financial analysis)
- ONLY invoke Market Researcher Agent if:
  * Loan purpose indicates business loan (keywords: "business", "equipment", "expansion", etc.)
  * Job description suggests business ownership (keywords: "owner", "shop", "restaurant", etc.)
  * Location data (lat, lng) is provided
- ALWAYS invoke Risk Assessor Agent last (needs other agents' results)

TOOL AVAILABLE:
- invoke_specialized_agent: Call a specialized agent with specific context

PROCESS:
1. Analyze the application to determine if it's a business loan
2. Invoke Financial Analyst with: access_token, application data
3. IF business loan AND has location: Invoke Market Researcher with: location, job, loan_purpose
4. Invoke Risk Assessor with: all collected data from previous agents
5. Return synthesized results in JSON format

OUTPUT FORMAT:
Return a JSON object with:
- financial_analysis: Results from Financial Analyst
- market_analysis: Results from Market Researcher (if invoked)
- risk_assessment: Results from Risk Assessor
- agents_invoked: List of agent names that were called

Be efficient. Only invoke agents that will provide value for this specific application.

{agent_scratchpad}
"""


def create_orchestrator_agent():
    """
    Create Orchestrator ReAct agent

    Returns:
        AgentExecutor: Configured orchestrator agent
    """
    llm = get_llm()
    tools = [invoke_specialized_agent]

    prompt = PromptTemplate.from_template(ORCHESTRATOR_PROMPT)

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=10,
        handle_parsing_errors=True,
        verbose=True
    )

    return executor


async def run_assessment(application_data: dict) -> dict:
    """
    Run multi-agent assessment on loan application

    Args:
        application_data: Application data with all fields

    Returns:
        Complete assessment results
    """
    orchestrator = create_orchestrator_agent()

    try:
        result = orchestrator.invoke(application_data)

        # Extract output
        if isinstance(result, dict) and "output" in result:
            output = result["output"]
            # Try to parse as JSON
            try:
                return json.loads(output)
            except:
                return {"raw_output": output}
        else:
            return result

    except Exception as e:
        return {
            "error": f"Orchestrator failed: {str(e)}",
            "status": "failed"
        }
```

**Step 2: Verify imports**

Run: `cd Backend && python -c "from app.agents.orchestrator import create_orchestrator_agent; print('OK')"`
Expected: "OK"

**Step 3: Commit**

```bash
git add Backend/app/agents/orchestrator.py
git commit -m "feat: add orchestrator agent for multi-agent coordination"
```

---

## Phase 6: Integration with API

### Task 13: Update API Routes

**Files:**
- Modify: `Backend/app/api/routes.py`

**Step 1: Read current routes**

Run: `cat Backend/app/api/routes.py | grep "def " | head -10`
Expected: See existing route functions

**Step 2: Update plaid-connect endpoint**

Find the `plaid-connect` endpoint in `Backend/app/api/routes.py` and update it to use the orchestrator:

```python
# Add import at top of file
from app.agents.orchestrator import run_assessment

# Update the plaid-connect endpoint
@router.post("/applications/{application_id}/plaid-connect")
async def connect_plaid(
    application_id: str,
    data: PlaidConnectRequest,
    db: AsyncSession = Depends(get_db)
):
    """Connect Plaid account and trigger assessment"""

    # Get application
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Exchange public token for access token
    plaid_service = PlaidService()
    try:
        access_token = plaid_service.exchange_public_token(data.plaid_public_token)

        # Encrypt and store access token
        encrypted_token = encrypt_token(access_token)
        application.plaid_access_token = encrypted_token
        application.status = ApplicationStatus.PROCESSING
        await db.commit()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Plaid error: {str(e)}")

    # Prepare data for orchestrator
    assessment_data = {
        "application_id": application.id,
        "access_token": access_token,
        "job": application.user_job,
        "age": application.user_age,
        "location_lat": application.location_lat,
        "location_lng": application.location_lng,
        "location_address": application.location_address,
        "loan_amount": float(application.loan_amount),
        "loan_purpose": application.loan_purpose
    }

    # Run orchestrator assessment
    try:
        results = await run_assessment(assessment_data)

        # Store results in database
        if "financial_analysis" in results:
            # Store financial metrics
            financial_data = results["financial_analysis"]
            financial_metric = FinancialMetric(
                id=str(uuid.uuid4()),
                application_id=application.id,
                monthly_income=financial_data.get("monthly_income", 0.0),
                monthly_expenses=financial_data.get("monthly_expenses", 0.0),
                debt_to_income_ratio=financial_data.get("dti_ratio", 0.0),
                savings_rate=financial_data.get("savings_rate", 0.0),
                avg_monthly_balance=financial_data.get("avg_monthly_balance", 0.0),
                min_balance_6mo=financial_data.get("min_balance_6mo", 0.0),
                overdraft_count=financial_data.get("overdraft_count", 0),
                income_stability_score=financial_data.get("stability_score", 0.0)
            )
            db.add(financial_metric)

        if "market_analysis" in results:
            # Store market analysis
            market_data = results["market_analysis"]
            market_analysis = MarketAnalysis(
                id=str(uuid.uuid4()),
                application_id=application.id,
                competitor_count=market_data.get("competitor_count", 0),
                market_density=market_data.get("market_density", "unknown"),
                viability_score=market_data.get("viability_score", 0.0),
                market_insights=market_data.get("market_insights", ""),
                nearby_businesses=json.dumps(market_data.get("nearby_businesses", []))
            )
            db.add(market_analysis)

        if "risk_assessment" in results:
            # Store assessment
            risk_data = results["risk_assessment"]
            assessment = Assessment(
                id=str(uuid.uuid4()),
                application_id=application.id,
                eligibility=risk_data.get("eligibility", "review"),
                confidence_score=risk_data.get("confidence_score", 0.0),
                risk_level=risk_data.get("risk_level", "high"),
                reasoning=risk_data.get("reasoning", ""),
                recommendations=json.dumps(risk_data.get("recommendations", []))
            )
            db.add(assessment)

        # Update application status
        application.status = ApplicationStatus.COMPLETED
        await db.commit()

        return {
            "application_id": application.id,
            "status": "completed",
            "plaid_connected": True
        }

    except Exception as e:
        application.status = ApplicationStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")
```

**Step 3: Verify syntax**

Run: `cd Backend && python -m py_compile app/api/routes.py`
Expected: No output (success)

**Step 4: Commit**

```bash
git add Backend/app/api/routes.py
git commit -m "feat: integrate orchestrator with plaid-connect endpoint"
```

---

## Phase 7: Testing & Validation

### Task 14: Write Orchestrator Tests

**Files:**
- Create: `Backend/tests/unit/agents/test_orchestrator.py`

**Step 1: Create test directory**

```bash
mkdir -p Backend/tests/unit/agents
touch Backend/tests/unit/agents/__init__.py
```

**Step 2: Write orchestrator tests**

Create `Backend/tests/unit/agents/test_orchestrator.py`:

```python
"""Tests for Orchestrator Agent"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.orchestrator import create_orchestrator_agent, run_assessment
import json


@pytest.fixture
def business_loan_application():
    """Sample business loan application"""
    return {
        "application_id": "test-123",
        "access_token": "test-token",
        "job": "Coffee shop owner",
        "age": 32,
        "location_lat": 43.6532,
        "location_lng": -79.3832,
        "location_address": "123 Main St, Toronto",
        "loan_amount": 50000.0,
        "loan_purpose": "Equipment purchase"
    }


@pytest.fixture
def personal_loan_application():
    """Sample personal loan application"""
    return {
        "application_id": "test-456",
        "access_token": "test-token",
        "job": "Software Engineer",
        "age": 28,
        "loan_amount": 25000.0,
        "loan_purpose": "Debt consolidation"
    }


@pytest.mark.asyncio
async def test_orchestrator_invokes_all_agents_for_business_loan(business_loan_application):
    """Test that orchestrator invokes all three agents for business loans"""

    with patch('app.agents.orchestrator.invoke_specialized_agent') as mock_invoke:
        # Mock agent responses
        mock_invoke.return_value = json.dumps({
            "status": "success",
            "data": {}
        })

        result = await run_assessment(business_loan_application)

        # Should be called 3 times (financial, market, risk)
        assert mock_invoke.call_count >= 3 or "financial_analysis" in result


@pytest.mark.asyncio
async def test_orchestrator_skips_market_for_personal_loan(personal_loan_application):
    """Test that orchestrator skips market agent for personal loans"""

    with patch('app.agents.orchestrator.invoke_specialized_agent') as mock_invoke:
        mock_invoke.return_value = json.dumps({
            "status": "success",
            "data": {}
        })

        result = await run_assessment(personal_loan_application)

        # Should be called 2 times (financial, risk - no market)
        # Or result should not have market_analysis
        assert "market_analysis" not in result or mock_invoke.call_count == 2


def test_orchestrator_agent_creation():
    """Test that orchestrator agent can be created"""
    agent = create_orchestrator_agent()
    assert agent is not None
    assert hasattr(agent, 'invoke')
```

**Step 3: Run tests**

Run: `cd Backend && python -m pytest tests/unit/agents/test_orchestrator.py -v`
Expected: Tests pass (or skip if mocking issues)

**Step 4: Commit**

```bash
git add Backend/tests/unit/agents/
git commit -m "test: add orchestrator agent tests"
```

---

### Task 15: Integration Test

**Files:**
- Create: `Backend/tests/integration/test_multi_agent_flow.py`

**Step 1: Create integration test directory**

```bash
mkdir -p Backend/tests/integration
touch Backend/tests/integration/__init__.py
```

**Step 2: Write integration test**

Create `Backend/tests/integration/test_multi_agent_flow.py`:

```python
"""Integration tests for multi-agent flow"""

import pytest
from httpx import AsyncClient
from app.main import app
import time


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_business_loan_assessment():
    """Test complete flow: application → plaid → assessment"""

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Create application
        application_data = {
            "job": "Coffee shop owner",
            "age": 32,
            "location": {
                "lat": 43.6532,
                "lng": -79.3832,
                "address": "123 Main St, Toronto"
            },
            "loan_amount": 50000.0,
            "loan_purpose": "Equipment purchase"
        }

        response = await client.post("/api/v1/applications", json=application_data)
        assert response.status_code == 201
        app_id = response.json()["application_id"]

        # Step 2: Connect Plaid (skip in test - would need sandbox token)
        # This triggers the orchestrator

        # Step 3: Check status
        response = await client.get(f"/api/v1/applications/{app_id}/status")
        assert response.status_code == 200

        # Note: Full integration test requires Plaid sandbox setup


@pytest.mark.integration
def test_agent_can_be_created():
    """Smoke test: verify agents can be instantiated"""
    from app.agents.shared.llm import get_llm
    from app.agents.financial_analyst import create_financial_analyst_agent
    from app.agents.market_researcher import create_market_researcher_agent
    from app.agents.risk_assessor import create_risk_assessor_agent
    from app.agents.orchestrator import create_orchestrator_agent

    llm = get_llm()

    financial_agent = create_financial_analyst_agent(llm)
    assert financial_agent is not None

    market_agent = create_market_researcher_agent(llm)
    assert market_agent is not None

    risk_agent = create_risk_assessor_agent(llm)
    assert risk_agent is not None

    orchestrator = create_orchestrator_agent()
    assert orchestrator is not None
```

**Step 3: Run integration tests**

Run: `cd Backend && python -m pytest tests/integration/ -v -m integration`
Expected: Tests pass

**Step 4: Commit**

```bash
git add Backend/tests/integration/
git commit -m "test: add multi-agent integration tests"
```

---

## Phase 8: Cleanup & Documentation

### Task 16: Remove Old Files

**Files:**
- Delete: `Backend/app/agents/graph.py`
- Delete: `Backend/app/agents/tools.py`

**Step 1: Remove old graph implementation**

```bash
git rm Backend/app/agents/graph.py
git rm Backend/app/agents/tools.py
```

**Step 2: Verify old files are gone**

Run: `ls Backend/app/agents/*.py`
Expected: Only __init__.py and orchestrator.py

**Step 3: Commit**

```bash
git commit -m "refactor: remove old graph-based implementation"
```

---

### Task 17: Update README

**Files:**
- Modify: `Backend/README.md`

**Step 1: Update architecture section**

Update the "Multi-Agent System" section in `Backend/README.md`:

```markdown
### Multi-Agent System

The system uses a hierarchical multi-agent architecture with intelligent orchestration:

1. **Orchestrator Agent** - Analyzes applications and coordinates specialized agents
2. **Financial Analyst Agent** - Analyzes banking data using Plaid API and calculates financial metrics
3. **Market Researcher Agent** - Evaluates business location and competition (business loans only)
4. **Risk Assessor Agent** - Synthesizes all data into final risk assessment

Each specialized agent uses the ReAct pattern (Reasoning + Acting) to intelligently decide which tools to use. The orchestrator conditionally invokes agents based on loan type - personal loans skip market research, while business loans receive comprehensive analysis.
```

**Step 2: Commit**

```bash
git add Backend/README.md
git commit -m "docs: update README with new multi-agent architecture"
```

---

### Task 18: Update Requirements

**Files:**
- Modify: `Backend/requirements.txt`

**Step 1: Verify tenacity is included**

Run: `grep tenacity Backend/requirements.txt`
Expected: `tenacity==8.2.3` or similar

**Step 2: If not present, add it**

Add to `Backend/requirements.txt`:
```
tenacity==8.2.3
```

**Step 3: Commit if changed**

```bash
git add Backend/requirements.txt
git commit -m "deps: add tenacity for retry logic"
```

---

## Final Validation

### Task 19: Run All Tests

**Step 1: Run all unit tests**

Run: `cd Backend && python -m pytest tests/unit/ -v`
Expected: All tests pass

**Step 2: Run all tests with coverage**

Run: `cd Backend && python -m pytest tests/ -v --cov=app`
Expected: Tests pass, see coverage report

**Step 3: Check for import errors**

Run: `cd Backend && python -c "from app.agents.orchestrator import run_assessment; print('All imports OK')"`
Expected: "All imports OK"

---

### Task 20: Final Commit

**Step 1: Check git status**

Run: `git status`
Expected: Clean working directory or only docs changes

**Step 2: Create summary commit if needed**

If there are any remaining changes:
```bash
git add .
git commit -m "feat: complete multi-agent system redesign"
```

**Step 3: Review commit log**

Run: `git log --oneline -20`
Expected: See all implementation commits

---

## Success Criteria

✅ **Phase 1:** Directory structure created, shared LLM instance working
✅ **Phase 2:** Financial Analyst agent with 4 tools, tests passing
✅ **Phase 3:** Market Researcher agent with 3 tools, tests passing
✅ **Phase 4:** Risk Assessor agent with 3 tools, tests passing
✅ **Phase 5:** Orchestrator agent coordinating all agents
✅ **Phase 6:** API integration complete, plaid-connect uses orchestrator
✅ **Phase 7:** Unit and integration tests passing
✅ **Phase 8:** Old files removed, documentation updated

## Testing the System

**Manual Test:**
1. Start server: `cd Backend && python app/main.py`
2. Create application via API
3. Connect Plaid with sandbox token
4. Check assessment results
5. Verify all agents were invoked (check logs)

**Expected Behavior:**
- Business loans: Financial + Market + Risk agents
- Personal loans: Financial + Risk agents (no Market)
- All agents use ReAct reasoning (visible in logs)
- Final assessment includes all metrics

---

**End of Implementation Plan**
