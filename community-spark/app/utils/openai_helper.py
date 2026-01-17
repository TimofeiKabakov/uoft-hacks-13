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


def llm_impact_decision(
    business_profile: dict,
    community_metrics: dict,
    auditor_score: int
) -> Optional[dict]:
    """
    Hybrid impact analysis combining deterministic community metrics with LLM reasoning.
    
    Uses deterministic logic for base multiplier and bounds, then LLM for
    nuanced community impact assessment within those constraints.
    
    Args:
        business_profile: Business information
        community_metrics: Community data
        auditor_score: Current audit score (context for impact)
    
    Returns:
        {
            "community_multiplier": float,
            "reasoning": str,
            "applied_factors": list
        }
        or None if LLM unavailable
    """
    if not openai_client:
        return None
    
    try:
        # STEP 1: Deterministic community impact calculation (base factors)
        business_type = business_profile.get("type", "unknown")
        nearest_competitor_miles = business_profile.get("nearest_competitor_miles", 999)
        hires_locally = business_profile.get("hires_locally", False)
        
        low_income_area = community_metrics.get("low_income_area", False)
        food_desert = community_metrics.get("food_desert", False)
        local_hiring_rate = community_metrics.get("local_hiring_rate", 0.5)
        nearest_grocery_miles = community_metrics.get("nearest_grocery_miles", 1.0)
        nearest_pharmacy_miles = community_metrics.get("nearest_pharmacy_miles", 0.8)
        
        # Calculate deterministic base multiplier
        base_multiplier = 1.0
        applied_factors = []
        
        if low_income_area:
            base_multiplier += 0.2
            applied_factors.append("low_income_area")
        
        if food_desert:
            base_multiplier += 0.20
            applied_factors.append("food_desert")
        
        grocery_types = ["grocery", "supermarket", "food", "market"]
        if any(gt in business_type.lower() for gt in grocery_types) and nearest_grocery_miles >= 5:
            base_multiplier += 0.10
            applied_factors.append("grocery_access_gap")
        
        pharmacy_types = ["pharmacy", "drugstore", "health"]
        if any(pt in business_type.lower() for pt in pharmacy_types) and nearest_pharmacy_miles >= 5:
            base_multiplier += 0.10
            applied_factors.append("pharmacy_access_gap")
        
        if local_hiring_rate >= 0.6:
            base_multiplier += 0.05
            applied_factors.append("high_local_hiring")
        
        if hires_locally:
            base_multiplier += 0.15
            applied_factors.append("commits_local_hiring")
        
        if nearest_competitor_miles > 10:
            base_multiplier += 0.15
            applied_factors.append("fills_market_gap")
        elif nearest_competitor_miles > 5:
            base_multiplier += 0.1
            applied_factors.append("moderate_competition")
        
        # Set bounds for LLM (community multipliers typically 1.0-1.6)
        min_multiplier = max(1.0, base_multiplier - 0.1)
        max_multiplier = min(1.6, base_multiplier + 0.15)
        
        # STEP 2: LLM analyzes community impact within bounds
        
        system_prompt = f"""You are a Community Impact Analyst evaluating how a business serves underserved communities.
Your role is to provide nuanced impact assessment within deterministically calculated bounds.

You must respond with ONLY a JSON object (no markdown, no extra text):
{{
  "community_multiplier": <float between {min_multiplier:.2f} and {max_multiplier:.2f}>,
  "reasoning": "<2-3 sentence explanation of community impact and social value>"
}}

MULTIPLIER CONSTRAINTS (CRITICAL):
- Your multiplier MUST be between {min_multiplier:.2f} and {max_multiplier:.2f}
- These bounds are from objective community need metrics
- You provide nuanced assessment WITHIN these bounds

Consider:
1. Severity of community need (food deserts, healthcare access, etc.)
2. Business's ability to address that need
3. Local economic impact (jobs, services, market gaps)
4. Current financial viability (context: auditor score is {auditor_score}/100)

Be specific about which community needs this business addresses."""

        user_prompt = f"""Assess this business's community impact:

**Business Profile:**
- Type: {business_type}
- ZIP: {business_profile.get('zip_code', 'N/A')}
- Hires locally: {hires_locally}
- Nearest competitor: {nearest_competitor_miles} miles

**Community Context:**
- Low-income area: {low_income_area}
- Food desert: {food_desert}
- Nearest grocery: {nearest_grocery_miles} miles
- Nearest pharmacy: {nearest_pharmacy_miles} miles
- Local hiring rate: {local_hiring_rate:.0%}

**Deterministic Community Analysis:**
- Base multiplier: {base_multiplier:.2f}x
- Applied factors: {', '.join(applied_factors) if applied_factors else 'Standard community profile'}
- Multiplier must be between {min_multiplier:.2f} and {max_multiplier:.2f}

**Financial Context:**
- Auditor score: {auditor_score}/100 (indicates business viability)

Within the bounds ({min_multiplier:.2f}-{max_multiplier:.2f}), assess:
1. How critical is this business to the community?
2. What specific needs does it address?
3. Is there sufficient financial viability to sustain the impact?

Provide your multiplier and reasoning."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=500
        )
        
        import json
        llm_result = json.loads(response.choices[0].message.content)
        
        # STEP 3: Combine deterministic + LLM results
        llm_multiplier = float(llm_result.get("community_multiplier", base_multiplier))
        
        # Enforce bounds (safety check)
        final_multiplier = max(min_multiplier, min(max_multiplier, llm_multiplier))
        final_multiplier = round(final_multiplier, 2)
        
        # Build final reasoning (clean, no verbose brackets)
        reasoning = llm_result.get("reasoning", "Community impact assessed.")
        
        return {
            "community_multiplier": final_multiplier,
            "reasoning": reasoning,
            "applied_factors": applied_factors,
            "method": "hybrid",
            "deterministic_base": base_multiplier,
            "llm_multiplier": llm_multiplier,
            "bounds_note": f"Multiplier bounded {min_multiplier:.2f}-{max_multiplier:.2f} from community metrics"  # Separate metadata
        }
    
    except Exception as e:
        print(f"[WARNING] LLM impact decision failed, using rule-based fallback: {str(e)}")
        return None


def llm_enhance_impact_summary(
    business_profile: dict,
    community_metrics: dict,
    community_multiplier: float
) -> str:
    """
    DEPRECATED: Use llm_impact_decision instead.
    
    Legacy function kept for backward compatibility.
    """
    if not openai_client:
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


def llm_compliance_rationale(
    final_decision: str,
    auditor_score: int,
    community_multiplier: float,
    adjusted_score: float,
    policy_checks: list,
    auditor_summary: str = "",
    impact_summary: str = ""
) -> Optional[str]:
    """
    Generate LLM-enhanced rationale for compliance decision.
    
    Decision itself is deterministic (rule-based), but explanation uses LLM
    for detailed, context-aware rationale that references agent findings.
    
    Args:
        final_decision: APPROVE, DENY, or REFER (already decided by rules)
        auditor_score: Financial score
        community_multiplier: Impact multiplier
        adjusted_score: Combined score
        policy_checks: List of policy check results
        auditor_summary: Auditor's reasoning
        impact_summary: Impact analyst's reasoning
        
    Returns:
        Detailed rationale string, or None if LLM unavailable
    """
    if not openai_client:
        return None
    
    try:
        # Build policy check summary
        failed_checks = [c for c in policy_checks if not c.get("passed", True)]
        passed_checks = [c for c in policy_checks if c.get("passed", False)]
        
        system_prompt = f"""You are a Senior Loan Compliance Officer explaining a lending decision.
