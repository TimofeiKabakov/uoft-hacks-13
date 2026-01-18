/**
 * Secure Financial Snapshot Section
 * 
 * Step 1: Explains secure data analysis
 */

import { motion, useReducedMotion } from 'framer-motion';
import { Lock, Database, ArrowRight, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { ScrollSection } from './ScrollSection';
import { SectionHeader } from './SectionHeader';
import { GlassCard } from '@/components/ui/GlassCard';

export function SecureSnapshotSection() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <ScrollSection className="py-32 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeader
          step={1}
          title="We analyze financial stability — securely"
          subtitle="Understanding your business's financial patterns helps us find the right loan terms, without compromising your privacy."
          icon={Lock}
        />

        <div className="grid md:grid-cols-2 gap-8 items-center">
          {/* Visual */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="relative"
          >
            <GlassCard hover="none" className="p-8 relative overflow-hidden">
              {/* Animated Flow */}
              <div className="flex items-center justify-between mb-8">
                <motion.div
                  className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center"
                  animate={shouldReduceMotion ? {} : {
                    scale: [1, 1.05, 1],
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  <Database className="w-8 h-8 text-primary" />
                </motion.div>

                {/* Animated Arrow */}
                <div className="flex-1 mx-4 relative h-1">
                  <div className="absolute inset-0 bg-border rounded-full" />
                  <motion.div
                    className="absolute left-0 top-0 h-full bg-primary rounded-full"
                    initial={{ width: '0%' }}
                    whileInView={{ width: '100%' }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.5, duration: 1.5, ease: 'easeOut' }}
                  />
                  {!shouldReduceMotion && (
                    <motion.div
                      className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary"
                      animate={{ left: ['0%', '100%', '0%'] }}
                      transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                    />
                  )}
                </div>

                <motion.div
                  className="w-16 h-16 rounded-2xl bg-success/10 flex items-center justify-center"
                  animate={shouldReduceMotion ? {} : {
                    scale: [1, 1.05, 1],
                  }}
                  transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
                >
                  <ShieldCheck className="w-8 h-8 text-success" />
                </motion.div>
              </div>

              {/* Labels */}
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Bank Data</span>
                <span className="text-success font-medium">Stability Signals</span>
              </div>

              {/* Animated Lock */}
              <motion.div
                className="absolute -bottom-4 -right-4 w-24 h-24 rounded-full bg-accent/10 flex items-center justify-center"
                initial={{ scale: 0, rotate: -45 }}
                whileInView={{ scale: 1, rotate: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.8, type: 'spring' }}
              >
                <Lock className="w-10 h-10 text-accent" />
              </motion.div>
            </GlassCard>

            {/* Caption */}
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 1 }}
              className="text-sm text-muted-foreground text-center mt-4 flex items-center justify-center gap-2"
            >
              <Lock className="w-4 h-4" />
              Data access is permissioned and temporary.
            </motion.p>
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="space-y-6"
          >
            <FeatureItem
              icon={Eye}
              title="Income consistency & spending patterns"
              description="We look at signals that indicate financial stability — like regular income deposits and responsible spending habits."
              delay={0.5}
            />
            
            <FeatureItem
              icon={EyeOff}
              title="We never store raw data"
              description="Your credentials are never accessed. We analyze anonymized patterns, not personal transaction details."
              delay={0.6}
            />
            
            <FeatureItem
              icon={ShieldCheck}
              title="Bank-level encryption"
              description="All data transmission uses the same security standards as major financial institutions."
              delay={0.7}
            />
          </motion.div>
        </div>
      </div>
    </ScrollSection>
  );
}

interface FeatureItemProps {
  icon: React.ElementType;
  title: string;
  description: string;
  delay: number;
}

function FeatureItem({ icon: Icon, title, description, delay }: FeatureItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="flex gap-4"
    >
      <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-primary" />
      </div>
      <div>
        <h3 className="font-semibold mb-1">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}
