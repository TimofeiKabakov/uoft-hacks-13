"""
Orchestrator - Coordinates Multi-Agent Loan Assessment

This orchestrator manages the workflow between specialized agents:
- Financial Analyst: Analyzes financial health
- Market Researcher: Evaluates market conditions
- Risk Assessor: Makes final loan decision
- Coach: Generates personalized recommendations

The orchestrator runs Financial Analyst and Market Researcher in parallel
for optimal performance, then passes results to Risk Assessor for final decision,
and finally generates recommendations via Coach agent.
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.agents.llm import get_llm
from app.agents.financial_analyst import FinancialAnalyst
from app.agents.market_researcher import MarketResearcher
from app.agents.risk_assessor import RiskAssessor
from app.agents.coach import CoachAgent


class Orchestrator:
    """
    Orchestrates multi-agent loan assessment workflow

    Coordinates execution of specialized agents and manages data flow
    between them for optimal performance and accuracy.
    """

    def __init__(self):
        """
        Initialize Orchestrator with all specialized agents
        """
        # Get shared LLM instance
        llm = get_llm()

        # Initialize all agents with shared LLM
        self.financial_analyst = FinancialAnalyst(llm)
        self.market_researcher = MarketResearcher(llm)
        self.risk_assessor = RiskAssessor(llm)
        self.coach = CoachAgent(llm)

    async def run_assessment(
        self,
        application_id: str,
        access_token: str,
        user_job: str,
        user_age: int,
        location_lat: float,
        location_lng: float,
        loan_amount: float,
        loan_purpose: str
    ) -> Dict[str, Any]:
        """
        Execute full multi-agent assessment workflow

        This method orchestrates the entire loan assessment process:
        1. Runs Financial Analyst and Market Researcher in parallel
        2. Passes results to Risk Assessor for final decision
        3. Aggregates all results into comprehensive assessment

        Args:
            application_id: Unique application identifier
            access_token: Decrypted Plaid access token
            user_job: Applicant's job/business
            user_age: Applicant's age
            location_lat: Business location latitude
            location_lng: Business location longitude
            loan_amount: Requested loan amount
            loan_purpose: Purpose of the loan

        Returns:
            Dictionary containing:
            - financial_metrics: Financial analysis results
            - market_analysis: Market research results
            - final_assessment: Risk assessment and decision
            - metadata: Processing information
        """
        start_time = datetime.now()
        messages = []

        try:
            # Phase 1: Run Financial Analyst and Market Researcher in PARALLEL
            messages.append("Starting parallel analysis (Financial + Market)")

            financial_task = self.financial_analyst.analyze(
                access_token=access_token,
                user_job=user_job,
                user_age=user_age,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose
            )

            market_task = self.market_researcher.analyze(
                user_job=user_job,
                location_lat=location_lat,
                location_lng=location_lng,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose
            )

            # Execute both agents in parallel
            financial_results, market_results = await asyncio.gather(
                financial_task,
                market_task,
                return_exceptions=True
            )

            # Handle exceptions from parallel execution
            if isinstance(financial_results, Exception):
                messages.append(f"Financial analysis error: {str(financial_results)}")
                financial_results = self._get_default_financial_results(str(financial_results))
            else:
                messages.append("Financial analysis completed")

            if isinstance(market_results, Exception):
                messages.append(f"Market analysis error: {str(market_results)}")
                market_results = self._get_default_market_results(str(market_results))
            else:
                messages.append("Market analysis completed")

            # Phase 2: Run Risk Assessor with results from both agents
            messages.append("Starting risk assessment")

            risk_results = await self.risk_assessor.assess(
                user_job=user_job,
                user_age=user_age,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose,
                financial_analysis=financial_results,
                market_analysis=market_results
            )

            messages.append("Risk assessment completed")

            # Phase 3: Generate Recommendations via Coach Agent
            messages.append("Generating personalized recommendations")

            try:
                recommendations = await self.coach.generate_recommendations(
                    financial_data=financial_results,
                    market_data=market_results,
                    assessment_data=risk_results,
                    user_job=user_job,
                    user_age=user_age,
                    loan_amount=loan_amount,
                    loan_purpose=loan_purpose
                )
                messages.append(f"Generated {len(recommendations)} recommendations")
            except Exception as e:
                messages.append(f"Recommendation generation error: {str(e)}")
                recommendations = []

            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            # Aggregate results
            return {
                'success': True,
                'application_id': application_id,
                'financial_metrics': financial_results,
                'market_analysis': market_results,
                'final_assessment': risk_results,
                'recommendations': recommendations,
                'metadata': {
                    'processing_time_seconds': processing_time,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'messages': messages,
                    'agents_used': ['FinancialAnalyst', 'MarketResearcher', 'RiskAssessor', 'Coach'],
                    'parallel_execution': True
                }
            }

        except Exception as e:
            # Handle orchestration-level errors
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            messages.append(f"Orchestration error: {str(e)}")

            return {
                'success': False,
                'application_id': application_id,
                'error': str(e),
                'financial_metrics': self._get_default_financial_results(str(e)),
                'market_analysis': self._get_default_market_results(str(e)),
                'final_assessment': self._get_default_risk_results(str(e)),
                'recommendations': [],
                'metadata': {
                    'processing_time_seconds': processing_time,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'messages': messages,
                    'agents_used': [],
                    'parallel_execution': False
                }
            }

    def _get_default_financial_results(self, error: str) -> Dict[str, Any]:
        """
        Get default financial results on error

        Args:
            error: Error message

        Returns:
            Default financial analysis dictionary
        """
        return {
            'success': False,
            'error': error,
            'monthly_income': 0.0,
            'monthly_expenses': 0.0,
            'debt_to_income_ratio': 0.0,
            'savings_rate': 0.0,
            'avg_monthly_balance': 0.0,
            'min_balance_6mo': 0.0,
            'overdraft_count': 0,
            'income_stability_score': 0.0,
            'financial_health_score': 0.0,
            'key_findings': [f'Error in financial analysis: {error}'],
            'concerns': ['Unable to retrieve financial data'],
            'strengths': []
        }

    def _get_default_market_results(self, error: str) -> Dict[str, Any]:
        """
        Get default market results on error

        Args:
            error: Error message

        Returns:
            Default market analysis dictionary
        """
        return {
            'success': False,
            'error': error,
            'competitor_count': 0,
            'market_density': 'unknown',
            'viability_score': 50.0,
            'nearby_businesses': [],
            'market_insights': f'Error in market analysis: {error}',
            'opportunities': [],
            'risks': ['Unable to retrieve market data'],
            'recommendations': ['Manual market research recommended']
        }

    def _get_default_risk_results(self, error: str) -> Dict[str, Any]:
        """
        Get default risk assessment results on error

        Args:
            error: Error message

        Returns:
            Default risk assessment dictionary
        """
        return {
            'success': False,
            'error': error,
            'eligibility': 'review',
            'confidence_score': 0.0,
            'risk_level': 'high',
            'reasoning': f'System error during assessment: {error}',
            'recommendations': ['Manual review required due to system error'],
            'key_factors': {
                'financial_score': 0.0,
                'market_score': 0.0,
                'overall_score': 0.0
            }
        }
