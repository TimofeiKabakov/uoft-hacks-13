/**
 * How It Works Page
 * 
 * Scroll-based storytelling page for Coverage Spark
 */

import { PageTransition } from '@/components/layout/PageTransition';
import { Header } from '@/components/layout/Header';
import { HeroSection } from '@/components/how-it-works/HeroSection';
import { SecureSnapshotSection } from '@/components/how-it-works/SecureSnapshotSection';
import { MultiAgentSection } from '@/components/how-it-works/MultiAgentSection';
import { EligibilitySection } from '@/components/how-it-works/EligibilitySection';
import { ImprovementSection } from '@/components/how-it-works/ImprovementSection';
import { SecuritySection } from '@/components/how-it-works/SecuritySection';
import { TrustSummarySection } from '@/components/how-it-works/TrustSummarySection';
import { FinalCTASection } from '@/components/how-it-works/FinalCTASection';

export default function HowItWorks() {
  return (
    <PageTransition>
      <Header />
      <main className="overflow-x-hidden">
        <HeroSection />
        <SecureSnapshotSection />
        <MultiAgentSection />
        <EligibilitySection />
        <ImprovementSection />
        <SecuritySection />
        <TrustSummarySection />
        <FinalCTASection />
      </main>
    </PageTransition>
  );
}
