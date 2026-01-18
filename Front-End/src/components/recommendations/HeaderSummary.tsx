/**
 * Header Summary Component
 * 
 * Displays decision badge, loan range, readiness indicator, and stat cards.
 */

import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Heart,
  TrendingUp,
  Droplets,
  AlertTriangle,
  LucideIcon
} from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { staggerContainer, fadeInUp, scaleIn } from '@/lib/animations';
import type { DecisionType, HeaderStats } from '@/types/recommendations';

interface HeaderSummaryProps {
  decision: DecisionType;
  estimatedLoanRange?: { min: number; max: number };
  readinessScore: number;
  stats: HeaderStats;
}

const decisionConfig: Record<DecisionType, { 
  icon: LucideIcon; 
  label: string; 
  className: string;
  bgClass: string;
}> = {
  APPROVE: { 
    icon: CheckCircle, 
    label: 'Approved', 
    className: 'text-success',
    bgClass: 'bg-success/10 border-success/30'
  },
  REFER: { 
    icon: AlertCircle, 
    label: 'Under Review', 
    className: 'text-warning',
    bgClass: 'bg-warning/10 border-warning/30'
  },
  DENY: { 
    icon: XCircle, 
    label: 'Not Approved', 
    className: 'text-destructive',
    bgClass: 'bg-destructive/10 border-destructive/30'
  },
};

const statCards: { 
  key: keyof HeaderStats; 
  label: string; 
  icon: LucideIcon;
  format: (value: number) => string;
  interpretation: (value: number) => string;
}[] = [
  { 
    key: 'fiscalHealthScore', 
    label: 'Fiscal Health Score', 
    icon: Heart,
    format: (v) => v.toString(),
    interpretation: (v) => v >= 700 ? 'Excellent' : v >= 600 ? 'Good' : 'Needs work'
  },
  { 
    key: 'communityImpactMultiplier', 
    label: 'Community Impact', 
    icon: TrendingUp,
    format: (v) => `${v.toFixed(1)}x`,
    interpretation: (v) => v >= 1.5 ? 'Strong ties' : v >= 1.0 ? 'Moderate' : 'Limited'
  },
  { 
    key: 'cashFlowStability', 
    label: 'Cash Flow Stability', 
    icon: Droplets,
    format: (v) => `${v}%`,
    interpretation: (v) => v >= 80 ? 'Very stable' : v >= 60 ? 'Moderate' : 'Volatile'
  },
  { 
    key: 'riskFlagsCount', 
    label: 'Risk Flags', 
    icon: AlertTriangle,
    format: (v) => v.toString(),
    interpretation: (v) => v === 0 ? 'None detected' : v <= 2 ? 'Minor concerns' : 'Needs attention'
  },
];

export function HeaderSummary({ decision, estimatedLoanRange, readinessScore, stats }: HeaderSummaryProps) {
  const config = decisionConfig[decision];
  const DecisionIcon = config.icon;

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* Title and Decision */}
      <motion.div variants={fadeInUp} className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Your Loan Improvement Recommendations
          </h1>
          <p className="text-muted-foreground mt-1">
            Specific actions to strengthen your eligibility and terms.
          </p>
        </div>
        
        <motion.div 
          variants={scaleIn}
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${config.bgClass}`}
        >
          <DecisionIcon className={`w-5 h-5 ${config.className}`} />
          <span className={`font-semibold ${config.className}`}>{config.label}</span>
        </motion.div>
      </motion.div>

      {/* Loan Range and Readiness */}
      <motion.div variants={fadeInUp} className="flex flex-wrap items-center gap-6">
        {estimatedLoanRange && (
          <GlassCard className="px-5 py-3">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Estimated Loan Range</p>
            <p className="text-xl font-bold text-foreground">
              ${estimatedLoanRange.min.toLocaleString()} – ${estimatedLoanRange.max.toLocaleString()}
            </p>
          </GlassCard>
        )}
        
        <GlassCard className="px-5 py-3 flex-1 min-w-[200px]">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Readiness Score</p>
            <span className="text-sm font-semibold text-primary">{readinessScore}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${readinessScore}%` }}
              transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
            />
          </div>
        </GlassCard>
      </motion.div>

      {/* Stat Cards */}
      <motion.div 
        variants={staggerContainer}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          const value = stats[stat.key];
          const isRiskFlag = stat.key === 'riskFlagsCount';
          
          return (
            <motion.div
              key={stat.key}
              variants={fadeInUp}
              custom={index}
              whileHover={{ scale: 1.02, y: -4 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <GlassCard className="p-4 h-full">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${isRiskFlag && value > 0 ? 'bg-destructive/10' : 'bg-primary/10'}`}>
                    <Icon className={`w-5 h-5 ${isRiskFlag && value > 0 ? 'text-destructive' : 'text-primary'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-muted-foreground truncate">{stat.label}</p>
                    <p className="text-2xl font-bold text-foreground">{stat.format(value)}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{stat.interpretation(value)}</p>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </motion.div>
    </motion.div>
  );
}
