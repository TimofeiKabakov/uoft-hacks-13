"""
OpenAI Helper for LLM-Enhanced Agent Reasoning

Provides optional OpenAI integration for agents to generate
more sophisticated analysis and explanations.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables FIRST (before accessing them)
load_dotenv()

# Initialize OpenAI client (will be None if API key not set)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Try to initialize OpenAI client with error handling
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}")
        openai_client = None


def llm_enhance_impact_summary(
    business_profile: dict,
    community_metrics: dict,
    community_multiplier: float
) -> str:
    """
    Use LLM to generate a detailed community impact summary.
    
    Falls back to basic summary if OpenAI is not configured.
    
    Args:
        business_profile: Business information
        community_metrics: Community data
        community_multiplier: Calculated multiplier (1.0-1.6)
        
    Returns:
        Detailed impact summary text
    """
    if not openai_client:
        # Fallback: basic summary without LLM
        return f"Community multiplier: {community_multiplier:.2f}x. Serving {business_profile.get('type', 'community')}."
    
    try:
        prompt = f"""You are analyzing the community impact of a small business loan application.

Business:
- Type: {business_profile.get('type', 'N/A')}
- Location: Zip {business_profile.get('zip_code', 'N/A')}
- Hires locally: {business_profile.get('hires_locally', False)}

Community Context:
- Low-income area: {community_metrics.get('low_income_area', False)}
- Food desert: {community_metrics.get('food_desert', False)}
- Nearest grocery: {community_metrics.get('nearest_grocery_miles', 'N/A')} miles
- Nearest pharmacy: {community_metrics.get('nearest_pharmacy_miles', 'N/A')} miles
- Local hiring rate: {community_metrics.get('local_hiring_rate', 0):.0%}

Community Impact Multiplier: {community_multiplier:.2f}x

Provide a concise 2-3 sentence explanation of this business's potential positive impact on its community."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a community development expert. Be concise and highlight positive social impact."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[WARNING] OpenAI API call failed: {str(e)}")
        # Fallback to basic summary
        return f"Community impact multiplier of {community_multiplier:.2f}x applied based on local need and business type."


def llm_enhance_compliance_rationale(
    final_decision: str,
    auditor_score: int,
    community_multiplier: float,
    adjusted_score: float,
    policy_checks: list
) -> str:
    """
    Use LLM to generate a detailed compliance decision rationale.
    
    Falls back to basic summary if OpenAI is not configured.
    
    Args:
        final_decision: APPROVE, DENY, or REFER
        auditor_score: Base audit score
        community_multiplier: Impact multiplier
        adjusted_score: Final adjusted score
        policy_checks: List of policy check results
        
    Returns:
        Detailed rationale text
    """
    if not openai_client:
        return f"Decision: {final_decision}. Score: {auditor_score} → {adjusted_score:.1f} (multiplier: {community_multiplier:.2f}x)."
    
    try:
        prompt = f"""You are a loan compliance officer making a final decision.

Analysis:
- Base audit score: {auditor_score}/100
- Community impact multiplier: {community_multiplier:.2f}x
- Adjusted score: {adjusted_score:.1f}/100
- Policy checks: {', '.join(policy_checks) if policy_checks else 'All passed'}

Final Decision: {final_decision}

Provide a clear, professional 2-3 sentence rationale for this decision that the applicant would understand."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional loan officer. Be clear, fair, and empathetic."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[WARNING] OpenAI API call failed: {str(e)}")
        # Fallback to basic rationale
        return f"Decision: {final_decision} based on adjusted score of {adjusted_score:.1f}/100."


def llm_audit_decision(bank_data: dict) -> Optional[dict]:
    """
    Hybrid audit decision combining deterministic rules with LLM reasoning.
    
    Uses deterministic logic for flags and score bounds, then LLM for
    nuanced analysis and explanation within those constraints.
    
    Args:
        bank_data: Financial data dict
    
    Returns:
        {
            "auditor_score": int,
            "flags": list,
            "reasoning": str
        }
        or None if LLM unavailable
    """
    if not openai_client:
        # Fallback to rule-based if no API key
        return None
    
    try:
        # STEP 1: Deterministic analysis (hard rules)
        avg_monthly_revenue = bank_data.get('avg_monthly_revenue', 0)
        revenue_months = bank_data.get('revenue_months', 0)
        volatility = bank_data.get('volatility', 1.0)
        nsf_count = bank_data.get('nsf_count', 0)
        debt_to_income = bank_data.get('debt_to_income', 0.0)
        traditional_credit_score = bank_data.get('traditional_credit_score', 0)
        
        # Calculate deterministic flags
        flags = []
        if avg_monthly_revenue == 0 or revenue_months == 0:
            flags.append("no_revenue")
        elif avg_monthly_revenue < 1000:
            flags.append("low_revenue")
        if revenue_months < 6 and revenue_months > 0:
            flags.append("insufficient_revenue_history")
        if volatility > 0.5:
            flags.append("high_revenue_volatility")
        if nsf_count >= 2:
            flags.append("multiple_nsf_occurrences")
        elif nsf_count >= 1:
            flags.append("nsf_occurrences")
        if debt_to_income > 0.5:
            flags.append("high_debt_to_income")
        if traditional_credit_score < 600:
            flags.append("low_traditional_credit_score")
        
        # Calculate deterministic score bounds (hard constraints)
        if avg_monthly_revenue == 0 or revenue_months == 0:
            min_score, max_score = 1, 35  # Severe risk
        elif avg_monthly_revenue < 1000:
            min_score, max_score = 20, 50  # High risk
        elif nsf_count >= 2:
            min_score, max_score = 25, 55  # Multiple NSFs = high risk
        elif revenue_months < 3:
            min_score, max_score = 30, 60  # Very short history
        elif revenue_months < 6:
            min_score, max_score = 35, 70  # Short history
        else:
            min_score, max_score = 40, 100  # Normal range
        
        # STEP 2: LLM analyzes within the bounds
        system_prompt = f"""You are a Senior Financial Auditor specializing in small business lending.
