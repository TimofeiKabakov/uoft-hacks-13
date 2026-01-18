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
    MarketDensity,
    RecommendationResponse,
    EvidenceData,
    Priority,
    CoachQuestionRequest,
    CoachResponse,
    ActionPlanSave,
    ActionPlanResponse,
    ActionItem,
    Target,
    FinancialSnapshotResponse,
    CashFlowDataPoint,
    SpendingCategory,
    StabilityDataPoint
)
from app.core.security import encrypt_token, decrypt_token
from app.services.plaid_service import PlaidService
from app.agents.orchestrator import Orchestrator
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
    Process loan assessment using multi-agent orchestrator

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

    # Create orchestrator and run assessment
    orchestrator = Orchestrator()
    results = await orchestrator.run_assessment(
        application_id=application_id,
        access_token=access_token,
        user_job=application.user_job,
        user_age=application.user_age,
        location_lat=application.location_lat,
        location_lng=application.location_lng,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose
    )

    # Extract results from orchestrator
    financial_metrics = results['financial_metrics']
    market_analysis = results['market_analysis']
    final_assessment = results['final_assessment']
    recommendations_list = results.get('recommendations', [])

    # Save results to database
    # Save financial metrics
    financial_id = str(uuid.uuid4())
    db_financial = models.FinancialMetrics(
        id=financial_id,
        application_id=application_id,
        monthly_income=financial_metrics.get('monthly_income', 0.0),
        monthly_expenses=financial_metrics.get('monthly_expenses', 0.0),
        debt_to_income_ratio=financial_metrics.get('debt_to_income_ratio', 0.0),
        savings_rate=financial_metrics.get('savings_rate', 0.0),
        avg_monthly_balance=financial_metrics.get('avg_monthly_balance', 0.0),
        min_balance_6mo=financial_metrics.get('min_balance_6mo', 0.0),
        overdraft_count=financial_metrics.get('overdraft_count', 0),
        income_stability_score=financial_metrics.get('income_stability_score', 0.0),
        raw_plaid_data=json.dumps(financial_metrics)
    )
    db.add(db_financial)

    # Save market analysis
    market_id = str(uuid.uuid4())
    db_market = models.MarketAnalysis(
        id=market_id,
        application_id=application_id,
        competitor_count=market_analysis.get('competitor_count', 0),
        market_density=market_analysis.get('market_density', 'unknown'),
        viability_score=market_analysis.get('viability_score', 50.0),
        market_insights=market_analysis.get('market_insights', ''),
        nearby_businesses=json.dumps(market_analysis.get('nearby_businesses', []))
    )
    db.add(db_market)

    # Save assessment
    assessment_id = str(uuid.uuid4())
    db_assessment = models.Assessment(
        id=assessment_id,
        application_id=application_id,
        eligibility=final_assessment.get('eligibility', 'review'),
        confidence_score=final_assessment.get('confidence_score', 0.0),
        risk_level=final_assessment.get('risk_level', 'medium'),
        reasoning=final_assessment.get('reasoning', ''),
        recommendations=json.dumps(final_assessment.get('recommendations', []))
    )
    db.add(db_assessment)

    # Save individual recommendations
    for rec in recommendations_list:
        rec_id = str(uuid.uuid4())
        db_recommendation = models.Recommendation(
            id=rec_id,
            application_id=application_id,
            priority=rec.get('priority', 'medium'),
            category=rec.get('category', 'General'),
            title=rec.get('title', ''),
            evidence_summary=rec.get('evidence_summary', ''),
            why_matters=rec.get('why_matters', ''),
            recommended_action=rec.get('recommended_action', ''),
            expected_impact=rec.get('expected_impact', ''),
            evidence_data=json.dumps({
                'transactions': rec.get('evidence_transactions', []),
                'patterns': rec.get('evidence_patterns', []),
                'stats': rec.get('evidence_stats', {})
            })
        )
        db.add(db_recommendation)

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


