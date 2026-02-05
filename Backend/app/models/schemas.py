from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ApplicationStatus(str, Enum):
    PENDING_PLAID = "pending_plaid"
    PROCESSING = "processing"
    COMPLETED = "completed"


class Eligibility(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    REVIEW = "review"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MarketDensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Request Schemas
class LocationData(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=1)


class ApplicationCreate(BaseModel):
    job: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=18, le=100)
    location: LocationData
    loan_amount: float = Field(..., gt=0)
    loan_purpose: str = Field(..., min_length=1, max_length=500)


class PlaidConnect(BaseModel):
    plaid_public_token: str = Field(..., min_length=1)


# Response Schemas
class ApplicationResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PlaidConnectResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    plaid_connected: bool


class NearbyBusiness(BaseModel):
    name: str
    type: str
    rating: Optional[float] = None
    distance_miles: float


class FinancialMetricsResponse(BaseModel):
    debt_to_income_ratio: Optional[float] = None
    savings_rate: Optional[float] = None
    avg_monthly_balance: Optional[float] = None
    min_balance_6mo: Optional[float] = None
    overdraft_count: Optional[int] = None
    income_stability_score: Optional[float] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None


class MarketAnalysisResponse(BaseModel):
    competitor_count: int
    market_density: MarketDensity
    viability_score: float
    market_insights: Optional[str] = None
    nearby_businesses: List[NearbyBusiness] = []


class ReasoningLogEntry(BaseModel):
    """Single entry in the agent reasoning log for traceability."""
    agent: str
    message: str
    timestamp: str
    severity: Optional[str] = "info"  # info, success, warning, error


class AssessmentResponse(BaseModel):
    eligibility: Eligibility
    confidence_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    reasoning: str
    recommendations: List[str]
    financial_metrics: FinancialMetricsResponse
    market_analysis: MarketAnalysisResponse
    assessed_at: datetime
    reasoning_log: Optional[List[ReasoningLogEntry]] = None


class ApplicationStatusResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    created_at: datetime
    assessed_at: Optional[datetime] = None
    has_results: bool


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# Business Profile Schemas
class BusinessProfileCreate(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=200)
    business_type: str = Field(..., min_length=1, max_length=100)
    location_zip: str = Field(..., min_length=1, max_length=20)
    location_city: str = Field(..., min_length=1, max_length=100)
    location_state: str = Field(..., min_length=1, max_length=100)
    community_tags: List[str] = []
    years_in_operation: int = Field(..., ge=0)
    employee_count: int = Field(..., ge=0)
    annual_revenue: float = Field(..., ge=0)
    employment_details: str = Field(..., min_length=1)


class ApplicationCreateExtended(BaseModel):
    user_id: Optional[str] = None
    job: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=18, le=100)
    location: LocationData
    loan_amount: float = Field(..., gt=0)
    loan_purpose: str = Field(..., min_length=1, max_length=500)
    business_profile: Optional[BusinessProfileCreate] = None


# Recommendation Schemas
class EvidenceData(BaseModel):
    transactions: Optional[List[Dict[str, Any]]] = []
    patterns: Optional[List[str]] = []
    stats: Optional[Dict[str, Any]] = {}


class RecommendationResponse(BaseModel):
    id: str
    priority: Priority
    category: str
    title: str
    evidence_summary: str
    why_matters: str
    recommended_action: str
    expected_impact: str
    evidence_data: Optional[EvidenceData] = None

    class Config:
        from_attributes = True


# Action Plan Schemas
class ActionItem(BaseModel):
    id: str
    title: str
    description: str
    status: str  # pending, in_progress, done
    difficulty: str  # easy, medium, hard
    impact: str  # low, medium, high
    estimated_time: Optional[str] = None


class Target(BaseModel):
    name: str
    current: float
    recommended: float
    unit: str
    description: Optional[str] = None


class ActionPlanSave(BaseModel):
    application_id: str
    timeframe: str  # 30, 60, 90
    action_items: List[ActionItem]
    targets: Optional[List[Target]] = []


class ActionPlanResponse(BaseModel):
    id: str
    user_id: str
    application_id: str
    timeframe: str
    action_items: List[ActionItem]
    targets: Optional[List[Target]] = []
    saved_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Financial Snapshot Schemas
class CashFlowDataPoint(BaseModel):
    date: str
    inflow: float
    outflow: float
    balance: float


class SpendingCategory(BaseModel):
    category: str
    amount: float
    percentage: float


class StabilityDataPoint(BaseModel):
    date: str
    score: float


class FinancialSnapshotResponse(BaseModel):
    cash_flow_data: List[CashFlowDataPoint]
    spending_by_category: List[SpendingCategory]
    stability_trend: List[StabilityDataPoint]

    class Config:
        from_attributes = True


# Coach Schemas
class CoachQuestionRequest(BaseModel):
    application_id: Optional[str] = None
    question: str = Field(..., min_length=1, max_length=500)
    context: Optional[Dict[str, Any]] = None


class CoachResponse(BaseModel):
    question: str
    response: str
    action_steps: List[str] = []
    expected_impact: Optional[str] = None

    class Config:
        from_attributes = True


# Enhanced Assessment Response with Recommendations
class AssessmentWithRecommendationsResponse(BaseModel):
    eligibility: Eligibility
    confidence_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    reasoning: str
    recommendations: List[RecommendationResponse]  # Changed from List[str]
    financial_metrics: FinancialMetricsResponse
    market_analysis: MarketAnalysisResponse
    assessed_at: datetime
