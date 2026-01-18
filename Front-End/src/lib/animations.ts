/**
 * Shared Framer Motion animation variants and presets
 */

// Container that staggers child animations
export const staggerContainer = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.05,
    },
  },
};

// Fade up for cards/sections
export const fadeInUp = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: 'easeOut' },
  },
};

// Fade down from top (for nav/header)
export const fadeInDown = {
  hidden: { opacity: 0, y: -14 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Page-level transitions for route changes
export const pageVariants = {
  initial: { opacity: 0, y: 12 },
  enter: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

// Step transitions for the evaluation wizard
export const wizardStepVariants = {
  initial: { opacity: 0, x: 20 },
  enter: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.25, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    x: -15,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

// Gentle scale-in for metric tiles
export const scaleIn = {
  hidden: { opacity: 0, scale: 0.95 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Springy scale-in for icons/badges
export const scaleInBounce = {
  hidden: { opacity: 0, scale: 0.9 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { type: 'spring', stiffness: 260, damping: 18 },
  },
};

// Button hover/tap micro-interaction
export const buttonHover = {
  whileHover: { scale: 1.02, boxShadow: '0 12px 30px rgba(0,0,0,0.12)' },
  whileTap: { scale: 0.98 },
};

// Card hover effects
export const cardHover = {
  whileHover: { y: -4, scale: 1.01, boxShadow: '0 18px 35px rgba(0,0,0,0.12)' },
  whileTap: { scale: 0.995 },
};

export const cardHoverSubtle = {
  whileHover: { y: -2, scale: 1.005, boxShadow: '0 12px 24px rgba(0,0,0,0.08)' },
};

// Soft glow pulse for primary buttons
export const buttonGlow = {
  initial: { boxShadow: '0 0 0 rgba(0,0,0,0)' },
  animate: {
    boxShadow: [
      '0 0 0 rgba(0,0,0,0)',
      '0 0 18px rgba(59,130,246,0.45)',
      '0 0 0 rgba(0,0,0,0)',
    ],
    transition: { repeat: Infinity, duration: 2.4, ease: 'easeInOut' },
  },
};

// Modal overlay and content transitions
export const modalOverlayVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1 },
};

export const modalContentVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  show: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};
