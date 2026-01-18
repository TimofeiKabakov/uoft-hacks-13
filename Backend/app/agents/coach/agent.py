"""
Coach Agent

Generates personalized recommendations and provides guidance to applicants
"""
import json
import re
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agents.coach.prompts import (
    RECOMMENDATION_GENERATION_PROMPT,
    COACH_Q_AND_A_PROMPT
)


class CoachAgent:
    """
    Agent responsible for generating recommendations and providing guidance

    Creates actionable recommendations based on financial and market analysis,
    and answers user questions about their assessment.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize Coach agent

        Args:
            llm: Shared LLM instance
        """
        self.llm = llm

    async def generate_recommendations(
        self,
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any],
        assessment_data: Dict[str, Any],
        user_job: str,
        user_age: int,
        loan_amount: float,
        loan_purpose: str
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on complete assessment

        Args:
            financial_data: Financial analyst results
            market_data: Market researcher results
            assessment_data: Risk assessor results
            user_job: Applicant's job/business
            user_age: Applicant's age
            loan_amount: Requested loan amount
            loan_purpose: Purpose of the loan

        Returns:
            List of recommendation dictionaries
        """
        try:
            # Format the prompt with all data
            prompt = RECOMMENDATION_GENERATION_PROMPT.format(
                user_job=user_job,
                user_age=user_age,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose,
                # Financial metrics
                monthly_income=financial_data.get('monthly_income', 0),
                monthly_expenses=financial_data.get('monthly_expenses', 0),
                debt_to_income_ratio=financial_data.get('debt_to_income_ratio', 0),
                savings_rate=financial_data.get('savings_rate', 0),
                avg_monthly_balance=financial_data.get('avg_monthly_balance', 0),
                min_balance_6mo=financial_data.get('min_balance_6mo', 0),
                overdraft_count=financial_data.get('overdraft_count', 0),
                income_stability_score=financial_data.get('income_stability_score', 0),
                # Market metrics
                competitor_count=market_data.get('competitor_count', 0),
                market_density=market_data.get('market_density', 'unknown'),
                viability_score=market_data.get('viability_score', 0),
                market_insights=market_data.get('market_insights', 'No insights available'),
                # Assessment
                eligibility=assessment_data.get('eligibility', 'review'),
                risk_level=assessment_data.get('risk_level', 'medium'),
                confidence_score=assessment_data.get('confidence_score', 0),
                reasoning=assessment_data.get('reasoning', '')
            )

            # Call LLM
            response = await self.llm.ainvoke(prompt)
            response_text = response.content

            # Parse JSON response
            recommendations = self._parse_recommendations_response(response_text)

            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            # Return default recommendations on error
            return self._get_default_recommendations(financial_data, market_data)

    async def answer_question(
        self,
        question: str,
        financial_data: Dict[str, Any],
        assessment_data: Dict[str, Any],
        user_job: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Answer user's question about their assessment

        Args:
            question: User's question
            financial_data: Financial analyst results
            assessment_data: Risk assessor results
            user_job: Applicant's job/business
            context: Additional context

        Returns:
            Dictionary with response, action steps, and expected impact
        """
        try:
            # Format the prompt
            prompt = COACH_Q_AND_A_PROMPT.format(
                user_job=user_job,
                eligibility=assessment_data.get('eligibility', 'review'),
                risk_level=assessment_data.get('risk_level', 'medium'),
                confidence_score=assessment_data.get('confidence_score', 0),
                monthly_income=financial_data.get('monthly_income', 0),
                monthly_expenses=financial_data.get('monthly_expenses', 0),
                debt_to_income_ratio=financial_data.get('debt_to_income_ratio', 0),
                savings_rate=financial_data.get('savings_rate', 0),
                overdraft_count=financial_data.get('overdraft_count', 0),
                question=question,
                context=json.dumps(context) if context else "No additional context"
            )

            # Call LLM
            response = await self.llm.ainvoke(prompt)
            response_text = response.content

            # Parse JSON response
            result = self._parse_coach_response(response_text)

            return result

        except Exception as e:
            print(f"Error answering question: {str(e)}")
            return {
                'response': f"I understand your question about '{question}'. Based on your assessment, I recommend focusing on improving your financial metrics. Please try asking a more specific question, and I'll provide detailed guidance.",
                'action_steps': [
                    "Review your current financial metrics",
                    "Identify areas with the lowest scores",
                    "Create a 30-day action plan"
                ],
                'expected_impact': "Focused improvements can increase approval likelihood"
            }

    def _parse_recommendations_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response for recommendations"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('recommendations', [])

            # Try parsing entire response as JSON
            data = json.loads(response_text)
            return data.get('recommendations', [])

        except Exception as e:
            print(f"Error parsing recommendations response: {str(e)}")
            return []

    def _parse_coach_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for Q&A"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Try parsing entire response as JSON
            return json.loads(response_text)

        except Exception as e:
            print(f"Error parsing coach response: {str(e)}")
            return {
                'response': response_text[:200],
                'action_steps': ["Review your assessment", "Focus on key metrics", "Follow recommendations"],
                'expected_impact': "Improvements will increase approval likelihood"
            }

    def _get_default_recommendations(
        self,
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate default recommendations when LLM fails"""
        recommendations = []

        # Check DTI ratio
        dti = financial_data.get('debt_to_income_ratio', 0)
        if dti > 40:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Cash Flow',
                'title': 'Reduce Debt-to-Income Ratio',
                'evidence_summary': f'Your debt-to-income ratio is {dti:.1f}%, which is above the recommended 40% threshold.',
                'why_matters': 'A high DTI ratio indicates financial stress and reduces loan approval likelihood. Lenders prefer DTI below 40%.',
                'recommended_action': '• Review all debt obligations and prioritize high-interest debts\n• Explore debt consolidation options\n• Increase income or reduce discretionary expenses\n• Aim to reduce DTI by at least 10% within 90 days',
                'expected_impact': 'Reducing DTI to below 40% could significantly improve approval chances',
                'evidence_transactions': [],
                'evidence_patterns': ['High debt obligations relative to income'],
                'evidence_stats': {'current_dti': dti, 'recommended_dti': 40}
            })

        # Check overdrafts
        overdrafts = financial_data.get('overdraft_count', 0)
        if overdrafts > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Banking Habits',
                'title': 'Eliminate Overdraft Incidents',
                'evidence_summary': f'Your account had {overdrafts} overdraft incidents in the past 6 months.',
                'why_matters': 'Overdrafts signal poor cash flow management and are a major red flag for lenders. Zero overdrafts demonstrate financial responsibility.',
                'recommended_action': '• Set up low balance alerts on your bank account\n• Create a cash flow buffer of at least 1 month expenses\n• Enable overdraft protection if available\n• Track expenses daily to avoid surprises',
                'expected_impact': 'Zero overdrafts for 90 days will significantly improve your financial profile',
                'evidence_transactions': [],
                'evidence_patterns': ['Multiple overdraft fees charged'],
                'evidence_stats': {'overdraft_count': overdrafts, 'target': 0}
            })

        # Check savings rate
        savings_rate = financial_data.get('savings_rate', 0)
        if savings_rate < 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Cash Flow',
                'title': 'Increase Savings Rate',
                'evidence_summary': f'Your current savings rate is {savings_rate:.1f}%, below the recommended 15-20% for business owners.',
                'why_matters': 'A healthy savings rate demonstrates financial discipline and creates a safety net for unexpected expenses or slow periods.',
                'recommended_action': '• Review expenses and identify areas to cut\n• Automate savings transfers on income receipt days\n• Start with a goal of saving 15% of income\n• Build an emergency fund covering 3 months of expenses',
                'expected_impact': 'Increasing savings rate to 15% will strengthen your financial position',
                'evidence_transactions': [],
                'evidence_patterns': ['Low savings compared to income'],
                'evidence_stats': {'current_savings_rate': savings_rate, 'recommended': 15}
            })

        # Check market viability
        viability = market_data.get('viability_score', 0)
        if viability < 60:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Market Position',
                'title': 'Strengthen Market Positioning',
                'evidence_summary': f'Market viability score is {viability:.1f}/100, indicating moderate to high competition in your area.',
                'why_matters': 'Market positioning affects revenue potential and business sustainability, which are key factors in loan repayment ability.',
                'recommended_action': '• Identify your unique value proposition vs competitors\n• Focus on underserved customer segments\n• Develop a differentiation strategy\n• Consider partnerships or complementary services',
                'expected_impact': 'Better market positioning can increase revenue and loan repayment confidence',
                'evidence_transactions': [],
                'evidence_patterns': ['High competition in service area'],
                'evidence_stats': {'viability_score': viability, 'competitor_count': market_data.get('competitor_count', 0)}
            })

        return recommendations[:7]  # Return max 7 recommendations
