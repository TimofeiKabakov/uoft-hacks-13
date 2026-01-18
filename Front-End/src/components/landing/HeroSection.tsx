/**
 * Hero Section Component
 * 
 * Main hero section for the landing page with animated text and CTA.
 */

import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { staggerContainer, fadeInUp, buttonHover, buttonGlow } from '@/lib/animations';

export function HeroSection() {
  return (
    <motion.section
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="min-h-screen flex items-center justify-center pt-24 pb-12 px-6"
    >
      <div className="max-w-5xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          variants={fadeInUp}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-8"
        >
          <Sparkles className="w-4 h-4" />
          <span>AI-Powered Impact Lending</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          variants={fadeInUp}
          className="text-display-lg font-bold tracking-tight mb-6"
        >
          Impact Loans for
          <br />
          <span className="relative">
            <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-shift">
              Businesses Banks Overlook
            </span>
            {/* Animated underline */}
            <motion.svg
              viewBox="0 0 400 20"
              className="absolute -bottom-2 left-0 w-full h-auto"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 0.8, duration: 1, ease: 'easeInOut' }}
            >
              <motion.path
                d="M 0 15 Q 100 5 200 15 Q 300 25 400 15"
                fill="none"
                stroke="hsl(var(--primary))"
                strokeWidth="3"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.8, duration: 1, ease: 'easeInOut' }}
              />
            </motion.svg>
          </span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          variants={fadeInUp}
          className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Our multi-agent AI evaluates businesses holistically—analyzing fiscal health, 
          community impact, and compliance to unlock fair financing for underserved entrepreneurs.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          variants={fadeInUp}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link to="/evaluate">
            <motion.div
              variants={{ ...buttonHover, ...buttonGlow }}
              initial="rest"
              whileHover="hover"
              whileTap="tap"
            >
              <Button size="lg" className="rounded-xl px-8 py-6 text-lg font-semibold group">
                Start Evaluation
                <motion.span
                  className="ml-2"
                  animate={{ x: [0, 4, 0] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                >
                  <ArrowRight className="w-5 h-5" />
                </motion.span>
              </Button>
            </motion.div>
          </Link>

          <Link to="/about">
            <motion.div
              variants={buttonHover}
              initial="rest"
              whileHover="hover"
              whileTap="tap"
            >
              <Button 
                variant="outline" 
                size="lg" 
                className="rounded-xl px-8 py-6 text-lg font-semibold"
              >
                See How It Works
              </Button>
            </motion.div>
          </Link>
        </motion.div>

        {/* Stats */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-3 gap-8 mt-20 pt-10 border-t border-border/50"
        >
          {[
            { value: '4', label: 'AI Agents' },
            { value: '<3s', label: 'Evaluation Time' },
            { value: '97%', label: 'Accuracy Rate' },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              variants={fadeInUp}
              className="text-center"
            >
              <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.section>
  );
}
