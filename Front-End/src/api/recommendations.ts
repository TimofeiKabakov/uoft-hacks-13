/**
 * Community Spark - Recommendations API Client
 * 
 * Frontend-only API layer for recommendations data.
 * Falls back to demo data if endpoints are unavailable.
 */

import { BASE_URL, ENDPOINTS } from '@/config';
import type {
  RecommendationsState,
  Recommendation,
  ActionItem,
  Target,
  Alert,
  FinancialSnapshot,
  HeaderStats,
  ProgressData,
} from '@/types/recommendations';

// Demo/fallback data
export const DEMO_STATS: HeaderStats = {
  fiscalHealthScore: 682,
  communityImpactMultiplier: 1.4,
  cashFlowStability: 73,
  riskFlagsCount: 3,
};

export const DEMO_RECOMMENDATIONS: Recommendation[] = [
  {
    id: 'rec-1',
    title: 'High subscription spend relative to revenue',
    whatWeSaw: '$847/month in recurring subscriptions (12% of monthly revenue). 3 subscriptions appear unused in 60+ days.',
    whyItMatters: 'Lenders view high fixed costs as a risk factor. Reducing discretionary subscriptions improves your debt-to-income ratio.',
    recommendedAction: 'Cancel or pause SaaS tools not actively used. Target: reduce to under $500/month.',
    expectedImpact: '+5–8 points to Fiscal Health Score',
    priority: 'high',
    category: 'Subscription Bloat',
    evidence: [
      { id: 'e1', type: 'transaction', merchant: 'Adobe Creative Cloud', date: '2024-01-15', amount: 54.99, description: 'Monthly subscription - no logins in 45 days', category: 'Software' },
      { id: 'e2', type: 'transaction', merchant: 'Salesforce', date: '2024-01-10', amount: 150.00, description: 'CRM subscription - 2 active users of 10 seats', category: 'Software' },
      { id: 'e3', type: 'stat', description: 'Total recurring: $847/mo across 12 subscriptions', category: 'Summary' },
    ],
  },
  {
    id: 'rec-2',
    title: 'Recent overdraft events detected',
    whatWeSaw: '2 NSF fees totaling $68 in the past 60 days. Account balance dropped below $0 on Jan 8 and Jan 22.',
    whyItMatters: 'Overdrafts signal cash flow stress and poor reserves. This is a key risk indicator for lenders.',
    recommendedAction: 'Set up low balance alerts at $500. Maintain a 5-day buffer minimum.',
    expectedImpact: '+10–15 points if no overdrafts for 90 days',
    priority: 'high',
    category: 'Cash Flow Risk',
    evidence: [
      { id: 'e4', type: 'transaction', merchant: 'Bank Fee', date: '2024-01-22', amount: -34.00, description: 'NSF/Overdraft fee', category: 'Fees' },
      { id: 'e5', type: 'transaction', merchant: 'Bank Fee', date: '2024-01-08', amount: -34.00, description: 'NSF/Overdraft fee', category: 'Fees' },
      { id: 'e6', type: 'pattern', description: 'Balance dropped below $100 on 5 occasions in 60 days', category: 'Risk Pattern' },
    ],
  },
  {
    id: 'rec-3',
    title: 'Revenue concentration risk',
    whatWeSaw: '78% of income comes from a single client (Acme Corp). No secondary revenue streams detected.',
    whyItMatters: 'Single-client dependency is a business continuity risk. Diversified income signals stability.',
    recommendedAction: 'Pursue 1-2 additional clients to reduce concentration below 50%.',
    expectedImpact: '+3–5 points to stability score',
    priority: 'medium',
    category: 'Revenue Risk',
    evidence: [
      { id: 'e7', type: 'stat', description: 'Acme Corp: $12,400/mo (78% of total)', category: 'Income' },
      { id: 'e8', type: 'stat', description: 'Other clients: $3,500/mo combined', category: 'Income' },
    ],
  },
  {
    id: 'rec-4',
    title: 'Strong community engagement (positive)',
    whatWeSaw: 'Active local business network member. 4 vendor relationships with local suppliers. Community bank customer for 3+ years.',
    whyItMatters: 'Community ties indicate stability and reduce flight risk. This positively influences your evaluation.',
    recommendedAction: 'Continue community involvement. Consider documenting partnerships.',
    expectedImpact: 'Already contributing +8 points to Impact Multiplier',
    priority: 'low',
    category: 'Positive Signal',
    evidence: [
      { id: 'e9', type: 'pattern', description: 'Member: Downtown Business Alliance since 2021', category: 'Community' },
      { id: 'e10', type: 'pattern', description: '4 recurring payments to local suppliers', category: 'Community' },
    ],
  },
  {
    id: 'rec-5',
    title: 'Irregular payment timing',
    whatWeSaw: 'Bill payments vary by 5-15 days month over month. 2 late fees in past 90 days.',
    whyItMatters: 'Consistent payment timing demonstrates financial discipline and reduces perceived risk.',
    recommendedAction: 'Set up auto-pay for recurring bills. Target: all bills paid within 3-day window.',
    expectedImpact: '+4–6 points to Fiscal Health Score',
    priority: 'medium',
    category: 'Payment Behavior',
    evidence: [
      { id: 'e11', type: 'transaction', merchant: 'Internet Provider', date: '2024-01-18', amount: -15.00, description: 'Late fee', category: 'Fees' },
      { id: 'e12', type: 'pattern', description: 'Rent paid between 1st and 12th across 6 months', category: 'Timing' },
    ],
  },
];

