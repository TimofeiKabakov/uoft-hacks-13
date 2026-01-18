/**
 * Personalized Improvement Plan Section
 * 
 * Step 4: Concrete actions to improve affordability
 */

import { useState, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Lightbulb, Check, Target, Clock, TrendingUp } from 'lucide-react';
import { ScrollSection } from './ScrollSection';
import { SectionHeader } from './SectionHeader';
import { GlassCard } from '@/components/ui/GlassCard';

const actions = [
  {
    id: 1,
    title: 'Reduce overdraft occurrences',
    description: 'Set up low-balance alerts to avoid unexpected overdrafts',
    impact: '+15 points',
    timeframe: '30 days',
  },
  {
    id: 2,
    title: 'Stabilize monthly cash flow',
    description: 'Maintain a consistent buffer between income and expenses',
    impact: '+20 points',
    timeframe: '60 days',
  },
  {
    id: 3,
    title: 'Automate savings transfers',
    description: 'Set up automatic transfers to a savings account after each paycheck',
    impact: '+10 points',
    timeframe: '30 days',
  },
];

const milestones = [
  { days: 30, label: '30 Days', progress: 33 },
  { days: 60, label: '60 Days', progress: 66 },
  { days: 90, label: '90 Days', progress: 100 },
];

export function ImprovementSection() {
  const [completedItems, setCompletedItems] = useState<number[]>([]);
  const [isInView, setIsInView] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  // Animate checklist items when in view
  useEffect(() => {
    if (isInView && !shouldReduceMotion) {
      const timers = actions.map((_, index) => 
        setTimeout(() => {
          setCompletedItems(prev => [...prev, index]);
        }, 1000 + index * 500)
      );
      return () => timers.forEach(clearTimeout);
    }
  }, [isInView, shouldReduceMotion]);

  return (
    <ScrollSection className="py-32 px-6 bg-muted/30">
      <div className="max-w-5xl mx-auto">
        <SectionHeader
          step={4}
          title="A real plan to improve your loan terms"
          subtitle="Concrete actions tailored to your business — not generic advice. See exactly what to do and when."
          icon={Lightbulb}
        />

        <div className="grid md:grid-cols-2 gap-8">
          {/* Action Checklist */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            onViewportEnter={() => setIsInView(true)}
            transition={{ delay: 0.3 }}
          >
            <GlassCard hover="none" className="p-6">
              <h3 className="font-semibold mb-6 flex items-center gap-2">
                <Target className="w-5 h-5 text-primary" />
                Priority Actions
              </h3>
              
              <div className="space-y-4">
                {actions.map((action, index) => {
                  const isCompleted = completedItems.includes(index);
                  
                  return (
                    <motion.div
                      key={action.id}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      className={`p-4 rounded-xl border transition-all ${
                        isCompleted 
                          ? 'bg-success/10 border-success/30' 
                          : 'bg-card border-border'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <motion.div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                            isCompleted 
                              ? 'bg-success text-success-foreground' 
                              : 'bg-muted'
                          }`}
                          animate={isCompleted ? { scale: [1, 1.2, 1] } : {}}
                          transition={{ duration: 0.3 }}
                        >
                          {isCompleted ? (
                            <Check className="w-5 h-5" />
                          ) : (
                            <span className="text-sm font-medium">{action.id}</span>
                          )}
                        </motion.div>
                        
                        <div className="flex-1 min-w-0">
                          <p className={`font-medium ${isCompleted ? 'line-through text-muted-foreground' : ''}`}>
                            {action.title}
                          </p>
                          <p className="text-sm text-muted-foreground mt-1">
                            {action.description}
                          </p>
                          <div className="flex items-center gap-4 mt-2 text-xs">
                            <span className="text-success flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              {action.impact}
                            </span>
                            <span className="text-muted-foreground flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {action.timeframe}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </GlassCard>
          </motion.div>

          {/* Progress Timeline */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
          >
            <GlassCard hover="none" className="p-6">
              <h3 className="font-semibold mb-6 flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary" />
                Your 90-Day Journey
              </h3>

              {/* Timeline */}
              <div className="relative">
                {/* Progress Bar Background */}
                <div className="h-2 bg-muted rounded-full mb-8">
                  <motion.div
                    className="h-full bg-gradient-to-r from-primary to-success rounded-full"
                    initial={{ width: '0%' }}
                    whileInView={{ width: '66%' }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.6, duration: 1.5, ease: 'easeOut' }}
                  />
                </div>

                {/* Milestones */}
                <div className="flex justify-between">
                  {milestones.map((milestone, index) => (
                    <motion.div
                      key={milestone.days}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                      className="text-center"
                    >
                      <motion.div
                        className={`w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center ${
                          milestone.progress <= 66 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-muted'
                        }`}
                        animate={milestone.progress <= 66 && !shouldReduceMotion ? {
                          scale: [1, 1.1, 1],
                        } : {}}
                        transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
                      >
                        {milestone.progress <= 66 ? (
                          <Check className="w-5 h-5" />
                        ) : (
                          <span className="text-xs font-medium">{milestone.days}</span>
                        )}
                      </motion.div>
                      <p className="text-sm font-medium">{milestone.label}</p>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Score Projection */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 1 }}
                className="mt-8 p-4 rounded-xl bg-success/10 border border-success/20"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Projected Score Improvement</p>
                    <p className="text-xl font-bold text-success">+45 points</p>
                  </div>
                  <motion.div
                    animate={shouldReduceMotion ? {} : { rotate: [0, 10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <TrendingUp className="w-8 h-8 text-success" />
                  </motion.div>
                </div>
              </motion.div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </ScrollSection>
  );
}
