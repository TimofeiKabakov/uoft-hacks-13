"""
Gemini Helper for LLM-Enhanced Agent Reasoning

Provides Gemini API integration for agents to generate
more sophisticated analysis and explanations.
Temporarily replacing OpenAI due to quota limits.
"""

import os
from typing import Optional
try:
    import google.genai as genai
except ImportError:
    # Fallback to deprecated package if new one not available
    try:
        import google.generativeai as genai_old
        genai = genai_old
        USE_OLD_API = True
    except ImportError:
        genai = None
        USE_OLD_API = False
else:
    USE_OLD_API = False

from dotenv import load_dotenv
import json

# Load environment variables FIRST (before accessing them)
load_dotenv()

# Initialize Gemini client (will be None if API key not set)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Try to initialize Gemini client with error handling
gemini_client = None
gemini_model = None
if GEMINI_API_KEY and genai:
    try:
        if USE_OLD_API:
            # Old deprecated API
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            gemini_client = genai
        else:
            # New google.genai API
            gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[ERROR] Failed to initialize Gemini client: {e}")
        gemini_client = None
        gemini_model = None


def llm_enhance_impact_summary(
    business_profile: dict,
    community_metrics: dict,
    community_multiplier: float
) -> str:
    """
    Use LLM to generate a detailed community impact summary.
    
    Falls back to basic summary if Gemini is not configured.
    
    Args:
        business_profile: Business information
        community_metrics: Community data
        community_multiplier: Calculated multiplier (1.0-1.6)
        
    Returns:
        Detailed impact summary text
    """
    if not gemini_client:
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

        response = gemini_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                'temperature': 0.5,
                'max_output_tokens': 150,
            }
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"[WARNING] Gemini API call failed: {str(e)}")
        # Fallback to basic summary
        return f"Community impact multiplier of {community_multiplier:.2f}x applied based on local need and business type."


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
    if not gemini_client and not gemini_model:
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
        
        min_multiplier = max(1.0, base_multiplier - 0.1)
        max_multiplier = min(1.6, base_multiplier + 0.15)
        
        # STEP 2: LLM analyzes community impact within bounds
        prompt = f"""You are a Community Impact Analyst evaluating how a business serves underserved communities.
Provide nuanced impact assessment within deterministically calculated bounds.

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "community_multiplier": <float between {min_multiplier:.2f} and {max_multiplier:.2f}>,
  "reasoning": "<2-3 sentence explanation of community impact and social value>"
}}

MULTIPLIER CONSTRAINTS (CRITICAL):
- Your multiplier MUST be between {min_multiplier:.2f} and {max_multiplier:.2f}
- These bounds are from objective community need metrics
- You provide nuanced assessment WITHIN these bounds

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

Provide your multiplier and reasoning as JSON."""

        if USE_OLD_API and gemini_model:
            response = gemini_model.generate_content(prompt)
            response_text = response.text
        else:
            response = gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            response_text = response.text
        
        # Parse JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        llm_result = json.loads(response_text)
        
        # STEP 3: Combine deterministic + LLM results
        llm_multiplier = float(llm_result.get("community_multiplier", base_multiplier))
        final_multiplier = max(min_multiplier, min(max_multiplier, llm_multiplier))
        final_multiplier = round(final_multiplier, 2)
        reasoning = llm_result.get("reasoning", "Community impact assessed.")
        
        return {
            "community_multiplier": final_multiplier,
            "reasoning": reasoning,
            "applied_factors": applied_factors,
            "method": "hybrid",
            "deterministic_base": base_multiplier,
            "llm_multiplier": llm_multiplier,
            "bounds_note": f"Multiplier bounded {min_multiplier:.2f}-{max_multiplier:.2f} from community metrics"
        }
    
    except Exception as e:
        print(f"[WARNING] Gemini impact decision failed, using rule-based fallback: {str(e)}")
        return None


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
    if not gemini_client and not gemini_model:
        return None
    
    try:
        failed_checks = [c for c in policy_checks if not c.get("passed", True)]
        passed_checks = [c for c in policy_checks if c.get("passed", False)]
        
        prompt = f"""You are a Senior Loan Compliance Officer explaining a lending decision.
Provide a clear, professional explanation for a **{final_decision}** decision.

Respond with ONLY valid JSON (no markdown, no extra text):
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
- If REFER: Explain what needs manual review

**Decision Made:** {final_decision}

**Scoring:**
- Base financial score: {auditor_score}/100
- Community multiplier: {community_multiplier:.2f}x
- Adjusted score: {adjusted_score:.1f}/100

**Auditor Analysis:**
{auditor_summary}

**Community Impact Analysis:**
{impact_summary}

**Policy Checks:**
{', '.join([c.get('reason', 'Check passed') for c in passed_checks]) if passed_checks else 'All checks passed'}
{', '.join([c.get('reason', 'Check failed') for c in failed_checks]) if failed_checks else ''}

Provide a clear rationale for the {final_decision} decision."""

        if USE_OLD_API and gemini_model:
            response = gemini_model.generate_content(prompt)
            response_text = response.text
        else:
            response = gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            response_text = response.text
        
        # Parse JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        return result.get("rationale", f"{final_decision} based on adjusted score of {adjusted_score:.1f}/100.")
    
    except Exception as e:
        print(f"[WARNING] Gemini compliance rationale failed: {str(e)}")
        return None


