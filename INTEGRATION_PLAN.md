# Backend-Frontend Integration Plan
## UofT Hacks 13 - Community Spark / Trajectory Platform

**Date:** 2026-01-18
**Status:** Planning Phase

---

## Executive Summary

This document outlines the complete integration plan for linking the existing backend (FastAPI multi-agent loan assessment system) with the frontend (React evaluation wizard and recommendations dashboard). The frontend currently uses extensive mock data and simulated workflows, while the backend has a fully functional multi-agent architecture with real Plaid and Google integrations.

**Key Challenges:**
1. Frontend has 5-step wizard vs Backend's 2-step flow (application creation + Plaid connect)
2. Frontend expects 4 agents (AUDITOR, IMPACT, COMPLIANCE, COACH) vs Backend has 3 agents (Financial Analyst, Market Researcher, Risk Assessor)
3. Frontend has recommendations dashboard with no corresponding backend endpoint
4. Frontend dashboard requires user authentication (none exists)
5. Mock data in recommendations page needs real financial data from Plaid
6. Frontend expects real-time agent logs streaming vs Backend's async processing

---

## Phase 1: Data Model & Schema Alignment

### 1.1 Backend Schema Updates Required

**New Table: `users`**
```sql
- id (String, PK)
- email (String, unique)
- name (String)
- created_at (DateTime)
- updated_at (DateTime)
```

**Update: `applications` table**
```sql
+ user_id (String, FK to users.id)
+ business_name (String)
+ business_type (String)
+ location_zip (String)
+ location_city (String)
+ location_state (String)
+ community_tags (JSON array)
+ years_in_operation (Integer)
+ employee_count (Integer)
+ annual_revenue (Float)
+ employment_details (Text)
```

**New Table: `recommendations`**
```sql
- id (String, PK)
- application_id (String, FK)
- priority (String: high/medium/low)
- category (String)
- title (String)
- evidence_summary (Text)
- why_matters (Text)
- recommended_action (Text)
- expected_impact (Text)
- evidence_data (JSON)
- created_at (DateTime)
```

**New Table: `action_plans`**
```sql
- id (String, PK)
- user_id (String, FK)
- application_id (String, FK)
- timeframe (String: 30/60/90 days)
- action_items (JSON array)
- targets (JSON array)
- saved_at (DateTime)
- updated_at (DateTime)
```

**New Table: `financial_snapshots`**
```sql
- id (String, PK)
- application_id (String, FK)
- cash_flow_data (JSON)
- spending_by_category (JSON)
- stability_trend (JSON)
- generated_at (DateTime)
```

**New Table: `coach_sessions`**
```sql
- id (String, PK)
- user_id (String, FK)
- application_id (String, FK)
- question (Text)
- response (Text)
- context (JSON)
- created_at (DateTime)
```

---

### 1.2 Pydantic Schema Updates

**File: `Backend/app/models/schemas.py`**

Add new request schemas:
```python
class UserCreate(BaseModel):
    email: EmailStr
    name: str

class BusinessProfileCreate(BaseModel):
    business_name: str
    business_type: str
    location_zip: str
    location_city: str
    location_state: str
    community_tags: List[str]
    years_in_operation: int
    employee_count: int
    annual_revenue: float
    employment_details: str

class ApplicationCreateExtended(ApplicationCreate):
    user_id: str
    business_profile: BusinessProfileCreate

class CoachQuestionRequest(BaseModel):
    application_id: str
    question: str
    context: Optional[Dict[str, Any]]

class ActionPlanSave(BaseModel):
    application_id: str
    timeframe: str
    action_items: List[Dict[str, Any]]
    targets: List[Dict[str, Any]]
```

