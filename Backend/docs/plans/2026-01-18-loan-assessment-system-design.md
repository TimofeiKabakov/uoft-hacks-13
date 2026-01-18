# Loan Assessment System - Design Specification

**Date:** 2026-01-18
**Project:** LLM-Based Loan Eligibility Assessment Backend
**Status:** Design Complete - Ready for Implementation

---

## 1. Executive Summary

A Python-based backend system that assesses small business loan eligibility by combining traditional financial metrics with AI-powered market viability analysis. The system uses a multi-agent LLM architecture to provide intelligent, explainable loan decisions.

### Key Features
- Multi-agent LLM orchestration using LangGraph
- Hybrid assessment: Rule-based financial metrics + AI-driven insights
- Market viability analysis using location data
- Integration with Plaid (financial data) and Google APIs (location/market)
- Local SQLite storage for demo/development

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Lovable Frontend                         │
│  (User Input, Plaid Link Integration, Results Display)      │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Multi-Agent Orchestration Layer              │   │
│  │              (LangGraph + Gemini)                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  External Service Integration Layer                  │   │
│  │  - Plaid API  - Google Maps  - Google Places        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  SQLite Database                             │
│     (Applications, Metrics, Assessments, Cache)             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

**Core Backend:**
- Python 3.11+
- FastAPI (web framework)
- SQLite (local database)
- Pydantic (data validation)

**LLM & Agents:**
- Google Gemini Pro (LLM - free student tier)
- LangGraph (multi-agent orchestration)
- LangChain (agent tools and utilities)

**External APIs:**
- Plaid Sandbox API (financial data)
- Google Maps API (location services)
- Google Places API (market research)

---

## 3. Multi-Agent Architecture

### 3.1 Agent Hierarchy

```
┌───────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT                           │
│  (Gemini-powered main controller)                         │
│  - Analyzes loan application                             │
│  - Decides which specialized agents to invoke            │
│  - Synthesizes results into final decision               │
└─────┬─────────────────────────────────────────────────────┘
      │
      ├──► ┌─────────────────────────────────────────┐
      │    │   FINANCIAL ANALYST AGENT               │
      │    │   Tools:                                │
      │    │   - fetch_plaid_transactions()          │
      │    │   - calculate_dti_ratio()               │
      │    │   - analyze_cash_flow()                 │
      │    │   - assess_income_stability()           │
      │    └─────────────────────────────────────────┘
      │
      ├──► ┌─────────────────────────────────────────┐
      │    │   MARKET RESEARCH AGENT                 │
      │    │   Tools:                                │
      │    │   - search_competitors()                │
      │    │   - analyze_market_saturation()         │
      │    │   - assess_location_viability()         │
      │    └─────────────────────────────────────────┘
      │
      └──► ┌─────────────────────────────────────────┐
           │   RISK ASSESSMENT AGENT                 │
           │   Tools:                                │
           │   - calculate_risk_score()              │
           │   - generate_recommendations()          │
           │   - explain_decision()                  │
           └─────────────────────────────────────────┘
```

### 3.2 Agent Workflows

**Orchestrator Decision Flow:**
1. Receives loan application with user data
2. Determines which analyses are needed
3. Invokes Financial Analyst Agent for metrics
4. Invokes Market Research Agent for location viability
5. Invokes Risk Assessment Agent for final scoring
6. Synthesizes all results into cohesive assessment

**Agent Communication:**
- LangGraph manages state between agents
- Agents communicate through structured message passing
- Orchestrator maintains application context
- Each agent returns structured output (Pydantic models)

---

## 4. Data Flow

### 4.1 Application Processing Pipeline

```
Step 1: User Info Collection
  Frontend → POST /api/applications/create
  Input: { job, age, location, loan_amount, loan_purpose }
  Output: { application_id, status: "pending_plaid" }

Step 2: Plaid Connection
  Frontend → POST /api/applications/{id}/connect-plaid
  Input: { plaid_public_token }
  Backend: Exchange token, fetch financial data
  Output: { status: "processing", plaid_connected: true }

Step 3: Multi-Agent Assessment
  Frontend → POST /api/applications/{id}/assess
  Backend Process:
    1. Orchestrator receives application
    2. Financial Analyst → calculates metrics
    3. Market Research → analyzes location
    4. Risk Assessment → generates score
    5. Orchestrator → final decision
  Output: {
    eligibility: "approved|denied|review",
    confidence_score: 0-100,
    reasoning: "...",
    recommendations: [...],
    financial_metrics: {...},
    market_analysis: {...}
  }

Step 4: Status Check
  Frontend → GET /api/applications/{id}/status
  Output: Current application state + results if complete
```

