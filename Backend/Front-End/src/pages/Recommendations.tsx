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
import { fetchRecommendations, savePlan, loadSavedPlan, DEMO_ACTIONS } from '@/api/recommendations';
import type { RecommendationsState, Recommendation, ActionItem, ActionStatus } from '@/types/recommendations';

export default function Recommendations() {
  const [state, setState] = useState<RecommendationsState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [actionPlan, setActionPlan] = useState<ActionItem[]>([]);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      const data = await fetchRecommendations();
      setState(data);
      const saved = loadSavedPlan();
      setActionPlan(saved || data.actionPlan);
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
    setActionPlan(prev => [...prev, newAction]);
    toast.success('Added to your 30-day plan');
  };

  const handleStatusChange = (actionId: string, status: ActionStatus) => {
    setActionPlan(prev => prev.map(a => a.id === actionId ? { ...a, status } : a));
  };

  const handleSave = async () => {
    await savePlan(actionPlan);
    toast.success('Plan saved successfully');
  };

  if (isLoading || !state) {
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
            <HeaderSummary
              decision={state.decision}
              estimatedLoanRange={state.estimatedLoanRange}
              readinessScore={state.readinessScore}
              stats={state.stats}
            />

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column - 2/3 */}
              <div className="lg:col-span-2 space-y-10">
                {/* Recommendations */}
                <motion.section variants={fadeInUp}>
                  <h2 className="text-xl font-bold text-foreground mb-4">Key Insights</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {state.recommendations.map((rec) => (
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
                <motion.section variants={fadeInUp}>
                  <h2 className="text-xl font-bold text-foreground mb-4">Financial Snapshot</h2>
                  <FinancialCharts snapshot={state.financialSnapshot} />
                </motion.section>

                {/* Targets */}
                <motion.section variants={fadeInUp}>
                  <TargetsPanel targets={state.targets} currentScore={state.stats.fiscalHealthScore} />
                </motion.section>

                {/* Action Plan */}
                <motion.section variants={fadeInUp}>
                  <PlanTabs actions={actionPlan} onStatusChange={handleStatusChange} />
                </motion.section>
              </div>

              {/* Right Column - 1/3 */}
              <div className="space-y-6">
                <CoachPanel />
                <AlertsPanel alerts={state.alerts} />
                <ProgressTracker progress={state.progress} onSave={handleSave} />
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
