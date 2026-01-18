/**
 * Community Spark - Recommendations API Client
 *
 * Fetches recommendations and financial data from the backend.
 */

import { BASE_URL, ENDPOINTS } from '@/config';
import type {
  Recommendation,
  ActionItem,
  Target,
  FinancialSnapshot,
  HeaderStats,
} from '@/types/recommendations';

const SANDBOX_USER_ID = 'sandbox-user-001';

// Helper: map frontend actions to backend schema
function toBackendActionItem(action: ActionItem) {
  return {
    id: action.id,
    title: action.title,
    description: action.step,
    status: action.status,
    difficulty: action.difficulty,
    impact: action.impact,
    estimated_time: action.timeEstimate,
  };
}

// Helper: map backend actions to frontend schema
function fromBackendActionItem(item: any, timeframe: 30 | 60 | 90 = 30): ActionItem {
  return {
    id: item.id || `action-${crypto.randomUUID ? crypto.randomUUID() : Date.now()}`,
    title: item.title || 'Action item',
    step: item.description || item.step || '',
    difficulty: (item.difficulty || 'medium') as ActionItem['difficulty'],
    impact: (item.impact || 'medium') as ActionItem['impact'],
    timeEstimate: item.estimated_time || item.timeEstimate || '15 min',
    linkedInsightId: item.linked_insight_id || item.linkedInsightId || '',
    status: (item.status || 'pending') as ActionItem['status'],
    timeframe,
  };
}

// Helper: map frontend targets to backend schema
function toBackendTarget(target: Target) {
  return {
    name: target.name,
    current: (target as any).current ?? (target as any).currentValue ?? 0,
    recommended: (target as any).recommended ?? (target as any).recommendedValue ?? 0,
    unit: target.unit,
    description: (target as any).whyItMatters,
  };
}

// ============ API Methods ============

/**
 * Fetch recommendations for an application
 */
export async function fetchRecommendations(applicationId: string): Promise<Recommendation[]> {
  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.getRecommendations(applicationId)}`);

    if (!response.ok) {
      console.error('Failed to fetch recommendations:', response.statusText);
      return [];
    }

    const data = await response.json();

    // Map backend format to frontend format
    return data.map((rec: any) => ({
      id: rec.id,
      title: rec.title,
      whatWeSaw: rec.evidence_summary,
      whyItMatters: rec.why_matters,
      recommendedAction: rec.recommended_action,
      expectedImpact: rec.expected_impact,
      priority: rec.priority.toLowerCase(),
      category: rec.category,
      evidence: [
        ...(rec.evidence_data?.transactions || []).map((txn: any, idx: number) => ({
          id: `txn-${idx}`,
          type: 'transaction',
          merchant: txn.merchant || 'Unknown',
          date: txn.date || '',
          amount: txn.amount || 0,
          description: txn.description || '',
          category: txn.category || 'Other',
        })),
        ...(rec.evidence_data?.patterns || []).map((pattern: string, idx: number) => ({
          id: `pattern-${idx}`,
          type: 'pattern',
          description: pattern,
          category: 'Pattern',
        })),
        ...Object.entries(rec.evidence_data?.stats || {}).map(([key, value], idx) => ({
          id: `stat-${idx}`,
          type: 'stat',
          description: `${key}: ${value}`,
          category: 'Summary',
        })),
      ],
    }));
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    return [];
  }
}

/**
 * Fetch financial snapshot for charts
 */
export async function fetchFinancialSnapshot(applicationId: string): Promise<FinancialSnapshot | null> {
  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.getFinancialSnapshot(applicationId)}`);

    if (!response.ok) {
      console.error('Failed to fetch financial snapshot:', response.statusText);
      return null;
    }

    const data = await response.json();

    return {
      cashFlow: data.cash_flow_data,
      spendingByCategory: data.spending_by_category,
      stabilityTrend: data.stability_trend,
    };
  } catch (error) {
    console.error('Error fetching financial snapshot:', error);
    return null;
  }
}

/**
 * Fetch assessment data for header stats
 */
