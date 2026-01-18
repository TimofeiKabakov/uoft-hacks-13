/**
 * Targets Panel Component
 * 
 * Displays financial targets/guardrails with what-if simulation.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  CreditCard, 
  Repeat, 
  Shield, 
  AlertTriangle,
  Sliders,
  TrendingUp,
  LucideIcon
} from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { staggerContainer, fadeInUp } from '@/lib/animations';
import type { Target } from '@/types/recommendations';

interface TargetsPanelProps {
  targets: Target[];
  currentScore: number;
}

const iconMap: Record<string, LucideIcon> = {
  CreditCard,
  Repeat,
  Shield,
  AlertTriangle,
};

export function TargetsPanel({ targets, currentScore }: TargetsPanelProps) {
  const [adjustedTargets, setAdjustedTargets] = useState<Record<string, number>>({});
  const [projectedScore, setProjectedScore] = useState(currentScore);

  const handleTargetChange = (targetId: string, value: number) => {
    const newAdjusted = { ...adjustedTargets, [targetId]: value };
    setAdjustedTargets(newAdjusted);
    
    // Simple projected score calculation (demo logic)
    let scoreChange = 0;
    targets.forEach((target) => {
      const adjusted = newAdjusted[target.id] ?? target.currentValue;
      const gap = target.currentValue - adjusted;
      const maxGap = target.currentValue - target.recommendedValue;
      if (maxGap !== 0) {
        const progress = gap / maxGap;
        scoreChange += progress * 5; // Each target can add up to 5 points
      }
    });
    setProjectedScore(Math.round(currentScore + scoreChange));
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      <motion.div variants={fadeInUp}>
        <h2 className="text-xl font-bold text-foreground mb-2">
          Targets & Guardrails
        </h2>
        <p className="text-sm text-muted-foreground">
          Concrete goals that will improve your loan terms. Adjust to see projected impact.
        </p>
      </motion.div>

      {/* What-If Simulator */}
      <motion.div variants={fadeInUp}>
        <GlassCard className="p-5 bg-gradient-to-br from-primary/5 to-accent/5">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-primary/10">
              <Sliders className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">What-If Simulator</h3>
              <p className="text-xs text-muted-foreground">
                Adjust targets to see projected score changes
              </p>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-card/50 rounded-lg">
            <div>
              <p className="text-sm text-muted-foreground">Projected Fiscal Health Score</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-3xl font-bold text-foreground">{projectedScore}</span>
                {projectedScore > currentScore && (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center text-success text-sm font-medium"
                  >
                    <TrendingUp className="w-4 h-4 mr-1" />
                    +{projectedScore - currentScore}
                  </motion.span>
                )}
              </div>
            </div>
            <Badge variant="secondary" className="text-xs">
              Estimate only
            </Badge>
          </div>
        </GlassCard>
      </motion.div>

      {/* Target Cards */}
      <motion.div 
        variants={staggerContainer}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {targets.map((target, index) => {
          const Icon = iconMap[target.icon] || Shield;
          const currentValue = adjustedTargets[target.id] ?? target.currentValue;
          const isImproving = target.recommendedValue < target.currentValue 
            ? currentValue < target.currentValue
            : currentValue > target.currentValue;
          const meetsTarget = target.recommendedValue < target.currentValue
            ? currentValue <= target.recommendedValue
            : currentValue >= target.recommendedValue;
          
          return (
            <motion.div
              key={target.id}
              variants={fadeInUp}
              custom={index}
            >
              <GlassCard className="p-5">
                <div className="flex items-start gap-3 mb-4">
                  <div className={`p-2 rounded-lg ${meetsTarget ? 'bg-success/10' : 'bg-primary/10'}`}>
                    <Icon className={`w-5 h-5 ${meetsTarget ? 'text-success' : 'text-primary'}`} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-foreground">{target.name}</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {target.whyItMatters}
                    </p>
                  </div>
                </div>

                {/* Values */}
                <div className="flex items-center justify-between mb-3 text-sm">
                  <div>
                    <span className="text-muted-foreground">Current: </span>
                    <span className="font-medium text-foreground">
                      {target.name.includes('$') || target.unit.includes('$') 
                        ? `$${target.currentValue.toLocaleString()}`
                        : `${target.currentValue} ${target.unit}`}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Target: </span>
                    <span className="font-medium text-success">
                      {target.name.includes('$') || target.unit.includes('$')
                        ? `$${target.recommendedValue.toLocaleString()}`
                        : `${target.recommendedValue} ${target.unit}`}
                    </span>
                  </div>
                </div>

                {/* Slider */}
                <div className="space-y-2">
                  <Slider
                    value={[currentValue]}
                    min={Math.min(target.recommendedValue, target.currentValue) * 0.5}
                    max={Math.max(target.recommendedValue, target.currentValue) * 1.2}
                    step={target.unit === 'events' ? 1 : target.currentValue > 100 ? 50 : 1}
                    onValueChange={([value]) => handleTargetChange(target.id, value)}
                    className="w-full"
                  />
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-medium ${
                      meetsTarget ? 'text-success' : isImproving ? 'text-primary' : 'text-muted-foreground'
                    }`}>
                      {meetsTarget ? '✓ Target met' : isImproving ? 'Improving' : 'Adjust to simulate'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {target.name.includes('$') || target.unit.includes('$')
                        ? `$${Math.round(currentValue).toLocaleString()}`
                        : `${Math.round(currentValue)} ${target.unit}`}
                    </span>
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
