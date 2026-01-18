/**
 * Gradient Orbs Background
 * 
 * Decorative floating gradient orbs for visual depth.
 */

import { motion } from 'framer-motion';

interface GradientOrbsProps {
  variant?: 'default' | 'hero' | 'subtle';
}

export function GradientOrbs({ variant = 'default' }: GradientOrbsProps) {
  const orbConfigs = {
    default: [
      { size: 400, x: '10%', y: '20%', color: 'from-primary/20 to-primary/5', delay: 0 },
      { size: 300, x: '70%', y: '60%', color: 'from-accent/20 to-accent/5', delay: 2 },
      { size: 250, x: '80%', y: '10%', color: 'from-primary/15 to-transparent', delay: 4 },
    ],
    hero: [
      { size: 600, x: '5%', y: '10%', color: 'from-primary/25 to-primary/5', delay: 0 },
      { size: 500, x: '60%', y: '50%', color: 'from-accent/25 to-accent/5', delay: 1 },
      { size: 400, x: '85%', y: '5%', color: 'from-primary/20 to-transparent', delay: 2 },
      { size: 300, x: '20%', y: '70%', color: 'from-accent/15 to-transparent', delay: 3 },
    ],
    subtle: [
      { size: 300, x: '15%', y: '30%', color: 'from-primary/10 to-transparent', delay: 0 },
      { size: 250, x: '75%', y: '50%', color: 'from-accent/10 to-transparent', delay: 2 },
    ],
  };

  const orbs = orbConfigs[variant];

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      {orbs.map((orb, index) => (
        <motion.div
          key={index}
          className={`absolute rounded-full bg-gradient-radial ${orb.color} blur-3xl`}
          style={{
            width: orb.size,
            height: orb.size,
            left: orb.x,
            top: orb.y,
          }}
          animate={{
            x: [0, 30, -20, 0],
            y: [0, -20, 30, 0],
            scale: [1, 1.1, 0.95, 1],
          }}
          transition={{
            duration: 20 + index * 2,
            repeat: Infinity,
            delay: orb.delay,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}
