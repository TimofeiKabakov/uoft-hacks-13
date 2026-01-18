/**
 * Feature Card Component
 * 
 * Animated card for displaying agent features on the landing page.
 */

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { fadeInUp } from '@/lib/animations';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  color: 'primary' | 'accent' | 'success';
  delay?: number;
}

const colorClasses = {
  primary: {
    bg: 'bg-primary/10',
    icon: 'text-primary',
    border: 'border-primary/20',
    glow: 'group-hover:shadow-[0_0_30px_rgba(62,190,201,0.3)]',
  },
  accent: {
    bg: 'bg-accent/10',
    icon: 'text-accent',
    border: 'border-accent/20',
    glow: 'group-hover:shadow-[0_0_30px_rgba(94,39,80,0.3)]',
  },
  success: {
    bg: 'bg-success/10',
    icon: 'text-success',
    border: 'border-success/20',
    glow: 'group-hover:shadow-[0_0_30px_rgba(34,197,94,0.3)]',
  },
};

export function FeatureCard({ icon: Icon, title, description, color, delay = 0 }: FeatureCardProps) {
  const colors = colorClasses[color];

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-50px' }}
      transition={{ delay }}
      className="group"
    >
      <GlassCard 
        hover="lift"
        className={`h-full transition-shadow duration-500 ${colors.glow}`}
      >
        {/* Icon */}
        <motion.div
          className={`w-14 h-14 rounded-2xl ${colors.bg} ${colors.border} border flex items-center justify-center mb-5`}
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <Icon className={`w-7 h-7 ${colors.icon}`} />
        </motion.div>

        {/* Content */}
        <h3 className="text-xl font-semibold mb-3">{title}</h3>
        <p className="text-muted-foreground leading-relaxed">{description}</p>

        {/* Decorative gradient line */}
        <motion.div
          className={`h-1 rounded-full mt-6 ${colors.bg}`}
          initial={{ scaleX: 0, originX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true }}
          transition={{ delay: delay + 0.3, duration: 0.8, ease: 'easeOut' }}
        />
      </GlassCard>
    </motion.div>
  );
}