def llm_enhance_compliance_rationale(
    final_decision: str,
    auditor_score: int,
    community_multiplier: float,
    adjusted_score: float,
    policy_checks: list
) -> str:
    """
    Use LLM to generate a detailed compliance decision rationale.
    
    Falls back to basic summary if Gemini is not configured.
    
    Args:
        final_decision: APPROVE, DENY, or REFER
        auditor_score: Base audit score
        community_multiplier: Impact multiplier
        adjusted_score: Final adjusted score
        policy_checks: List of policy check results
        
    Returns:
        Detailed rationale text
    """
    if not gemini_client:
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

        response = gemini_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                'temperature': 0.3,
                'max_output_tokens': 150,
            }
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"[WARNING] Gemini API call failed: {str(e)}")
        # Fallback to basic rationale
        return f"Decision: {final_decision} based on adjusted score of {adjusted_score:.1f}/100."


def llm_audit_decision(bank_data: dict) -> Optional[dict]:
    """
    Hybrid audit decision combining deterministic rules with LLM reasoning.
    
    Uses deterministic logic for flags and score bounds, then Gemini for
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
    if not gemini_client:
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
            flags.append("no_revenue_data")
        elif avg_monthly_revenue < 1000:
            flags.append("low_revenue")
        if revenue_months < 6 and revenue_months > 0:
            flags.append("insufficient_revenue_history")
        if volatility > 0.5:
            flags.append("high_volatility")
        if nsf_count >= 2:
            flags.append("nsf_occurrences")
        elif nsf_count >= 1:
            flags.append("nsf_occurrences")
        if debt_to_income > 0.5:
            flags.append("high_debt_to_income")
        if traditional_credit_score < 600:
            flags.append("low_credit_score")
        
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
        
        # STEP 2: Gemini analyzes within the bounds
        prompt = f"""You are a Senior Financial Auditor specializing in small business lending.
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

Be specific in your reasoning - cite actual numbers from the data.

