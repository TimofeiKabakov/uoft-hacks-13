# Multi-Agent Loan Assessment System - Redesign Specification

**Date:** 2026-01-18
**Project:** LLM-Based Loan Eligibility Assessment Backend
**Status:** Design Complete - Ready for Implementation

---

## Executive Summary

This document specifies a complete redesign of the loan assessment backend to implement a true multi-agent architecture. The current implementation uses a simple linear pipeline (financial → market → decision) with only the final step using LLM reasoning. The new design creates a hierarchical multi-agent system where an intelligent orchestrator coordinates three specialized ReAct agents, each capable of reasoning about which tools to use.

### Key Design Decisions

1. **Smart Orchestrator** - LLM-powered orchestrator analyzes application type and decides which agents to invoke
2. **ReAct Agents** - Each specialized agent uses the ReAct pattern (Reasoning + Acting) to decide which tools to call
3. **Orchestrator-Directed Communication** - Orchestrator controls what information flows between agents
4. **Agent-Specific Tools** - Each agent has its own tool files for clear ownership and organization
5. **Conditional Agent Invocation** - Market Researcher only invoked for business loans with location data
6. **Retry with Fallback** - Each agent retries once on failure, then uses fallback logic
7. **Shared LLM Instance** - All agents share Gemini Pro for cost efficiency

---

## 1. System Architecture

### 1.1 Agent Hierarchy

```
Orchestrator Agent (app/agents/orchestrator.py)
├─ Analyzes loan application type and context
├─ Decides which specialized agents to invoke
├─ Controls information flow between agents
└─ Synthesizes all results into final assessment

Specialized ReAct Agents:
├─ Financial Analyst Agent (app/agents/financial_analyst/agent.py)
│  └─ Tools: fetch_plaid_transactions, calculate_dti_ratio,
│             analyze_cash_flow, assess_income_stability
│
├─ Market Researcher Agent (app/agents/market_researcher/agent.py)
│  └─ Tools: search_competitors, analyze_market_saturation,
│             assess_location_viability
│
└─ Risk Assessor Agent (app/agents/risk_assessor/agent.py)
   └─ Tools: calculate_risk_score, generate_recommendations,
             explain_decision
```

### 1.2 Orchestrator Decision Logic

**Agent Invocation Rules:**
- **Always invokes:** Financial Analyst Agent (every loan needs financial analysis)
- **Conditionally invokes:** Market Researcher Agent (only for business loans with location data)
- **Always invokes:** Risk Assessor Agent (makes final decision with available data)

**Business Loan Detection:**
```python
is_business_loan = (
    "business" in loan_purpose.lower() or
    "equipment" in loan_purpose.lower() or
    job_description indicates self-employment or business ownership
)

has_location = (location_lat and location_lng are provided)

invoke_market_agent = is_business_loan and has_location
```

### 1.3 Communication Pattern

The Orchestrator controls information flow between agents:

1. **Financial Analyst receives:**
   - Full application data
   - Plaid access token
   - Loan amount and purpose

2. **Market Researcher receives (if invoked):**
   - Job/business type
   - Location (lat, lng, address)
   - Loan purpose
   - (Does NOT see financial data initially)

3. **Risk Assessor receives:**
   - Full application data
   - Financial analysis results
   - Market analysis results (if available)
   - Previous agents' reasoning

---

## 2. ReAct Agent Implementation

### 2.1 How ReAct Agents Work

Each specialized agent uses the **ReAct pattern** (Reasoning + Acting), which allows them to:
- Think through problems step-by-step
- Decide which tools to use
- Adapt based on tool results
- Handle partial or missing data

**Example: Financial Analyst Agent Reasoning**
```
Thought: I need to analyze this applicant's financial health
Action: fetch_plaid_transactions
Action Input: {"access_token": "xxx", "days": 180}
Observation: Retrieved 180 days of transactions, 450 total transactions

Thought: I see regular income deposits, let me assess stability
Action: assess_income_stability
Action Input: {"transactions": "[...]"}
Observation: Income stability score: 87/100 (consistent bi-weekly deposits)

Thought: Now I need to calculate debt-to-income ratio
Action: calculate_dti_ratio
Action Input: {"transactions": "[...]"}
Observation: DTI ratio: 32% (healthy range)

Thought: Let me analyze cash flow patterns
Action: analyze_cash_flow
Action Input: {"transactions": "[...]"}
Observation: Avg balance: $8,500, Min balance: $2,100, Overdrafts: 0

Thought: I have comprehensive financial data to provide analysis
Final Answer: {
  "monthly_income": 6500.0,
  "monthly_expenses": 4200.0,
  "debt_to_income_ratio": 32.0,
  "savings_rate": 35.4,
  "avg_monthly_balance": 8500.0,
  "income_stability_score": 87.0,
  "overdraft_count": 0,
  "analysis": "Strong financial health with consistent income..."
}
```

### 2.2 Agent Structure

Each agent folder contains:

```
app/agents/<agent_name>/
├── __init__.py          # Exports create_agent function
├── agent.py             # ReAct agent definition
├── tools.py             # LangChain Tool wrappers
└── prompts.py           # Agent-specific system prompts
```