Add new response schemas:
```python
class RecommendationResponse(BaseModel):
    id: str
    priority: str
    category: str
    title: str
    evidence_summary: str
    why_matters: str
    recommended_action: str
    expected_impact: str
    evidence_data: Dict[str, Any]

class FinancialSnapshotResponse(BaseModel):
    cash_flow_data: List[Dict[str, Any]]
    spending_by_category: List[Dict[str, Any]]
    stability_trend: List[Dict[str, Any]]

class CoachResponse(BaseModel):
    question: str
    response: str
    action_steps: List[str]
    expected_impact: str

class DashboardResponse(BaseModel):
    user: UserResponse
    latest_application: Optional[ApplicationResponse]
    fiscal_health_score: Optional[float]
    cash_flow_stability: Optional[float]
    community_multiplier: Optional[float]
    risk_flags_count: int
    next_milestone: Optional[str]
    days_to_milestone: Optional[int]
    recent_alerts: List[Dict[str, Any]]
```

---

## Phase 2: API Endpoint Expansion

### 2.1 New Backend Endpoints Required

**File: `Backend/app/api/routes.py`**

#### Authentication & Users
```python
POST   /api/v1/auth/register          # Create user account
POST   /api/v1/auth/login             # Login (return JWT token)
GET    /api/v1/users/me               # Get current user
PUT    /api/v1/users/me               # Update user profile
```

#### Enhanced Application Flow
```python
POST   /api/v1/applications/complete  # Extended application with business profile
GET    /api/v1/applications           # List user's applications
DELETE /api/v1/applications/{id}      # Delete application
```

#### Recommendations
```python
GET    /api/v1/applications/{id}/recommendations  # Get AI recommendations
POST   /api/v1/recommendations/{id}/evidence      # Get detailed evidence
```

#### Action Plans
```python
POST   /api/v1/action-plans           # Save action plan
GET    /api/v1/action-plans/{user_id} # Get user's saved plans
PUT    /api/v1/action-plans/{id}      # Update action plan progress
```

#### Financial Snapshots
```python
GET    /api/v1/applications/{id}/financial-snapshot  # Get charts data
GET    /api/v1/applications/{id}/transactions        # Raw transaction data
```

#### AI Coach
```python
POST   /api/v1/coach/ask              # Ask coach a question
GET    /api/v1/coach/questions        # Get suggested questions
```

#### Dashboard
```python
GET    /api/v1/dashboard              # Get full dashboard data
GET    /api/v1/dashboard/alerts       # Get recent alerts
```

#### Real-time Streaming (Future)
```python
WS     /api/v1/ws/evaluate/{id}       # WebSocket for agent log streaming
```

---

### 2.2 Frontend API Client Updates

**File: `Frontend/src/api/client.ts`**

Update `API_ENDPOINTS` constant:
```typescript
export const API_ENDPOINTS = {
  // Authentication
  register: '/api/v1/auth/register',
  login: '/api/v1/auth/login',
  getCurrentUser: '/api/v1/users/me',

  // Applications
  createApplication: '/api/v1/applications/complete',
  getApplications: '/api/v1/applications',
  getApplication: (id: string) => `/api/v1/applications/${id}`,
  getApplicationStatus: (id: string) => `/api/v1/applications/${id}/status`,
  getAssessment: (id: string) => `/api/v1/applications/${id}/assessment`,

  // Plaid
  connectPlaid: (id: string) => `/api/v1/applications/${id}/plaid-connect`,

  // Recommendations
  getRecommendations: (id: string) => `/api/v1/applications/${id}/recommendations`,
  getEvidence: (id: string) => `/api/v1/recommendations/${id}/evidence`,

  // Action Plans
  savePlan: '/api/v1/action-plans',
  getPlans: (userId: string) => `/api/v1/action-plans/${userId}`,
  updatePlan: (id: string) => `/api/v1/action-plans/${id}`,

  // Financial Data
  getFinancialSnapshot: (id: string) => `/api/v1/applications/${id}/financial-snapshot`,
  getTransactions: (id: string) => `/api/v1/applications/${id}/transactions`,

  // Coach
  askCoach: '/api/v1/coach/ask',
  getSuggestedQuestions: '/api/v1/coach/questions',

  // Dashboard
  getDashboard: '/api/v1/dashboard',
  getAlerts: '/api/v1/dashboard/alerts',

  // Health
  health: '/health',
}
```