Your role is to provide a clear, professional explanation for a **{final_decision}** decision.

You must respond with ONLY a JSON object (no markdown, no extra text):
{{
  "rationale": "<2-3 sentence professional explanation>"
}}

IMPORTANT:
- The decision ({final_decision}) was made by regulatory rules, NOT by you
- Your job is to EXPLAIN why this decision makes sense
- Reference specific data points and agent findings
- Be clear, fair, and professional
- If DENY: Be empathetic but firm about regulatory requirements
- If APPROVE: Highlight strengths and confirm compliance
- If REFER: Explain what needs manual review"""

        user_prompt = f"""Explain this {final_decision} decision:

**Deterministic Decision Analysis:**
- Base Score (Auditor): {auditor_score}/100
- Community Multiplier (Impact): {community_multiplier:.2f}x
- Adjusted Score: {adjusted_score:.1f}/100
- Final Decision: {final_decision}

**Policy Checks:**
"""
        
        if failed_checks:
            user_prompt += "Failed:\n"
            for check in failed_checks:
                user_prompt += f"  - {check.get('check')}: {check.get('value')} (threshold: {check.get('threshold')}) - {check.get('reason', '')}\n"
        
        if passed_checks:
            user_prompt += "Passed:\n"
            for check in passed_checks:
                user_prompt += f"  - {check.get('check')}: {check.get('value')} vs threshold {check.get('threshold')}\n"
        
        user_prompt += f"""
**Agent Findings:**
Auditor Assessment: {auditor_summary[:200] if auditor_summary else 'N/A'}
Impact Assessment: {impact_summary[:200] if impact_summary else 'N/A'}

Provide a professional 2-3 sentence explanation for this {final_decision} decision that:
1. References the key factors (scores, policy checks)
2. Acknowledges both financial and community aspects
3. Is clear and actionable for the applicant"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=300
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        rationale = result.get("rationale", "")
        
        # Return clean rationale (method is tracked separately in log)
        return rationale
    
    except Exception as e:
        print(f"[WARNING] LLM compliance rationale failed, using basic fallback: {str(e)}")
        return None


def llm_enhance_compliance_rationale(
    final_decision: str,
    auditor_score: int,
    community_multiplier: float,
    adjusted_score: float,
    policy_checks: list
) -> str:
    """
    DEPRECATED: Use llm_compliance_rationale instead.
    
    Kept for backward compatibility.
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
        
        # Build final reasoning (clean, no verbose brackets)
        reasoning = llm_result.get("reasoning", "Assessment completed.")
        
        return {
            "auditor_score": final_score,
            "flags": flags,  # Use deterministic flags
            "reasoning": reasoning,
            "method": "hybrid",  # Tag as hybrid
            "deterministic_bounds": [min_score, max_score],
            "llm_score": llm_score,
            "bounds_note": f"Score bounded {min_score}-{max_score} by risk rules"  # Separate metadata
        }
    
    except Exception as e:
        print(f"[WARNING] LLM audit decision failed, using rule-based fallback: {str(e)}")
        return None