**Agent Creation Pattern:**
```python
# app/agents/financial_analyst/agent.py

from langchain.agents import create_react_agent, AgentExecutor
from .tools import (
    fetch_plaid_transactions,
    calculate_dti_ratio,
    analyze_cash_flow,
    assess_income_stability
)
from .prompts import FINANCIAL_ANALYST_PROMPT

def create_financial_analyst_agent(llm):
    """Create Financial Analyst ReAct agent"""
    tools = [
        fetch_plaid_transactions,
        calculate_dti_ratio,
        analyze_cash_flow,
        assess_income_stability
    ]

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=FINANCIAL_ANALYST_PROMPT
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=5,
        handle_parsing_errors=True,
        verbose=True  # For debugging
    )

    return executor
```

### 2.3 Error Handling (Retry with Fallback)

Each tool implements retry logic:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@tool
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_plaid_transactions(access_token: str, days: int = 180) -> str:
    """
    Fetch transaction history from Plaid API

    Args:
        access_token: Plaid access token
        days: Number of days of history to fetch

    Returns:
        JSON string with transaction data
    """
    try:
        plaid_service = PlaidService()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        result = plaid_service.get_transactions(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )

        return json.dumps(result)

    except PlaidError as e:
        raise ToolException(f"Plaid API error: {str(e)}")
    except Exception as e:
        raise ToolException(f"Failed to fetch transactions: {str(e)}")
```

**Fallback Strategy:**
- If tool fails after retry, agent receives error as observation
- Agent can try alternative approach or work with partial data
- If agent completely fails, orchestrator uses rule-based fallback

---

## 3. Orchestrator Implementation

### 3.1 Orchestrator Workflow

```python
Step 1: Analyze Application
Input: Loan application data
↓
Thought: "Is this a business loan? Does it have location data?"
Decision: Determine which agents to invoke
↓

Step 2: Invoke Financial Analyst
Context: Full application + Plaid token
↓
Financial Agent uses tools → Returns metrics
↓
Orchestrator stores: financial_analysis
↓

Step 3: Conditionally Invoke Market Researcher
IF business_loan AND has_location:
    Context: Business type + location
    ↓
    Market Agent uses tools → Returns market data
    ↓
    Orchestrator stores: market_analysis
ELSE:
    Skip market analysis
↓

Step 4: Invoke Risk Assessor
Context: Application + financial_analysis + market_analysis (if available)
↓
Risk Agent uses tools → Returns final assessment
↓
Orchestrator stores: risk_assessment
↓

Step 5: Synthesize Results
Combine all outputs → Return to API
```

### 3.2 State Management

The orchestrator maintains an accumulating state object:

```python
{
  "application": {
    "id": "uuid",
    "job": "Coffee shop owner",
    "age": 32,
    "loan_amount": 50000.0,
    "loan_purpose": "Equipment purchase",
    "location": {...},
    "plaid_access_token": "encrypted_token"
  },

  "financial_analysis": {
    "monthly_income": 6500.0,
    "debt_to_income_ratio": 32.0,
    "savings_rate": 35.4,
    ...
  },

  "market_analysis": {
    "competitor_count": 5,
    "market_density": "medium",
    "viability_score": 72.0,
    ...
  },

  "risk_assessment": {
    "eligibility": "approved",
    "confidence_score": 85.0,
    "risk_level": "low",
    "reasoning": "...",
    "recommendations": [...]
  },

  "metadata": {
    "agents_invoked": ["financial_analyst", "market_researcher", "risk_assessor"],
    "execution_time_ms": 4250,
    "execution_log": [...]
  }
}
```

### 3.3 Orchestrator as ReAct Agent

The orchestrator itself is a ReAct agent with a special tool:

```python
# app/agents/orchestrator.py

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
    context_data = json.loads(context)

    if agent_name == "financial_analyst":
        agent = get_financial_analyst_agent()
        result = agent.invoke(context_data)
        return json.dumps(result)

    elif agent_name == "market_researcher":
        agent = get_market_researcher_agent()
        result = agent.invoke(context_data)
        return json.dumps(result)

    elif agent_name == "risk_assessor":
        agent = get_risk_assessor_agent()
        result = agent.invoke(context_data)
        return json.dumps(result)

    else:
        raise ValueError(f"Unknown agent: {agent_name}")


def create_orchestrator_agent(llm):
    """Create Orchestrator ReAct agent"""
    tools = [invoke_specialized_agent]

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=ORCHESTRATOR_PROMPT
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return executor
```

---

## 4. Tool Definitions

### 4.1 Financial Analyst Tools

**File:** `app/agents/financial_analyst/tools.py`

```python
from langchain.tools import tool
from app.services.plaid_service import PlaidService
from app.services.financial_calculator import FinancialCalculator
import json

@tool
def fetch_plaid_transactions(access_token: str, days: int = 180) -> str:
    """
    Fetch transaction history from Plaid API

    Args:
        access_token: Plaid access token
        days: Number of days of history to fetch (default: 180)

    Returns:
        JSON string with transaction data including:
        - transactions: List of transaction objects
        - income_streams: Detected income sources
        - balance_history: Historical balance data
    """
    # Implementation with retry logic
    pass

@tool
def calculate_dti_ratio(transactions: str) -> str:
    """
    Calculate debt-to-income ratio from transaction data

    Args:
        transactions: JSON string with transaction data

    Returns:
        JSON string with:
        - dti_ratio: Debt-to-income percentage
        - monthly_debt: Total monthly debt payments
        - monthly_income: Average monthly income
    """
    # Implementation
    pass

@tool
def analyze_cash_flow(transactions: str) -> str:
    """
    Analyze balance trends and cash flow patterns

    Args:
        transactions: JSON string with transaction data

    Returns:
        JSON string with:
        - avg_monthly_balance: Average balance over period
        - min_balance_6mo: Minimum balance in 6 months
        - overdraft_count: Number of overdraft incidents
        - balance_trend: "increasing", "stable", or "decreasing"
    """
    # Implementation
    pass

