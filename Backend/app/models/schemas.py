from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
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


class AssessmentResponse(BaseModel):
    eligibility: Eligibility
    confidence_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    reasoning: str
    recommendations: List[str]
    financial_metrics: FinancialMetricsResponse
    market_analysis: MarketAnalysisResponse
    assessed_at: datetime


class ApplicationStatusResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    created_at: datetime
    assessed_at: Optional[datetime] = None
    has_results: bool
