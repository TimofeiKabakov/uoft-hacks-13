/**
 * Evaluation State Hook
 * 
 * Manages the evaluation wizard state.
 */

import { useState, useCallback } from 'react';
import type { 
  BusinessProfile, 
  BankDataMode, 
  SandboxScenario, 
  AgentLog, 
  EvaluationResponse 
} from '@/types';

export interface EvaluationState {
  step: number;
  businessProfile: Partial<BusinessProfile>;
  bankDataMode: BankDataMode;
  selectedScenario: SandboxScenario | null;
  selectedAccounts: string[];
  isEvaluating: boolean;
  evaluationProgress: number;
  activeAgent: AgentLog['agent'] | null;
  logs: AgentLog[];
  result: EvaluationResponse | null;
}

const initialState: EvaluationState = {
  step: 0,
  businessProfile: {},
  bankDataMode: 'sandbox',
  selectedScenario: null,
  selectedAccounts: [],
  isEvaluating: false,
  evaluationProgress: 0,
  activeAgent: null,
  logs: [],
  result: null,
};

export function useEvaluationState() {
  const [state, setState] = useState<EvaluationState>(initialState);

  const setStep = useCallback((step: number) => {
    setState(prev => ({ ...prev, step }));
  }, []);

  const nextStep = useCallback(() => {
    setState(prev => ({ ...prev, step: Math.min(prev.step + 1, 4) }));
  }, []);

  const prevStep = useCallback(() => {
    setState(prev => ({ ...prev, step: Math.max(prev.step - 1, 0) }));
  }, []);

  const setBusinessProfile = useCallback((profile: Partial<BusinessProfile>) => {
    setState(prev => ({ 
      ...prev, 
      businessProfile: { ...prev.businessProfile, ...profile } 
    }));
  }, []);

  const setBankDataMode = useCallback((mode: BankDataMode) => {
    setState(prev => ({ ...prev, bankDataMode: mode }));
  }, []);

  const setSelectedScenario = useCallback((scenario: SandboxScenario | null) => {
    setState(prev => ({ ...prev, selectedScenario: scenario }));
  }, []);

  const setSelectedAccounts = useCallback((accounts: string[]) => {
    setState(prev => ({ ...prev, selectedAccounts: accounts }));
  }, []);

  const startEvaluation = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      isEvaluating: true, 
      evaluationProgress: 0,
      logs: [],
      result: null,
    }));
  }, []);

  const setEvaluationProgress = useCallback((progress: number, activeAgent?: AgentLog['agent']) => {
    setState(prev => ({ 
      ...prev, 
      evaluationProgress: progress,
      activeAgent: activeAgent || prev.activeAgent,
    }));
  }, []);

  const addLog = useCallback((log: AgentLog) => {
    setState(prev => ({ ...prev, logs: [...prev.logs, log] }));
  }, []);

  const setResult = useCallback((result: EvaluationResponse) => {
    setState(prev => ({ 
      ...prev, 
      result, 
      isEvaluating: false,
      evaluationProgress: 100,
    }));
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return {
    state,
    setStep,
    nextStep,
    prevStep,
    setBusinessProfile,
    setBankDataMode,
    setSelectedScenario,
    setSelectedAccounts,
    startEvaluation,
    setEvaluationProgress,
    addLog,
    setResult,
    reset,
  };
}
