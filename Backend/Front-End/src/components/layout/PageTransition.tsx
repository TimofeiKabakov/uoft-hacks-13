/**
 * Page Transition Wrapper
 * 
 * Wraps page content with animated transitions.
 */

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { pageVariants } from '@/lib/animations';

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

export function PageTransition({ children, className = '' }: PageTransitionProps) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      className={className}
    >
      {children}
    </motion.div>
  );
}
