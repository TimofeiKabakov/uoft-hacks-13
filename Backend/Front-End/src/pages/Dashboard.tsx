/**
 * Dashboard Page
 * 
 * Home for signed-in users - displays their financial snapshot directly.
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  TrendingUp, 
  TrendingDown,
  Heart,
  Droplets,
  AlertTriangle,
  Sparkles,
  ChevronRight
} from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { GradientOrbs } from '@/components/layout/GradientOrbs';
import { PageTransition } from '@/components/layout/PageTransition';
import { GlassCard } from '@/components/ui/GlassCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { FinancialCharts } from '@/components/recommendations/FinancialCharts';
import { staggerContainer, fadeInUp, scaleIn } from '@/lib/animations';
import { DEMO_FINANCIAL_SNAPSHOT, DEMO_STATS, DEMO_PROGRESS, DEMO_ALERTS } from '@/api/recommendations';

// Mock user for demo
const DEMO_USER = {
  name: 'Sarah',
  businessName: 'Bright Ideas Consulting',
  lastEvaluation: '2 days ago',
  nextMilestone: 'Zero overdrafts for 30 days',
  daysToMilestone: 16,
};

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate data fetch
    const timer = setTimeout(() => setIsLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <GradientOrbs />
        <main className="container mx-auto px-4 pt-24 pb-16">
          <div className="space-y-6">
            <Skeleton className="h-16 w-1/2" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[1,2,3,4].map(i => <Skeleton key={i} className="h-28" />)}
            </div>
            <Skeleton className="h-80" />
          </div>
        </main>
      </div>
    );
  }

  const scoreTrend = DEMO_PROGRESS.scoreTrend;
  const TrendIcon = scoreTrend === 'up' ? TrendingUp : scoreTrend === 'down' ? TrendingDown : Sparkles;
  const trendColor = scoreTrend === 'up' ? 'text-success' : scoreTrend === 'down' ? 'text-destructive' : 'text-muted-foreground';

  return (
    <PageTransition>
      <div className="min-h-screen bg-background">
        <Header />
        <GradientOrbs />
        
        <main className="container mx-auto px-4 pt-24 pb-16">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="show"
            className="space-y-8"
          >
            {/* Welcome Header */}
            <motion.div variants={fadeInUp} className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
              <div>
                <p className="text-muted-foreground">Welcome back,</p>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground">
                  {DEMO_USER.name} 👋
                </h1>
                <p className="text-muted-foreground mt-1">
                  {DEMO_USER.businessName} • Last evaluated {DEMO_USER.lastEvaluation}
                </p>
              </div>
              
              <Link to="/recommendations">
                <Button size="lg" className="rounded-xl">
                  View Full Recommendations
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </motion.div>

            {/* Quick Stats */}
            <motion.div 
              variants={staggerContainer}
              className="grid grid-cols-2 md:grid-cols-4 gap-4"
            >
              {/* Fiscal Health Score */}
              <motion.div variants={scaleIn}>
                <GlassCard className="p-5 h-full">
                  <div className="flex items-start justify-between">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Heart className="w-5 h-5 text-primary" />
                    </div>
                    <div className={`flex items-center gap-1 ${trendColor}`}>
                      <TrendIcon className="w-4 h-4" />
                      <span className="text-xs font-medium">+12</span>
                    </div>
                  </div>
                  <p className="text-3xl font-bold text-foreground mt-3">
                    {DEMO_STATS.fiscalHealthScore}
                  </p>
                  <p className="text-sm text-muted-foreground">Fiscal Health Score</p>
                </GlassCard>
              </motion.div>

              {/* Cash Flow Stability */}
              <motion.div variants={scaleIn}>
                <GlassCard className="p-5 h-full">
                  <div className="p-2 rounded-lg bg-primary/10 w-fit">
                    <Droplets className="w-5 h-5 text-primary" />
                  </div>
                  <p className="text-3xl font-bold text-foreground mt-3">
                    {DEMO_STATS.cashFlowStability}%
                  </p>
                  <p className="text-sm text-muted-foreground">Cash Flow Stability</p>
                </GlassCard>
              </motion.div>

              {/* Community Impact */}
              <motion.div variants={scaleIn}>
                <GlassCard className="p-5 h-full">
                  <div className="p-2 rounded-lg bg-accent/10 w-fit">
                    <Sparkles className="w-5 h-5 text-accent" />
                  </div>
                  <p className="text-3xl font-bold text-foreground mt-3">
                    {DEMO_STATS.communityImpactMultiplier}x
                  </p>
                  <p className="text-sm text-muted-foreground">Community Impact</p>
                </GlassCard>
              </motion.div>

              {/* Risk Flags */}
              <motion.div variants={scaleIn}>
                <GlassCard className={`p-5 h-full ${DEMO_STATS.riskFlagsCount > 0 ? 'border-warning/30' : ''}`}>
                  <div className={`p-2 rounded-lg w-fit ${DEMO_STATS.riskFlagsCount > 0 ? 'bg-warning/10' : 'bg-success/10'}`}>
                    <AlertTriangle className={`w-5 h-5 ${DEMO_STATS.riskFlagsCount > 0 ? 'text-warning' : 'text-success'}`} />
                  </div>
                  <p className="text-3xl font-bold text-foreground mt-3">
                    {DEMO_STATS.riskFlagsCount}
                  </p>
                  <p className="text-sm text-muted-foreground">Risk Flags</p>
                </GlassCard>
              </motion.div>
            </motion.div>

            {/* Next Milestone */}
            <motion.div variants={fadeInUp}>
              <GlassCard className="p-5 bg-gradient-to-r from-primary/5 to-accent/5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="relative w-14 h-14">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="28" cy="28" r="24" fill="none" stroke="hsl(var(--muted))" strokeWidth="4" />
                        <motion.circle
                          cx="28" cy="28" r="24" fill="none"
                          stroke="hsl(var(--primary))" strokeWidth="4" strokeLinecap="round"
                          strokeDasharray={`${2 * Math.PI * 24}`}
                          initial={{ strokeDashoffset: 2 * Math.PI * 24 }}
                          animate={{ strokeDashoffset: 2 * Math.PI * 24 * (1 - (30 - DEMO_USER.daysToMilestone) / 30) }}
                          transition={{ duration: 1, ease: 'easeOut' }}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-xs font-bold text-foreground">{DEMO_USER.daysToMilestone}d</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Next Milestone</p>
                      <p className="font-semibold text-foreground">{DEMO_USER.nextMilestone}</p>
                      <p className="text-xs text-muted-foreground">{DEMO_USER.daysToMilestone} days remaining</p>
                    </div>
                  </div>
                  <Link to="/recommendations">
                    <Button variant="outline" className="rounded-xl">
                      See Action Plan
                      <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </Link>
                </div>
              </GlassCard>
            </motion.div>

            {/* Financial Snapshot */}
            <motion.section variants={fadeInUp}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-foreground">Your Financial Snapshot</h2>
                <Badge variant="secondary">Last 30 days</Badge>
              </div>
              <FinancialCharts snapshot={DEMO_FINANCIAL_SNAPSHOT} />
            </motion.section>

            {/* Recent Alerts */}
            {DEMO_ALERTS.length > 0 && (
              <motion.section variants={fadeInUp}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-foreground">Recent Alerts</h2>
                  <Link to="/recommendations" className="text-sm text-primary hover:underline">
                    View all
                  </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {DEMO_ALERTS.slice(0, 3).map((alert) => (
                    <GlassCard 
                      key={alert.id} 
                      className={`p-4 ${
                        alert.severity === 'critical' ? 'border-destructive/30' :
                        alert.severity === 'warning' ? 'border-warning/30' : ''
                      }`}
                    >
                      <p className="font-medium text-foreground text-sm">{alert.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{alert.message}</p>
                    </GlassCard>
                  ))}
                </div>
              </motion.section>
            )}
          </motion.div>
        </main>
      </div>
    </PageTransition>
  );
}
