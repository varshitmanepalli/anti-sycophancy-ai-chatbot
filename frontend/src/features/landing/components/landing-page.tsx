import { CtaSection } from "./cta-section";
import { ComparisonSection } from "./comparison-section";
import { FaqSection } from "./faq-section";
import { FeaturesSection } from "./features-section";
import { FooterSection } from "./footer-section";
import { HeroSection } from "./hero-section";
import { HowItWorksSection } from "./how-it-works-section";
import { LandingNav } from "./landing-nav";

/** Full marketing landing page composition. */
export function LandingPage() {
  return (
    <div className="min-h-screen bg-background pb-safe">
      <LandingNav />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <ComparisonSection />
        <FaqSection />
        <CtaSection />
      </main>
      <FooterSection />
    </div>
  );
}
