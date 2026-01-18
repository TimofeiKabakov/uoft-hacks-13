"""
Risk Assessor Agent

Synthesizes financial and market data to make final loan decisions
"""
from typing import Dict, Any
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI

from .prompts import get_assessment_prompt, SYSTEM_PROMPT


class RiskAssessor:
    """
    Agent responsible for final risk assessment and loan decision

    Synthesizes data from Financial Analyst and Market Researcher
    to make informed loan approval decisions.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize Risk Assessor agent

        Args:
            llm: Shared LLM instance
        """
        self.llm = llm

    async def assess(
        self,
        user_job: str,
        user_age: int,
        loan_amount: float,
        loan_purpose: str,
        financial_analysis: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform final risk assessment and make loan decision

        Args:
            user_job: Applicant's job/business
            user_age: Applicant's age
            loan_amount: Requested loan amount
            loan_purpose: Purpose of loan
            financial_analysis: Results from Financial Analyst
            market_analysis: Results from Market Researcher

        Returns:
            Dictionary with final assessment and decision
        """
        try:
            # Build prompt with all data
            prompt = get_assessment_prompt(
                user_job=user_job,
                user_age=user_age,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose,
                financial_analysis=financial_analysis,
                market_analysis=market_analysis
            )

            # Get LLM assessment
            response = self.llm.invoke(prompt)
            content = response.content

            # Parse LLM response
            assessment = self._parse_response(content)

            # Validate and enhance assessment
            assessment = self._validate_assessment(
                assessment,
                financial_analysis,
                market_analysis
            )

            return {
                'success': True,
                **assessment
            }

        except Exception as e:
            # Return safe default on error
            return {
                'success': False,
                'error': str(e),
                'eligibility': 'review',
                'confidence_score': 0.0,
                'risk_level': 'high',
                'reasoning': f'Error during assessment: {str(e)}',
                'recommendations': ['Manual review required due to system error'],
                'key_factors': {
                    'financial_score': 0.0,
                    'market_score': 0.0,
                    'overall_score': 0.0
                }
            }

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract assessment

        Args:
            content: LLM response content

        Returns:
            Parsed assessment dictionary
        """
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)

        if json_match:
            try:
                assessment = json.loads(json_match.group())
                return assessment
            except json.JSONDecodeError:
                pass

        # Fallback if parsing fails
        return {
            'eligibility': 'review',
            'confidence_score': 50.0,
            'risk_level': 'medium',
            'reasoning': 'Unable to parse LLM response - manual review recommended',
            'recommendations': ['Manual review required'],
            'key_factors': {
                'financial_score': 50.0,
                'market_score': 50.0,
                'overall_score': 50.0
            }
        }

    def _validate_assessment(
        self,
        assessment: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and enhance assessment with rule-based checks

        Args:
            assessment: LLM-generated assessment
            financial_analysis: Financial data
            market_analysis: Market data

        Returns:
            Validated and enhanced assessment
        """
        # Ensure required fields exist
        if 'eligibility' not in assessment:
            assessment['eligibility'] = 'review'

        if 'confidence_score' not in assessment:
            assessment['confidence_score'] = 50.0

        if 'risk_level' not in assessment:
            assessment['risk_level'] = 'medium'

        if 'reasoning' not in assessment:
            assessment['reasoning'] = 'Assessment completed'

        if 'recommendations' not in assessment:
            assessment['recommendations'] = []

        if 'key_factors' not in assessment:
            # Calculate key factors from data
            financial_score = financial_analysis.get('financial_health_score', 50.0)
            market_score = market_analysis.get('viability_score', 50.0)
            overall_score = (financial_score + market_score) / 2

            assessment['key_factors'] = {
                'financial_score': financial_score,
                'market_score': market_score,
                'overall_score': overall_score
            }

        # Apply rule-based validation
        assessment = self._apply_business_rules(
            assessment,
            financial_analysis,
            market_analysis
        )

        return assessment

    def _apply_business_rules(
        self,
        assessment: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply business rules to validate LLM decision

        Args:
            assessment: Current assessment
            financial_analysis: Financial data
            market_analysis: Market data

        Returns:
            Assessment with business rules applied
        """
        # Extract key metrics
        dti_ratio = financial_analysis.get('debt_to_income_ratio', 0)
        income_stability = financial_analysis.get('income_stability_score', 0)
        overdrafts = financial_analysis.get('overdraft_count', 0)
        financial_health = financial_analysis.get('financial_health_score', 0)
        market_viability = market_analysis.get('viability_score', 0)

        # Critical rejection criteria
        if dti_ratio > 60:
            assessment['eligibility'] = 'denied'
            assessment['risk_level'] = 'high'
            if 'Debt-to-income ratio exceeds 60%' not in assessment['reasoning']:
                assessment['reasoning'] += ' Critical: Debt-to-income ratio exceeds 60%.'

        if overdrafts > 5:
            assessment['risk_level'] = 'high'
            if assessment['eligibility'] == 'approved':
                assessment['eligibility'] = 'review'
            if 'Multiple overdrafts' not in assessment['reasoning']:
                assessment['reasoning'] += ' Concern: Multiple overdrafts detected.'

        if income_stability < 30:
            assessment['risk_level'] = 'high'
            if assessment['eligibility'] == 'approved':
                assessment['eligibility'] = 'review'

        # Strong approval criteria
        if (financial_health >= 75 and market_viability >= 70 and
            dti_ratio < 30 and overdrafts == 0):
            if assessment['eligibility'] == 'review':
                assessment['eligibility'] = 'approved'
                assessment['risk_level'] = 'low'

        # Ensure risk level matches eligibility
        if assessment['eligibility'] == 'denied' and assessment['risk_level'] == 'low':
            assessment['risk_level'] = 'high'

        if assessment['eligibility'] == 'approved' and assessment['risk_level'] == 'high':
            assessment['eligibility'] = 'review'

        return assessment
