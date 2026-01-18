from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    user_job = Column(String, nullable=False)
    user_age = Column(Integer, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    location_address = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String, nullable=False)
    plaid_access_token = Column(String, nullable=True)  # Encrypted
    status = Column(String, nullable=False)  # pending_plaid, processing, completed
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