Your role is to provide nuanced analysis and scoring within deterministically calculated bounds.

You must respond with ONLY a JSON object (no markdown, no extra text):
{{
  "auditor_score": <integer between {min_score} and {max_score}>,
  "reasoning": "<2-3 sentence explanation referencing specific data points>"
}}

SCORING CONSTRAINTS (CRITICAL):
- Your score MUST be between {min_score} and {max_score} (hard bounds from risk analysis)
- These bounds are calculated from objective criteria (revenue, NSF, history)
- You provide nuanced scoring WITHIN these bounds based on the full picture

Analysis priorities:
1. Revenue strength and consistency (primary for business viability)
2. Credit history and payment patterns
3. Debt management and financial discipline
4. Risk flags and red flags

Be specific in your reasoning - cite actual numbers from the data."""

        user_prompt = f"""Analyze this business's financial data and provide your nuanced assessment:

**Bank Transaction Data:**
- Average monthly revenue: ${avg_monthly_revenue:,.2f}
- Revenue months tracked: {revenue_months} months
- Revenue volatility: {volatility:.3f} (0 = stable, 1 = highly volatile)
- NSF (overdraft) incidents: {nsf_count}
- Debt-to-income ratio: {debt_to_income:.3f}
- Traditional credit score: {traditional_credit_score}

**Deterministic Risk Analysis:**
- Identified flags: {', '.join(flags) if flags else 'None'}
- Score must be between {min_score} and {max_score} based on objective risk criteria

Within these bounds ({min_score}-{max_score}), provide your expert assessment considering:
1. How the metrics compare to typical small business benchmarks
2. Any mitigating or aggravating factors
3. Overall creditworthiness for a business loan

Provide your score and detailed reasoning."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4,  # Slightly higher for nuanced analysis
            max_tokens=500
        )
        
        import json
        llm_result = json.loads(response.choices[0].message.content)
        
        # STEP 3: Combine deterministic + LLM results
        llm_score = int(llm_result.get("auditor_score", (min_score + max_score) // 2))
        
        # Enforce bounds (safety check)
        final_score = max(min_score, min(max_score, llm_score))
        
        # Build final reasoning with transparency
        reasoning = llm_result.get("reasoning", "Assessment completed.")
        reasoning_with_context = f"[Hybrid Analysis: Score bounds {min_score}-{max_score} from risk rules, {final_score} from LLM analysis] {reasoning}"
        
        return {
            "auditor_score": final_score,
            "flags": flags,  # Use deterministic flags
            "reasoning": reasoning_with_context,
            "method": "hybrid",  # Tag as hybrid
            "deterministic_bounds": [min_score, max_score],
            "llm_score": llm_score
        }
    
    except Exception as e:
        print(f"[WARNING] LLM audit decision failed, using rule-based fallback: {str(e)}")
        return None
