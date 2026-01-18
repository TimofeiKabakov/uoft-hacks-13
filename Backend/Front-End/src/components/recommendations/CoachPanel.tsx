/**
 * Coach Panel Component
 * Structured coach guidance with predefined questions.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, ChevronRight, Info, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { fadeInUp } from '@/lib/animations';

const COACH_QUESTIONS = [
  { id: 'q1', question: "What should I focus on first?", response: { summary: "Start with eliminating overdrafts - this has the highest impact on your score.", steps: ["Set up low balance alerts at $500", "Review upcoming bills for the next 7 days", "Transfer buffer funds if needed"], expectedImpact: "+10-15 points in 90 days", cautions: "Requires consistent monitoring" }},
  { id: 'q2', question: "What's hurting my score the most?", response: { summary: "Recent NSF fees and high subscription costs are your main detractors.", steps: ["Address the 2 NSF events from January", "Cancel unused Adobe subscription", "Review Salesforce seat count"], expectedImpact: "Removing these could add +15-20 points", cautions: undefined }},
  { id: 'q3', question: "How can I improve fastest?", response: { summary: "Quick wins: Cancel unused subscriptions and set up auto-pay.", steps: ["Cancel Adobe Creative Cloud (10 min)", "Enable auto-pay for rent (15 min)", "Set up balance alerts (5 min)"], expectedImpact: "+8-12 points in 30 days", cautions: undefined }},
  { id: 'q4', question: "What can I fix this week?", response: { summary: "This week, focus on the 3 easy actions that take under 30 minutes total.", steps: ["Cancel Adobe subscription", "Set up low balance alert", "Enable auto-pay for one bill"], expectedImpact: "Immediate risk reduction", cautions: undefined }},
];

export function CoachPanel() {
  const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null);
  const response = COACH_QUESTIONS.find(q => q.id === selectedQuestion)?.response;

  return (
    <GlassCard className="p-5">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 rounded-lg bg-primary/10">
          <MessageCircle className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-semibold text-foreground">Coach Guidance</h3>
          <p className="text-xs text-muted-foreground">Ask a question to get personalized advice</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {COACH_QUESTIONS.map((q) => (
          <Button
            key={q.id}
            variant={selectedQuestion === q.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedQuestion(selectedQuestion === q.id ? null : q.id)}
            className="text-xs"
          >
            {q.question}
          </Button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {response && (
          <motion.div
            key={selectedQuestion}
            variants={fadeInUp}
            initial="hidden"
            animate="show"
            exit={{ opacity: 0, y: -10 }}
            className="space-y-3"
          >
            <div className="p-3 bg-primary/5 rounded-lg border border-primary/10">
              <p className="font-medium text-foreground">{response.summary}</p>
            </div>
            <div className="space-y-2">
              {response.steps.map((step, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <ChevronRight className="w-4 h-4 text-primary mt-0.5" />
                  <span className="text-muted-foreground">{step}</span>
                </div>
              ))}
            </div>
            <p className="text-sm text-success font-medium">{response.expectedImpact}</p>
            {response.cautions && (
              <p className="text-xs text-warning flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {response.cautions}
              </p>
            )}
            <p className="text-xs text-muted-foreground flex items-center gap-1 pt-2 border-t border-border">
              <Info className="w-3 h-3" />
              Coach responses are generated from your data.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </GlassCard>
  );
}