export const DEMO_TARGETS: Target[] = [
  {
    id: 'target-1',
    name: 'Max Discretionary Spend',
    currentValue: 2400,
    recommendedValue: 1800,
    unit: '$/month',
    whyItMatters: 'Lower discretionary spend improves your debt-to-income ratio',
    icon: 'CreditCard',
  },
  {
    id: 'target-2',
    name: 'Subscription Cap',
    currentValue: 847,
    recommendedValue: 500,
    unit: '$/month',
    whyItMatters: 'Reducing fixed costs demonstrates financial discipline',
    icon: 'Repeat',
  },
  {
    id: 'target-3',
    name: 'Minimum Buffer Days',
    currentValue: 8,
    recommendedValue: 15,
    unit: 'days',
    whyItMatters: 'Higher reserves protect against cash flow disruptions',
    icon: 'Shield',
  },
  {
    id: 'target-4',
    name: 'Monthly Overdrafts',
    currentValue: 2,
    recommendedValue: 0,
    unit: 'events',
    whyItMatters: 'Zero overdrafts is a key threshold for preferred rates',
    icon: 'AlertTriangle',
  },
];

export const DEMO_ACTIONS: ActionItem[] = [
  // 30-day actions
  { id: 'a1', title: 'Cancel unused Adobe subscription', step: 'Log into Adobe, navigate to subscriptions, select cancel', difficulty: 'easy', impact: 'medium', timeEstimate: '10 min', linkedInsightId: 'rec-1', status: 'pending', timeframe: 30 },
  { id: 'a2', title: 'Set up low balance alert', step: 'Configure bank alert for when balance drops below $500', difficulty: 'easy', impact: 'high', timeEstimate: '5 min', linkedInsightId: 'rec-2', status: 'pending', timeframe: 30 },
  { id: 'a3', title: 'Enable auto-pay for rent', step: 'Set up automatic payment for the 1st of each month', difficulty: 'easy', impact: 'medium', timeEstimate: '15 min', linkedInsightId: 'rec-5', status: 'in_progress', timeframe: 30 },
  // 60-day actions
  { id: 'a4', title: 'Reduce Salesforce seats', step: 'Contact Salesforce to downgrade from 10 to 4 seats', difficulty: 'medium', impact: 'medium', timeEstimate: '30 min', linkedInsightId: 'rec-1', status: 'pending', timeframe: 60 },
  { id: 'a5', title: 'Build $2,000 emergency buffer', step: 'Set aside $500/week for 4 weeks into savings', difficulty: 'medium', impact: 'high', timeEstimate: 'Ongoing', linkedInsightId: 'rec-2', status: 'pending', timeframe: 60 },
  { id: 'a6', title: 'Pitch 2 new prospective clients', step: 'Identify and contact 2 potential clients to diversify revenue', difficulty: 'hard', impact: 'high', timeEstimate: '2 hours', linkedInsightId: 'rec-3', status: 'pending', timeframe: 60 },
  // 90-day actions
  { id: 'a7', title: 'Maintain zero overdrafts', step: 'Track balance daily, maintain minimum $500 buffer', difficulty: 'medium', impact: 'high', timeEstimate: 'Ongoing', linkedInsightId: 'rec-2', status: 'pending', timeframe: 90 },
  { id: 'a8', title: 'Close secondary revenue deal', step: 'Finalize contract with at least one new client', difficulty: 'hard', impact: 'high', timeEstimate: '1-2 weeks', linkedInsightId: 'rec-3', status: 'pending', timeframe: 90 },
  { id: 'a9', title: 'Document community partnerships', step: 'Collect letters of support from 2 local partners', difficulty: 'easy', impact: 'low', timeEstimate: '1 hour', linkedInsightId: 'rec-4', status: 'pending', timeframe: 90 },
];

