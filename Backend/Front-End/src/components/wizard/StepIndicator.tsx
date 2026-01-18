/**
 * Step Indicator Component
 * 
 * Shows the current wizard step with animated progress.
 */

import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Step {
  id: number;
  title: string;
  description: string;
}

interface StepIndicatorProps {
  steps: Step[];
  currentStep: number;
  onStepClick?: (step: number) => void;
}

export function StepIndicator({ steps, currentStep, onStepClick }: StepIndicatorProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between relative">
        {/* Progress Line Background */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" />
        
        {/* Animated Progress Line */}
        <motion.div
          className="absolute top-5 left-0 h-0.5 bg-primary"
          initial={{ width: '0%' }}
          animate={{ 
            width: `${(currentStep / (steps.length - 1)) * 100}%` 
          }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
        />

        {steps.map((step, index) => {
          const isCompleted = index < currentStep;
          const isCurrent = index === currentStep;
          const isClickable = onStepClick && index <= currentStep;

          return (
            <motion.div
              key={step.id}
              className={cn(
                'relative z-10 flex flex-col items-center',
                isClickable && 'cursor-pointer'
              )}
              onClick={() => isClickable && onStepClick(index)}
              whileHover={isClickable ? { scale: 1.05 } : undefined}
              whileTap={isClickable ? { scale: 0.95 } : undefined}
            >
              {/* Step Circle */}
              <motion.div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold border-2 transition-colors',
                  isCompleted && 'bg-primary border-primary text-primary-foreground',
                  isCurrent && 'bg-background border-primary text-primary',
                  !isCompleted && !isCurrent && 'bg-background border-border text-muted-foreground'
                )}
                animate={isCurrent ? {
                  boxShadow: [
                    '0 0 0 0 rgba(62, 190, 201, 0)',
                    '0 0 0 8px rgba(62, 190, 201, 0.2)',
                    '0 0 0 0 rgba(62, 190, 201, 0)',
                  ],
                } : {}}
                transition={{ duration: 2, repeat: isCurrent ? Infinity : 0 }}
              >
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 300 }}
                  >
                    <Check className="w-5 h-5" />
                  </motion.div>
                ) : (
                  <span>{index + 1}</span>
                )}
              </motion.div>

              {/* Step Label */}
              <div className="mt-3 text-center">
                <motion.p
                  className={cn(
                    'text-sm font-medium transition-colors',
                    isCurrent ? 'text-foreground' : 'text-muted-foreground'
                  )}
                  animate={{ opacity: isCurrent ? 1 : 0.7 }}
                >
                  {step.title}
                </motion.p>
                <p className="text-xs text-muted-foreground mt-0.5 hidden md:block">
                  {step.description}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
