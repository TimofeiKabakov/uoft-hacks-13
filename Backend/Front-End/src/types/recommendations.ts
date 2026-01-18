/**
 * Community Spark - Recommendations Page Types
 * 
 * All TypeScript interfaces for the Recommendations feature.
 */

// Priority levels for recommendations
export type Priority = 'low' | 'medium' | 'high';

// Difficulty levels for actions
export type Difficulty = 'easy' | 'medium' | 'hard';

// Impact levels
export type Impact = 'low' | 'medium' | 'high';

// Decision types
export type DecisionType = 'APPROVE' | 'REFER' | 'DENY';

// Action status
export type ActionStatus = 'pending' | 'in_progress' | 'done';

// Time range for charts
export type TimeRange = 30 | 60 | 90;

// Account scope
export type AccountScope = 'single' | 'portfolio';

// Evidence item (transaction or pattern)
export interface EvidenceItem {
  id: string;
  type: 'transaction' | 'pattern' | 'stat';
  merchant?: string;
  date?: string;
  amount?: number;
  description: string;
  category?: string;
}

// Recommendation card data
export interface Recommendation {
  id: string;
  title: string;
  whatWeSaw: string;
  whyItMatters: string;
  recommendedAction: string;
  expectedImpact: string;
  priority: Priority;
  category: string;
  evidence: EvidenceItem[];
}

// Action item for the plan
export interface ActionItem {
  id: string;
  title: string;
  step: string;
  difficulty: Difficulty;
  impact: Impact;
  timeEstimate: string;
  linkedInsightId: string;
  status: ActionStatus;
  timeframe: 30 | 60 | 90;
}

// Target/Guardrail
export interface Target {
  id: string;
  name: string;
  currentValue: number;
  recommendedValue: number;
  unit: string;
  whyItMatters: string;
  icon: string;
}

// Coach question and response
export interface CoachQuestion {
  id: string;
  question: string;
}

export interface CoachResponse {
  summary: string;
  steps: string[];
  expectedImpact: string;
  cautions?: string;
}

// Alert item
export interface Alert {
  id: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  suggestedAction: string;
  timestamp?: string;
}

// Financial snapshot data point
export interface FinancialDataPoint {
  date: string;
  inflow: number;
  outflow: number;
  balance?: number;
}

// Spending category
export interface SpendingCategory {
  name: string;
  value: number;
  color: string;
}

// Financial snapshot (for charts)
export interface FinancialSnapshot {
  cashFlow: FinancialDataPoint[];
  spendingByCategory: SpendingCategory[];
  stabilityTrend: { date: string; score: number }[];
}

// Header stats
export interface HeaderStats {
  fiscalHealthScore: number;
  communityImpactMultiplier: number;
  cashFlowStability: number;
  riskFlagsCount: number;
}

// Progress/momentum data
export interface ProgressData {
  streakDays: number;
  streakType: string;
  completedActions: number;
  totalActions: number;
  scoreTrend: 'up' | 'down' | 'stable';
  approvalProgress: number;
}

// Full recommendations state
export interface RecommendationsState {
  decision: DecisionType;
  estimatedLoanRange?: { min: number; max: number };
  readinessScore: number;
  stats: HeaderStats;
  recommendations: Recommendation[];
  targets: Target[];
  actionPlan: ActionItem[];
  alerts: Alert[];
  financialSnapshot: FinancialSnapshot;
  progress: ProgressData;
  isLoading: boolean;
  error?: string;
}