@router.get("/applications/{application_id}/recommendations", response_model=list[RecommendationResponse])
async def get_recommendations(
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized recommendations for an application
    """
    # Verify application exists
    app_result = await db.execute(
        select(models.Application).where(models.Application.id == application_id)
    )
    application = app_result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Get recommendations
    recs_result = await db.execute(
        select(models.Recommendation).where(
            models.Recommendation.application_id == application_id
        )
    )
    recommendations = recs_result.scalars().all()

    # Convert to response format
    result = []
    for rec in recommendations:
        evidence = json.loads(rec.evidence_data) if rec.evidence_data else {}
        result.append(RecommendationResponse(
            id=rec.id,
            priority=Priority(rec.priority),
            category=rec.category,
            title=rec.title,
            evidence_summary=rec.evidence_summary,
            why_matters=rec.why_matters,
            recommended_action=rec.recommended_action,
            expected_impact=rec.expected_impact,
            evidence_data=EvidenceData(**evidence)
        ))

    return result


@router.post("/coach/ask", response_model=CoachResponse)
async def ask_coach(
    request: CoachQuestionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ask the coach agent a question about assessment
    """
    from app.agents.coach import CoachAgent
    from app.agents.llm import get_llm
    from app.core.auth import DummyAuthService

    # Get current user (sandbox user for now)
    user = DummyAuthService.get_current_user()

    # If application_id provided, get assessment data
    financial_data = {}
    assessment_data = {}
    user_job = "Business Owner"

    if request.application_id:
        # Get application
        app_result = await db.execute(
            select(models.Application).where(models.Application.id == request.application_id)
        )
        application = app_result.scalar_one_or_none()

        if application:
            user_job = application.user_job

            # Get financial metrics
            financial_result = await db.execute(
                select(models.FinancialMetrics).where(
                    models.FinancialMetrics.application_id == request.application_id
                )
            )
            financial = financial_result.scalar_one_or_none()

            if financial:
                financial_data = {
                    'monthly_income': financial.monthly_income or 0,
                    'monthly_expenses': financial.monthly_expenses or 0,
                    'debt_to_income_ratio': financial.debt_to_income_ratio or 0,
                    'savings_rate': financial.savings_rate or 0,
                    'overdraft_count': financial.overdraft_count or 0
                }

            # Get assessment
            assessment_result = await db.execute(
                select(models.Assessment).where(
                    models.Assessment.application_id == request.application_id
                )
            )
            assessment = assessment_result.scalar_one_or_none()

            if assessment:
                assessment_data = {
                    'eligibility': assessment.eligibility,
                    'risk_level': assessment.risk_level,
                    'confidence_score': assessment.confidence_score or 0
                }

    # Create coach agent and answer question
    llm = get_llm()
    coach = CoachAgent(llm)

    response = await coach.answer_question(
        question=request.question,
        financial_data=financial_data,
        assessment_data=assessment_data,
        user_job=user_job,
        context=request.context
    )

    # Save to database
    session_id = str(uuid.uuid4())
    db_session = models.CoachSession(
        id=session_id,
        user_id=user.id,
        application_id=request.application_id,
        question=request.question,
        response=response['response'],
        context=json.dumps(request.context) if request.context else None
    )
    db.add(db_session)
    await db.commit()

    return CoachResponse(**response)


@router.post("/action-plans", response_model=ActionPlanResponse)
async def save_action_plan(
    plan: ActionPlanSave,
    db: AsyncSession = Depends(get_db)
):
    """
    Save an action plan
    """
    from app.core.auth import DummyAuthService

    # Get current user
    user = DummyAuthService.get_current_user()

    # Verify application exists
    app_result = await db.execute(
        select(models.Application).where(models.Application.id == plan.application_id)
    )
    application = app_result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Create action plan
    plan_id = str(uuid.uuid4())
    db_plan = models.ActionPlan(
        id=plan_id,
        user_id=user.id,
        application_id=plan.application_id,
        timeframe=plan.timeframe,
        action_items=json.dumps([item.model_dump() for item in plan.action_items]),
        targets=json.dumps([target.model_dump() for target in plan.targets]) if plan.targets else None
    )
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)

    return ActionPlanResponse(
        id=db_plan.id,
        user_id=db_plan.user_id,
        application_id=db_plan.application_id,
        timeframe=db_plan.timeframe,
        action_items=plan.action_items,
        targets=plan.targets or [],
        saved_at=db_plan.saved_at,
        updated_at=db_plan.updated_at
    )


