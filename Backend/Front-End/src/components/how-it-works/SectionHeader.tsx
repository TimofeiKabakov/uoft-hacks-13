/**
 * Section Header Component
 * 
 * Consistent header styling for how-it-works sections.
 */

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface SectionHeaderProps {
  step?: number;
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  centered?: boolean;
}

export function SectionHeader({ 
  step, 
  title, 
  subtitle, 
  icon: Icon,
  centered = true 
}: SectionHeaderProps) {
  return (
    <div className={`mb-12 ${centered ? 'text-center' : ''}`}>
      {step !== undefined && (
        <motion.div
          initial={{ scale: 0 }}
          whileInView={{ scale: 1 }}
          viewport={{ once: true }}
          transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6"
        >
          {Icon && <Icon className="w-4 h-4" />}
          <span>Step {step}</span>
        </motion.div>
      )}
      
      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: 0.15 }}
        className="text-3xl md:text-4xl font-bold tracking-tight mb-4"
      >
        {title}
      </motion.h2>
      
      {subtitle && (
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed"
        >
          {subtitle}
        </motion.p>
      )}
    </div>
  );
}