### 4.2 Data Models

**Application Model:**
```python
{
  "id": "uuid",
  "user_job": "string",
  "user_age": "integer",
  "location": {
    "lat": "float",
    "lng": "float",
    "address": "string"
  },
  "loan_amount": "decimal",
  "loan_purpose": "string",
  "plaid_access_token": "string (encrypted)",
  "status": "pending_plaid|processing|completed",
  "created_at": "timestamp"
}
```

**Financial Metrics Model:**
```python
{
  "debt_to_income_ratio": "float",
  "savings_rate": "float",
  "avg_monthly_balance": "decimal",
  "min_balance_6mo": "decimal",
  "overdraft_count": "integer",
  "income_stability_score": "0-100",
  "monthly_income": "decimal",
  "monthly_expenses": "decimal"
}
```

**Market Analysis Model:**
```python
{
  "competitor_count": "integer",
  "market_density": "low|medium|high",
  "nearby_businesses": [
    {
      "name": "string",
      "type": "string",
      "rating": "float",
      "distance_miles": "float"
    }
  ],
  "viability_score": "0-100",
  "market_insights": "string"
}
```

**Assessment Result Model:**
```python
{
  "application_id": "uuid",
  "eligibility": "approved|denied|review",
  "confidence_score": "0-100",
  "risk_level": "low|medium|high",
  "reasoning": "string (LLM explanation)",
  "recommendations": ["array of strings"],
  "financial_metrics": "FinancialMetrics",
  "market_analysis": "MarketAnalysis",
  "assessed_at": "timestamp"
}
```

---

## 5. Financial Metrics Engine

### 5.1 Core Metrics

**Debt-to-Income Ratio (DTI):**
- Formula: `(Monthly Debt / Monthly Income) × 100`
- Data Source: Plaid recurring transactions + income streams
- Threshold: <43% = good, 43-50% = moderate, >50% = high risk

**Savings Rate:**
- Formula: `(Income - Expenses) / Income × 100`
- Indicates financial discipline and cushion
- Threshold: >20% = excellent, 10-20% = good, <10% = concerning

**Cash Flow Analysis:**
- Average monthly balance (6 months)
- Minimum balance (detect financial stress)
- Overdraft frequency (risk indicator)

**Income Stability:**
- Regularity of income deposits
- Income trend analysis (growing/stable/declining)
- Multiple income sources vs. single source

**Spending Pattern Analysis:**
- Essential spending ratio (rent, utilities, groceries)
- Discretionary spending (entertainment, dining)
- Large irregular expenses
- Bill payment consistency

### 5.2 Calculation Process

1. **Fetch Plaid Data:**
   - Last 6 months of transactions
   - Income verification data
   - Credit score (if available)

2. **Categorize Transactions:**
   - Income sources
   - Fixed expenses (rent, loan payments)
   - Variable expenses (utilities, groceries)
   - Discretionary expenses

3. **Compute Metrics:**
   - Run calculations for each metric
   - Store in structured format
   - Flag any anomalies

4. **Pass to Agent:**
   - Financial Analyst Agent receives metrics
   - Provides context and interpretation
   - Identifies patterns and risks

---

## 6. Market Viability Analysis

### 6.1 Location-Based Assessment

**Process:**
1. **Extract Business Context:**
   - User's job/business type
   - Exact location (lat/lng from Google Maps)

2. **Competitor Search (Google Places API):**
   - Search radius: 1-2 miles
   - Query: Similar business types
   - Collect: name, rating, type, distance

3. **Market Saturation Analysis:**
   - Count competitors in radius
   - Assess rating distribution
   - Identify market gaps

4. **Viability Scoring:**
   - Market Research Agent analyzes data
   - Considers: competition density, business type fit, area demographics
   - Returns viability score (0-100)

### 6.2 LLM-Powered Insights

Gemini analyzes market data to answer:
- Is this business type oversaturated in the area?
- What competitive advantages might be needed?
- Does the location support this business type?
- Are there demographic or area characteristics to consider?

