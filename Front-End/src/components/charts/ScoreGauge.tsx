/**
 * Score Gauge Component
 * 
 * Animated circular gauge for displaying scores.
 */

import { useEffect, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';

interface ScoreGaugeProps {
  value: number;
  maxValue?: number;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'success' | 'warning' | 'destructive' | 'accent';
  showValue?: boolean;
  delay?: number;
}

const sizeConfig = {
  sm: { size: 100, strokeWidth: 8, fontSize: 'text-xl' },
  md: { size: 140, strokeWidth: 10, fontSize: 'text-2xl' },
  lg: { size: 180, strokeWidth: 12, fontSize: 'text-3xl' },
};

const colorConfig = {
  primary: 'stroke-primary',
  success: 'stroke-success',
  warning: 'stroke-warning',
  destructive: 'stroke-destructive',
  accent: 'stroke-accent',
};

export function ScoreGauge({
  value,
  maxValue = 100,
  label,
  size = 'md',
  color = 'primary',
  showValue = true,
  delay = 0,
}: ScoreGaugeProps) {
  const [isInView, setIsInView] = useState(false);
  const config = sizeConfig[size];
  
  const normalizedValue = Math.min(Math.max(value / maxValue, 0), 1);
  const circumference = 2 * Math.PI * ((config.size - config.strokeWidth) / 2);
  
  const springValue = useSpring(0, {
    stiffness: 50,
    damping: 20,
  });

  const strokeDashoffset = useTransform(
    springValue,
    [0, 1],
    [circumference, circumference * (1 - normalizedValue)]
  );

  const displayValue = useTransform(springValue, (v) => 
    Math.round(v * value)
  );

  useEffect(() => {
    if (isInView) {
      const timer = setTimeout(() => {
        springValue.set(1);
      }, delay * 1000);
      return () => clearTimeout(timer);
    }
  }, [isInView, springValue, delay]);

  // Determine color based on score
  const getScoreColor = () => {
    if (color !== 'primary') return colorConfig[color];
    const percentage = normalizedValue * 100;
    if (percentage >= 80) return 'stroke-success';
    if (percentage >= 60) return 'stroke-primary';
    if (percentage >= 40) return 'stroke-warning';
    return 'stroke-destructive';
  };

  return (
    <motion.div
      className="flex flex-col items-center"
      onViewportEnter={() => setIsInView(true)}
      viewport={{ once: true, margin: '-50px' }}
    >
      <div className="relative" style={{ width: config.size, height: config.size }}>
        {/* Background Circle */}
        <svg
          className="transform -rotate-90"
          width={config.size}
          height={config.size}
        >
          <circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={(config.size - config.strokeWidth) / 2}
            fill="none"
            className="stroke-muted"
            strokeWidth={config.strokeWidth}
          />
          
          {/* Animated Progress Circle */}
          <motion.circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={(config.size - config.strokeWidth) / 2}
            fill="none"
            className={getScoreColor()}
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            style={{ strokeDashoffset }}
          />
        </svg>

        {/* Value Display */}
        {showValue && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.span className={`font-bold ${config.fontSize}`}>
              {displayValue}
            </motion.span>
            {maxValue > 100 && (
              <span className="text-xs text-muted-foreground">/ {maxValue}</span>
            )}
          </div>
        )}

        {/* Glow Effect */}
        <motion.div
          className="absolute inset-0 rounded-full"
          animate={isInView ? {
            boxShadow: [
              '0 0 0 0 rgba(62, 190, 201, 0)',
              '0 0 20px 0 rgba(62, 190, 201, 0.3)',
              '0 0 0 0 rgba(62, 190, 201, 0)',
            ],
          } : {}}
          transition={{ duration: 2, delay: delay + 1, repeat: 2 }}
        />
      </div>

      {/* Label */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ delay: delay + 0.3 }}
        className="mt-3 text-sm font-medium text-muted-foreground text-center"
      >
        {label}
      </motion.p>
    </motion.div>
  );
}
