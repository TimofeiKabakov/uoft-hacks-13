from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for backward compatibility
    user_job = Column(String, nullable=False)
    user_age = Column(Integer, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    location_address = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String, nullable=False)
    plaid_access_token = Column(String, nullable=True)  # Encrypted
    status = Column(String, nullable=False)  # pending_plaid, processing, completed
    # Additional fields for frontend integration
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    location_zip = Column(String, nullable=True)
    location_city = Column(String, nullable=True)
    location_state = Column(String, nullable=True)
    community_tags = Column(Text, nullable=True)  # JSON array
    years_in_operation = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)
    annual_revenue = Column(Float, nullable=True)
    employment_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialMetrics(Base):
    __tablename__ = "financial_metrics"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    debt_to_income_ratio = Column(Float, nullable=True)
    savings_rate = Column(Float, nullable=True)
    avg_monthly_balance = Column(Float, nullable=True)
    min_balance_6mo = Column(Float, nullable=True)
    overdraft_count = Column(Integer, nullable=True)
    income_stability_score = Column(Float, nullable=True)
    monthly_income = Column(Float, nullable=True)
    monthly_expenses = Column(Float, nullable=True)
    raw_plaid_data = Column(Text, nullable=True)  # JSON blob
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketAnalysis(Base):
    __tablename__ = "market_analysis"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    competitor_count = Column(Integer, nullable=True)
    market_density = Column(String, nullable=True)  # low, medium, high
    viability_score = Column(Float, nullable=True)
    market_insights = Column(Text, nullable=True)
    nearby_businesses = Column(Text, nullable=True)  # JSON array
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    eligibility = Column(String, nullable=False)  # approved, denied, review
    confidence_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)  # low, medium, high
    reasoning = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)  # JSON array
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    priority = Column(String, nullable=False)  # high, medium, low
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    evidence_summary = Column(Text, nullable=True)
    why_matters = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    expected_impact = Column(Text, nullable=True)
    evidence_data = Column(Text, nullable=True)  # JSON blob
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    timeframe = Column(String, nullable=False)  # 30/60/90
    action_items = Column(Text, nullable=False)  # JSON array
    targets = Column(Text, nullable=True)  # JSON array
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    cash_flow_data = Column(Text, nullable=True)  # JSON array
    spending_by_category = Column(Text, nullable=True)  # JSON array
    stability_trend = Column(Text, nullable=True)  # JSON array
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class CoachSession(Base):
    __tablename__ = "coach_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    application_id = Column(String, ForeignKey("applications.id"), nullable=True)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(Text, nullable=True)  # JSON blob
    created_at = Column(DateTime(timezone=True), server_default=func.now())