Remove all `MOCK_*` constants and implement real API calls.

---

## Phase 3: Agent Architecture Reconciliation

### 3.1 Current State Analysis

**Frontend Expects:**
- AUDITOR (financial health check)
- IMPACT (community impact analysis)
- COMPLIANCE (regulatory/risk check)
- COACH (personalized guidance)

**Backend Provides:**
- Financial Analyst (calculates financial metrics)
- Market Researcher (analyzes location & competition)
- Risk Assessor (makes final decision)

### 3.2 Proposed Backend Agent Updates

**Option A: Add New Agents (Recommended)**

**New Agent: Impact Analyzer**
- **Location:** `Backend/app/agents/impact_analyzer/`
- **Purpose:** Calculate community impact multiplier
- **Inputs:** Business type, location, community tags, employment details
- **Outputs:**
  - Community impact score (0-100)
  - Impact multiplier (1.0-2.0x)
  - Social benefit analysis
  - Job creation potential
  - Local economic impact

**New Agent: Compliance Checker**
- **Location:** `Backend/app/agents/compliance_checker/`
- **Purpose:** Verify regulatory requirements and risk flags
- **Inputs:** Business type, location, financial metrics
- **Outputs:**
  - Compliance status
  - Required licenses/permits
  - Risk flags with severity
  - Regulatory recommendations

**Enhanced Agent: Coach Agent**
- **Location:** `Backend/app/agents/coach/`
- **Purpose:** Provide personalized guidance
- **Inputs:** Assessment results, user question, context
- **Outputs:**
  - Tailored response
  - Action steps
  - Priority recommendations
  - Expected impact

**Renamed Agent: Financial Analyst → Auditor**
- Keep existing functionality
- Rename for frontend alignment
- Add more detailed breakdowns for UI display

### 3.3 Updated Orchestrator Flow

**File: `Backend/app/agents/orchestrator/orchestrator.py`**

```python
async def run_assessment(application_id: str):
    # Phase 1: Parallel data gathering
    auditor_task = auditor.analyze(...)           # Financial health
    impact_task = impact_analyzer.analyze(...)    # Community impact
    market_task = market_researcher.analyze(...)  # Market viability

    results = await asyncio.gather(
        auditor_task,
        impact_task,
        market_task
    )

    # Phase 2: Compliance check
    compliance_result = await compliance_checker.analyze(
        business_data=...,
        financial_data=results[0],
        market_data=results[2]
    )

    # Phase 3: Risk assessment
    risk_result = await risk_assessor.analyze(
        auditor_data=results[0],
        impact_data=results[1],
        market_data=results[2],
        compliance_data=compliance_result
    )

    # Phase 4: Generate recommendations
    recommendations = await generate_recommendations(
        all_results=...
    )

    return {
        'assessment': risk_result,
        'recommendations': recommendations,
        'agent_logs': all_logs
    }
```

---

## Phase 4: Feature-by-Feature Integration Tasks

### 4.1 Evaluation Wizard Integration

#### Task 4.1.1: Business Profile Submission
**Frontend Changes:**
- Remove mock data from `BusinessProfileStep.tsx`
- Call `POST /api/v1/applications/complete` with full business profile
- Store returned `application_id` in state

**Backend Changes:**
- Create `POST /api/v1/applications/complete` endpoint
- Save business profile fields to `applications` table
- Return application ID and status

**Files to Modify:**
- `Frontend/src/components/wizard/BusinessProfileStep.tsx`
- `Frontend/src/hooks/useEvaluationState.ts`
- `Backend/app/api/routes.py`
- `Backend/app/database/models.py`

