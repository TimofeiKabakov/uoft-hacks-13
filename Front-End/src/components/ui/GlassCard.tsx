/**
 * Glass Card Component
 * 
 * A card with glassmorphism effect and optional hover animations.
 */

import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';
import { cardHover, cardHoverSubtle } from '@/lib/animations';

interface GlassCardProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  hover?: 'lift' | 'subtle' | 'none';
  glow?: boolean;
  className?: string;
}

export function GlassCard({
  children,
  hover = 'lift',
  glow = false,
  className,
  ...props
}: GlassCardProps) {
  const hoverVariant = hover === 'lift' ? cardHover : hover === 'subtle' ? cardHoverSubtle : undefined;

  return (
    <motion.div
      variants={hoverVariant}
      initial="rest"
      whileHover={hover !== 'none' ? 'hover' : undefined}
      whileTap={hover !== 'none' ? 'tap' : undefined}
      className={cn(
        'glass-card rounded-2xl p-6',
        glow && 'pulse-glow',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}