---

## 7. API Endpoints Specification

### 7.1 Application Management

**POST /api/applications/create**
```
Request:
{
  "job": "Coffee shop owner",
  "age": 32,
  "location": {
    "lat": 43.6532,
    "lng": -79.3832,
    "address": "123 Main St, Toronto, ON"
  },
  "loan_amount": 50000,
  "loan_purpose": "Equipment purchase"
}

Response (201):
{
  "application_id": "uuid",
  "status": "pending_plaid",
  "created_at": "2026-01-18T10:30:00Z"
}
```

**POST /api/applications/{id}/connect-plaid**
```
Request:
{
  "plaid_public_token": "public-sandbox-xxx"
}

Response (200):
{
  "application_id": "uuid",
  "status": "processing",
  "plaid_connected": true
}
```

**POST /api/applications/{id}/assess**
```
Request: (empty body)

Response (200):
{
  "eligibility": "approved",
  "confidence_score": 85,
  "risk_level": "low",
  "reasoning": "Strong financial metrics with DTI of 28% and healthy savings rate. Market analysis shows moderate competition in the area with room for differentiation. Income stability is excellent with consistent deposits over 6 months.",
  "recommendations": [
    "Consider increasing loan amount slightly to build emergency fund",
    "Focus on unique value proposition given 3 competitors within 1 mile",
    "Maintain current savings rate during business ramp-up"
  ],
  "financial_metrics": {
    "debt_to_income_ratio": 28.5,
    "savings_rate": 22.3,
    "avg_monthly_balance": 8500,
    "income_stability_score": 92
  },
  "market_analysis": {
    "competitor_count": 3,
    "market_density": "medium",
    "viability_score": 78
  },
  "assessed_at": "2026-01-18T10:35:00Z"
}
```

**GET /api/applications/{id}/status**
```
Response (200):
{
  "application_id": "uuid",
  "status": "completed",
  "created_at": "2026-01-18T10:30:00Z",
  "assessed_at": "2026-01-18T10:35:00Z",
  "has_results": true
}
```

### 7.2 Health & Utility Endpoints

**GET /api/health**
```
Response (200):
{
  "status": "healthy",
  "database": "connected",
  "plaid_api": "available",
  "gemini_api": "available"
}
```

---

## 8. Database Schema

### 8.1 SQLite Tables