@router.get("/action-plans/{user_id}", response_model=list[ActionPlanResponse])
async def get_action_plans(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all action plans for a user
    """
    plans_result = await db.execute(
        select(models.ActionPlan).where(models.ActionPlan.user_id == user_id)
    )
    plans = plans_result.scalars().all()

    result = []
    for plan in plans:
        action_items_data = json.loads(plan.action_items)
        targets_data = json.loads(plan.targets) if plan.targets else []

        result.append(ActionPlanResponse(
            id=plan.id,
            user_id=plan.user_id,
            application_id=plan.application_id,
            timeframe=plan.timeframe,
            action_items=[ActionItem(**item) for item in action_items_data],
            targets=[Target(**target) for target in targets_data],
            saved_at=plan.saved_at,
            updated_at=plan.updated_at
        ))

    return result


@router.get("/applications/{application_id}/financial-snapshot", response_model=FinancialSnapshotResponse)
async def get_financial_snapshot(
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get financial snapshot chart data
    """
    # Check if snapshot already exists
    snapshot_result = await db.execute(
        select(models.FinancialSnapshot).where(
            models.FinancialSnapshot.application_id == application_id
        )
    )
    snapshot = snapshot_result.scalar_one_or_none()

    if snapshot:
        # Return existing snapshot
        return FinancialSnapshotResponse(
            cash_flow_data=json.loads(snapshot.cash_flow_data),
            spending_by_category=json.loads(snapshot.spending_by_category),
            stability_trend=json.loads(snapshot.stability_trend)
        )

    # Generate new snapshot from Plaid data
    from app.services.plaid_service import PlaidService
    from datetime import timedelta

    # Get application
    app_result = await db.execute(
        select(models.Application).where(models.Application.id == application_id)
    )
    application = app_result.scalar_one_or_none()

    if not application or not application.plaid_access_token:
        raise HTTPException(status_code=404, detail="Application or Plaid data not found")

    # Decrypt access token
    access_token = decrypt_token(application.plaid_access_token)

    # Get transactions
    plaid_service = PlaidService()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    transactions_result = plaid_service.get_transactions(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )

    transactions = transactions_result.get('transactions', [])

    # Generate chart data
    from collections import defaultdict

    # Cash flow data (weekly)
    cash_flow = []
    weekly_data = defaultdict(lambda: {'inflow': 0, 'outflow': 0})

    for txn in transactions:
        date = txn.get('date', '')
        amount = txn.get('amount', 0)

        # Group by week
        week = date[:7] if len(date) >= 7 else date  # YYYY-MM format

        if amount < 0:
            weekly_data[week]['inflow'] += abs(amount)
        else:
            weekly_data[week]['outflow'] += amount

    balance = 0
    for week in sorted(weekly_data.keys())[-8:]:  # Last 8 weeks
        inflow = weekly_data[week]['inflow']
        outflow = weekly_data[week]['outflow']
        balance += inflow - outflow

        cash_flow.append({
            'date': week,
            'inflow': round(inflow, 2),
            'outflow': round(outflow, 2),
            'balance': round(balance, 2)
        })

    # Spending by category
    category_spending = defaultdict(float)
    total_spending = 0

    for txn in transactions:
        if txn.get('amount', 0) > 0:  # Positive = expense
            category = txn.get('category', ['Other'])[0] if txn.get('category') else 'Other'
            amount = txn.get('amount', 0)
            category_spending[category] += amount
            total_spending += amount

    spending_categories = []
    for category, amount in sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:6]:
        spending_categories.append({
            'category': category,
            'amount': round(amount, 2),
            'percentage': round((amount / total_spending * 100) if total_spending > 0 else 0, 1)
        })

    # Stability trend (weekly balance variance)
    stability = []
    for week in sorted(weekly_data.keys())[-6:]:  # Last 6 weeks
        inflow = weekly_data[week]['inflow']
        outflow = weekly_data[week]['outflow']
        net = inflow - outflow

        # Simple stability score: higher = more stable
        score = 100 - min(abs(net) / 100, 100)  # Simplified calculation

        stability.append({
            'date': week,
            'score': round(score, 1)
        })

    # Save snapshot to database
    snapshot_id = str(uuid.uuid4())
    db_snapshot = models.FinancialSnapshot(
        id=snapshot_id,
        application_id=application_id,
        cash_flow_data=json.dumps(cash_flow),
        spending_by_category=json.dumps(spending_categories),
        stability_trend=json.dumps(stability)
    )
    db.add(db_snapshot)
    await db.commit()

    return FinancialSnapshotResponse(
        cash_flow_data=[CashFlowDataPoint(**item) for item in cash_flow],
        spending_by_category=[SpendingCategory(**item) for item in spending_categories],
        stability_trend=[StabilityDataPoint(**item) for item in stability]
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
