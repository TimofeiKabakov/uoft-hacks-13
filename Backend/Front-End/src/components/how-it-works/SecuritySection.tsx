/**
 * Secure Final Actions Section
 * 
 * Step 5: Identity-grade security for high-value actions
 */

import { motion, useReducedMotion } from 'framer-motion';
import { Fingerprint, ShieldCheck, CheckCircle2, Lock, KeyRound } from 'lucide-react';
import { ScrollSection } from './ScrollSection';
import { SectionHeader } from './SectionHeader';
import { GlassCard } from '@/components/ui/GlassCard';

export function SecuritySection() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <ScrollSection className="py-32 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeader
          step={5}
          title="High-value actions require identity-grade security"
          subtitle="When it matters most, we use the most secure authentication available — no passwords, no SMS codes."
          icon={KeyRound}
        />

        <div className="grid md:grid-cols-2 gap-8 items-center">
          {/* Visual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="flex justify-center"
          >
            <div className="relative">
              {/* Animated Rings */}
              {!shouldReduceMotion && (
                <>
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-primary/30"
                    style={{ width: 280, height: 280, left: -20, top: -20 }}
                    animate={{
                      scale: [1, 1.1, 1],
                      opacity: [0.3, 0.6, 0.3],
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-accent/20"
                    style={{ width: 320, height: 320, left: -40, top: -40 }}
                    animate={{
                      scale: [1, 1.15, 1],
                      opacity: [0.2, 0.4, 0.2],
                    }}
                    transition={{ duration: 4, repeat: Infinity, delay: 0.5 }}
                  />
                </>
              )}
              
              {/* Main Card */}
              <GlassCard hover="none" className="w-60 p-8 relative z-10">
                <motion.div
                  className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-accent mx-auto mb-6 flex items-center justify-center"
                  animate={shouldReduceMotion ? {} : {
                    boxShadow: [
                      '0 0 0 0 rgba(62, 190, 201, 0)',
                      '0 0 30px 10px rgba(62, 190, 201, 0.3)',
                      '0 0 0 0 rgba(62, 190, 201, 0)',
                    ],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Fingerprint className="w-10 h-10 text-white" />
                </motion.div>

                {/* State Transition */}
                <motion.div
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.8 }}
                  className="text-center"
                >
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 1, type: 'spring' }}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success text-success-foreground text-sm font-medium"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Signed & Verified
                  </motion.div>
                </motion.div>
              </GlassCard>
            </div>
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            <div className="space-y-4">
              <SecurityFeature
                icon={Fingerprint}
                title="Passkey authentication"
                description="Use your device's biometrics (Face ID, fingerprint, or security key) to confirm important actions like finalizing applications."
                delay={0.5}
              />
              
              <SecurityFeature
                icon={Lock}
                title="No passwords to steal"
                description="Passkeys are cryptographically bound to your device — they can't be phished, leaked, or stolen from a database."
                delay={0.6}
              />
              
              <SecurityFeature
                icon={ShieldCheck}
                title="Works with your existing setup"
                description="Compatible with 1Password, Apple Keychain, Google Password Manager, and hardware security keys."
                delay={0.7}
              />
            </div>

            {/* Trust Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.8 }}
              className="p-4 rounded-xl bg-primary/10 border border-primary/20"
            >
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Trust-first design:</span> High-value actions 
                like finalizing loan applications or updating business details require the same security standard 
                used by major banks and financial institutions.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </ScrollSection>
  );
}

interface SecurityFeatureProps {
  icon: React.ElementType;
  title: string;
  description: string;
  delay: number;
}

function SecurityFeature({ icon: Icon, title, description, delay }: SecurityFeatureProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="flex gap-4"
    >
      <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-accent" />
      </div>
      <div>
        <h3 className="font-semibold mb-1">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}