**applications**
```sql
CREATE TABLE applications (
  id TEXT PRIMARY KEY,
  user_job TEXT NOT NULL,
  user_age INTEGER NOT NULL,
  location_lat REAL NOT NULL,
  location_lng REAL NOT NULL,
  location_address TEXT NOT NULL,
  loan_amount REAL NOT NULL,
  loan_purpose TEXT NOT NULL,
  plaid_access_token TEXT,  -- encrypted
  status TEXT NOT NULL,  -- pending_plaid, processing, completed
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**financial_metrics**
```sql
CREATE TABLE financial_metrics (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL,
  debt_to_income_ratio REAL,
  savings_rate REAL,
  avg_monthly_balance REAL,
  min_balance_6mo REAL,
  overdraft_count INTEGER,
  income_stability_score REAL,
  monthly_income REAL,
  monthly_expenses REAL,
  raw_plaid_data TEXT,  -- JSON blob
  calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (application_id) REFERENCES applications(id)
);
```

**market_analysis**
```sql
CREATE TABLE market_analysis (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL,
  competitor_count INTEGER,
  market_density TEXT,  -- low, medium, high
  viability_score REAL,
  market_insights TEXT,
  nearby_businesses TEXT,  -- JSON array
  analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (application_id) REFERENCES applications(id)
);
```

**assessments**
```sql
CREATE TABLE assessments (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL,
  eligibility TEXT NOT NULL,  -- approved, denied, review
  confidence_score REAL,
  risk_level TEXT,  -- low, medium, high
  reasoning TEXT,
  recommendations TEXT,  -- JSON array
  assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (application_id) REFERENCES applications(id)
);
```

---

## 9. Security & Privacy Considerations

### 9.1 Data Protection
- **Plaid Access Tokens:** Encrypted at rest using environment-specific keys
- **PII:** User data stored securely, no sharing with third parties
- **API Keys:** Stored in environment variables, never in code

### 9.2 API Security
- **CORS:** Configure allowed origins (Lovable frontend domain)
- **Rate Limiting:** Prevent abuse (future enhancement)
- **Input Validation:** Pydantic models validate all inputs

### 9.3 Demo Limitations
- Using Plaid Sandbox (test data only)
- SQLite local storage (not production-ready for scale)
- No user authentication (add in production)

---

## 10. Error Handling

### 10.1 Error Scenarios

**Plaid API Errors:**
- Invalid token → Return 400 with message
- API down → Return 503, retry logic
- Insufficient data → Return 422 with requirements

**LLM/Agent Errors:**
- API timeout → Retry with exponential backoff
- Rate limit → Queue request, return 429
- Invalid response → Fallback to rule-based decision

**Database Errors:**
- Connection issues → Return 500
- Constraint violations → Return 400 with details

### 10.2 Graceful Degradation

If LLM unavailable:
- Use rule-based assessment only
- Return results with lower confidence score
- Mark assessment as "preliminary"

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Financial metric calculations
- Agent tool functions
- Data model validation

### 11.2 Integration Tests
- Plaid API integration (sandbox)
- Google APIs integration
- Database operations
- End-to-end assessment pipeline

### 11.3 Agent Tests
- Mock LLM responses
- Test agent tool invocation
- Validate agent output formats

---

## 12. Future Enhancements

### 12.1 Short-term (Post-Demo)
- User authentication (Firebase Auth)
- Production database (PostgreSQL/Firebase)
- Real Plaid production environment
- Enhanced error handling and logging

### 12.2 Long-term
- Additional specialized agents:
  - Credit Score Analyst
  - Fraud Detection Agent
  - Industry-Specific Analyst
- Real-time dashboard for loan officers
- Automated document upload and OCR
- Integration with loan management systems
- A/B testing of LLM prompts
- Model performance monitoring

---

## 13. Success Metrics

### 13.1 Demo Success Criteria
- Complete loan assessment in <30 seconds
- Accurate financial metric calculation
- Meaningful market viability insights
- Clear, explainable LLM reasoning
- Smooth frontend-backend integration

### 13.2 Quality Metrics
- Assessment accuracy (compare to manual review)
- LLM explanation quality (human evaluation)
- API response time (<5s per endpoint)
- Zero critical errors during demo

---

## Appendix A: Agent Tool Definitions

### Financial Analyst Agent Tools

**fetch_plaid_transactions(access_token: str, months: int = 6)**
- Fetches transaction history from Plaid
- Returns categorized transactions

**calculate_dti_ratio(transactions: List) -> float**
- Computes debt-to-income ratio
- Returns percentage

**analyze_cash_flow(transactions: List) -> dict**
- Analyzes balance trends
- Returns metrics: avg_balance, min_balance, overdrafts

**assess_income_stability(transactions: List) -> float**
- Scores income consistency
- Returns stability score (0-100)

### Market Research Agent Tools

**search_competitors(location: dict, business_type: str, radius_miles: float) -> List**
- Queries Google Places API
- Returns competitor data

**analyze_market_saturation(competitors: List, business_type: str) -> dict**
- Assesses competition level
- Returns saturation score and insights

**assess_location_viability(location: dict, business_type: str, competitors: List) -> float**
- Evaluates location fit
- Returns viability score (0-100)

### Risk Assessment Agent Tools

**calculate_risk_score(financial_metrics: dict, market_analysis: dict) -> dict**
- Combines all metrics
- Returns risk score and level

**generate_recommendations(assessment_data: dict) -> List[str]**
- Creates actionable recommendations
- Returns list of suggestions

**explain_decision(assessment_data: dict) -> str**
- Generates human-readable explanation
- Returns reasoning text

---

## Appendix B: Environment Variables

```bash
# API Keys
GEMINI_API_KEY=your_gemini_key
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
GOOGLE_MAPS_API_KEY=your_google_maps_key
GOOGLE_PLACES_API_KEY=your_google_places_key

# Configuration
PLAID_ENV=sandbox  # sandbox, development, production
DATABASE_URL=sqlite:///./loan_assessment.db
CORS_ORIGINS=http://localhost:3000,https://your-lovable-frontend.com

# Encryption
ENCRYPTION_KEY=your_encryption_key_for_tokens
```

---

**End of Design Specification**
