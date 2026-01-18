/**
 * Recommendation Card Component
 * 
 * Displays a single recommendation with evidence-driven insights.
 */

import { motion } from 'framer-motion';
import { 
  Eye, 
  Plus, 
  Check,
  ChevronRight,
  AlertTriangle,
  AlertCircle,
  Info
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { Badge } from '@/components/ui/badge';
import { cardHover } from '@/lib/animations';
import type { Recommendation, Priority } from '@/types/recommendations';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onViewEvidence: (recommendation: Recommendation) => void;
  onAddToPlan: (recommendation: Recommendation) => void;
  isInPlan?: boolean;
}

const priorityConfig: Record<Priority, { 
  label: string; 
  className: string;
  icon: typeof AlertTriangle;
}> = {
  high: { 
    label: 'High Priority', 
    className: 'bg-destructive/10 text-destructive border-destructive/30',
    icon: AlertTriangle
  },
  medium: { 
    label: 'Medium', 
    className: 'bg-warning/10 text-warning border-warning/30',
    icon: AlertCircle
  },
  low: { 
    label: 'Low', 
    className: 'bg-muted text-muted-foreground border-muted-foreground/30',
    icon: Info
  },
};

export function RecommendationCard({ 
  recommendation, 
  onViewEvidence, 
  onAddToPlan,
  isInPlan = false 
}: RecommendationCardProps) {
  const priorityConf = priorityConfig[recommendation.priority];
  const PriorityIcon = priorityConf.icon;

  return (
    <motion.div
      variants={cardHover}
      initial="rest"
      whileHover="hover"
      whileTap="tap"
    >
      <GlassCard className="p-5 h-full flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className={`text-xs ${priorityConf.className}`}>
                <PriorityIcon className="w-3 h-3 mr-1" />
                {priorityConf.label}
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {recommendation.category}
              </Badge>
            </div>
            <h3 className="font-semibold text-foreground leading-tight">
              {recommendation.title}
            </h3>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-3 flex-1">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
              What we saw
            </p>
            <p className="text-sm text-foreground">
              {recommendation.whatWeSaw}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
              Why it matters
            </p>
            <p className="text-sm text-muted-foreground">
              {recommendation.whyItMatters}
            </p>
          </div>

          <div className="p-3 bg-primary/5 rounded-lg border border-primary/10">
            <p className="text-xs font-medium text-primary uppercase tracking-wider mb-1">
              Recommended Action
            </p>
            <p className="text-sm text-foreground font-medium">
              {recommendation.recommendedAction}
            </p>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <ChevronRight className="w-4 h-4 text-success" />
            <span className="text-success font-medium">{recommendation.expectedImpact}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewEvidence(recommendation)}
            className="flex-1"
          >
            <Eye className="w-4 h-4 mr-1" />
            View Evidence
          </Button>
          <Button
            variant={isInPlan ? "secondary" : "default"}
            size="sm"
            onClick={() => onAddToPlan(recommendation)}
            className="flex-1"
            disabled={isInPlan}
          >
            {isInPlan ? (
              <>
                <Check className="w-4 h-4 mr-1" />
                In Plan
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-1" />
                Add to Plan
              </>
            )}
          </Button>
        </div>
      </GlassCard>
    </motion.div>
  );
}
