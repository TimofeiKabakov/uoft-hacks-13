/**
 * Alerts Panel & Progress Tracker Components
 */

import { motion } from 'framer-motion';
import { AlertTriangle, AlertCircle, Info, TrendingUp, Flame, Download, Save } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { staggerContainer, fadeInUp } from '@/lib/animations';
import type { Alert, ProgressData } from '@/types/recommendations';

// Alerts Panel
interface AlertsPanelProps { alerts: Alert[]; }

const severityConfig = {
  critical: { icon: AlertTriangle, className: 'bg-destructive/10 border-destructive/30 text-destructive' },
  warning: { icon: AlertCircle, className: 'bg-warning/10 border-warning/30 text-warning' },
  info: { icon: Info, className: 'bg-primary/10 border-primary/30 text-primary' },
};

export function AlertsPanel({ alerts }: AlertsPanelProps) {
  return (
    <GlassCard className="p-5">
      <h3 className="font-semibold text-foreground mb-4">Alerts & Timing</h3>
      <motion.div variants={staggerContainer} initial="hidden" animate="show" className="space-y-3">
        {alerts.map((alert, index) => {
          const config = severityConfig[alert.severity];
          const Icon = config.icon;
          return (
            <motion.div key={alert.id} variants={fadeInUp} custom={index} className={`p-3 rounded-lg border ${config.className}`}>
              <div className="flex items-start gap-2">
                <Icon className="w-4 h-4 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-foreground text-sm">{alert.title}</p>
                  <p className="text-xs text-muted-foreground mt-1">{alert.message}</p>
                  <p className="text-xs font-medium mt-2">→ {alert.suggestedAction}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>
    </GlassCard>
  );
}

// Progress Tracker
interface ProgressTrackerProps { progress: ProgressData; onSave: () => void; }

export function ProgressTracker({ progress, onSave }: ProgressTrackerProps) {
  return (
    <GlassCard className="p-5">
      <h3 className="font-semibold text-foreground mb-4">Progress & Momentum</h3>
      <div className="space-y-4">
        {/* Streak */}
        <div className="flex items-center gap-3 p-3 bg-success/5 rounded-lg border border-success/20">
          <Flame className="w-5 h-5 text-success" />
          <div>
            <p className="font-medium text-foreground">{progress.streakDays} day streak</p>
            <p className="text-xs text-muted-foreground">{progress.streakType}</p>
          </div>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-muted/50 rounded-lg text-center">
            <p className="text-2xl font-bold text-foreground">{progress.completedActions}</p>
            <p className="text-xs text-muted-foreground">Actions Done</p>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg text-center">
            <p className="text-2xl font-bold text-foreground flex items-center justify-center gap-1">
              {progress.approvalProgress}%
              {progress.scoreTrend === 'up' && <TrendingUp className="w-4 h-4 text-success" />}
            </p>
            <p className="text-xs text-muted-foreground">To Approval</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onSave} className="flex-1">
            <Save className="w-4 h-4 mr-1" /> Save Plan
          </Button>
          <Button variant="outline" size="sm" onClick={() => window.print()} className="flex-1">
            <Download className="w-4 h-4 mr-1" /> Export
          </Button>
        </div>
      </div>
    </GlassCard>
  );
}
