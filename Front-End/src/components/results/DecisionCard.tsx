/**
 * Decision Card Component
 * 
 * Displays the evaluation decision with strong visual treatment.
 */

import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, AlertCircle, DollarSign, Percent, Calendar } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { scaleInBounce } from '@/lib/animations';
import type { EvaluationResponse } from '@/types';

interface DecisionCardProps {
  decision: EvaluationResponse['decision'];
  loanTerms?: EvaluationResponse['loanTerms'];
  onCelebrate?: () => void;
}

const decisionConfig = {
  APPROVE: {
    icon: CheckCircle2,
    title: 'Approved',
    subtitle: 'Congratulations! Your business qualifies for funding.',
    bgClass: 'bg-gradient-to-br from-success/20 to-success/5',
    borderClass: 'border-success/30',
    iconClass: 'text-success',
    badgeClass: 'bg-success text-success-foreground',
  },
  DENY: {
    icon: XCircle,
    title: 'Not Approved',
    subtitle: 'Unfortunately, the business doesn\'t meet our criteria at this time.',
    bgClass: 'bg-gradient-to-br from-destructive/20 to-destructive/5',
    borderClass: 'border-destructive/30',
    iconClass: 'text-destructive',
    badgeClass: 'bg-destructive text-destructive-foreground',
  },
  REVIEW: {
    icon: AlertCircle,
    title: 'Under Review',
    subtitle: 'The application requires additional review. Please address the flagged concerns and consider reapplying.',
    bgClass: 'bg-gradient-to-br from-warning/20 to-warning/5',
    borderClass: 'border-warning/30',
    iconClass: 'text-warning',
    badgeClass: 'bg-warning text-warning-foreground',
  },
  REFER: {
    icon: AlertCircle,
    title: 'Under Review',
    subtitle: 'The application requires additional review by our team.',
    bgClass: 'bg-gradient-to-br from-warning/20 to-warning/5',
    borderClass: 'border-warning/30',
    iconClass: 'text-warning',
    badgeClass: 'bg-warning text-warning-foreground',
  },
};

export function DecisionCard({ decision, loanTerms, onCelebrate }: DecisionCardProps) {
  const config = decisionConfig[decision];
  const Icon = config.icon;

  return (
    <motion.div
      variants={scaleInBounce}
      initial="hidden"
      animate="show"
      onAnimationComplete={() => {
        if (decision === 'APPROVE' && onCelebrate) {
          onCelebrate();
        }
      }}
    >
      <GlassCard 
        hover="none" 
        className={`p-8 ${config.bgClass} border ${config.borderClass}`}
      >
        <div className="flex items-start gap-6">
          {/* Icon */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            className={`w-16 h-16 rounded-2xl ${config.badgeClass} flex items-center justify-center flex-shrink-0`}
          >
            <Icon className="w-8 h-8" />
          </motion.div>

          {/* Content */}
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-3 ${config.badgeClass}`}>
                {config.title}
              </span>
              <p className="text-lg text-foreground/80">{config.subtitle}</p>
            </motion.div>

            {/* Loan Terms (for approved) */}
            {decision === 'APPROVE' && loanTerms && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-6 grid grid-cols-3 gap-4"
              >
                <LoanTermItem
                  icon={DollarSign}
                  label="Loan Amount"
                  value={`$${loanTerms.amount.toLocaleString()}`}
                  delay={0.6}
                />
                <LoanTermItem
                  icon={Percent}
                  label="APR"
                  value={`${loanTerms.apr}%`}
                  delay={0.7}
                />
                <LoanTermItem
                  icon={Calendar}
                  label="Term"
                  value={`${loanTerms.termMonths} months`}
                  delay={0.8}
                />
              </motion.div>
            )}

            {decision === 'APPROVE' && loanTerms?.monthlyPayment && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.9 }}
                className="mt-4 p-4 rounded-xl bg-success/10 border border-success/20"
              >
                <p className="text-sm text-muted-foreground">Estimated Monthly Payment</p>
                <p className="text-2xl font-bold text-success">
                  ${loanTerms.monthlyPayment.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
}

interface LoanTermItemProps {
  icon: React.ElementType;
  label: string;
  value: string;
  delay: number;
}

function LoanTermItem({ icon: Icon, label, value, delay }: LoanTermItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="text-center p-3 rounded-xl bg-background/50"
    >
      <Icon className="w-5 h-5 mx-auto mb-2 text-muted-foreground" />
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </motion.div>
  );
}
