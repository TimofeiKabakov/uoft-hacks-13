/**
 * Security & Trust Summary Section
 * 
 * "Designed for trust from day one"
 */

import { motion, useReducedMotion } from 'framer-motion';
import { Shield, Lock, FileText, UserCheck, CheckCircle2 } from 'lucide-react';
import { ScrollSection } from './ScrollSection';
import { GlassCard } from '@/components/ui/GlassCard';

const trustItems = [
  {
    icon: Lock,
    text: 'Secrets managed via encrypted vaults',
  },
  {
    icon: FileText,
    text: 'No .env files or hardcoded credentials',
  },
  {
    icon: Shield,
    text: 'Full audit trail for every action',
  },
  {
    icon: UserCheck,
    text: 'User-controlled data access',
  },
];

export function TrustSummarySection() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <ScrollSection className="py-32 px-6 bg-muted/30">
      <div className="max-w-4xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Animated Shield */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="flex justify-center order-2 md:order-1"
          >
            <div className="relative">
              {/* Outer Glow */}
              {!shouldReduceMotion && (
                <motion.div
                  className="absolute inset-0 rounded-3xl bg-gradient-to-br from-primary/20 to-accent/20 blur-2xl"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 0.8, 0.5],
                  }}
                  transition={{ duration: 4, repeat: Infinity }}
                  style={{ width: 200, height: 200, left: -20, top: -20 }}
                />
              )}

              {/* Shield Container */}
              <motion.div
                className="relative w-40 h-48 flex items-center justify-center"
                animate={shouldReduceMotion ? {} : {
                  y: [0, -10, 0],
                }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              >
                {/* Shield SVG */}
                <svg
                  viewBox="0 0 100 120"
                  className="w-full h-full"
                  fill="none"
                >
                  {/* Shield Background */}
                  <motion.path
                    d="M50 5 L95 20 L95 60 C95 85 75 105 50 115 C25 105 5 85 5 60 L5 20 Z"
                    fill="url(#shieldGradient)"
                    initial={{ pathLength: 0, opacity: 0 }}
                    whileInView={{ pathLength: 1, opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.5, duration: 1.5 }}
                  />
                  
                  {/* Shield Border */}
                  <motion.path
                    d="M50 5 L95 20 L95 60 C95 85 75 105 50 115 C25 105 5 85 5 60 L5 20 Z"
                    fill="none"
                    stroke="hsl(var(--primary))"
                    strokeWidth="2"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3, duration: 1.5 }}
                  />

                  {/* Checkmark */}
                  <motion.path
                    d="M30 60 L45 75 L70 45"
                    fill="none"
                    stroke="hsl(var(--primary-foreground))"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 1.2, duration: 0.5 }}
                  />

                  <defs>
                    <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="hsl(var(--primary))" />
                      <stop offset="100%" stopColor="hsl(var(--accent))" />
                    </linearGradient>
                  </defs>
                </svg>
              </motion.div>
            </div>
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="order-1 md:order-2"
          >
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-3xl md:text-4xl font-bold tracking-tight mb-6"
            >
              Designed for trust from day one
            </motion.h2>

            <GlassCard hover="none" className="p-6">
              <div className="space-y-4">
                {trustItems.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      className="flex items-center gap-4"
                    >
                      <motion.div
                        className="w-8 h-8 rounded-lg bg-success/10 flex items-center justify-center flex-shrink-0"
                        whileInView={{ scale: [0, 1.2, 1] }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.6 + index * 0.1, type: 'spring' }}
                      >
                        <CheckCircle2 className="w-4 h-4 text-success" />
                      </motion.div>
                      <div className="flex items-center gap-3">
                        <Icon className="w-5 h-5 text-muted-foreground" />
                        <span className="text-sm font-medium">{item.text}</span>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </ScrollSection>
  );
}
