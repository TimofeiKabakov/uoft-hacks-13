/**
 * Multi-Agent Intelligence Section
 * 
 * Step 2: Core differentiator - multiple expert systems
 */

import { motion, useReducedMotion } from 'framer-motion';
import { TrendingUp, Heart, Shield, ArrowRight, Zap } from 'lucide-react';
import { ScrollSection } from './ScrollSection';
import { SectionHeader } from './SectionHeader';
import { GlassCard } from '@/components/ui/GlassCard';

const agents = [
  {
    icon: TrendingUp,
    title: 'Fiscal Health Auditor',
    description: 'Evaluates cash flow patterns, revenue stability, and financial resilience over time.',
    color: 'primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary/20',
  },
  {
    icon: Heart,
    title: 'Community Impact Analyst',
    description: 'Considers local business ties and community factors that traditional lenders miss.',
    color: 'accent',
    bgColor: 'bg-accent/10',
    borderColor: 'border-accent/20',
  },
  {
    icon: Shield,
    title: 'Compliance & Fairness Sentry',
    description: 'Ensures unbiased evaluation and regulatory compliance in every lending decision.',
    color: 'success',
    bgColor: 'bg-success/10',
    borderColor: 'border-success/20',
  },
];

export function MultiAgentSection() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <ScrollSection className="py-32 px-6 bg-muted/30">
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          step={2}
          title="Multiple expert systems review your profile"
          subtitle="No single algorithm makes the decision. Our AI agents collaborate to give you a fair, comprehensive evaluation."
          icon={Zap}
        />

        {/* Agent Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {agents.map((agent, index) => (
            <AgentCard 
              key={agent.title} 
              agent={agent} 
              index={index}
              shouldReduceMotion={shouldReduceMotion}
            />
          ))}
        </div>

        {/* Collaboration Visualization */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6 }}
          className="max-w-2xl mx-auto"
        >
          <GlassCard hover="none" className="p-6">
            <div className="flex items-center justify-center gap-4 flex-wrap">
              {agents.map((agent, index) => {
                const Icon = agent.icon;
                return (
                  <div key={agent.title} className="flex items-center">
                    <motion.div
                      className={`w-12 h-12 rounded-xl ${agent.bgColor} flex items-center justify-center`}
                      whileHover={{ scale: 1.1 }}
                      animate={shouldReduceMotion ? {} : {
                        y: [0, -5, 0],
                      }}
                      transition={{ 
                        duration: 2, 
                        repeat: Infinity, 
                        delay: index * 0.3,
                      }}
                    >
                      <Icon className={`w-6 h-6 text-${agent.color}`} />
                    </motion.div>
                    
                    {index < agents.length - 1 && (
                      <div className="flex items-center mx-3">
                        <motion.div
                          className="flex"
                          animate={shouldReduceMotion ? {} : { x: [0, 5, 0] }}
                          transition={{ duration: 1.5, repeat: Infinity, delay: index * 0.2 }}
                        >
                          <ArrowRight className="w-5 h-5 text-muted-foreground" />
                        </motion.div>
                      </div>
                    )}
                  </div>
                );
              })}
              
              <div className="flex items-center ml-4">
                <ArrowRight className="w-5 h-5 text-muted-foreground mr-3" />
                <motion.div
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold"
                  animate={shouldReduceMotion ? {} : {
                    boxShadow: [
                      '0 0 0 0 rgba(62, 190, 201, 0)',
                      '0 0 20px 0 rgba(62, 190, 201, 0.3)',
                      '0 0 0 0 rgba(62, 190, 201, 0)',
                    ],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  Final Decision
                </motion.div>
              </div>
            </div>
            
            <p className="text-center text-sm text-muted-foreground mt-4">
              Collaborative intelligence ensures balanced, fair outcomes
            </p>
          </GlassCard>
        </motion.div>
      </div>
    </ScrollSection>
  );
}

interface AgentCardProps {
  agent: typeof agents[0];
  index: number;
  shouldReduceMotion: boolean | null;
}

function AgentCard({ agent, index, shouldReduceMotion }: AgentCardProps) {
  const Icon = agent.icon;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: 0.2 + index * 0.1 }}
    >
      <motion.div
        whileHover={shouldReduceMotion ? {} : { scale: 1.03, y: -5 }}
        transition={{ type: 'spring', stiffness: 300 }}
      >
        <GlassCard 
          hover="none" 
          className={`p-6 h-full border ${agent.borderColor} transition-shadow hover:shadow-lg`}
        >
          <motion.div
            className={`w-14 h-14 rounded-2xl ${agent.bgColor} flex items-center justify-center mb-5`}
            whileHover={{ rotate: 5 }}
          >
            <Icon className={`w-7 h-7 text-${agent.color}`} />
          </motion.div>
          
          <h3 className="text-lg font-semibold mb-2">{agent.title}</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {agent.description}
          </p>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}
