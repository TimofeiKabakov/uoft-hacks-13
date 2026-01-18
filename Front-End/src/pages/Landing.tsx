/**
 * Landing Page
 */

import { PageTransition } from '@/components/layout/PageTransition';
import { Header } from '@/components/layout/Header';
import { GradientOrbs } from '@/components/layout/GradientOrbs';
import { HeroSection } from '@/components/landing/HeroSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';

export default function Landing() {
  return (
    <PageTransition>
      <GradientOrbs variant="hero" />
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
      </main>
    </PageTransition>
  );
}