export async function fetchHeaderStats(applicationId: string): Promise<HeaderStats | null> {
  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.getAssessment(applicationId)}`);

    if (!response.ok) {
      console.error('Failed to fetch assessment:', response.statusText);
      return null;
    }

    const data = await response.json();

    // Calculate fiscal health score using same logic as RunEvaluationStep
    const metrics = data?.financial_metrics;
    let fiscalScore = 500;

    if (metrics) {
      // Good debt-to-income (below 0.3)
      if (metrics.debt_to_income_ratio && metrics.debt_to_income_ratio < 0.3) {
        fiscalScore += 200;
      } else if (metrics.debt_to_income_ratio && metrics.debt_to_income_ratio > 1.0) {
        // Bad debt-to-income (above 1.0) - penalize heavily
        fiscalScore -= 300;
      }

      // Savings rate bonus
      if (metrics.savings_rate && metrics.savings_rate > 20) {
        fiscalScore += 100;
      }

      // Income stability bonus
      if (metrics.income_stability_score && metrics.income_stability_score > 90) {
        fiscalScore += 100;
      }

      // Overdraft penalty - major red flag
      if (metrics.overdraft_count && metrics.overdraft_count > 0) {
        fiscalScore -= metrics.overdraft_count * 50; // -50 per overdraft
      }

      // Low balance penalty
      if (metrics.min_balance_6mo !== undefined && metrics.min_balance_6mo <= 0) {
        fiscalScore -= 100;
      }
    }

    // Ensure score stays in 0-1000 range
    fiscalScore = Math.max(0, Math.min(1000, fiscalScore));

    const cashFlowStability = metrics?.savings_rate || 0;

    return {
      fiscalHealthScore: fiscalScore,
      communityImpactMultiplier: 1.0, // TODO: Add to backend response
      cashFlowStability,
      riskFlagsCount: 0, // TODO: Calculate from recommendations
    };
  } catch (error) {
    console.error('Error fetching header stats:', error);
    return null;
  }
}

/**
 * Save action plan
 */
export async function savePlan(plan: {
  applicationId: string;
  timeframe: string;
  actionItems: ActionItem[];
  targets: Target[];
}): Promise<boolean> {
  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.savePlan}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        application_id: plan.applicationId,
        timeframe: plan.timeframe,
        action_items: plan.actionItems.map(toBackendActionItem),
        targets: plan.targets?.map(toBackendTarget) || [],
      }),
    });

    if (response.ok) {
      localStorage.setItem('savedActionPlan', JSON.stringify(plan.actionItems));
      return true;
    }

    console.error('Backend rejected action plan:', await response.text());
    return false;
  } catch (error) {
    console.error('Error saving plan:', error);
    return false;
  }
}

/**
 * Ask coach a question
 */
export async function askCoach(question: string, applicationId?: string): Promise<{
  response: string;
  action_steps: string[];
  expected_impact: string;
} | null> {
  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.askCoach}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        application_id: applicationId,
        context: {},
      }),
    });

    if (!response.ok) {
      console.error('Failed to ask coach:', response.statusText);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error asking coach:', error);
    return null;
  }
}

/**
 * Load saved plan (backend first, localStorage fallback)
 */
export async function loadSavedPlan(userId?: string): Promise<ActionItem[]> {
  const resolvedUserId = userId || localStorage.getItem('currentUserId') || SANDBOX_USER_ID;

  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.getPlans(resolvedUserId)}`);

    if (response.ok) {
      const plans = await response.json();
      if (Array.isArray(plans) && plans.length > 0) {
        const latestPlan = plans[0];
        const timeframeValue = parseInt(latestPlan.timeframe, 10);
        const timeframe: 30 | 60 | 90 =
          timeframeValue === 60 || timeframeValue === 90 ? timeframeValue : 30;

        const actions = (latestPlan.action_items || []).map(
          (item: any) => fromBackendActionItem(item, timeframe)
        );

        localStorage.setItem('savedActionPlan', JSON.stringify(actions));
        return actions;
      }
    } else {
      console.warn('No action plans found for user:', resolvedUserId);
    }
  } catch (error) {
    console.error('Error loading saved plan from backend:', error);
  }

  try {
    const saved = localStorage.getItem('savedActionPlan');
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Error loading saved plan from localStorage:', error);
    return [];
  }
}
