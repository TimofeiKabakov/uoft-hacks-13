/**
 * Evidence Drawer Component
 * 
 * Shows the signals and evidence behind a recommendation.
 */

import { motion, AnimatePresence } from 'framer-motion';
import { X, FileText, TrendingUp, DollarSign, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { Badge } from '@/components/ui/badge';
import { modalOverlayVariants, modalContentVariants, staggerContainer, fadeInUp } from '@/lib/animations';
import type { Recommendation, EvidenceItem } from '@/types/recommendations';

interface EvidenceDrawerProps {
  recommendation: Recommendation | null;
  isOpen: boolean;
  onClose: () => void;
}

const evidenceTypeConfig: Record<EvidenceItem['type'], { 
  icon: typeof FileText; 
  label: string;
  className: string;
}> = {
  transaction: { 
    icon: DollarSign, 
    label: 'Transaction',
    className: 'bg-chart-1/10 text-chart-1'
  },
  pattern: { 
    icon: TrendingUp, 
    label: 'Pattern',
    className: 'bg-chart-2/10 text-chart-2'
  },
  stat: { 
    icon: FileText, 
    label: 'Summary',
    className: 'bg-chart-3/10 text-chart-3'
  },
};

export function EvidenceDrawer({ recommendation, isOpen, onClose }: EvidenceDrawerProps) {
  if (!recommendation) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            variants={modalOverlayVariants}
            initial="hidden"
            animate="show"
            exit="exit"
            className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          
          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full max-w-lg bg-card border-l border-border shadow-2xl z-50 overflow-y-auto"
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1 pr-4">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                    Evidence for
                  </p>
                  <h2 className="text-xl font-bold text-foreground">
                    {recommendation.title}
                  </h2>
                </div>
                <Button variant="ghost" size="icon" onClick={onClose}>
                  <X className="w-5 h-5" />
                </Button>
              </div>

              {/* Transparency Notice */}
              <motion.div
                variants={fadeInUp}
                initial="hidden"
                animate="show"
                className="mb-6"
              >
                <GlassCard className="p-4 bg-primary/5 border-primary/20">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        How we analyze your data
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        We summarize patterns from your financial data — we don't expose all raw transactions. 
                        Only aggregated insights are used for recommendations.
                      </p>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>

              {/* Evidence Items */}
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="show"
                className="space-y-4"
              >
                <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Supporting Evidence ({recommendation.evidence.length} items)
                </p>
                
                {recommendation.evidence.map((item, index) => {
                  const config = evidenceTypeConfig[item.type];
                  const Icon = config.icon;
                  
                  return (
                    <motion.div
                      key={item.id}
                      variants={fadeInUp}
                      custom={index}
                    >
                      <GlassCard className="p-4">
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${config.className}`}>
                            <Icon className="w-4 h-4" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant="secondary" className="text-xs">
                                {config.label}
                              </Badge>
                              {item.category && (
                                <Badge variant="outline" className="text-xs">
                                  {item.category}
                                </Badge>
                              )}
                            </div>
                            
                            {item.merchant && (
                              <p className="font-medium text-foreground">
                                {item.merchant}
                              </p>
                            )}
                            
                            <p className="text-sm text-muted-foreground">
                              {item.description}
                            </p>
                            
                            {(item.date || item.amount) && (
                              <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                                {item.date && <span>{item.date}</span>}
                                {item.amount && (
                                  <span className={item.amount < 0 ? 'text-destructive' : 'text-success'}>
                                    {item.amount < 0 ? '-' : '+'}${Math.abs(item.amount).toFixed(2)}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </GlassCard>
                    </motion.div>
                  );
                })}
              </motion.div>

              {/* Summary */}
              <motion.div
                variants={fadeInUp}
                initial="hidden"
                animate="show"
                transition={{ delay: 0.3 }}
                className="mt-6 pt-6 border-t border-border"
              >
                <h3 className="font-semibold text-foreground mb-2">
                  Why this matters
                </h3>
                <p className="text-sm text-muted-foreground">
                  {recommendation.whyItMatters}
                </p>
                
                <div className="mt-4 p-3 bg-success/5 rounded-lg border border-success/20">
                  <p className="text-sm text-success font-medium">
                    Expected Impact: {recommendation.expectedImpact}
                  </p>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
