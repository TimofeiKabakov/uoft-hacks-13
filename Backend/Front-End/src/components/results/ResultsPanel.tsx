/**
 * Results Panel Component
 * 
 * Displays the complete evaluation results with animated sections.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb, 
  FileText,
  ChevronDown,
  ChevronUp,
  Fingerprint,
  RotateCcw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { ScoreGauge } from '@/components/charts/ScoreGauge';
import { DecisionCard } from './DecisionCard';
import { Confetti } from '@/components/effects/Confetti';
import { staggerContainer, fadeInUp, buttonHover } from '@/lib/animations';
import { FEATURE_FLAGS } from '@/config';
import type { EvaluationResponse } from '@/types';
import { toast } from '@/hooks/use-toast';

interface ResultsPanelProps {
  result: EvaluationResponse;
  onReset: () => void;
}

export function ResultsPanel({ result, onReset }: ResultsPanelProps) {
  const [showConfetti, setShowConfetti] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['scores']));

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const handleCelebrate = () => {
    if (FEATURE_FLAGS.enableCelebrations) {
      setShowConfetti(true);
    }
  };

  const handlePasskeySign = () => {
    if (!FEATURE_FLAGS.enablePasskeys) {
      toast({
        title: 'Passkeys Not Configured',
        description: 'Passkey signing is not enabled in the current configuration.',
        variant: 'destructive',
      });
      return;
    }

    // In a real app, this would trigger WebAuthn
    toast({
      title: 'Passkey Signing',
      description: 'This would trigger WebAuthn authentication in a production environment.',
    });
  };

  // Normalize scores (handle both 0-100 and 0-1000 scales)
  const normalizeScore = (score: number) => score > 100 ? score / 10 : score;
  const maxScore = result.fiscalHealthScore > 100 ? 1000 : 100;

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="max-w-4xl mx-auto space-y-6"
    >
      <Confetti trigger={showConfetti} />

      {/* Decision Card */}
      <motion.div variants={fadeInUp}>
        <DecisionCard 
          decision={result.decision} 
          loanTerms={result.loanTerms}
          onCelebrate={handleCelebrate}
        />
      </motion.div>

      {/* Score Breakdown */}
      <motion.div variants={fadeInUp}>
        <CollapsibleSection
          title="Score Breakdown"
          icon={TrendingUp}
          isExpanded={expandedSections.has('scores')}
          onToggle={() => toggleSection('scores')}
        >
          <div className="grid grid-cols-3 gap-8 py-6">
            <ScoreGauge
              value={result.fiscalHealthScore}
              maxValue={maxScore}
              label="Fiscal Health"
              size="lg"
              delay={0}
            />
            <ScoreGauge
              value={result.communityMultiplier * 100}
              maxValue={200}
              label="Community Multiplier"
              size="lg"
              color="accent"
              delay={0.2}
            />
            <ScoreGauge
              value={result.finalScore}
              maxValue={maxScore}
              label="Final Score"
              size="lg"
              color="success"
              delay={0.4}
            />
          </div>
        </CollapsibleSection>
      </motion.div>

      {/* Account Summaries */}
      {result.accountSummaries && result.accountSummaries.length > 0 && (
        <motion.div variants={fadeInUp}>
          <CollapsibleSection
            title="Account Breakdown"
            icon={FileText}
            isExpanded={expandedSections.has('accounts')}
            onToggle={() => toggleSection('accounts')}
          >
            <div className="divide-y divide-border">
              {result.accountSummaries.map((account, index) => (
                <motion.div
                  key={account.accountId}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="py-4 flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium">{account.name}</p>
                    <p className="text-sm text-muted-foreground capitalize">{account.subtype}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    {account.flags.length > 0 && (
                      <div className="flex gap-1">
                        {account.flags.map((flag, i) => (
                          <span 
                            key={i}
                            className="px-2 py-1 text-xs rounded-full bg-warning/10 text-warning"
                          >
                            {flag}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="text-right">
                      <p className="text-lg font-semibold">{account.score}</p>
                      <p className="text-xs text-muted-foreground">score</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CollapsibleSection>
        </motion.div>
      )}

      {/* Risk Flags */}
      {result.riskFlags && result.riskFlags.length > 0 && (
        <motion.div variants={fadeInUp}>
          <CollapsibleSection
            title="Risk Flags"
            icon={AlertTriangle}
            isExpanded={expandedSections.has('risks')}
            onToggle={() => toggleSection('risks')}
            badge={result.riskFlags.length}
          >
            <div className="space-y-3">
              {result.riskFlags.map((flag, index) => (
                <motion.div
                  key={flag.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-xl border ${
                    flag.severity === 'critical' ? 'bg-destructive/10 border-destructive/30' :
                    flag.severity === 'high' ? 'bg-warning/10 border-warning/30' :
                    flag.severity === 'medium' ? 'bg-primary/10 border-primary/30' :
                    'bg-muted border-border'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <AlertTriangle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                      flag.severity === 'critical' ? 'text-destructive' :
                      flag.severity === 'high' ? 'text-warning' :
                      'text-muted-foreground'
                    }`} />
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium">{flag.title}</p>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          flag.severity === 'critical' ? 'bg-destructive/20 text-destructive' :
                          flag.severity === 'high' ? 'bg-warning/20 text-warning' :
                          flag.severity === 'medium' ? 'bg-primary/20 text-primary' :
                          'bg-muted text-muted-foreground'
                        }`}>
                          {flag.severity}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{flag.description}</p>
                      {flag.recommendation && (
                        <p className="text-sm mt-2 text-primary">{flag.recommendation}</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CollapsibleSection>
        </motion.div>
      )}

      {/* Improvement Plan */}
      {result.improvementPlan && (
        <motion.div variants={fadeInUp}>
          <CollapsibleSection
            title="Recommended Actions"
            icon={Lightbulb}
            isExpanded={expandedSections.has('improvements')}
            onToggle={() => toggleSection('improvements')}
          >
            <div className="space-y-4">
              {result.improvementPlan.priorityActions.map((action, index) => (
                <motion.div
                  key={action.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 rounded-xl bg-success/5 border border-success/20"
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      action.priority === 'high' ? 'bg-primary text-primary-foreground' :
                      action.priority === 'medium' ? 'bg-accent text-accent-foreground' :
                      'bg-muted'
                    }`}>
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{action.title}</p>
                      <p className="text-sm text-muted-foreground mt-1">{action.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs">
                        <span className="text-success">{action.estimatedImpact}</span>
                        {action.timeframe && (
                          <span className="text-muted-foreground">{action.timeframe}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CollapsibleSection>
        </motion.div>
      )}

      {/* Actions */}
      <motion.div variants={fadeInUp} className="flex items-center justify-between pt-6">
        <motion.div variants={buttonHover} initial="rest" whileHover="hover" whileTap="tap">
          <Button variant="outline" onClick={onReset} className="rounded-xl">
            <RotateCcw className="w-4 h-4 mr-2" />
            Start New Evaluation
          </Button>
        </motion.div>

        {result.decision === 'APPROVE' && FEATURE_FLAGS.enablePasskeys && (
          <motion.div variants={buttonHover} initial="rest" whileHover="hover" whileTap="tap">
            <Button onClick={handlePasskeySign} className="rounded-xl px-8">
              <Fingerprint className="w-5 h-5 mr-2" />
              Sign with Passkey
            </Button>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
}

// Collapsible Section Component
interface CollapsibleSectionProps {
  title: string;
  icon: React.ElementType;
  isExpanded: boolean;
  onToggle: () => void;
  badge?: number;
  children: React.ReactNode;
}

function CollapsibleSection({ 
  title, 
  icon: Icon, 
  isExpanded, 
  onToggle, 
  badge,
  children 
}: CollapsibleSectionProps) {
  return (
    <GlassCard hover="none" className="overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full p-6 flex items-center justify-between hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold">{title}</h3>
          {badge !== undefined && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary">
              {badge}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-5 h-5 text-muted-foreground" />
        )}
      </button>
      
      <motion.div
        initial={false}
        animate={{
          height: isExpanded ? 'auto' : 0,
          opacity: isExpanded ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <div className="px-6 pb-6">
          {children}
        </div>
      </motion.div>
    </GlassCard>
  );
}
