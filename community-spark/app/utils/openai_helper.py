"""
OpenAI Helper for LLM-Enhanced Agent Reasoning

Provides optional OpenAI integration for agents to generate
more sophisticated analysis and explanations.
"""

import os
from typing import Optional
from openai import OpenAI

# Initialize OpenAI client (will be None if API key not set)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def llm_enhance_audit_summary(
    bank_data: dict,
    audit_score: int,
    flags: list
) -> str:
    """
    Use LLM to generate a detailed audit summary.
    
    Falls back to basic summary if OpenAI is not configured.
    
    Args:
        bank_data: Financial data
        audit_score: Calculated audit score (1-100)
        flags: List of risk flags
        
    Returns:
        Detailed audit summary text
    """
    if not openai_client:
        # Fallback: basic summary without LLM
        return f"Audit score: {audit_score}/100. Flags: {len(flags)}. Basic financial assessment."
    
    try:
        prompt = f"""You are a financial auditor analyzing a small business loan application.

Bank Data:
- Average monthly revenue: ${bank_data.get('avg_monthly_revenue', 0):,.2f}
- Revenue months tracked: {bank_data.get('revenue_months', 0)}
- Revenue volatility: {bank_data.get('volatility', 0):.2f}
- NSF incidents: {bank_data.get('nsf_count', 0)}
- Debt-to-income ratio: {bank_data.get('debt_to_income', 0):.2f}
- Credit score: {bank_data.get('traditional_credit_score', 'N/A')}

Calculated Audit Score: {audit_score}/100
Risk Flags: {', '.join(flags) if flags else 'None'}

Provide a concise 2-3 sentence professional audit summary explaining the score and any concerns."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[
                {"role": "system", "content": "You are a professional financial auditor. Be concise and factual."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[WARNING] OpenAI API call failed: {str(e)}")
        # Fallback to basic summary
        return f"Audit score: {audit_score}/100 based on financial data analysis. {len(flags)} risk flag(s) identified."


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
        # Fallback: basic rationale without LLM
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