@tool
def assess_income_stability(transactions: str) -> str:
    """
    Score income consistency and stability (0-100)

    Args:
        transactions: JSON string with transaction data

    Returns:
        JSON string with:
        - stability_score: 0-100 score
        - income_regularity: "regular", "irregular", or "variable"
        - income_sources: Number of distinct income sources
        - income_trend: "growing", "stable", or "declining"
    """
    # Implementation
    pass
```

### 4.2 Market Researcher Tools

**File:** `app/agents/market_researcher/tools.py`

```python
@tool
def search_competitors(lat: float, lng: float, business_type: str, radius_miles: float = 2.0) -> str:
    """
    Search for competing businesses using Google Places API

    Args:
        lat: Latitude
        lng: Longitude
        business_type: Type of business (e.g., "cafe", "restaurant")
        radius_miles: Search radius in miles (default: 2.0)

    Returns:
        JSON string with list of competitors:
        - name: Business name
        - rating: Google rating
        - distance_miles: Distance from location
        - type: Business type
        - price_level: Price level (1-4)
    """
    # Implementation
    pass

@tool
def analyze_market_saturation(competitors: str, business_type: str) -> str:
    """
    Assess market density and saturation level

    Args:
        competitors: JSON string with competitor data
        business_type: Type of business

    Returns:
        JSON string with:
        - density: "low", "medium", or "high"
        - saturation_score: 0-100 (higher = more saturated)
        - avg_competitor_rating: Average rating of competitors
        - market_gap_analysis: Insights about market gaps
    """
    # Implementation
    pass

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
        - foot_traffic_estimate: "low", "medium", or "high"
        - area_characteristics: Description of area
        - location_strengths: List of advantages
        - location_weaknesses: List of disadvantages
    """
    # Implementation
    pass
```

### 4.3 Risk Assessor Tools

**File:** `app/agents/risk_assessor/tools.py`

```python
@tool
def calculate_risk_score(financial_metrics: str, market_analysis: str) -> str:
    """
    Calculate overall risk score from all metrics

    Args:
        financial_metrics: JSON string with financial analysis
        market_analysis: JSON string with market analysis (may be empty)

    Returns:
        JSON string with:
        - risk_score: 0-100 (higher = lower risk)
        - risk_level: "low", "medium", or "high"
        - risk_factors: List of identified risks
        - mitigating_factors: List of positive factors
    """
    # Implementation
    pass

@tool
def generate_recommendations(assessment_data: str) -> str:
    """
    Generate actionable recommendations based on assessment

    Args:
        assessment_data: JSON string with full assessment data

    Returns:
        JSON string with:
        - recommendations: List of actionable suggestions
        - priorities: Priority order for recommendations
        - timeline: Suggested timeline for each recommendation
    """
    # Implementation
    pass

@tool
def explain_decision(assessment_data: str) -> str:
    """
    Generate human-readable explanation of the decision

    Args:
        assessment_data: JSON string with full assessment data

    Returns:
        JSON string with:
        - reasoning: Detailed explanation
        - key_factors: Most important decision factors
        - confidence_explanation: Why confidence score is X
    """
    # Implementation
    pass
```

### 4.4 Tool Implementation Notes

**Key Requirements:**
1. All tools accept and return JSON strings (LangChain requirement)
2. Each tool has comprehensive docstrings (used by LLM to understand tool purpose)
3. Tools wrap existing services (PlaidService, GoogleService, FinancialCalculator)
4. Retry logic with exponential backoff for external API calls
5. Structured error messages that agents can understand

---

## 5. Data Flow & API Integration

### 5.1 Complete Application Processing Flow

```
1. POST /api/v1/applications
   ↓
   Create application record (status: "pending_plaid")
   Store in database
   Return: {application_id, status: "pending_plaid"}
   ↓

2. POST /api/v1/applications/{id}/plaid-connect
   ↓
   Exchange Plaid public token for access token
   Encrypt access token using Fernet
   Update application record
   ↓
   Trigger Orchestrator Agent (async)
   ↓

   ┌─────────────────────────────────────────────────┐
   │     Orchestrator Agent Execution                │
   ├─────────────────────────────────────────────────┤
   │                                                 │
   │ 1. Analyze Application Type                     │
   │    Thought: "Is this business or personal?"     │
   │    Decision: business loan, has location        │
   │                                                 │
   │ 2. Invoke Financial Analyst Agent               │
   │    Action: invoke_specialized_agent             │
   │    Input: {agent: "financial_analyst", ...}     │
   │    ↓                                            │
   │    Financial Agent runs (uses 4 tools)          │
   │    ↓                                            │
   │    Returns: financial_metrics                   │
   │    ↓                                            │
   │    Store in DB: financial_metrics table         │
   │                                                 │
   │ 3. Invoke Market Researcher Agent               │
   │    Action: invoke_specialized_agent             │
   │    Input: {agent: "market_researcher", ...}     │
   │    ↓                                            │
   │    Market Agent runs (uses 3 tools)             │
   │    ↓                                            │
   │    Returns: market_analysis                     │
   │    ↓                                            │
   │    Store in DB: market_analysis table           │
   │                                                 │
   │ 4. Invoke Risk Assessor Agent                   │
   │    Action: invoke_specialized_agent             │
   │    Input: {agent: "risk_assessor",              │
   │            context: financial + market}         │
   │    ↓                                            │
   │    Risk Agent runs (uses 3 tools)               │
   │    ↓                                            │
   │    Returns: final_assessment                    │
   │    ↓                                            │
   │    Store in DB: assessments table               │
   │                                                 │
   │ 5. Update Application Status                    │
   │    UPDATE applications SET status='completed'   │
   │                                                 │
   └─────────────────────────────────────────────────┘
   ↓
   Return: {status: "processing", application_id}
   ↓

3. GET /api/v1/applications/{id}/assessment
   ↓
   Retrieve from database:
   - Application data
   - Financial metrics
   - Market analysis (if exists)
   - Assessment results
   ↓
   Return: Complete assessment JSON
```

### 5.2 Database Updates During Execution

```sql
-- After Financial Analyst completes
INSERT INTO financial_metrics (
    id,
    application_id,
    monthly_income,
    monthly_expenses,
    debt_to_income_ratio,
    savings_rate,
    avg_monthly_balance,
    min_balance_6mo,
    overdraft_count,
    income_stability_score,
    raw_plaid_data,
    calculated_at
) VALUES (...);

-- After Market Researcher completes (if invoked)
INSERT INTO market_analysis (
    id,
    application_id,
    competitor_count,
    market_density,
    viability_score,
    market_insights,
    nearby_businesses,
    analyzed_at
) VALUES (...);

-- After Risk Assessor completes
INSERT INTO assessments (
    id,
    application_id,
    eligibility,
    confidence_score,
    risk_level,
    reasoning,
    recommendations,
    assessed_at
) VALUES (...);

-- Finally, update application status
UPDATE applications
SET status = 'completed',
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?;
```

### 5.3 Error Scenarios & Handling

| Scenario | Handler | Outcome |
|----------|---------|---------|
| Financial Agent fails | Fallback to basic calculations | Continue with degraded metrics, lower confidence |
| Market Agent fails | Skip market analysis | Continue without market data, note in assessment |
| Risk Agent fails | Return "review" status | Mark for manual review, return partial results |
| Plaid API down | Retry with backoff | If still fails, return error to user |
| Google API down | Use cached/default data | Continue with limited market insights |
| LLM timeout | Retry once | If still fails, use rule-based fallback |
| Complete orchestrator failure | Catch and log | Update status to "failed", notify user |

---

## 6. LangChain Integration

### 6.1 Architecture Decision: Pure LangChain (No LangGraph)

**Why NOT LangGraph:**
- LangGraph is designed for fixed workflow graphs
- Our orchestrator needs **dynamic** decision-making (which agents to call)
- Agent invocation itself is a tool the orchestrator uses
- More flexibility with pure ReAct agents

**Why Pure LangChain:**
- Orchestrator is a ReAct agent with `invoke_specialized_agent` tool
- Can dynamically decide which agents to call based on reasoning
- Each specialized agent is also a ReAct agent with domain-specific tools
- Clean separation of concerns

### 6.2 Shared LLM Instance

**File:** `app/agents/shared/llm.py`

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings

settings = get_settings()

# Singleton LLM instance shared by all agents
_llm_instance = None

def get_llm():
    """Get shared LLM instance for all agents"""
    global _llm_instance

    if _llm_instance is None:
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            max_output_tokens=2048
        )

    return _llm_instance
```

### 6.3 Prompt Engineering

Each agent has a specialized system prompt that defines its role and capabilities.

**Orchestrator Prompt:**
```python
ORCHESTRATOR_PROMPT = """
You are the Orchestrator Agent for a loan assessment system. Your role is to:
1. Analyze loan applications and determine which specialized agents to invoke
2. Coordinate between Financial Analyst, Market Researcher, and Risk Assessor agents
3. Control what information each agent receives
4. Synthesize all results into a comprehensive assessment

