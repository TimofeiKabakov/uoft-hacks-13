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
import { fetchFinancialSnapshot, fetchHeaderStats } from '@/api/recommendations';
import { api } from '@/api/client';
import type { FinancialSnapshot, HeaderStats } from '@/types/recommendations';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<HeaderStats | null>(null);
  const [snapshot, setSnapshot] = useState<FinancialSnapshot | null>(null);
  const [userData, setUserData] = useState<{ name: string; email: string } | null>(null);
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      setIsLoading(true);
      setError(null);

      try {
        // Login with dummy auth to get sandbox user
        const loginResponse = await api.login('sandbox@demo.com', 'password');
        if (loginResponse.success && loginResponse.data) {
          setUserData({
            name: loginResponse.data.user.name,
            email: loginResponse.data.user.email,
          });
        }

        // Fetch latest application for this user
        // For now, we'll use a placeholder applicationId if available
        const testApplicationId = localStorage.getItem('lastApplicationId');

        if (testApplicationId) {
          setApplicationId(testApplicationId);

          // Fetch header stats
          const statsData = await fetchHeaderStats(testApplicationId);
          if (statsData) {
            setStats(statsData);
          }

          // Fetch financial snapshot
          const snapshotData = await fetchFinancialSnapshot(testApplicationId);
          if (snapshotData) {
            setSnapshot(snapshotData);
          }
        }
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard load error:', err);
      } finally {
        setIsLoading(false);
      }
    }

    fetchDashboardData();
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

  // Default values if no data
  const fiscalScore = stats?.fiscalHealthScore || 0;
  const TrendIcon = Sparkles;
  const trendColor = 'text-muted-foreground';

  return (
    <PageTransition>
      <div className="min-h-screen bg-background">
        <Header />
        <GradientOrbs />

        <main className="container mx-auto px-4 pt-24 pb-16">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
              {error}
            </div>
          )}

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
                  {userData?.name || 'User'}
                </h1>
                <p className="text-muted-foreground mt-1">
                  {userData?.email || 'No email'} {applicationId && `• Application ${applicationId.substring(0, 8)}`}
                </p>
              </div>

              {applicationId && (
                <Link to="/recommendations">
                  <Button size="lg" className="rounded-xl">
                    View Full Recommendations
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              )}
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
                    </div>
                  </div>
                  <p className="text-3xl font-bold text-foreground mt-3">
                    {stats?.fiscalHealthScore || '-'}
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
                    {stats?.cashFlowStability ? `${stats.cashFlowStability}%` : '-'}
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
                    {stats?.communityImpactMultiplier ? `${stats.communityImpactMultiplier}x` : '-'}
                  </p>
                  <p className="text-sm text-muted-foreground">Community Impact</p>
                </GlassCard>
              </motion.div>

              {/* Risk Flags */}
              <motion.div variants={scaleIn}>
                <GlassCard className={`p-5 h-full ${(stats?.riskFlagsCount || 0) > 0 ? 'border-warning/30' : ''}`}>
                  <div className={`p-2 rounded-lg w-fit ${(stats?.riskFlagsCount || 0) > 0 ? 'bg-warning/10' : 'bg-success/10'}`}>
                    <AlertTriangle className={`w-5 h-5 ${(stats?.riskFlagsCount || 0) > 0 ? 'text-warning' : 'text-success'}`} />
                  </div>
                  <p className="text-3xl font-bold text-foreground mt-3">
                    {stats?.riskFlagsCount ?? '-'}
                  </p>
                  <p className="text-sm text-muted-foreground">Risk Flags</p>
                </GlassCard>
              </motion.div>
            </motion.div>

            {/* Financial Snapshot */}
            {snapshot && (
              <motion.section variants={fadeInUp}>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-foreground">Your Financial Snapshot</h2>
                  <Badge variant="secondary">Last 30 days</Badge>
                </div>
                <FinancialCharts snapshot={snapshot} />
              </motion.section>
            )}

            {/* No Data State */}
            {!applicationId && !isLoading && (
              <motion.div variants={fadeInUp} className="text-center py-12">
                <GlassCard className="p-8">
                  <p className="text-muted-foreground mb-4">You haven't completed an evaluation yet</p>
                  <Link to="/evaluation">
                    <Button size="lg" className="rounded-xl">
                      Start Your First Evaluation
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </GlassCard>
              </motion.div>
            )}
          </motion.div>
        </main>
      </div>
    </PageTransition>
  );
}
