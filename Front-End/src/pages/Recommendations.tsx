/**
 * Recommendations Page
 * Premium loan improvement recommendations dashboard.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { Header } from '@/components/layout/Header';
import { GradientOrbs } from '@/components/layout/GradientOrbs';
import { PageTransition } from '@/components/layout/PageTransition';
import { HeaderSummary } from '@/components/recommendations/HeaderSummary';
import { RecommendationCard } from '@/components/recommendations/RecommendationCard';
import { EvidenceDrawer } from '@/components/recommendations/EvidenceDrawer';
import { FinancialCharts } from '@/components/recommendations/FinancialCharts';
import { TargetsPanel } from '@/components/recommendations/TargetsPanel';
import { PlanTabs } from '@/components/recommendations/PlanTabs';
import { CoachPanel } from '@/components/recommendations/CoachPanel';
import { AlertsPanel, ProgressTracker } from '@/components/recommendations/AlertsProgress';
import { Skeleton } from '@/components/ui/skeleton';
import { staggerContainer, fadeInUp } from '@/lib/animations';
import { fetchRecommendations, fetchHeaderStats, fetchFinancialSnapshot, savePlan, loadSavedPlan } from '@/api/recommendations';
import type { Recommendation, ActionItem, ActionStatus, HeaderStats, FinancialSnapshot, Alert, ProgressData } from '@/types/recommendations';

const computeProgress = (actions: ActionItem[]): ProgressData => {
  const completed = actions.filter((a) => a.status === 'done').length;
  const total = actions.length;

  return {
    streakDays: completed,
    streakType: completed > 0 ? 'On track' : 'Getting started',
    completedActions: completed,
    totalActions: total,
    scoreTrend: completed > 0 ? 'up' : 'stable',
    approvalProgress: total ? Math.round((completed / total) * 100) : 0,
  };
};

export default function Recommendations() {
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [headerStats, setHeaderStats] = useState<HeaderStats | null>(null);
  const [financialSnapshot, setFinancialSnapshot] = useState<FinancialSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [actionPlan, setActionPlan] = useState<ActionItem[]>([]);
  const [alerts] = useState<Alert[]>([]);
  const [progress, setProgress] = useState<ProgressData>(computeProgress([]));

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);

      // Get applicationId from localStorage
      const storedApplicationId = localStorage.getItem('lastApplicationId');
      setApplicationId(storedApplicationId);

      if (!storedApplicationId) {
        console.warn('No application ID found');
        setIsLoading(false);
        return;
      }

      // Fetch all data in parallel
      const [recs, stats, snapshot, savedPlan] = await Promise.all([
        fetchRecommendations(storedApplicationId),
        fetchHeaderStats(storedApplicationId),
        fetchFinancialSnapshot(storedApplicationId),
        loadSavedPlan(),
      ]);

      setRecommendations(recs);
      setHeaderStats(stats);
      setFinancialSnapshot(snapshot);

      const planActions = savedPlan || [];
      setActionPlan(planActions);
      setProgress(computeProgress(planActions));
      setIsLoading(false);
    };
    loadData();
  }, []);

  const handleViewEvidence = (rec: Recommendation) => {
    setSelectedRecommendation(rec);
    setDrawerOpen(true);
  };

  const handleAddToPlan = (rec: Recommendation) => {
    const existingAction = actionPlan.find(a => a.linkedInsightId === rec.id);
    if (existingAction) {
      toast.info('Already in your plan');
      return;
    }
    const newAction: ActionItem = {
      id: `custom-${Date.now()}`,
      title: rec.title,
      step: rec.recommendedAction,
      difficulty: rec.priority === 'high' ? 'medium' : 'easy',
      impact: rec.priority,
      timeEstimate: '15 min',
      linkedInsightId: rec.id,
      status: 'pending',
      timeframe: 30,
    };
    setActionPlan(prev => {
      const next = [...prev, newAction];
      setProgress(computeProgress(next));
      return next;
    });
    toast.success('Added to your 30-day plan');
  };

  const handleStatusChange = (actionId: string, status: ActionStatus) => {
    setActionPlan(prev => {
      const next = prev.map(a => a.id === actionId ? { ...a, status } : a);
      setProgress(computeProgress(next));
      return next;
    });
  };

  const handleSave = async () => {
    if (!applicationId) {
      toast.error('Missing application ID. Please restart the flow.');
      return;
    }

    const success = await savePlan({
      applicationId,
      timeframe: '30',
      actionItems: actionPlan,
      targets: [],
    });

    if (success) {
      toast.success('Plan saved successfully');
    } else {
      toast.error('Unable to save plan right now');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <GradientOrbs />
        <main className="container mx-auto px-4 pt-24 pb-16">
          <div className="space-y-6">
            <Skeleton className="h-12 w-2/3" />
            <div className="grid grid-cols-4 gap-4">
              {[1,2,3,4].map(i => <Skeleton key={i} className="h-24" />)}
            </div>
            <Skeleton className="h-64" />
          </div>
        </main>
      </div>
    );
  }

  const planInsightIds = actionPlan.map(a => a.linkedInsightId);

  return (
    <PageTransition>
      <div className="min-h-screen bg-background">
        <Header />
        <GradientOrbs />

        <main className="container mx-auto px-4 pt-24 pb-16">
          <motion.div variants={staggerContainer} initial="hidden" animate="show" className="space-y-12">
            {/* Header */}
            {headerStats && (
              <HeaderSummary
                decision="PENDING"
                estimatedLoanRange={{ min: 0, max: 0 }}
                readinessScore={headerStats.fiscalHealthScore}
                stats={headerStats}
              />
            )}

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column - 2/3 */}
              <div className="lg:col-span-2 space-y-10">
                {/* Recommendations */}
                <motion.section variants={fadeInUp}>
                  <h2 className="text-xl font-bold text-foreground mb-4">Key Insights</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {recommendations.map((rec) => (
                      <RecommendationCard
                        key={rec.id}
                        recommendation={rec}
                        onViewEvidence={handleViewEvidence}
                        onAddToPlan={handleAddToPlan}
                        isInPlan={planInsightIds.includes(rec.id)}
                      />
                    ))}
                  </div>
                </motion.section>

                {/* Charts */}
                {financialSnapshot && (
                  <motion.section variants={fadeInUp}>
                    <h2 className="text-xl font-bold text-foreground mb-4">Financial Snapshot</h2>
                    <FinancialCharts snapshot={financialSnapshot} />
                  </motion.section>
                )}

                {/* Targets */}
                <motion.section variants={fadeInUp}>
                  <TargetsPanel targets={[]} currentScore={headerStats?.fiscalHealthScore || 0} />
                </motion.section>

                {/* Action Plan */}
                <motion.section variants={fadeInUp}>
                  <PlanTabs actions={actionPlan} onStatusChange={handleStatusChange} />
                </motion.section>
              </div>

              {/* Right Column - 1/3 */}
              <div className="space-y-6">
                <CoachPanel />
                <AlertsPanel alerts={alerts} />
                <ProgressTracker progress={progress} onSave={handleSave} />
              </div>
            </div>
          </motion.div>
        </main>

        <EvidenceDrawer
          recommendation={selectedRecommendation}
          isOpen={drawerOpen}
          onClose={() => setDrawerOpen(false)}
        />
      </div>
    </PageTransition>
  );
}