---

#### Task 4.1.2: Location Verification
**Frontend Changes:**
- Integrate Google Places Autocomplete API
- Send selected location to backend for geocoding
- Update location data in application

**Backend Changes:**
- Use existing `google_service.geocode_address()` method
- Return lat/lng coordinates
- Save to application record

**Files to Modify:**
- `Frontend/src/components/wizard/LocationStep.tsx`
- `Backend/app/services/google_service.py` (already exists, just expose endpoint)
- `Backend/app/api/routes.py`

---

#### Task 4.1.3: Real Plaid Integration
**Frontend Changes:**
- Remove `SANDBOX_INSTITUTIONS` mock data
- Install Plaid React SDK: `npm install react-plaid-link`
- Initialize Plaid Link with backend-provided `link_token`
- Send `public_token` to backend on success

**Backend Changes:**
- Expose `POST /api/v1/plaid/create-link-token` endpoint
- Use existing `plaid_service.create_link_token()` method
- Existing Plaid connect endpoint works as-is

**Files to Modify:**
- `Frontend/src/components/wizard/BankDataStep.tsx`
- `Frontend/package.json` (add dependency)
- `Backend/app/api/routes.py` (add link token endpoint)
- `Backend/app/services/plaid_service.py` (already has method)

**New Dependencies:**
```bash
cd Frontend
npm install react-plaid-link
```

---

#### Task 4.1.4: Real-time Evaluation Streaming
**Frontend Changes:**
- Remove `MOCK_EVALUATION_RESPONSE`
- Implement WebSocket connection to `/api/v1/ws/evaluate/{id}`
- Stream agent logs in real-time
- Update progress bar based on agent completion

**Backend Changes:**
- Install WebSocket support: `pip install websockets`
- Create WebSocket endpoint
- Modify orchestrator to emit events during processing
- Send JSON messages for each agent log entry

**Files to Modify:**
- `Frontend/src/components/wizard/EvaluationStep.tsx`
- `Frontend/src/api/client.ts`
- `Backend/app/api/routes.py`
- `Backend/app/agents/orchestrator/orchestrator.py`
- `Backend/requirements.txt`

**Backend Implementation:**
```python
@router.websocket("/ws/evaluate/{application_id}")
async def websocket_evaluate(
    websocket: WebSocket,
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    await websocket.accept()

    async def send_log(agent: str, message: str, progress: int):
        await websocket.send_json({
            "type": "log",
            "agent": agent,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        })

    # Run assessment with callback
    result = await orchestrator.run_assessment_streaming(
        application_id,
        callback=send_log
    )

    await websocket.send_json({
        "type": "complete",
        "result": result
    })
    await websocket.close()
```

---

#### Task 4.1.5: Results Display
**Frontend Changes:**
- Map backend assessment response to frontend `EvaluationResponse` type
- Display real loan terms from backend
- Show actual risk flags from compliance agent
- Display real improvement plan

**Backend Changes:**
- Ensure assessment response includes all fields frontend expects:
  - `decision` (map to APPROVE/REFER/DENY)
  - `fiscalHealthScore`
  - `communityMultiplier` (from impact agent)
  - `loanTerms` (calculate from loan_amount + risk_level)
  - `accountSummaries` (from Plaid data)
  - `riskFlags` (from compliance agent)
  - `improvementPlan` (from recommendations)

**Files to Modify:**
- `Frontend/src/components/wizard/ResultsStep.tsx`
- `Frontend/src/types/index.ts`
- `Backend/app/models/schemas.py`
- `Backend/app/agents/risk_assessor/agent.py`

---

### 4.2 Recommendations Page Integration

#### Task 4.2.1: Generate Recommendations from Assessment
**Backend Changes:**
- Create recommendations generation service
- Analyze financial metrics to identify issues
- Create 5-7 recommendations with evidence
- Store in `recommendations` table