export const DEMO_ALERTS: Alert[] = [
  {
    id: 'alert-1',
    severity: 'critical',
    title: 'End of month approaching',
    message: 'Historically, your balance drops significantly between the 25th-28th. Consider reserving funds.',
    suggestedAction: 'Transfer $800 to savings before the 25th',
    timestamp: new Date().toISOString(),
  },
  {
    id: 'alert-2',
    severity: 'warning',
    title: 'Subscription renewal in 5 days',
    message: 'Adobe Creative Cloud will renew on Jan 28 for $54.99.',
    suggestedAction: 'Cancel before renewal to save $54.99/month',
  },
  {
    id: 'alert-3',
    severity: 'info',
    title: 'Positive pattern detected',
    message: 'No overdrafts in the past 14 days - keep it up!',
    suggestedAction: 'Maintain current buffer levels',
  },
];

export const DEMO_FINANCIAL_SNAPSHOT: FinancialSnapshot = {
  cashFlow: [
    { date: 'Dec 1', inflow: 4200, outflow: 3800, balance: 2400 },
    { date: 'Dec 8', inflow: 1200, outflow: 2100, balance: 1500 },
    { date: 'Dec 15', inflow: 5800, outflow: 3200, balance: 4100 },
    { date: 'Dec 22', inflow: 800, outflow: 2900, balance: 2000 },
    { date: 'Dec 29', inflow: 3500, outflow: 2400, balance: 3100 },
    { date: 'Jan 5', inflow: 4800, outflow: 3600, balance: 4300 },
    { date: 'Jan 12', inflow: 1100, outflow: 2800, balance: 2600 },
    { date: 'Jan 19', inflow: 6200, outflow: 4100, balance: 4700 },
  ],
  spendingByCategory: [
    { name: 'Fees', value: 312, color: 'hsl(var(--destructive))' },
    { name: 'Subscriptions', value: 847, color: 'hsl(var(--chart-2))' },
    { name: 'Rent', value: 2400, color: 'hsl(var(--chart-1))' },
    { name: 'Utilities', value: 380, color: 'hsl(var(--chart-3))' },
    { name: 'Other', value: 1260, color: 'hsl(var(--chart-4))' },
  ],
  stabilityTrend: [
    { date: 'Week 1', score: 65 },
    { date: 'Week 2', score: 68 },
    { date: 'Week 3', score: 62 },
    { date: 'Week 4', score: 71 },
    { date: 'Week 5', score: 69 },
    { date: 'Week 6', score: 73 },
  ],
};

export const DEMO_PROGRESS: ProgressData = {
  streakDays: 14,
  streakType: 'No overdrafts',
  completedActions: 2,
  totalActions: 9,
  scoreTrend: 'up',
  approvalProgress: 68,
};

// API functions with fallback
export async function fetchRecommendations(): Promise<RecommendationsState> {
  try {
    const response = await fetch(`${BASE_URL}${ENDPOINTS.evaluate}`);
    if (!response.ok) throw new Error('Failed to fetch');
    return await response.json();
  } catch {
    // Return demo data as fallback
    return {
      decision: 'REFER',
      estimatedLoanRange: { min: 15000, max: 35000 },
      readinessScore: 68,
      stats: DEMO_STATS,
      recommendations: DEMO_RECOMMENDATIONS,
      targets: DEMO_TARGETS,
      actionPlan: DEMO_ACTIONS,
      alerts: DEMO_ALERTS,
      financialSnapshot: DEMO_FINANCIAL_SNAPSHOT,
      progress: DEMO_PROGRESS,
      isLoading: false,
    };
  }
}

export async function savePlan(plan: ActionItem[]): Promise<boolean> {
  try {
    // Try to save to backend
    const response = await fetch(`${BASE_URL}/api/save-plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan }),
    });
    if (!response.ok) throw new Error('Failed to save');
    return true;
  } catch {
    // Fallback to localStorage
    localStorage.setItem('communityspark-plan', JSON.stringify(plan));
    return true;
  }
}

export function loadSavedPlan(): ActionItem[] | null {
  const saved = localStorage.getItem('communityspark-plan');
  return saved ? JSON.parse(saved) : null;
}
