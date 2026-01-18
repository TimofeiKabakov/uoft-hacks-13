/**
 * Run Evaluation Step
 * 
 * Step 3: Execute the multi-agent evaluation with animated progress.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Search, Heart, Shield, GraduationCap, Loader2, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { staggerContainer, fadeInUp, buttonHover, scaleInBounce } from '@/lib/animations';
import { FEATURE_FLAGS, UI_CONFIG } from '@/config';
import type { AgentLog, EvaluationResponse, BusinessProfile, SandboxScenario } from '@/types';
import { api } from '@/api/client';

interface RunEvaluationStepProps {
  applicationId: string | null;
  businessProfile: Partial<BusinessProfile>;
  scenario: SandboxScenario | null;
  isEvaluating: boolean;
  progress: number;
  activeAgent: AgentLog['agent'] | null;
  logs: AgentLog[];
  onStart: () => void;
  onProgress: (progress: number, agent?: AgentLog['agent']) => void;
  onAddLog: (log: AgentLog) => void;
  onComplete: (result: EvaluationResponse) => void;
  onBack: () => void;
}

const agents = [
  { id: 'AUDITOR', name: 'Forensic Auditor', icon: Search, color: 'text-primary' },
  { id: 'IMPACT', name: 'Impact Analyst', icon: Heart, color: 'text-success' },
  { id: 'COMPLIANCE', name: 'Compliance Sentry', icon: Shield, color: 'text-warning' },
  { id: 'COACH', name: 'Business Coach', icon: GraduationCap, color: 'text-accent' },
] as const;

export function RunEvaluationStep({
  applicationId,
  businessProfile,
  scenario,
  isEvaluating,
  progress,
  activeAgent,
  logs,
  onStart,
  onProgress,
  onAddLog,
  onComplete,
  onBack,
}: RunEvaluationStepProps) {
  const [currentAgentIndex, setCurrentAgentIndex] = useState(-1);
  const [error, setError] = useState<string | null>(null);

  // Run real backend evaluation
  const runRealEvaluation = useCallback(async () => {
    if (!applicationId) {
      setError('No application ID found');
      return;
    }

    setError(null);

    try {
      // Simulate agent progression with status polling
      for (let i = 0; i < agents.length; i++) {
        setCurrentAgentIndex(i);
        const agent = agents[i];
        onProgress((i / agents.length) * 100, agent.id);

        // Add simulated log for agent start
        onAddLog({
          agent: agent.id,
          message: `${agent.name} analyzing...`,
          timestamp: new Date().toISOString(),
          severity: 'info',
        });

        // Simulate agent working
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Poll for assessment results
      onProgress(90);
      onAddLog({
        agent: 'COACH',
        message: 'Waiting for assessment to complete...',
        timestamp: new Date().toISOString(),
        severity: 'info',
      });

      // Poll the backend for status
      let attempts = 0;
      const maxAttempts = 30;
      let assessmentComplete = false;

      while (attempts < maxAttempts && !assessmentComplete) {
        await new Promise(resolve => setTimeout(resolve, 2000));

        const statusResponse = await api.getApplicationStatus(applicationId);
        if (statusResponse.success && statusResponse.data.has_results) {
          assessmentComplete = true;
        }

        attempts++;
      }

      if (!assessmentComplete) {
        throw new Error('Assessment timeout - results not ready');
      }

      // Fetch the assessment results
      const assessmentResponse = await api.getAssessmentResults(applicationId);
      if (!assessmentResponse.success || !assessmentResponse.data) {
        throw new Error('Failed to fetch assessment results');
      }

      // Fetch recommendations
      const recsResponse = await api.getRecommendationsList(applicationId);
      const recommendations = recsResponse.success ? recsResponse.data : [];

      // Map backend response to frontend EvaluationResponse format
      const result: EvaluationResponse = {
        id: applicationId,
        decision: 'APPROVE', // TODO: Get from assessment
        fiscalHealthScore: Math.round((assessmentResponse.data.financial_metrics?.income_stability_score || 0) * 100),
        communityMultiplier: 1.0, // TODO: Get from assessment
        finalScore: Math.round((assessmentResponse.data.financial_metrics?.income_stability_score || 0) * 100),
        loanTerms: {
          amount: 0, // TODO: Get from assessment
          apr: 0,
          termMonths: 0,
          monthlyPayment: 0,
          totalInterest: 0,
        },
        logs: logs,
        accountSummaries: [],
        riskFlags: [],
        improvementPlan: {
          priorityActions: recommendations.slice(0, 3).map(rec => ({
            id: rec.id,
            title: rec.title,
            description: rec.recommended_action,
            priority: rec.priority,
            estimatedImpact: rec.expected_impact,
            timeframe: '3-6 months',
          })),
          alerts: [],
          targets: [],
        },
        evaluatedAt: new Date().toISOString(),
        processingTimeMs: 0,
      };

      onProgress(100);
      onComplete(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      console.error('Error running evaluation:', err);
    }
  }, [applicationId, onProgress, onAddLog, onComplete, logs]);

  useEffect(() => {
    if (isEvaluating && currentAgentIndex === -1) {
      runRealEvaluation();
    }
  }, [isEvaluating, currentAgentIndex, runRealEvaluation]);

  const handleStart = () => {
    setCurrentAgentIndex(-1);
    setError(null);
    onStart();
  };

  return (
    <div className="flex gap-6 h-full">
      {/* Main Panel */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="flex-1 max-w-2xl"
      >
        <motion.div variants={fadeInUp} className="text-center mb-8">
          <h2 className="text-2xl font-bold mb-2">Run Evaluation</h2>
          <p className="text-muted-foreground">
            Our AI agents will analyze the business data
          </p>
        </motion.div>

        {/* Summary Card */}
        <GlassCard hover="none" className="p-6 mb-6">
          <h3 className="font-semibold mb-4">Evaluation Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Business:</span>
              <p className="font-medium">{businessProfile.businessName || 'N/A'}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Type:</span>
              <p className="font-medium capitalize">{businessProfile.businessType || 'N/A'}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Location:</span>
              <p className="font-medium">{businessProfile.location?.zipCode || 'N/A'}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Scenario:</span>
              <p className="font-medium">{scenario?.name || 'N/A'}</p>
            </div>
          </div>
        </GlassCard>

        {/* Agent Progress */}
        <GlassCard hover="none" className="p-6 mb-6">
          <h3 className="font-semibold mb-6">Agent Pipeline</h3>
          <div className="space-y-4">
            {agents.map((agent, index) => {
              const Icon = agent.icon;
              const isActive = currentAgentIndex === index;
              const isComplete = currentAgentIndex > index;
              const isPending = currentAgentIndex < index;

              return (
                <motion.div
                  key={agent.id}
                  className={`flex items-center gap-4 p-4 rounded-xl transition-all ${
                    isActive ? 'bg-primary/10 ring-1 ring-primary' : 
                    isComplete ? 'bg-success/5' : 'bg-muted/30'
                  }`}
                  animate={isActive ? {
                    boxShadow: [
                      '0 0 0 0 rgba(62, 190, 201, 0)',
                      '0 0 20px 0 rgba(62, 190, 201, 0.2)',
                      '0 0 0 0 rgba(62, 190, 201, 0)',
                    ],
                  } : {}}
                  transition={{ duration: 1.5, repeat: isActive ? Infinity : 0 }}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    isComplete ? 'bg-success text-success-foreground' :
                    isActive ? 'bg-primary text-primary-foreground' :
                    'bg-muted'
                  }`}>
                    {isActive ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : isComplete ? (
                      <motion.svg
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-6 h-6"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </motion.svg>
                    ) : (
                      <Icon className="w-6 h-6" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <p className={`font-medium ${isPending ? 'text-muted-foreground' : ''}`}>
                      {agent.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {isActive ? 'Analyzing...' : isComplete ? 'Complete' : 'Pending'}
                    </p>
                  </div>

                  {isComplete && (
                    <motion.span
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="text-xs px-2 py-1 rounded-full bg-success/10 text-success"
                    >
                      ✓ Done
                    </motion.span>
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Progress Bar */}
          {isEvaluating && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6"
            >
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-muted-foreground">Overall Progress</span>
                <span className="font-medium">{Math.round(progress)}%</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </motion.div>
          )}
        </GlassCard>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <GlassCard hover="none" className="p-4 bg-destructive/10 border-destructive/20">
              <p className="text-sm text-destructive font-medium">Error: {error}</p>
            </GlassCard>
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div variants={fadeInUp} className="flex items-center justify-between">
          <motion.div variants={buttonHover} initial="rest" whileHover="hover" whileTap="tap">
            <Button
              variant="outline"
              onClick={onBack}
              className="rounded-xl"
              disabled={isEvaluating}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </motion.div>

          {!isEvaluating && currentAgentIndex === -1 && (
            <motion.div
              variants={scaleInBounce}
              initial="hidden"
              animate="show"
            >
              <motion.div variants={buttonHover} initial="rest" whileHover="hover" whileTap="tap">
                <Button
                  onClick={handleStart}
                  disabled={!applicationId}
                  className="rounded-xl px-8 py-6 text-lg font-semibold"
                  size="lg"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Run Multi-Agent Evaluation
                </Button>
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      </motion.div>

      {/* Agent Log Panel */}
      <AgentLogPanel logs={logs} activeAgent={activeAgent} />
    </div>
  );
}

// Agent Log Panel Component
interface AgentLogPanelProps {
  logs: AgentLog[];
  activeAgent: AgentLog['agent'] | null;
}

function AgentLogPanel({ logs, activeAgent }: AgentLogPanelProps) {
  const [filter, setFilter] = useState<'all' | AgentLog['agent']>('all');

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.agent === filter);

  const filterOptions = [
    { id: 'all', label: 'All', color: 'bg-muted' },
    { id: 'AUDITOR', label: 'Auditor', color: 'bg-primary/20 text-primary' },
    { id: 'IMPACT', label: 'Impact', color: 'bg-success/20 text-success' },
    { id: 'COMPLIANCE', label: 'Compliance', color: 'bg-warning/20 text-warning' },
    { id: 'COACH', label: 'Coach', color: 'bg-accent/20 text-accent' },
  ] as const;

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
      className="w-96 flex-shrink-0"
    >
      <GlassCard hover="none" className="h-full flex flex-col">
        <div className="p-4 border-b border-border">
          <h3 className="font-semibold mb-3">Agent Reasoning Log</h3>
          
          {/* Filter Chips */}
          <div className="flex flex-wrap gap-2">
            {filterOptions.map((option) => (
              <motion.button
                key={option.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilter(option.id as typeof filter)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                  filter === option.id 
                    ? option.color + ' ring-1 ring-current' 
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                {option.label}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Log Entries */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
          <AnimatePresence mode="popLayout">
            {filteredLogs.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-muted-foreground py-12"
              >
                <p>No logs yet</p>
                <p className="text-sm">Start the evaluation to see agent reasoning</p>
              </motion.div>
            ) : (
              filteredLogs.map((log, index) => (
                <LogEntry key={`${log.agent}-${index}`} log={log} index={index} />
              ))
            )}
          </AnimatePresence>
        </div>
      </GlassCard>
    </motion.div>
  );
}

// Log Entry Component
interface LogEntryProps {
  log: AgentLog;
  index: number;
}

function LogEntry({ log, index }: LogEntryProps) {
  const getAgentConfig = (agent: AgentLog['agent']) => {
    switch (agent) {
      case 'AUDITOR': return { icon: Search, color: 'bg-primary/10 text-primary border-primary/20' };
      case 'IMPACT': return { icon: Heart, color: 'bg-success/10 text-success border-success/20' };
      case 'COMPLIANCE': return { icon: Shield, color: 'bg-warning/10 text-warning border-warning/20' };
      case 'COACH': return { icon: GraduationCap, color: 'bg-accent/10 text-accent border-accent/20' };
    }
  };

  const config = getAgentConfig(log.agent);
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20, height: 0 }}
      animate={{ opacity: 1, x: 0, height: 'auto' }}
      exit={{ opacity: 0, x: -20, height: 0 }}
      transition={{ 
        type: 'spring', 
        stiffness: 300, 
        damping: 30,
        delay: FEATURE_FLAGS.enableLogStreaming ? index * 0.05 : 0,
      }}
      className={`p-3 rounded-xl border ${config.color}`}
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-current/10 flex items-center justify-center flex-shrink-0">
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium">{log.agent}</span>
            {log.severity && log.severity !== 'info' && (
              <span className={`text-xs px-1.5 py-0.5 rounded ${
                log.severity === 'success' ? 'bg-success/20 text-success' :
                log.severity === 'warning' ? 'bg-warning/20 text-warning' :
                'bg-destructive/20 text-destructive'
              }`}>
                {log.severity}
              </span>
            )}
          </div>
          <p className="text-sm leading-relaxed">{log.message}</p>
          {log.timestamp && (
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(log.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
