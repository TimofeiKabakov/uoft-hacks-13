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
import { LoanAmountStep } from '@/components/wizard/LoanAmountStep';
import { BankDataStep } from '@/components/wizard/BankDataStep';
import { RunEvaluationStep } from '@/components/wizard/RunEvaluationStep';
import { ResultsPanel } from '@/components/results/ResultsPanel';
import { useEvaluationState } from '@/hooks/useEvaluationState';
import { wizardStepVariants } from '@/lib/animations';
import type { LocationDetails } from '@/types';
import { api } from '@/api/client';
import { useState } from 'react';

const steps = [
  { id: 0, title: 'Business Profile', description: 'Tell us about your business' },
  { id: 1, title: 'Location', description: 'Verify your location' },
  { id: 2, title: 'Loan Amount', description: 'Specify loan amount' },
  { id: 3, title: 'Bank Data', description: 'Connect financial data' },
  { id: 4, title: 'Evaluation', description: 'Run AI analysis' },
  { id: 5, title: 'Results', description: 'View your results' },
];

export default function Evaluation() {
  const {
    state,
    setStep,
    nextStep,
    prevStep,
    setBusinessProfile,
    setLoanAmount,
    setBankDataMode,
    setSelectedScenario,
    startEvaluation,
    setEvaluationProgress,
    addLog,
    setResult,
    setApplicationId,
    reset,
  } = useEvaluationState();

  const [isCreatingApplication, setIsCreatingApplication] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleBusinessProfileSubmit = async (profile: typeof state.businessProfile) => {
    setBusinessProfile(profile);
    setError(null);
    // Defer application creation until we have a location (next step)
    nextStep();
  };

  const handleLocationSubmit = async (location: LocationDetails) => {
    setBusinessProfile({ ...state.businessProfile, selectedLocation: location });
    setError(null);
    // Move to loan amount step
    nextStep();
  };

  const handleLoanAmountSubmit = async (amount: number) => {
    setLoanAmount(amount);

    // If we already have an applicationId, just move to next step
    if (state.applicationId) {
      nextStep();
      return;
    }

    const location = state.businessProfile.selectedLocation;

    // Ensure we have coordinates before creating the application
    if (!location?.coordinates?.lat || !location?.coordinates?.lng) {
      setError('Missing location data. Please go back and select a location.');
      return;
    }

    // Create application in backend
    setIsCreatingApplication(true);
    setError(null);

    try {
      const profile = state.businessProfile;
      const safeAge = Math.min(Math.max(profile.yearsInOperation || 30, 18), 100);

      const response = await api.createApplication({
        job: profile.businessName || profile.businessType || 'Business Owner',
        age: safeAge,
        location: {
          lat: location.coordinates.lat,
          lng: location.coordinates.lng,
          address: location.formattedAddress || location.city || 'Unknown address',
        },
        loan_amount: amount,
        loan_purpose: profile.businessType
          ? `Working capital for ${profile.businessType}`
          : 'Working capital',
      });

      if (response.success && response.data) {
        const appId = response.data.application_id;
        setApplicationId(appId);
        // Store in localStorage so dashboard can access it
        localStorage.setItem('lastApplicationId', appId);
        nextStep();
      } else {
        setError(response.error?.message || 'Failed to create application. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred while creating the application.');
      console.error('Error creating application:', err);
    } finally {
      setIsCreatingApplication(false);
    }
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
            <LoanAmountStep
              initialAmount={state.loanAmount}
              onSubmit={handleLoanAmountSubmit}
              onBack={prevStep}
            />
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            key="step-3"
            variants={wizardStepVariants}
            initial="enter"
            animate="center"
            exit="exit"
            custom={1}
          >
            <BankDataStep
              applicationId={state.applicationId}
              onNext={nextStep}
              onBack={prevStep}
            />
          </motion.div>
        );

      case 4:
      case 5:
        return (
          <motion.div
            key="step-4"
            variants={wizardStepVariants}
            initial="enter"
            animate="center"
            exit="exit"
            custom={1}
          >
            <RunEvaluationStep
              applicationId={state.applicationId}
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
                setStep(5);
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
          {error && (
            <div className="mb-6 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

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