**New Service:**
- **File:** `Backend/app/services/recommendation_service.py`
- **Methods:**
  - `generate_recommendations(assessment_id)` → List[Recommendation]
  - `get_evidence_for_recommendation(rec_id)` → Evidence
  - `prioritize_recommendations(recs)` → Sorted list

**Files to Create/Modify:**
- `Backend/app/services/recommendation_service.py` (NEW)
- `Backend/app/api/routes.py`
- `Backend/app/database/models.py`

---

#### Task 4.2.2: Financial Snapshot Charts
**Backend Changes:**
- Create financial snapshot generator
- Extract time-series data from Plaid transactions
- Generate cash flow, spending categories, stability trend
- Cache in `financial_snapshots` table

**New Service:**
- **File:** `Backend/app/services/snapshot_service.py`
- **Methods:**
  - `generate_cash_flow_chart(transactions)` → ChartData
  - `generate_spending_breakdown(transactions)` → CategoryData
  - `generate_stability_trend(balance_history)` → TrendData

**Files to Create/Modify:**
- `Backend/app/services/snapshot_service.py` (NEW)
- `Backend/app/api/routes.py`
- `Backend/app/database/models.py`

**Frontend Changes:**
- Remove `DEMO_FINANCIAL_SNAPSHOT`
- Call `GET /api/v1/applications/{id}/financial-snapshot`
- Map response to chart components

**Files to Modify:**
- `Frontend/src/api/recommendations.ts`
- `Frontend/src/components/recommendations/FinancialCharts.tsx`

---

#### Task 4.2.3: Dynamic Targets
**Backend Changes:**
- Calculate recommended targets based on financial metrics
- Compare current vs recommended for each target
- Track progress over time

**Targets to Calculate:**
- Max Discretionary Spend (income - fixed costs - 20% buffer)
- Subscription Cap (5-10% of monthly income)
- Minimum Buffer Days (expenses / daily burn rate)
- Monthly Overdrafts (target: 0)

**Files to Create/Modify:**
- `Backend/app/services/target_calculator.py` (NEW)
- `Backend/app/api/routes.py`

**Frontend Changes:**
- Remove `DEMO_TARGETS`
- Call backend for real targets
- Update `TargetsPanel.tsx` to use real data

**Files to Modify:**
- `Frontend/src/components/recommendations/TargetsPanel.tsx`
- `Frontend/src/api/recommendations.ts`

---

#### Task 4.2.4: Action Plan Persistence
**Backend Changes:**
- Create action plan endpoints
- Save user-customized plans to database
- Track action item completion status
- Send reminder notifications (future)

**Files to Create/Modify:**
- `Backend/app/api/routes.py`
- `Backend/app/database/models.py`

**Frontend Changes:**
- Remove localStorage fallback
- Use real backend endpoints
- Sync action item status with backend

**Files to Modify:**
- `Frontend/src/api/recommendations.ts`
- `Frontend/src/components/recommendations/PlanTabs.tsx`

---

#### Task 4.2.5: AI Coach Integration
**Backend Changes:**
- Create coach agent (LLM-powered)
- Accept natural language questions
- Generate personalized responses based on assessment
- Store Q&A history

**New Agent:**
- **File:** `Backend/app/agents/coach/agent.py`
- **Methods:**
  - `answer_question(question, context)` → Response
  - `get_suggested_questions(assessment)` → List[str]

**Files to Create/Modify:**
- `Backend/app/agents/coach/agent.py` (NEW)
- `Backend/app/agents/coach/prompts.py` (NEW)
- `Backend/app/api/routes.py`

**Frontend Changes:**
- Remove hardcoded Q&A responses
- Add text input for custom questions
- Call `POST /api/v1/coach/ask` with user question

**Files to Modify:**
- `Frontend/src/components/recommendations/CoachPanel.tsx`
- `Frontend/src/api/recommendations.ts`

---

