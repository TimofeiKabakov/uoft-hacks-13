/**
 * Scroll Section Component
 * 
 * Reusable section with scroll-triggered reveal animation.
 */

import { ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ScrollSectionProps {
  children: ReactNode;
  className?: string;
  id?: string;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

export function ScrollSection({ 
  children, 
  className, 
  id,
  delay = 0,
  direction = 'up' 
}: ScrollSectionProps) {
  const shouldReduceMotion = useReducedMotion();

  const directionOffset = {
    up: { y: 60, x: 0 },
    down: { y: -60, x: 0 },
    left: { x: 60, y: 0 },
    right: { x: -60, y: 0 },
  };

  const offset = directionOffset[direction];

  return (
    <motion.section
      id={id}
      initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, ...offset }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ 
        duration: shouldReduceMotion ? 0.3 : 0.8, 
        delay,
        ease: [0.22, 1, 0.36, 1] 
      }}
      className={cn('relative', className)}
    >
      {children}
    </motion.section>
  );
}
