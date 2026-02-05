"""
Risk Assessor Agent

Synthesizes financial and market data to make final loan decisions
"""
from typing import Dict, Any, Optional, List
import json
import re
import logging
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from .prompts import get_assessment_prompt, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class KeyFactors(BaseModel):
    """Key factors in the assessment"""
    financial_score: float = Field(ge=0, le=100)
    market_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)


class AssessmentOutput(BaseModel):
    """Structured output schema for risk assessment"""
    eligibility: str = Field(description="One of: approved, denied, review")
    confidence_score: float = Field(ge=0, le=100, description="Confidence score 0-100")
    risk_level: str = Field(description="One of: low, medium, high")
    reasoning: str = Field(description="Detailed 2-3 sentence explanation of decision")
    recommendations: List[str] = Field(description="List of specific recommendations")
    key_factors: KeyFactors


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

            # Use structured output to force valid JSON (Gemini 3 supports this)
            try:
                structured_llm = self.llm.with_structured_output(AssessmentOutput, method="json_schema")
                assessment_obj = structured_llm.invoke(prompt)
                # Convert Pydantic model to dict
                assessment = assessment_obj.model_dump()
            except Exception as struct_error:
                logger.warning(f"Structured output failed, falling back to parsing: {struct_error}")
                # Fallback to text parsing if structured output fails
                response = self.llm.invoke(prompt)
                content = response.content
                # LangChain/Gemini can return content as list of blocks (e.g. Gemini 3); normalize to str
                if isinstance(content, list):
                    content = " ".join(
                        (getattr(block, "text", None) or str(block) if not isinstance(block, str) else block)
                        for block in content
                    )
                elif not isinstance(content, str):
                    content = str(content)
                
                logger.debug(f"Raw LLM response (first 500 chars): {content[:500]}")
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
        Parse LLM response to extract assessment JSON.
        Handles markdown code blocks, raw JSON, and balanced-brace extraction.
        """
        if isinstance(content, list):
            content = " ".join(
                (getattr(block, "text", None) or str(block) if not isinstance(block, str) else block)
                for block in content
            )
        if not isinstance(content, str):
            content = str(content)

        # 1) Extract from markdown code block (```json ... ``` or ``` ... ```)
        for pattern in (r"```(?:json)?\s*([\s\S]*?)\s*```", r"```\s*([\s\S]*?)\s*```"):
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                raw = match.group(1).strip()
                out = self._try_parse_json(raw)
                if out is not None:
                    return out

        # 2) Extract first balanced {...} object
        start = content.find("{")
        if start != -1:
            depth = 0
            for i in range(start, len(content)):
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        raw = content[start : i + 1]
                        out = self._try_parse_json(raw)
                        if out is not None:
                            return out
                        break

        # 3) Greedy regex as last resort
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            out = self._try_parse_json(json_match.group())
            if out is not None:
                return out

        return {
            "eligibility": "review",
            "confidence_score": 50.0,
            "risk_level": "medium",
            "reasoning": "Unable to parse LLM response - manual review recommended",
            "recommendations": ["Manual review required"],
            "key_factors": {
                "financial_score": 50.0,
                "market_score": 50.0,
                "overall_score": 50.0,
            },
        }

    def _try_parse_json(self, raw: str) -> Optional[Dict[str, Any]]:
        """Try to parse a string as JSON; return None on failure."""
        if not raw or not raw.strip():
            return None
        raw = raw.strip()
        # Fix common LLM issues: replace single quotes with double (careful with apostrophes)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        # Try replacing single-quoted keys/strings (naive, for last resort)
        try:
            fixed = re.sub(r"'([^']*)'(\s*):", r'"\1"\2:', raw)
            fixed = re.sub(r":\s*'([^']*)'", r': "\1"', fixed)
            return json.loads(fixed)
        except (json.JSONDecodeError, TypeError):
            return None

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
        # Ensure required fields exist and are the right type
        if 'eligibility' not in assessment:
            assessment['eligibility'] = 'review'

        if 'confidence_score' not in assessment:
            assessment['confidence_score'] = 50.0

        if 'risk_level' not in assessment:
            assessment['risk_level'] = 'medium'

        if 'reasoning' not in assessment:
            assessment['reasoning'] = 'Assessment completed'
        # LLM may return reasoning as a list (e.g. multiple blocks); normalize to str
        if isinstance(assessment['reasoning'], list):
            assessment['reasoning'] = ' '.join(str(x) for x in assessment['reasoning'])
        elif not isinstance(assessment['reasoning'], str):
            assessment['reasoning'] = str(assessment['reasoning'])

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
