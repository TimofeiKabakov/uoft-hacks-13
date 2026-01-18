/**
 * Community Spark - API Client
 * 
 * Centralized API client for all backend communication.
 * All API calls should go through this file.
 */

import { BASE_URL, ENDPOINTS } from '@/config';
import type {
  ApiResponse,
  ApiError,
  SandboxScenario,
  PortfolioAccount,
  EvaluationRequest,
  EvaluationResponse,
  FinalizeRequest,
  FinalizeResponse,
} from '@/types';

// ============ HTTP Client ============

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        if (!response.ok) {
          return {
            success: false,
            error: {
              code: 'NON_JSON_ERROR',
              message: `Server returned ${response.status}: ${response.statusText}`,
            },
          };
        }
        // For successful non-JSON responses (like health checks)
        return {
          success: true,
          data: { status: 'ok' } as T,
        };
      }

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: {
            code: data.code || 'API_ERROR',
            message: data.message || 'An error occurred',
            details: data.details,
          },
        };
      }

      return {
        success: true,
        data: data as T,
      };
    } catch (error) {
      // Network errors, CORS issues, etc.
      const isNetworkError = error instanceof TypeError && error.message.includes('fetch');
      
      return {
        success: false,
        error: {
          code: isNetworkError ? 'NETWORK_ERROR' : 'UNKNOWN_ERROR',
          message: isNetworkError 
            ? 'Unable to connect to the server. Please check if the backend is running.'
            : 'An unexpected error occurred',
          details: error instanceof Error ? error.message : String(error),
        },
      };
    }
  }

  private get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  private post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // ============ Public API Methods ============

  /**
   * Check if the backend is available
   */
  async checkHealth(): Promise<ApiResponse<{ status: string }>> {
    return this.get(ENDPOINTS.health);
  }

  /**
   * Fetch available sandbox scenarios
   */
  async getScenarios(): Promise<ApiResponse<SandboxScenario[]>> {
    return this.get<SandboxScenario[]>(ENDPOINTS.scenarios);
  }

  /**
   * Fetch linked portfolio accounts
   */
  async getAccounts(): Promise<ApiResponse<PortfolioAccount[]>> {
    return this.get<PortfolioAccount[]>(ENDPOINTS.accounts);
  }

  /**
   * Run multi-agent evaluation
   */
  async runEvaluation(request: EvaluationRequest): Promise<ApiResponse<EvaluationResponse>> {
    return this.post<EvaluationResponse>(ENDPOINTS.evaluate, request);
  }

  /**
   * Finalize evaluation with optional passkey signing
   */
  async finalizeEvaluation(request: FinalizeRequest): Promise<ApiResponse<FinalizeResponse>> {
    return this.post<FinalizeResponse>(ENDPOINTS.finalize, request);
  }

  /**
   * Get workflow diagram URL or data
   */
  async getWorkflowDiagram(): Promise<ApiResponse<{ url?: string; svg?: string }>> {
    return this.get(ENDPOINTS.workflowDiagram);
  }
}

// ============ Singleton Export ============

export const api = new ApiClient(BASE_URL);

// ============ Error Handling Utilities ============

export function isApiError(response: ApiResponse<unknown>): response is { success: false; error: ApiError } {
  return !response.success && !!response.error;
}

export function getErrorMessage(error: ApiError): string {
  switch (error.code) {
    case 'NETWORK_ERROR':
      return 'Unable to connect to the server. Please check your connection.';
    case 'NOT_FOUND':
      return 'The requested resource was not found.';
    case 'UNAUTHORIZED':
      return 'You are not authorized to perform this action.';
    case 'VALIDATION_ERROR':
      return error.message || 'Please check your input and try again.';
    default:
      return error.message || 'An unexpected error occurred.';
  }
}

// ============ Mock Data for Development ============

export const MOCK_SCENARIOS: SandboxScenario[] = [
  {
    id: 'healthy-restaurant',
    name: 'Healthy Restaurant Business',
    description: 'A well-established restaurant with strong cash flow and consistent revenue',
    category: 'Food & Beverage',
    previewData: {
      accountCount: 3,
      totalBalance: 45000,
      transactionCount: 1250,
    },
  },
  {
    id: 'struggling-retail',
    name: 'Struggling Retail Store',
    description: 'A retail business facing cash flow challenges with seasonal fluctuations',
    category: 'Retail',
    previewData: {
      accountCount: 2,
      totalBalance: 8500,
      transactionCount: 890,
    },
  },
  {
    id: 'growing-tech',
    name: 'Growing Tech Startup',
    description: 'A technology company with rapid growth but variable income patterns',
    category: 'Technology',
    previewData: {
      accountCount: 4,
      totalBalance: 125000,
      transactionCount: 2100,
    },
  },
  {
    id: 'community-nonprofit',
    name: 'Community Nonprofit',
    description: 'A nonprofit organization with grant-based funding and community impact',
    category: 'Nonprofit',
    previewData: {
      accountCount: 2,
      totalBalance: 32000,
      transactionCount: 450,
    },
  },
];

