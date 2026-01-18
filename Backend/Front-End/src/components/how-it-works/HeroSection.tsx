/**
 * Hero Section - How It Works
 * 
 * "A Better Way to Qualify for Funding"
 */

import { motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export function HeroSection() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <section className="min-h-screen flex items-center justify-center relative overflow-hidden py-20 px-6">
      {/* Animated Background Gradient Mesh */}
      <div className="absolute inset-0 -z-10">
        {!shouldReduceMotion && (
          <>
            <motion.div
              className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-primary/20 blur-3xl"
              animate={{
                x: [0, 50, 0],
                y: [0, -30, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div
              className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-accent/20 blur-3xl"
              animate={{
                x: [0, -40, 0],
                y: [0, 40, 0],
                scale: [1, 1.15, 1],
              }}
              transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-primary/10 blur-3xl"
              animate={{
                scale: [1, 1.05, 1],
                opacity: [0.3, 0.5, 0.3],
              }}
              transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
            />
          </>
        )}
      </div>

      <div className="max-w-4xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent text-sm font-medium mb-8"
        >
          <Sparkles className="w-4 h-4" />
          <span>Smarter Small Business Lending</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 leading-tight"
        >
          Business loans that look at your{' '}
          <span className="relative inline-block">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              real potential
            </span>
            <motion.svg
              viewBox="0 0 200 12"
              className="absolute -bottom-2 left-0 w-full h-3"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
            >
              <motion.path
                d="M 0 8 Q 50 2 100 8 Q 150 14 200 8"
                fill="none"
                stroke="hsl(var(--primary))"
                strokeWidth="3"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 1, duration: 0.8 }}
              />
            </motion.svg>
          </span>
          {' '}— not just your credit score
        </motion.h1>

        {/* Subtext */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Community Spark helps small businesses understand their loan eligibility and find 
          real ways to improve their terms — with complete transparency.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Link to="/evaluate">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button size="lg" className="rounded-xl px-8 py-6 text-lg font-semibold group">
                Start Your Evaluation
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </motion.div>
          </Link>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            className="flex flex-col items-center gap-2 text-muted-foreground"
          >
            <span className="text-sm">Scroll to explore</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12l7 7 7-7" />
            </svg>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
