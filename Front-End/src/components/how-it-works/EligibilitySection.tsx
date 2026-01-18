/**
 * Transparent Eligibility Outcome Section
 * 
 * Step 3: Clear, explainable results
 */

import { useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Award, ChevronDown, ChevronUp, HelpCircle, CheckCircle2 } from 'lucide-react';
import { ScrollSection } from './ScrollSection';
import { SectionHeader } from './SectionHeader';
import { GlassCard } from '@/components/ui/GlassCard';
import { ScoreGauge } from '@/components/charts/ScoreGauge';

const loanTiers = [
  { id: 'starter', name: 'Basic', range: '$10k-25k', color: 'bg-muted' },
  { id: 'standard', name: 'Growth', range: '$25k-50k', color: 'bg-primary/20' },
  { id: 'preferred', name: 'Scale', range: '$50k-100k', color: 'bg-success/20', active: true },
];

const reasons = [
  'Consistent revenue deposits over 12 months',
  'Low overdraft frequency (2 in past year)',
  'Stable operating cash flow',
  'Community impact multiplier applied',
];

export function EligibilitySection() {
  const [isExpanded, setIsExpanded] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  return (
    <ScrollSection className="py-32 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeader
          step={3}
          title="A clear, explainable result"
          subtitle="See exactly where you stand — and understand why. No hidden formulas or black boxes."
          icon={Award}
        />

        <div className="grid md:grid-cols-2 gap-8 items-start">
          {/* Score Visualization */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            <GlassCard hover="none" className="p-8 text-center">
              <div className="flex justify-center mb-6">
                <ScoreGauge
                  value={78}
                  maxValue={100}
                  label="Eligibility Score"
                  size="lg"
                  delay={0.5}
                />
              </div>

              {/* Loan Tier */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.8 }}
              >
                <p className="text-sm text-muted-foreground mb-3">Your Loan Tier</p>
                <div className="flex gap-2 justify-center">
                  {loanTiers.map((tier, index) => (
                    <motion.div
                      key={tier.id}
                      initial={{ opacity: 0, scale: 0.8 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.9 + index * 0.1 }}
                      className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                        tier.active 
                          ? 'bg-success text-success-foreground ring-2 ring-success ring-offset-2 ring-offset-background' 
                          : tier.color + ' text-muted-foreground'
                      }`}
                    >
                      {tier.name}
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Estimated Loan Amount */}
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 1.2 }}
                className="mt-6 p-4 rounded-xl bg-success/10 border border-success/20"
              >
                <p className="text-sm text-muted-foreground">Estimated Loan Range</p>
                <p className="text-2xl font-bold text-success">$50,000 - $75,000</p>
              </motion.div>
            </GlassCard>
          </motion.div>

          {/* Explainability */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
          >
            <GlassCard hover="none" className="overflow-hidden">
              {/* Expandable Header */}
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full p-6 flex items-center justify-between hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <HelpCircle className="w-5 h-5 text-primary" />
                  <span className="font-semibold">Why this result?</span>
                </div>
                <motion.div
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                </motion.div>
              </button>

              {/* Expandable Content */}
              <motion.div
                initial={false}
                animate={{
                  height: isExpanded ? 'auto' : 0,
                  opacity: isExpanded ? 1 : 0,
                }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="px-6 pb-6 space-y-3">
                  {reasons.map((reason, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={isExpanded ? { opacity: 1, x: 0 } : {}}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-3"
                    >
                      <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{reason}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </GlassCard>

            {/* No Black Boxes Callout */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="mt-4 p-4 rounded-xl bg-accent/10 border border-accent/20 flex items-center gap-3"
            >
              <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                <Award className="w-5 h-5 text-accent" />
              </div>
              <div>
                <p className="font-medium text-sm">No black boxes</p>
                <p className="text-xs text-muted-foreground">
                  Every factor in your score is visible and explained
                </p>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </ScrollSection>
  );
}
