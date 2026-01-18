/**
 * Evaluation Page
 * 
 * Multi-step wizard for business evaluation.
 */

import { AnimatePresence, motion } from 'framer-motion';
import { PageTransition } from '@/components/layout/PageTransition';
import { Header } from '@/components/layout/Header';
import { GradientOrbs } from '@/components/layout/GradientOrbs';
import { StepIndicator } from '@/components/wizard/StepIndicator';
import { BusinessProfileStep } from '@/components/wizard/BusinessProfileStep';
import { LocationStep } from '@/components/wizard/LocationStep';
import { BankDataStep } from '@/components/wizard/BankDataStep';
import { RunEvaluationStep } from '@/components/wizard/RunEvaluationStep';
import { ResultsPanel } from '@/components/results/ResultsPanel';
import { useEvaluationState } from '@/hooks/useEvaluationState';
import { wizardStepVariants } from '@/lib/animations';
import type { LocationDetails } from '@/types';

const steps = [
  { id: 0, title: 'Business Profile', description: 'Tell us about your business' },
  { id: 1, title: 'Location', description: 'Verify your location' },
  { id: 2, title: 'Bank Data', description: 'Connect financial data' },
  { id: 3, title: 'Evaluation', description: 'Run AI analysis' },
  { id: 4, title: 'Results', description: 'View your results' },
];

export default function Evaluation() {
  const {
    state,
    setStep,
    nextStep,
    prevStep,
    setBusinessProfile,
    setBankDataMode,
    setSelectedScenario,
    startEvaluation,
    setEvaluationProgress,
    addLog,
    setResult,
    reset,
  } = useEvaluationState();

  const handleBusinessProfileSubmit = (profile: typeof state.businessProfile) => {
    setBusinessProfile(profile);
    nextStep();
  };

  const handleLocationSubmit = (location: LocationDetails) => {
    setBusinessProfile({ ...state.businessProfile, selectedLocation: location });
    nextStep();
  };

  const renderStep = () => {
    // Show results if we have them
    if (state.result) {
      return (
        <motion.div
          key="results"
          variants={wizardStepVariants}
          initial="enter"
          animate="center"
          exit="exit"
          custom={1}
        >
          <ResultsPanel result={state.result} onReset={reset} />
        </motion.div>
      );
    }

    switch (state.step) {
      case 0:
        return (
          <motion.div
            key="step-0"
            variants={wizardStepVariants}
            initial="enter"
            animate="center"
            exit="exit"
            custom={1}
          >
            <BusinessProfileStep
              initialData={state.businessProfile}
              onSubmit={handleBusinessProfileSubmit}
            />
          </motion.div>
        );

      case 1:
        return (
          <motion.div
            key="step-1"
            variants={wizardStepVariants}
            initial="enter"
            animate="center"
            exit="exit"
            custom={1}
          >
            <LocationStep
              initialLocation={state.businessProfile.selectedLocation}
              onSubmit={handleLocationSubmit}
              onBack={prevStep}
            />
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            key="step-2"
            variants={wizardStepVariants}
            initial="enter"
            animate="center"
            exit="exit"
            custom={1}
          >
            <BankDataStep
              onNext={nextStep}
              onBack={prevStep}
            />
          </motion.div>
        );

      case 3:
      case 4:
        return (
          <motion.div
            key="step-3"
            variants={wizardStepVariants}
            initial="enter"
            animate="center"
            exit="exit"
            custom={1}
          >
            <RunEvaluationStep
              businessProfile={state.businessProfile}
              scenario={state.selectedScenario}
              isEvaluating={state.isEvaluating}
              progress={state.evaluationProgress}
              activeAgent={state.activeAgent}
              logs={state.logs}
              onStart={startEvaluation}
              onProgress={setEvaluationProgress}
              onAddLog={addLog}
              onComplete={(result) => {
                setResult(result);
                setStep(4);
              }}
              onBack={prevStep}
            />
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <PageTransition>
      <GradientOrbs variant="subtle" />
      <Header />
      
      <main className="min-h-screen pt-28 pb-12 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Step Indicator */}
          {!state.result && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-12"
            >
              <StepIndicator
                steps={steps}
                currentStep={state.step}
                onStepClick={(step) => {
                  if (step < state.step) {
                    setStep(step);
                  }
                }}
              />
            </motion.div>
          )}

          {/* Step Content */}
          <AnimatePresence mode="wait">
            {renderStep()}
          </AnimatePresence>
        </div>
      </main>
    </PageTransition>
  );
}
