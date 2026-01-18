/**
 * Plan Tabs Component
 * 
 * Action plan builder with 30/60/90 day tabs and checklist.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Check, 
  Clock, 
  ChevronRight,
  Sparkles,
  Zap,
  Target
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { staggerContainer, fadeInUp, scaleInBounce } from '@/lib/animations';
import type { ActionItem, ActionStatus, Difficulty, Impact } from '@/types/recommendations';

interface PlanTabsProps {
  actions: ActionItem[];
  onStatusChange: (actionId: string, status: ActionStatus) => void;
}

const difficultyConfig: Record<Difficulty, { label: string; className: string }> = {
  easy: { label: 'Easy', className: 'bg-success/10 text-success border-success/30' },
  medium: { label: 'Medium', className: 'bg-warning/10 text-warning border-warning/30' },
  hard: { label: 'Hard', className: 'bg-destructive/10 text-destructive border-destructive/30' },
};

const impactConfig: Record<Impact, { label: string; className: string; icon: typeof Zap }> = {
  low: { label: 'Low Impact', className: 'text-muted-foreground', icon: Target },
  medium: { label: 'Medium Impact', className: 'text-primary', icon: Sparkles },
  high: { label: 'High Impact', className: 'text-success', icon: Zap },
};

export function PlanTabs({ actions, onStatusChange }: PlanTabsProps) {
  const [activeTab, setActiveTab] = useState<'30' | '60' | '90'>('30');

  const getActionsForTimeframe = (timeframe: number) => 
    actions.filter((a) => a.timeframe === timeframe);

  const getProgress = (timeframe: number) => {
    const timeframeActions = getActionsForTimeframe(timeframe);
    const completed = timeframeActions.filter((a) => a.status === 'done').length;
    return timeframeActions.length > 0 ? (completed / timeframeActions.length) * 100 : 0;
  };

  const totalCompleted = actions.filter((a) => a.status === 'done').length;
  const totalProgress = actions.length > 0 ? (totalCompleted / actions.length) * 100 : 0;

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="space-y-6"
    >
      {/* Header with Progress Ring */}
      <motion.div variants={fadeInUp} className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-foreground">Action Plan Builder</h2>
          <p className="text-sm text-muted-foreground">
            {totalCompleted} of {actions.length} actions completed
          </p>
        </div>
        
        <div className="relative w-16 h-16">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="32"
              cy="32"
              r="28"
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="4"
            />
            <motion.circle
              cx="32"
              cy="32"
              r="28"
              fill="none"
              stroke="hsl(var(--primary))"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 28}`}
              initial={{ strokeDashoffset: 2 * Math.PI * 28 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 28 * (1 - totalProgress / 100) }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-sm font-bold text-foreground">
              {Math.round(totalProgress)}%
            </span>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as '30' | '60' | '90')}>
        <TabsList className="grid w-full grid-cols-3 mb-6">
          {[30, 60, 90].map((days) => (
            <TabsTrigger key={days} value={days.toString()} className="relative">
              <span>{days} Days</span>
              <motion.div
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                initial={false}
                animate={{ 
                  scaleX: activeTab === days.toString() ? 1 : 0,
                  opacity: activeTab === days.toString() ? 1 : 0
                }}
                transition={{ duration: 0.2 }}
              />
            </TabsTrigger>
          ))}
        </TabsList>

        {[30, 60, 90].map((days) => (
          <TabsContent key={days} value={days.toString()}>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {/* Progress for this timeframe */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-muted-foreground">
                    {days}-day progress
                  </span>
                  <span className="font-medium text-foreground">
                    {Math.round(getProgress(days))}%
                  </span>
                </div>
                <Progress value={getProgress(days)} className="h-2" />
              </div>

              {/* Actions List */}
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="show"
                className="space-y-3"
              >
                <AnimatePresence mode="popLayout">
                  {getActionsForTimeframe(days).map((action, index) => {
                    const diffConf = difficultyConfig[action.difficulty];
                    const impConf = impactConfig[action.impact];
                    const ImpactIcon = impConf.icon;

                    return (
                      <motion.div
                        key={action.id}
                        layout
                        variants={fadeInUp}
                        custom={index}
                        initial="hidden"
                        animate="show"
                        exit={{ opacity: 0, x: -20 }}
                      >
                        <GlassCard className={`p-4 transition-all ${
                          action.status === 'done' ? 'opacity-60' : ''
                        }`}>
                          <div className="flex items-start gap-3">
                            {/* Status Button */}
                            <button
                              onClick={() => onStatusChange(
                                action.id,
                                action.status === 'done' ? 'pending' : 
                                action.status === 'pending' ? 'in_progress' : 'done'
                              )}
                              className={`mt-0.5 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                                action.status === 'done'
                                  ? 'bg-success border-success text-success-foreground'
                                  : action.status === 'in_progress'
                                  ? 'border-primary bg-primary/10'
                                  : 'border-border hover:border-primary'
                              }`}
                            >
                              {action.status === 'done' && (
                                <motion.div
                                  variants={scaleInBounce}
                                  initial="hidden"
                                  animate="show"
                                >
                                  <Check className="w-4 h-4" />
                                </motion.div>
                              )}
                              {action.status === 'in_progress' && (
                                <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                              )}
                            </button>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap mb-1">
                                <h4 className={`font-medium ${
                                  action.status === 'done' ? 'line-through text-muted-foreground' : 'text-foreground'
                                }`}>
                                  {action.title}
                                </h4>
                                <Badge variant="outline" className={`text-xs ${diffConf.className}`}>
                                  {diffConf.label}
                                </Badge>
                              </div>
                              
                              <p className="text-sm text-muted-foreground mb-2">
                                {action.step}
                              </p>

                              <div className="flex items-center gap-4 text-xs">
                                <span className={`flex items-center gap-1 ${impConf.className}`}>
                                  <ImpactIcon className="w-3 h-3" />
                                  {impConf.label}
                                </span>
                                <span className="flex items-center gap-1 text-muted-foreground">
                                  <Clock className="w-3 h-3" />
                                  {action.timeEstimate}
                                </span>
                              </div>
                            </div>

                            {/* Status Badge */}
                            {action.status !== 'pending' && (
                              <Badge 
                                variant={action.status === 'done' ? 'default' : 'secondary'}
                                className="text-xs"
                              >
                                {action.status === 'done' ? 'Completed' : 'In Progress'}
                              </Badge>
                            )}
                          </div>
                        </GlassCard>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>

                {getActionsForTimeframe(days).length === 0 && (
                  <motion.div variants={fadeInUp}>
                    <GlassCard className="p-8 text-center">
                      <p className="text-muted-foreground">
                        No actions planned for this timeframe yet.
                      </p>
                    </GlassCard>
                  </motion.div>
                )}
              </motion.div>
            </motion.div>
          </TabsContent>
        ))}
      </Tabs>
    </motion.div>
  );
}