export const MOCK_EVALUATION_RESPONSE: EvaluationResponse = {
  id: 'eval-' + Date.now(),
  decision: 'APPROVE',
  fiscalHealthScore: 720,
  communityMultiplier: 1.35,
  finalScore: 972,
  loanTerms: {
    amount: 50000,
    apr: 8.5,
    termMonths: 36,
    monthlyPayment: 1578.45,
    totalInterest: 6824.20,
  },
  logs: [
    { agent: 'AUDITOR', message: 'Beginning forensic audit of financial data...', timestamp: new Date().toISOString(), severity: 'info' },
    { agent: 'AUDITOR', message: 'Analyzed 1,250 transactions across 3 accounts', timestamp: new Date().toISOString(), severity: 'info' },
    { agent: 'AUDITOR', message: 'Cash flow patterns indicate stable monthly revenue of $45,000', timestamp: new Date().toISOString(), severity: 'success' },
    { agent: 'AUDITOR', message: 'No significant red flags detected in transaction patterns', timestamp: new Date().toISOString(), severity: 'success' },
    { agent: 'IMPACT', message: 'Evaluating community impact metrics...', timestamp: new Date().toISOString(), severity: 'info' },
    { agent: 'IMPACT', message: 'Business located in designated opportunity zone', timestamp: new Date().toISOString(), severity: 'success' },
    { agent: 'IMPACT', message: 'Local employment contribution: 12 full-time positions', timestamp: new Date().toISOString(), severity: 'info' },
    { agent: 'IMPACT', message: 'Community multiplier calculated: 1.35x', timestamp: new Date().toISOString(), severity: 'success' },
    { agent: 'COMPLIANCE', message: 'Running compliance verification checks...', timestamp: new Date().toISOString(), severity: 'info' },
    { agent: 'COMPLIANCE', message: 'KYC/AML checks passed', timestamp: new Date().toISOString(), severity: 'success' },
    { agent: 'COMPLIANCE', message: 'Business registration verified with state records', timestamp: new Date().toISOString(), severity: 'success' },
    { agent: 'COACH', message: 'Generating recommendations for business improvement...', timestamp: new Date().toISOString(), severity: 'info' },
    { agent: 'COACH', message: 'Identified 3 priority actions to improve fiscal health', timestamp: new Date().toISOString(), severity: 'info' },
  ],
  accountSummaries: [
    { accountId: 'acc-1', name: 'Business Checking', subtype: 'checking', score: 85, flags: [] },
    { accountId: 'acc-2', name: 'Business Savings', subtype: 'savings', score: 92, flags: [] },
    { accountId: 'acc-3', name: 'Credit Line', subtype: 'credit', score: 78, flags: ['High utilization'] },
  ],
  riskFlags: [
    {
      id: 'rf-1',
      title: 'Seasonal Revenue Variation',
      description: 'Revenue shows 20% variation between peak and off-peak seasons',
      severity: 'low',
      category: 'Cash Flow',
      recommendation: 'Consider building a 3-month operating reserve',
    },
  ],
  improvementPlan: {
    priorityActions: [
      {
        id: 'action-1',
        title: 'Build Emergency Reserve',
        description: 'Establish a dedicated savings account with 3 months of operating expenses',
        priority: 'high',
        estimatedImpact: '+50 points to fiscal health score',
        timeframe: '6 months',
      },
      {
        id: 'action-2',
        title: 'Reduce Credit Line Usage',
        description: 'Pay down credit line to below 30% utilization',
        priority: 'medium',
        estimatedImpact: '+25 points to fiscal health score',
        timeframe: '3 months',
      },
    ],
    alerts: [],
    targets: [
      { metric: 'Operating Reserve', currentValue: 15000, targetValue: 45000, timeframe: '6 months' },
      { metric: 'Credit Utilization', currentValue: 65, targetValue: 30, timeframe: '3 months' },
    ],
  },
  evaluatedAt: new Date().toISOString(),
  processingTimeMs: 3450,
};
