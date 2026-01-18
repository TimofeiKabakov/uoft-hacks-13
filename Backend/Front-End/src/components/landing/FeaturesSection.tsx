/**
 * Features Section Component
 * 
 * Displays the three main agent features with animated cards.
 */

import { motion } from 'framer-motion';
import { Search, Heart, Shield, GraduationCap } from 'lucide-react';
import { FeatureCard } from './FeatureCard';
import { staggerContainer, fadeInUp } from '@/lib/animations';

const features = [
  {
    icon: Search,
    title: 'Forensic Auditor',
    description: 'Deep analysis of financial transactions, cash flow patterns, and account health to assess true fiscal stability.',
    color: 'primary' as const,
  },
  {
    icon: Heart,
    title: 'Impact Analyst',
    description: 'Evaluates community benefit, local employment impact, and opportunity zone placement for impact multipliers.',
    color: 'accent' as const,
  },
  {
    icon: Shield,
    title: 'Compliance Sentry',
    description: 'Automated KYC/AML verification, business registration checks, and regulatory compliance validation.',
    color: 'success' as const,
  },
];

export function FeaturesSection() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <motion.div
            variants={fadeInUp}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent text-sm font-medium mb-6"
          >
            <GraduationCap className="w-4 h-4" />
            <span>Multi-Agent Intelligence</span>
          </motion.div>

          <motion.h2
            variants={fadeInUp}
            className="text-display-sm font-bold mb-4"
          >
            Four Specialized Agents
          </motion.h2>

          <motion.p
            variants={fadeInUp}
            className="text-lg text-muted-foreground max-w-2xl mx-auto"
          >
            Our AI agents work together to provide a comprehensive, fair evaluation 
            that traditional credit scoring misses.
          </motion.p>
        </motion.div>

        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard
              key={feature.title}
              {...feature}
              delay={index * 0.1}
            />
          ))}
        </div>

        {/* Additional Agent */}
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="mt-6 max-w-md mx-auto"
        >
          <FeatureCard
            icon={GraduationCap}
            title="Business Coach"
            description="Provides actionable improvement plans and recommendations to help businesses grow and succeed."
            color="accent"
            delay={0.3}
          />
        </motion.div>
      </div>
    </section>
  );
}
