/**
 * Community Spark - TypeScript Type Definitions
 * 
 * These types define the data structures used throughout the frontend.
 * They should match the expected API response shapes from the backend.
 */

// ============ Business Profile ============

export interface EmploymentDetails {
  employmentStatus: 'employed' | 'self-employed' | 'business-owner' | 'unemployed' | 'retired';
  employer?: string;
  jobTitle?: string;
  monthlyIncome?: number;
  yearsAtCurrentJob?: number;
}

export interface LocationDetails {
  formattedAddress: string;
  placeId?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
}

export interface BusinessProfile {
  businessName: string;
  businessType: string;
  location: {
    zipCode: string;
    address?: string;
    city?: string;
    state?: string;
  };
  communityTags?: string[];
  yearsInOperation?: number;
  employeeCount?: number;
  annualRevenue?: number;
  employmentDetails?: EmploymentDetails;
  selectedLocation?: LocationDetails;
}

// ============ Bank Data / Scenarios ============

export interface SandboxScenario {
  id: string;
  name: string;
  description: string;
  category?: string;
  previewData?: {
    accountCount: number;
    totalBalance: number;
    transactionCount: number;
  };
}

export interface PortfolioAccount {
  id: string;
  name: string;
  type: 'checking' | 'savings' | 'credit' | 'investment' | 'loan';
  subtype?: string;
  institution?: string;
  mask?: string; // Last 4 digits
  balance?: number;
}

export type BankDataMode = 'sandbox' | 'portfolio';

// ============ Evaluation Request/Response ============

export interface EvaluationRequest {
  businessProfile: BusinessProfile;
  bankDataMode: BankDataMode;
  scenarioId?: string; // For sandbox mode
  accountIds?: string[]; // For portfolio mode
}

export interface AgentLog {
  agent: 'AUDITOR' | 'IMPACT' | 'COMPLIANCE' | 'COACH';
  message: string;
  timestamp?: string;
  severity?: 'info' | 'warning' | 'error' | 'success';
  details?: string;
  metrics?: Record<string, number | string>;
}

export interface LoanTerms {
  amount: number;
  apr: number;
  termMonths: number;
  monthlyPayment?: number;
  totalInterest?: number;
}

export interface AccountSummary {
  accountId: string;
  name: string;
  subtype: string;
  score: number;
  flags: string[];
  metrics?: {
    avgBalance: number;
    volatility: number;
    overdraftCount: number;
  };
}

export interface RiskFlag {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  recommendation?: string;
}

export interface ImprovementAction {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  estimatedImpact: string;
  timeframe?: string;
}

export interface ImprovementPlan {
  priorityActions: ImprovementAction[];
  alerts: string[];
  targets: {
    metric: string;
    currentValue: number;
    targetValue: number;
    timeframe: string;
  }[];
}

export interface EvaluationResponse {
  id: string;
  decision: 'APPROVE' | 'DENY' | 'REFER' | 'REVIEW';
  
  // Scores (can be 0-100 or 0-1000 scale)
  fiscalHealthScore: number;
  communityMultiplier: number;
  finalScore: number;
  
  // Optional detailed data
  loanTerms?: LoanTerms;
  logs: AgentLog[];
  accountSummaries?: AccountSummary[];
  riskFlags?: RiskFlag[];
  improvementPlan?: ImprovementPlan;
  
  // Metadata
  evaluatedAt: string;
  processingTimeMs?: number;
}

// ============ Finalization ============

export interface FinalizeRequest {
  evaluationId: string;
  passkeySigned?: boolean;
  signature?: string;
}

export interface FinalizeResponse {
  success: boolean;
  message: string;
  finalizedAt?: string;
  documentUrl?: string;
}

// ============ Workflow/Graph ============

export interface WorkflowNode {
  id: string;
  type: 'start' | 'agent' | 'decision' | 'end';
  label: string;
  description?: string;
  agent?: 'AUDITOR' | 'IMPACT' | 'COMPLIANCE' | 'COACH';
  status?: 'pending' | 'active' | 'complete' | 'error';
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated?: boolean;
}

// ============ API Response Wrappers ============

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

// ============ UI State Types ============

export interface WizardStep {
  id: string;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

export type LogFilter = 'all' | 'AUDITOR' | 'IMPACT' | 'COMPLIANCE' | 'COACH';

export interface EvaluationState {
  step: number;
  businessProfile: Partial<BusinessProfile>;
  bankDataMode: BankDataMode;
  selectedScenario?: SandboxScenario;
  selectedAccounts: string[];
  isEvaluating: boolean;
  evaluationProgress: number;
  activeAgent?: AgentLog['agent'];
  logs: AgentLog[];
  result?: EvaluationResponse;
}
