from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import uuid
import json
from datetime import datetime

from app.database.session import get_db
from app.database import models
from app.models.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    PlaidConnect,
    PlaidConnectResponse,
    AssessmentResponse,
    ApplicationStatusResponse,
    ApplicationStatus,
    FinancialMetricsResponse,
    MarketAnalysisResponse,
    NearbyBusiness,
    Eligibility,
    RiskLevel,
    MarketDensity
)
from app.core.security import encrypt_token, decrypt_token
from app.services.plaid_service import PlaidService
from app.agents.graph import create_assessment_graph, AgentState
from sqlalchemy import select

router = APIRouter()


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new loan application

    Returns application_id and status
    """
    # Generate unique ID
    app_id = str(uuid.uuid4())

    # Create database record
    db_application = models.Application(
        id=app_id,
        user_job=application.job,
        user_age=application.age,
        location_lat=application.location.lat,
        location_lng=application.location.lng,
        location_address=application.location.address,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose,
        status=ApplicationStatus.PENDING_PLAID.value
    )

    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)

    return ApplicationResponse(
        application_id=app_id,
        status=ApplicationStatus.PENDING_PLAID,
        created_at=db_application.created_at
    )


@router.post("/applications/{application_id}/plaid-connect", response_model=PlaidConnectResponse)
async def connect_plaid(
    application_id: str,
    plaid_data: PlaidConnect,
    db: AsyncSession = Depends(get_db)
):
    """
    Connect Plaid account to application

    Exchanges public token for access token and triggers assessment
    """
    # Get application
    result = await db.execute(
        select(models.Application).where(models.Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Exchange token
    plaid_service = PlaidService()
    try:
        access_token = plaid_service.exchange_public_token(
            plaid_data.plaid_public_token
        )

        # Encrypt and store access token
        encrypted_token = encrypt_token(access_token)
        application.plaid_access_token = encrypted_token
        application.status = ApplicationStatus.PROCESSING.value

        await db.commit()

        # Trigger async assessment (in production, use background task)
        # For now, we'll process synchronously
        await process_assessment(application_id, db)

        return PlaidConnectResponse(
            application_id=application_id,
            status=ApplicationStatus.PROCESSING,
            plaid_connected=True
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect Plaid: {str(e)}"
        )


async def process_assessment(application_id: str, db: AsyncSession):
    """
    Process loan assessment using multi-agent system

    This would typically be run as a background task
    """
    # Get application
    result = await db.execute(
        select(models.Application).where(models.Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        return

    # Decrypt access token
    access_token = decrypt_token(application.plaid_access_token)

    # Create initial state
    initial_state = AgentState(
        application_id=application_id,
        access_token=access_token,
        user_job=application.user_job,
        user_age=application.user_age,
        location_lat=application.location_lat,
        location_lng=application.location_lng,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose,
        financial_metrics={},
        market_analysis={},
        final_assessment=None,
        messages=[]
    )

    # Run agent graph
    graph = create_assessment_graph()
    final_state = graph.invoke(initial_state)

    # Save results to database
    # Save financial metrics
    financial_id = str(uuid.uuid4())
    db_financial = models.FinancialMetrics(
        id=financial_id,
        application_id=application_id,
        **final_state['financial_metrics'],
        raw_plaid_data=json.dumps(final_state['financial_metrics'])
    )
    db.add(db_financial)

    # Save market analysis
    market_id = str(uuid.uuid4())
    db_market = models.MarketAnalysis(
        id=market_id,
        application_id=application_id,
        competitor_count=final_state['market_analysis']['competitor_count'],
        market_density=final_state['market_analysis']['market_density'],
        viability_score=final_state['market_analysis']['viability_score'],
        market_insights=final_state['market_analysis']['market_insights'],
        nearby_businesses=json.dumps(final_state['market_analysis']['nearby_businesses'])
    )
    db.add(db_market)

    # Save assessment
    assessment_id = str(uuid.uuid4())
    final_assessment = final_state['final_assessment']
    db_assessment = models.Assessment(
        id=assessment_id,
        application_id=application_id,
        eligibility=final_assessment['eligibility'],
        confidence_score=final_assessment['confidence_score'],
        risk_level=final_assessment['risk_level'],
        reasoning=final_assessment['reasoning'],
        recommendations=json.dumps(final_assessment['recommendations'])
    )
    db.add(db_assessment)

    # Update application status
    application.status = ApplicationStatus.COMPLETED.value
    await db.commit()


@router.get("/applications/{application_id}/status", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get application status
    """
    result = await db.execute(
        select(models.Application).where(models.Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if assessment exists
    assessment_result = await db.execute(
        select(models.Assessment).where(models.Assessment.application_id == application_id)
    )
    assessment = assessment_result.scalar_one_or_none()

    return ApplicationStatusResponse(
        application_id=application_id,
        status=ApplicationStatus(application.status),
        created_at=application.created_at,
        assessed_at=assessment.assessed_at if assessment else None,
        has_results=assessment is not None
    )


@router.get("/applications/{application_id}/assessment", response_model=AssessmentResponse)
async def get_assessment(
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete assessment results
    """
    # Get application
    app_result = await db.execute(
        select(models.Application).where(models.Application.id == application_id)
    )
    application = app_result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status != ApplicationStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail="Assessment not yet complete"
        )

    # Get assessment
    assessment_result = await db.execute(
        select(models.Assessment).where(models.Assessment.application_id == application_id)
    )
    assessment = assessment_result.scalar_one_or_none()

    # Get financial metrics
    financial_result = await db.execute(
        select(models.FinancialMetrics).where(models.FinancialMetrics.application_id == application_id)
    )
    financial = financial_result.scalar_one_or_none()

    # Get market analysis
    market_result = await db.execute(
        select(models.MarketAnalysis).where(models.MarketAnalysis.application_id == application_id)
    )
    market = market_result.scalar_one_or_none()

    if not assessment or not financial or not market:
        raise HTTPException(status_code=404, detail="Assessment data not found")

    # Parse nearby businesses
    nearby_businesses = json.loads(market.nearby_businesses) if market.nearby_businesses else []

    return AssessmentResponse(
        eligibility=Eligibility(assessment.eligibility),
        confidence_score=assessment.confidence_score,
        risk_level=RiskLevel(assessment.risk_level),
        reasoning=assessment.reasoning,
        recommendations=json.loads(assessment.recommendations),
        financial_metrics=FinancialMetricsResponse(
            debt_to_income_ratio=financial.debt_to_income_ratio,
            savings_rate=financial.savings_rate,
            avg_monthly_balance=financial.avg_monthly_balance,
            min_balance_6mo=financial.min_balance_6mo,
            overdraft_count=financial.overdraft_count,
            income_stability_score=financial.income_stability_score,
            monthly_income=financial.monthly_income,
            monthly_expenses=financial.monthly_expenses
        ),
        market_analysis=MarketAnalysisResponse(
            competitor_count=market.competitor_count,
            market_density=MarketDensity(market.market_density),
            viability_score=market.viability_score,
            market_insights=market.market_insights,
            nearby_businesses=[NearbyBusiness(**b) for b in nearby_businesses]
        ),
        assessed_at=assessment.assessed_at
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