### 4.3 Dashboard Integration

#### Task 4.3.1: User Authentication
**Backend Changes:**
- Install JWT library: `pip install python-jose[cryptography] passlib[bcrypt]`
- Create auth service with login/register
- Implement JWT token generation/validation
- Add authentication middleware

**New Files:**
- `Backend/app/core/auth.py` (JWT utilities)
- `Backend/app/core/password.py` (hashing)
- `Backend/app/api/auth.py` (auth routes)

**Frontend Changes:**
- Install auth library: `npm install @auth/react jwt-decode`
- Create login/register pages
- Store JWT in localStorage
- Add auth headers to all API calls
- Implement protected routes

**New Files:**
- `Frontend/src/pages/Login.tsx`
- `Frontend/src/pages/Register.tsx`
- `Frontend/src/contexts/AuthContext.tsx`
- `Frontend/src/utils/auth.ts`

**Files to Modify:**
- `Frontend/src/App.tsx` (add protected routes)
- `Frontend/src/api/client.ts` (add auth headers)
- `Backend/requirements.txt`
- `Frontend/package.json`

---

#### Task 4.3.2: Dashboard Data Aggregation
**Backend Changes:**
- Create dashboard aggregation endpoint
- Fetch latest application for user
- Calculate current fiscal health score
- Get recent alerts (new overdrafts, low balance, etc.)
- Calculate next milestone progress

**Files to Create/Modify:**
- `Backend/app/services/dashboard_service.py` (NEW)
- `Backend/app/api/routes.py`

**Frontend Changes:**
- Remove hardcoded "Sarah" user data
- Call `GET /api/v1/dashboard` on load
- Display real user name, business, metrics

**Files to Modify:**
- `Frontend/src/pages/Dashboard.tsx`
- `Frontend/src/api/client.ts`

---

#### Task 4.3.3: Alerts & Notifications
**Backend Changes:**
- Create alert generation service
- Monitor for critical events:
  - New overdraft detected
  - Balance below threshold
  - Large unexpected transaction
  - Milestone reached
- Store in `alerts` table

**New Table:**
```sql
CREATE TABLE alerts (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    application_id VARCHAR REFERENCES applications(id),
    type VARCHAR, -- critical/warning/info
    title VARCHAR,
    message TEXT,
    data JSON,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
)
```

**Files to Create/Modify:**
- `Backend/app/services/alert_service.py` (NEW)
- `Backend/app/database/models.py`
- `Backend/app/api/routes.py`

**Frontend Changes:**
- Remove `DEMO_ALERTS`
- Call `GET /api/v1/dashboard/alerts`
- Display real alerts with timestamps

**Files to Modify:**
- `Frontend/src/components/recommendations/AlertsProgress.tsx`
- `Frontend/src/pages/Dashboard.tsx`

---

## Phase 5: Data Migration & Cleanup

### 5.1 Remove Mock Data

**Files to Clean:**
```
Frontend/src/api/recommendations.ts
  ❌ Remove: DEMO_STATS
  ❌ Remove: DEMO_RECOMMENDATIONS
  ❌ Remove: DEMO_TARGETS
  ❌ Remove: DEMO_ACTIONS
  ❌ Remove: DEMO_ALERTS
  ❌ Remove: DEMO_FINANCIAL_SNAPSHOT
  ❌ Remove: DEMO_PROGRESS

Frontend/src/components/wizard/BankDataStep.tsx
  ❌ Remove: SANDBOX_INSTITUTIONS (replace with Plaid Link)

Frontend/src/components/wizard/EvaluationStep.tsx
  ❌ Remove: MOCK_EVALUATION_RESPONSE
  ❌ Remove: mockAgents simulation loop

Frontend/src/pages/Dashboard.tsx
  ❌ Remove: Hardcoded user object { name: 'Sarah', ... }

Frontend/src/api/client.ts
  ❌ Remove: MOCK_SCENARIOS
  ❌ Remove: All mock fallback logic in catch blocks
```