DECISION RULES:
- ALWAYS invoke Financial Analyst Agent (every loan needs financial analysis)
- ONLY invoke Market Researcher Agent if:
  * The loan purpose indicates a business loan (equipment, business expansion, etc.)
  * Location data (lat, lng) is provided
  * Job description suggests business ownership
- ALWAYS invoke Risk Assessor Agent last (needs other agents' results)

TOOL AVAILABLE:
- invoke_specialized_agent: Call a specialized agent with specific context

PROCESS:
1. Analyze the application to determine loan type
2. Invoke Financial Analyst with full application data
3. IF business loan AND has location: Invoke Market Researcher
4. Invoke Risk Assessor with all collected data
5. Return synthesized results

Be thorough but efficient. Only invoke agents that will provide value.
"""
```

**Financial Analyst Prompt:**
```python
FINANCIAL_ANALYST_PROMPT = """
You are the Financial Analyst Agent. Your role is to:
1. Analyze applicant's financial health using Plaid banking data
2. Calculate key financial metrics (DTI, savings rate, cash flow)
3. Assess income stability and spending patterns
4. Provide comprehensive financial assessment

TOOLS AVAILABLE:
- fetch_plaid_transactions: Get transaction history from Plaid
- calculate_dti_ratio: Calculate debt-to-income ratio
- analyze_cash_flow: Analyze balance trends and cash flow
- assess_income_stability: Score income consistency

PROCESS:
1. Fetch transaction data using Plaid access token
2. Assess income stability first
3. Calculate DTI ratio and cash flow metrics
4. Analyze spending patterns
5. Return comprehensive financial metrics

Focus on: income stability, debt levels, savings behavior, spending patterns.
Be thorough but efficient with tool usage.
"""
```

**Market Researcher Prompt:**
```python
MARKET_RESEARCHER_PROMPT = """
You are the Market Researcher Agent. Your role is to:
1. Analyze business location and market viability
2. Assess competition in the area
3. Evaluate market saturation
4. Provide market insights for business loan decisions

TOOLS AVAILABLE:
- search_competitors: Find competing businesses nearby
- analyze_market_saturation: Assess market density
- assess_location_viability: Evaluate location fit

PROCESS:
1. Search for competitors in the business area
2. Analyze market saturation level
3. Assess location viability for this business type
4. Return comprehensive market analysis

Focus on: competition level, market gaps, location advantages/disadvantages.
"""
```

**Risk Assessor Prompt:**
```python
RISK_ASSESSOR_PROMPT = """
You are the Risk Assessor Agent. Your role is to:
1. Synthesize financial and market data into risk assessment
2. Calculate overall risk score
3. Generate actionable recommendations
4. Provide clear explanation of decision

TOOLS AVAILABLE:
- calculate_risk_score: Compute risk from all metrics
- generate_recommendations: Create actionable suggestions
- explain_decision: Generate human-readable reasoning

PROCESS:
1. Review financial metrics from Financial Analyst
2. Review market analysis from Market Researcher (if available)
3. Calculate comprehensive risk score
4. Generate specific recommendations
5. Explain the decision clearly

Focus on: overall risk, approval likelihood, actionable recommendations.
Make decisions that balance risk with opportunity.
"""
```

---

## 7. Project Structure

### 7.1 Complete Directory Layout

```
Backend/
├── app/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   │
│   │   ├── orchestrator.py              # Main orchestrator agent
│   │   │
│   │   ├── financial_analyst/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                 # Financial ReAct agent
│   │   │   ├── tools.py                 # Plaid & calculation tools
│   │   │   └── prompts.py               # Agent-specific prompts
│   │   │
│   │   ├── market_researcher/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                 # Market ReAct agent
│   │   │   ├── tools.py                 # Google API tools
│   │   │   └── prompts.py               # Agent-specific prompts
│   │   │
│   │   ├── risk_assessor/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                 # Risk ReAct agent
│   │   │   ├── tools.py                 # Scoring tools
│   │   │   └── prompts.py               # Agent-specific prompts
│   │   │
│   │   └── shared/
│   │       ├── __init__.py
│   │       └── llm.py                   # Shared LLM instance
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                    # FastAPI endpoints (update to use orchestrator)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # Settings (existing)
│   │   └── security.py                  # Encryption (existing)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                    # SQLAlchemy models (existing)
│   │   └── session.py                   # DB session (existing)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                   # Pydantic schemas (existing)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── plaid_service.py             # Plaid integration (existing)
│   │   ├── google_service.py            # Google APIs (existing)
│   │   └── financial_calculator.py      # Calculations (existing)
│   │
│   └── main.py                          # FastAPI app (existing)
│
├── tests/
│   ├── __init__.py
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── test_orchestrator.py
│   │   │   ├── test_financial_analyst.py
│   │   │   ├── test_market_researcher.py
│   │   │   └── test_risk_assessor.py
│   │   │
│   │   ├── test_schemas.py              # (existing)
│   │   ├── test_plaid_service.py        # (existing)
│   │   ├── test_google_service.py       # (existing)
│   │   ├── test_financial_calculator.py # (existing)
│   │   ├── test_config.py               # (existing)
│   │   ├── test_database.py             # (existing)
│   │   └── test_api.py                  # (existing)
│   │
│   └── integration/
│       ├── __init__.py
│       └── test_multi_agent_flow.py     # End-to-end tests
│
├── docs/
│   └── plans/
│       ├── 2026-01-18-loan-assessment-system-design.md    # (existing)
│       └── 2026-01-18-multi-agent-redesign.md             # (this document)
│
├── scripts/
│   ├── setup.sh                         # (existing)
│   └── generate_encryption_key.py       # (existing)
│
├── .env.example                         # (existing)
├── .gitignore                           # (existing)
├── requirements.txt                     # (update with new dependencies)
├── pytest.ini                           # (existing)
└── README.md                            # (update with new architecture)
```

### 7.2 Files to Remove

```
app/agents/graph.py          # Old LangGraph implementation
app/agents/tools.py          # Old shared tools file
```

### 7.3 Files to Keep (Reuse)

All existing service files remain unchanged:
- `app/services/plaid_service.py`
- `app/services/google_service.py`
- `app/services/financial_calculator.py`
- All database models and schemas
- All existing unit tests for services

---

## 8. Testing Strategy

### 8.1 Unit Tests for Agents

**Test: Financial Analyst Agent**
```python
# tests/unit/agents/test_financial_analyst.py

import pytest
from unittest.mock import Mock, patch
from app.agents.financial_analyst.agent import create_financial_analyst_agent
from app.agents.shared.llm import get_llm

def test_financial_analyst_with_healthy_metrics():
    """Test agent produces correct analysis for healthy finances"""

    # Mock Plaid data
    mock_transactions = {
        "transactions": [...],  # Sample data
        "income_streams": [...]
    }

    # Mock tool responses
    with patch('app.agents.financial_analyst.tools.fetch_plaid_transactions') as mock_fetch:
        mock_fetch.return_value = json.dumps(mock_transactions)

        llm = get_llm()
        agent = create_financial_analyst_agent(llm)

        result = agent.invoke({
            "access_token": "test_token",
            "application_id": "test_123"
        })

        # Assertions
        assert "monthly_income" in result
        assert "debt_to_income_ratio" in result
        assert result["debt_to_income_ratio"] < 50  # Healthy range
        assert "income_stability_score" in result


def test_financial_analyst_handles_missing_data():
    """Test agent adapts when some data is unavailable"""

    with patch('app.agents.financial_analyst.tools.fetch_plaid_transactions') as mock_fetch:
        # Simulate incomplete data
        mock_fetch.side_effect = Exception("Insufficient transaction history")

        llm = get_llm()
        agent = create_financial_analyst_agent(llm)

        result = agent.invoke({
            "access_token": "test_token",
            "application_id": "test_123"
        })

        # Agent should still return something (fallback metrics)
        assert "monthly_income" in result
        assert "error" in result or "limited_data" in result
```

**Test: Orchestrator Agent**
```python
# tests/unit/agents/test_orchestrator.py

def test_orchestrator_skips_market_for_personal_loan():
    """Test orchestrator doesn't invoke market agent for personal loans"""

    application = {
        "id": "test_123",
        "job": "Software Engineer",
        "loan_purpose": "Debt consolidation",
        "loan_amount": 25000.0,
        "age": 35,
        "plaid_access_token": "test_token"
    }

    with patch('app.agents.orchestrator.invoke_specialized_agent') as mock_invoke:
        # Mock only financial and risk agents
        mock_invoke.return_value = json.dumps({"status": "success"})

        orchestrator = create_orchestrator_agent(get_llm())
        result = orchestrator.invoke(application)

        # Verify market agent was NOT called
        call_args = [call[0][0] for call in mock_invoke.call_args_list]
        assert "financial_analyst" in call_args
        assert "risk_assessor" in call_args
        assert "market_researcher" not in call_args


def test_orchestrator_invokes_all_agents_for_business_loan():
    """Test orchestrator invokes all three agents for business loans"""

    application = {
        "id": "test_123",
        "job": "Coffee shop owner",
        "loan_purpose": "Equipment purchase",
        "loan_amount": 50000.0,
        "location": {"lat": 43.6532, "lng": -79.3832},
        "age": 32,
        "plaid_access_token": "test_token"
    }

    with patch('app.agents.orchestrator.invoke_specialized_agent') as mock_invoke:
        mock_invoke.return_value = json.dumps({"status": "success"})

        orchestrator = create_orchestrator_agent(get_llm())
        result = orchestrator.invoke(application)

        # Verify all three agents were called
        call_args = [call[0][0] for call in mock_invoke.call_args_list]
        assert "financial_analyst" in call_args
        assert "market_researcher" in call_args
        assert "risk_assessor" in call_args
```

### 8.2 Integration Tests

```python
# tests/integration/test_multi_agent_flow.py

@pytest.mark.integration
def test_full_business_loan_assessment_flow():
    """Test complete flow: application → all agents → final assessment"""

    # Create test application
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

    # Create application via API
    response = client.post("/api/v1/applications", json=application_data)
    assert response.status_code == 201
    app_id = response.json()["application_id"]

    # Connect Plaid
    response = client.post(
        f"/api/v1/applications/{app_id}/plaid-connect",
        json={"plaid_public_token": "public-sandbox-test"}
    )
    assert response.status_code == 200

    # Wait for assessment to complete (or poll status)
    time.sleep(5)  # In production, use async/polling

    # Get assessment results
    response = client.get(f"/api/v1/applications/{app_id}/assessment")
    assert response.status_code == 200

    result = response.json()

    # Verify all sections are present
    assert "eligibility" in result
    assert result["eligibility"] in ["approved", "denied", "review"]
    assert "confidence_score" in result
    assert "financial_metrics" in result
    assert "market_analysis" in result
    assert "risk_assessment" in result

    # Verify financial metrics
    assert "monthly_income" in result["financial_metrics"]
    assert "debt_to_income_ratio" in result["financial_metrics"]

    # Verify market analysis
    assert "competitor_count" in result["market_analysis"]
    assert "market_density" in result["market_analysis"]

    # Verify assessment
    assert "reasoning" in result
    assert "recommendations" in result
    assert len(result["recommendations"]) > 0
```

### 8.3 Mocking Strategy

**Unit Tests:**
- Mock all LLM calls with predictable responses
- Mock external APIs (Plaid, Google)
- Fast execution, no external dependencies

**Integration Tests:**
- Use real LLM (with rate limiting)
- Mock external APIs OR use sandbox environments
- Test actual agent reasoning and tool usage

**Test Fixtures:**
```python
# tests/conftest.py

@pytest.fixture
def mock_plaid_data():
    """Sample Plaid transaction data"""
    return {
        "transactions": [...],
        "income": [...],
        "balance": {...}
    }

@pytest.fixture
def mock_google_places_data():
    """Sample Google Places competitor data"""
    return {
        "results": [...]
    }

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return Mock(content='{"result": "test"}')
```

---

## 9. Migration Plan

### 9.1 Implementation Phases

**Phase 1: Setup New Structure (No Breaking Changes)**
- Create new agent folders
- Create shared LLM instance
- Set up prompt templates
- Keep old `graph.py` running

**Phase 2: Build Specialized Agents**
- Implement Financial Analyst agent + tools
- Implement Market Researcher agent + tools
- Implement Risk Assessor agent + tools
- Write unit tests for each agent

**Phase 3: Build Orchestrator**
- Implement orchestrator agent
- Add `invoke_specialized_agent` tool
- Write orchestrator decision logic
- Test with mocked specialized agents

**Phase 4: Integration & Testing**
- Wire orchestrator into FastAPI routes
- Run integration tests
- Test error handling and fallbacks
- Performance testing

**Phase 5: Cleanup**
- Remove old `graph.py` file
- Remove old `tools.py` file
- Update documentation
- Final testing

### 9.2 Detailed Task Breakdown

**Phase 1 Tasks:**
1. Create directory structure:
   - `app/agents/financial_analyst/`
   - `app/agents/market_researcher/`
   - `app/agents/risk_assessor/`
   - `app/agents/shared/`
2. Create `app/agents/shared/llm.py` with shared LLM instance
3. Create prompt files for each agent
4. Update `requirements.txt` with LangChain dependencies

**Phase 2 Tasks:**
5. Implement `app/agents/financial_analyst/tools.py`:
   - `fetch_plaid_transactions`
   - `calculate_dti_ratio`
   - `analyze_cash_flow`
   - `assess_income_stability`
6. Implement `app/agents/financial_analyst/agent.py`
7. Write tests: `tests/unit/agents/test_financial_analyst.py`
8. Implement `app/agents/market_researcher/tools.py`:
   - `search_competitors`
   - `analyze_market_saturation`
   - `assess_location_viability`
9. Implement `app/agents/market_researcher/agent.py`
10. Write tests: `tests/unit/agents/test_market_researcher.py`
11. Implement `app/agents/risk_assessor/tools.py`:
    - `calculate_risk_score`
    - `generate_recommendations`
    - `explain_decision`
12. Implement `app/agents/risk_assessor/agent.py`
13. Write tests: `tests/unit/agents/test_risk_assessor.py`

**Phase 3 Tasks:**
14. Implement `app/agents/orchestrator.py`:
    - Create `invoke_specialized_agent` tool
    - Implement orchestrator agent
    - Add decision logic for agent selection
15. Write tests: `tests/unit/agents/test_orchestrator.py`

**Phase 4 Tasks:**
16. Update `app/api/routes.py`:
    - Replace `create_assessment_graph()` with orchestrator
    - Update `/plaid-connect` endpoint to use orchestrator
17. Write integration test: `tests/integration/test_multi_agent_flow.py`
18. Test error scenarios:
    - Plaid API failure
    - Google API failure
    - LLM timeout
    - Individual agent failures
19. Performance testing:
    - Measure end-to-end execution time
    - Optimize if needed

**Phase 5 Tasks:**
20. Remove `app/agents/graph.py`
21. Remove `app/agents/tools.py`
22. Update `README.md` with new architecture
23. Update `IMPLEMENTATION_SUMMARY.md`
24. Final regression testing
25. Commit all changes

### 9.3 Rollback Safety

**Feature Flag Approach:**
```python
# app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    USE_NEW_AGENT_SYSTEM: bool = False  # Feature flag
```

**Conditional Logic in API:**
```python
# app/api/routes.py

@router.post("/applications/{application_id}/plaid-connect")
async def connect_plaid(application_id: str, data: PlaidConnectRequest):
    # ... exchange token ...

    if settings.USE_NEW_AGENT_SYSTEM:
        # Use new orchestrator
        from app.agents.orchestrator import run_assessment
        result = await run_assessment(application)
    else:
        # Use old graph system
        from app.agents.graph import create_assessment_graph
        graph = create_assessment_graph()
        result = await graph.ainvoke(state)

    # ... store results ...
```

This allows:
- Deploying new code without immediately switching
- A/B testing between old and new systems
- Quick rollback if issues arise
- Gradual migration

### 9.4 Database Compatibility

**Good News:** No database schema changes required!

The existing database schema already supports the new multi-agent system:
- `applications` table: unchanged
- `financial_metrics` table: unchanged
- `market_analysis` table: unchanged
- `assessments` table: unchanged

Both old and new systems can read/write the same database structure.

---

## 10. Dependencies & Requirements

### 10.1 Updated requirements.txt

```txt
# Existing dependencies (keep all)
fastapi==0.109.0
uvicorn==0.25.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Plaid
plaid-python==16.0.0

# Google APIs
googlemaps==4.10.0
google-api-python-client==2.111.0

# LangChain (update/add)
langchain==0.1.4
langchain-google-genai==0.0.6
langchain-community==0.0.16

# Utilities
cryptography==41.0.7
tenacity==8.2.3

# Testing
pytest==7.4.4
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.26.0
```

### 10.2 Environment Variables

No new environment variables needed! Reuse existing:

```bash
# LLM
GEMINI_API_KEY=your_gemini_api_key

# Plaid
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox

# Google
GOOGLE_MAPS_API_KEY=your_google_maps_key
GOOGLE_PLACES_API_KEY=your_google_places_key

# Database
DATABASE_URL=sqlite:///./loan_assessment.db

# Security
ENCRYPTION_KEY=your_fernet_encryption_key

# CORS
CORS_ORIGINS=http://localhost:3000

# Feature Flag (optional)
USE_NEW_AGENT_SYSTEM=false  # Set to true when ready to switch
```

---

## 11. Expected Outcomes

### 11.1 What Changes for Users

**User Experience:** UNCHANGED
- Same API endpoints
- Same request/response formats
- Same processing time (or faster with optimizations)

**What's Different Behind the Scenes:**
- Intelligent orchestrator decides which analyses to run
- Each agent reasons about which tools to use
- More adaptive to different loan types
- Better error handling and fallbacks

### 11.2 Performance Expectations

**Execution Time Estimates:**

| Component | Old System | New System | Notes |
|-----------|------------|------------|-------|
| Financial Analysis | 2-3s | 2-4s | Slight overhead from agent reasoning |
| Market Analysis | 1-2s | 1-2s | Same (only when needed) |
| Risk Assessment | 1-2s | 2-3s | More sophisticated reasoning |
| **Total (business loan)** | 4-7s | 5-9s | ~1-2s overhead acceptable |
| **Total (personal loan)** | 3-5s | 3-6s | Skips market analysis |

**LLM API Calls:**

| Scenario | Old System | New System |
|----------|------------|------------|
| Business loan | 1 call (decision agent) | 4 calls (orchestrator + 3 agents) |
| Personal loan | 1 call (decision agent) | 3 calls (orchestrator + 2 agents) |

**Cost Impact:**
- ~4x increase in LLM API calls
- But: Gemini Pro is cheap (~$0.00025 per 1K tokens)
- Estimated cost per assessment: < $0.01
- Acceptable for demo/hackathon

### 11.3 Quality Improvements

**What Gets Better:**

1. **Adaptability:** System adjusts to different loan types automatically
2. **Explainability:** Each agent's reasoning is logged and traceable
3. **Error Resilience:** Better fallbacks when individual components fail
4. **Modularity:** Easy to add new specialized agents (e.g., Fraud Detection Agent)
5. **Tool Usage:** Agents intelligently decide which tools to use instead of running all tools always

---

## 12. Success Criteria

### 12.1 Functional Requirements

- ✅ Orchestrator correctly identifies business vs personal loans
- ✅ Market Researcher only invoked for business loans with location
- ✅ All agents can reason and select appropriate tools
- ✅ Financial metrics match or exceed quality of old system
- ✅ Market analysis provides actionable insights
- ✅ Risk assessment is explainable and reasonable
- ✅ Error handling works: system degrades gracefully
- ✅ All existing API endpoints continue to work

### 12.2 Testing Requirements

- ✅ All agent unit tests passing
- ✅ Integration test for full business loan flow passing
- ✅ Integration test for personal loan flow passing
- ✅ Error scenario tests passing
- ✅ Performance within acceptable range (<10s per assessment)

### 12.3 Code Quality Requirements

- ✅ Clear separation of concerns (agent/tool/service layers)
- ✅ Comprehensive docstrings on all tools (used by LLM)
- ✅ Proper error handling with retries
- ✅ Logging for debugging agent reasoning
- ✅ Type hints on all functions
- ✅ No breaking changes to existing database schema

---

## 13. Future Enhancements

### 13.1 Additional Specialized Agents

**Potential new agents to add:**

1. **Credit Score Analyst Agent**
   - Tools: fetch_credit_report, analyze_credit_history, predict_credit_trend
   - When: If credit score data becomes available

2. **Fraud Detection Agent**
   - Tools: check_identity_verification, analyze_application_patterns, risk_flag_detection
   - When: To add security layer

3. **Industry Expert Agent**
   - Tools: get_industry_trends, analyze_sector_health, benchmark_against_peers
   - When: For more sophisticated business analysis

4. **Document Analyzer Agent**
   - Tools: extract_text_from_pdf, verify_document_authenticity, cross_check_data
   - When: If users upload supporting documents

### 13.2 Orchestrator Intelligence Upgrades

**Smarter orchestration:**
- Learn from past assessments to optimize agent selection
- Parallel agent invocation where possible (Financial + Market simultaneously)
- Dynamic confidence scoring based on data quality
- Self-reflection: "Do I need more information?"

### 13.3 Advanced Tool Capabilities

**Tool enhancements:**
- Caching for expensive API calls (Google Places results)
- Real-time data sources (current market conditions)
- Historical trend analysis (loan performance data)
- Predictive modeling (likelihood of business success)

---

## 14. Appendix

### 14.1 Key Terminology

| Term | Definition |
|------|------------|
| ReAct Agent | Agent that follows Reasoning + Acting pattern: thinks about problem, takes action, observes result, repeats |
| Orchestrator | Top-level agent that coordinates specialized agents |
| Tool | Function that an agent can call to perform specific tasks |
| LangChain | Framework for building LLM-powered applications |
| LangGraph | Library for building stateful multi-agent workflows (not used in this design) |
| Agent Executor | LangChain component that runs ReAct loop for an agent |

### 14.2 Design Alternatives Considered

**Alternative 1: Fixed LangGraph Pipeline**
- Pros: Simpler, more predictable
- Cons: Not truly intelligent, always runs all agents
- **Rejected:** Doesn't meet requirement for smart orchestration

**Alternative 2: Each Agent is a Separate Microservice**
- Pros: True service isolation, independently scalable
- Cons: Complex deployment, network overhead, overkill for hackathon
- **Rejected:** Over-engineering for current scope

**Alternative 3: Single Super-Agent with All Tools**
- Pros: Simpler architecture, one LLM call
- Cons: Tool overload, harder to maintain, less specialized
- **Rejected:** Defeats purpose of multi-agent system

### 14.3 References

- [LangChain ReAct Documentation](https://python.langchain.com/docs/modules/agents/agent_types/react)
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/agents/tools/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Plaid API Documentation](https://plaid.com/docs/)
- [Google Places API Documentation](https://developers.google.com/maps/documentation/places/web-service)

---

**End of Design Specification**

This design provides a complete blueprint for implementing a true multi-agent loan assessment system with intelligent orchestration, specialized ReAct agents, and robust error handling. The system is modular, testable, and ready for implementation.