Analyze this business's financial data and provide your nuanced assessment:

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

        response = gemini_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                'temperature': 0.4,
                'max_output_tokens': 500,
                'response_mime_type': 'application/json',
            }
        )
        
        llm_result = json.loads(response.text)
        
        # STEP 3: Combine deterministic + LLM results
        llm_score = int(llm_result.get("auditor_score", (min_score + max_score) // 2))
        
        # Enforce bounds (safety check)
        final_score = max(min_score, min(max_score, llm_score))
        
        # Build final reasoning with transparency
        reasoning = llm_result.get("reasoning", "Assessment completed.")
        reasoning_with_context = f"[Hybrid Analysis: Score bounds {min_score}-{max_score} from risk rules, {final_score} from Gemini analysis] {reasoning}"
        
        return {
            "auditor_score": final_score,
            "flags": flags,  # Use deterministic flags
            "reasoning": reasoning_with_context,
            "method": "hybrid",  # Tag as hybrid
            "deterministic_bounds": [min_score, max_score],
            "llm_score": llm_score
        }
    
    except Exception as e:
        print(f"[WARNING] Gemini audit decision failed, using rule-based fallback: {str(e)}")
        return None


def llm_generate_improvement_plan(
    auditor_flags: list,
    auditor_score: int,
    bank_data: dict,
    business_profile: dict,
    decision_rationale: str,
    final_decision: str
) -> Optional[dict]:
    """
    Use Gemini to generate a personalized improvement plan with spending habit analysis.
    
    Analyzes transaction patterns, spending habits, and financial behaviors
    to provide specific, actionable recommendations.
    
    Args:
        auditor_flags: List of risk flags
        auditor_score: Current financial health score
        bank_data: Financial features and metrics
        business_profile: Business information
        decision_rationale: Why the decision was made
        final_decision: DENY or REFER
        
    Returns:
        Dict with improvement plan or None if LLM unavailable
    """
    if not gemini_client and not gemini_model:
        return None
    
    try:
        # Build context for Gemini
        prompt = f"""You are a financial coach helping a small business owner improve their loan application.

**Current Situation:**
- Decision: {final_decision}
- Financial Health Score: {auditor_score}/100 (Need 75+ for approval)
- Business: {business_profile.get('name', 'Unknown')} ({business_profile.get('type', 'Unknown')})
- Risk Flags: {', '.join(auditor_flags) if auditor_flags else 'None'}

**Financial Metrics:**
- Average Monthly Revenue: ${bank_data.get('avg_monthly_revenue', 0):,.2f}
- Revenue Months: {bank_data.get('revenue_months', 0)}
- Revenue Volatility: {bank_data.get('volatility', 0):.2f} (0=stable, 1=volatile)
- NSF/Overdraft Count: {bank_data.get('nsf_count', 0)}
- Debt-to-Income Ratio: {bank_data.get('debt_to_income', 0):.2f}

**Decision Rationale:**
{decision_rationale}

**Your Task:**
Analyze their spending habits and financial behavior. If there are NSF fees, overdrafts, payday loans, gambling, excessive subscriptions, or poor cash management, call them out specifically and explain how these habits are hurting their loan application.

Provide a detailed improvement plan in JSON format with:
{{
  "spending_analysis": "2-3 sentences analyzing their spending habits and financial behavior. Be direct about bad habits if present.",
  "critical_issues": ["list 2-3 most critical problems"],
  "recommendations": [
    {{
      "issue": "specific problem",
      "action": "actionable step to fix it",
      "priority": "Critical|High|Medium|Low",
      "expected_impact": "+X points",
      "timeframe": "how long to implement"
    }}
  ],
  "timeline": "overall timeline (e.g., '3-6 months')",
  "target_score": 75,
  "resources": [
    {{
      "name": "resource name",
      "type": "Guide|Course|Tool",
      "description": "what it helps with"
    }}
  ]
}}

Be honest and direct. If they have gambling expenses, payday loans, or overdraft fees, explicitly mention these as red flags."""

        # Generate improvement plan
        if USE_OLD_API and gemini_model:
            response = gemini_model.generate_content(prompt)
            response_text = response.text
        else:
            response = gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            response_text = response.text
        
        # Parse JSON from response
        # Handle markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        improvement_plan = json.loads(response_text)
        
        # Add business info
        improvement_plan["decision"] = final_decision
        improvement_plan["business_name"] = business_profile.get("name", "Unknown")
        improvement_plan["current_score"] = auditor_score
        
        # Build summary from spending analysis + critical issues
        summary = improvement_plan.get("spending_analysis", "")
        if improvement_plan.get("critical_issues"):
            summary += f" Key issues: {', '.join(improvement_plan['critical_issues'][:2])}."
        
        improvement_plan["summary"] = summary
        
        return improvement_plan
    
    except Exception as e:
        print(f"[WARNING] Gemini improvement plan failed: {str(e)}")
        return None