### 5.2 Update Type Definitions

**Frontend Types to Update:**
```typescript
// Frontend/src/types/index.ts
export interface EvaluationResponse {
  // Align with backend AssessmentResponse
  eligibility: 'approved' | 'denied' | 'review'  // was: decision: 'APPROVE'
  confidence_score: number
  risk_level: 'low' | 'medium' | 'high'
  reasoning: string
  recommendations: Recommendation[]
  financial_metrics: FinancialMetrics
  market_analysis: MarketAnalysis
  community_impact: CommunityImpact  // NEW
  assessed_at: string
}

export interface CommunityImpact {  // NEW
  impact_score: number
  impact_multiplier: number
  social_benefits: string[]
  job_creation_potential: number
  local_economic_impact: string
}
```

---

## Phase 6: Testing & Validation

### 6.1 Integration Testing

**Backend Tests to Add:**
```
tests/integration/
  ├── test_full_evaluation_flow.py
  ├── test_plaid_integration.py
  ├── test_recommendations_generation.py
  ├── test_coach_agent.py
  ├── test_websocket_streaming.py
  └── test_auth_flow.py
```

**Frontend Tests to Add:**
```
Frontend/src/__tests__/
  ├── integration/
  │   ├── evaluation-wizard.test.tsx
  │   ├── plaid-connection.test.tsx
  │   ├── recommendations-page.test.tsx
  │   └── dashboard.test.tsx
  └── api/
      └── client.test.ts
```

### 6.2 End-to-End Testing

**E2E Test Scenarios:**
1. Complete evaluation flow (register → evaluate → view results)
2. Plaid connection with real sandbox credentials
3. Recommendation generation and action plan saving
4. Coach Q&A with custom questions
5. Dashboard data refresh after new evaluation

**Tools:**
- Playwright or Cypress for E2E
- Jest for unit tests
- Pytest for backend tests

---

## Phase 7: Deployment & Infrastructure

### 7.1 Environment Configuration

**Backend `.env` Requirements:**
```bash
# Database
DATABASE_URL=postgresql://...  # Upgrade from SQLite to PostgreSQL

# API Keys (existing)
GEMINI_API_KEY=
PLAID_CLIENT_ID=
PLAID_SECRET=
PLAID_ENV=sandbox  # Change to production when ready
GOOGLE_MAPS_API_KEY=
GOOGLE_PLACES_API_KEY=

# Security (NEW)
SECRET_KEY=  # For JWT signing
ENCRYPTION_KEY=  # Already exists
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://yourdomain.com,http://localhost:3000

# Feature Flags (NEW)
ENABLE_WEBSOCKET_STREAMING=true
ENABLE_EMAIL_NOTIFICATIONS=false
```

**Frontend `.env` Requirements:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_PLAID_ENV=sandbox
VITE_GOOGLE_MAPS_API_KEY=  # For Places Autocomplete
VITE_ENABLE_PASSKEYS=true
```

### 7.2 Database Migration

**Upgrade from SQLite to PostgreSQL:**
```bash
# Install PostgreSQL driver
pip install asyncpg

# Update DATABASE_URL
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Run migrations with Alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 7.3 Deployment Checklist

**Backend:**
- [ ] Set up PostgreSQL database (RDS, Supabase, or similar)
- [ ] Deploy to cloud (Railway, Render, AWS, etc.)
- [ ] Configure environment variables
- [ ] Enable HTTPS
- [ ] Set up WebSocket support
- [ ] Configure CORS for production domain
- [ ] Set up logging and monitoring (Sentry, LogRocket)

**Frontend:**
- [ ] Build production bundle: `npm run build`
- [ ] Deploy to Vercel/Netlify/Cloudflare Pages
- [ ] Configure environment variables
- [ ] Set up custom domain
- [ ] Enable HTTPS
- [ ] Configure CDN caching

