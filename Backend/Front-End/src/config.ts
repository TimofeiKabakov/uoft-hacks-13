/**
 * Community Spark Frontend Configuration
 * 
 * This file contains all configurable settings for the frontend application.
 * Backend endpoint URLs should be configured here.
 */

// Base URL for all API calls - configure this to point to your backend
export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API Endpoints - configure these based on your backend routes
export const ENDPOINTS = {
  // Health check endpoint
  health: '/health',
  
  // Get available sandbox scenarios
  scenarios: '/api/scenarios',
  
  // Get linked portfolio accounts (Plaid-connected)
  accounts: '/api/accounts',
  
  // Run multi-agent evaluation
  evaluate: '/api/evaluate',
  
  // Finalize evaluation with optional passkey signing
  finalize: '/api/finalize',
  
  // Get workflow diagram (if backend provides SVG/image)
  workflowDiagram: '/api/workflow-diagram',
} as const;

// Feature flags - toggle features on/off
export const FEATURE_FLAGS = {
  // Enable passkey (WebAuthn) signing for finalization
  enablePasskeys: true,
  
  // Enable the sandbox scenario dropdown selector
  enablePlaidScenarioDropdown: true,
  
  // Enable portfolio accounts mode (requires Plaid integration)
  enablePortfolioAccounts: true,
  
  // Enable agent reasoning log streaming animation
  enableLogStreaming: true,
  
  // Enable celebration animations (confetti on approval)
  enableCelebrations: true,
  
  // Enable workflow graph animations
  enableGraphAnimations: true,
} as const;

// UI Configuration
export const UI_CONFIG = {
  // Animation durations (in seconds)
  animations: {
    pageTransition: 0.5,
    cardHover: 0.2,
    gaugeAnimation: 1.5,
    logStreamDelay: 0.1, // Delay between streaming log entries
    stepTransition: 0.4,
  },
  
  // Score thresholds for visual treatment
  scores: {
    excellent: 800,
    good: 650,
    fair: 500,
    poor: 350,
  },
  
  // Agent colors for the reasoning log
  agentColors: {
    AUDITOR: 'primary',
    IMPACT: 'success',
    COMPLIANCE: 'warning',
    COACH: 'accent',
  } as const,
  
  // Decision colors
  decisionColors: {
    APPROVE: 'success',
    DENY: 'destructive',
    REFER: 'warning',
  } as const,
} as const;

// Export types for TypeScript
export type AgentType = keyof typeof UI_CONFIG.agentColors;
export type DecisionType = keyof typeof UI_CONFIG.decisionColors;