---

## Phase 8: Nice-to-Have Features (Post-MVP)

### 8.1 WebAuthn/Passkey Signing
- Implement passkey registration endpoint
- Add WebAuthn challenge/verification
- Store credentials in database
- Enable passwordless login

### 8.2 Email Notifications
- Set up email service (SendGrid, AWS SES)
- Send evaluation completion emails
- Send milestone achievement emails
- Send action plan reminders

### 8.3 Multi-language Support
- Add i18n to frontend (react-i18next)
- Translate UI strings
- Support for Spanish, French, etc.

### 8.4 Mobile App
- Build React Native version
- Reuse API client logic
- Optimize UI for mobile

### 8.5 Advanced Analytics
- Track user engagement metrics
- A/B testing for recommendations
- Conversion funnel analysis
- User retention dashboard

---

## Implementation Timeline

### Week 1: Foundation
- **Days 1-2:** Database schema updates + migrations
- **Days 3-4:** Authentication system (backend + frontend)
- **Days 5-7:** Agent architecture updates (add Impact, Compliance, Coach)

### Week 2: Core Integration
- **Days 1-2:** Evaluation wizard backend endpoints
- **Days 3-4:** Real Plaid integration (frontend + backend)
- **Days 5-6:** WebSocket streaming for evaluation
- **Day 7:** Results display with real data

### Week 3: Recommendations & Dashboard
- **Days 1-2:** Recommendation generation service
- **Days 3-4:** Financial snapshot charts
- **Days 5-6:** Coach agent implementation
- **Day 7:** Dashboard data aggregation

### Week 4: Testing & Polish
- **Days 1-3:** Integration testing
- **Days 4-5:** E2E testing + bug fixes
- **Days 6-7:** Deployment + production setup

---

## Risk Mitigation

### High-Risk Items:
1. **Plaid API Rate Limits** → Implement caching, request throttling
2. **LLM Response Time** → Add timeout handling, queue system
3. **WebSocket Connection Drops** → Implement reconnection logic, fallback to polling
4. **Database Performance** → Add indexes, query optimization, caching layer
5. **API Key Costs** → Monitor usage, set spending limits

### Contingency Plans:
- Keep mock data fallback during development
- Implement graceful degradation for missing features
- Add feature flags to disable problematic features
- Have rollback strategy for database migrations

---

## Success Metrics

### Technical Metrics:
- [ ] 100% of mock data removed
- [ ] All evaluation steps connected to backend
- [ ] <3s evaluation completion time (with WebSocket)
- [ ] 99% uptime for API endpoints
- [ ] <500ms average API response time

### User Experience Metrics:
- [ ] Plaid connection success rate >95%
- [ ] Evaluation completion rate >80%
- [ ] User satisfaction score >4/5
- [ ] Action plan completion rate >40%

---

## Next Steps

1. **Review this plan** with the team
2. **Prioritize tasks** based on business value
3. **Set up project management** (GitHub Projects, Jira)
4. **Create detailed tickets** for each task
5. **Assign owners** to each phase
6. **Begin Week 1 implementation**

---

## Questions & Decisions Needed

1. **Authentication Method:** JWT tokens or session-based? (Recommended: JWT)
2. **Database:** PostgreSQL, MySQL, or MongoDB? (Recommended: PostgreSQL)
3. **Deployment Platform:** Railway, Render, AWS, or other? (Recommended: Railway for ease)
4. **Real-time Updates:** WebSocket or Server-Sent Events? (Recommended: WebSocket)
5. **Email Provider:** SendGrid, AWS SES, or other? (Recommended: SendGrid)
6. **Error Monitoring:** Sentry, LogRocket, or other? (Recommended: Sentry)
7. **API Documentation:** Auto-generate with FastAPI or manual? (Recommended: Auto-generate with Swagger)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-18
**Owner:** Development Team
