"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Navigation";
import { Hero } from "@/components/Hero";
import { UseCases } from "@/components/UseCases";
import { DecisionNarrative } from "@/components/DecisionNarrative";
import { ConnectedEcosystem } from "@/components/ConnectedEcosystem";
import { IntelligenceVoyage } from "@/components/IntelligenceVoyage";
import { EvidenceExploration } from "@/components/EvidenceExploration";
import { ScenarioReplay } from "@/components/ScenarioReplay";
import { MapExploration } from "@/components/MapExploration";
import { OceanRoadmap } from "@/components/OceanRoadmap";
import { CommunityImpact } from "@/components/CommunityImpact";
import { FaqSection } from "@/components/FaqSection";
import { ClosingCta } from "@/components/ClosingCta";
import { Footer } from "@/components/Footer";
import { IntroAnimation } from "@/components/IntroAnimation";

export default function HomePage() {
  const [showIntro, setShowIntro] = useState(false);

  useEffect(() => {
    // Only play intro on fresh session entry and if user does not prefer reduced motion
    const hasSeenIntro = sessionStorage.getItem("sagarvani_intro_seen");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!hasSeenIntro && !prefersReducedMotion) {
      // Defer state update slightly to prevent synchronous cascading render error in React 19 / Next.js
      const timer = setTimeout(() => {
        setShowIntro(true);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleIntroComplete = () => {
    sessionStorage.setItem("sagarvani_intro_seen", "true");
    setShowIntro(false);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-warm-ivory)] selection:bg-[var(--color-icy-blue)] selection:text-[var(--color-charcoal-blue)]">
      {/* Intro Animation Overlay */}
      {showIntro && <IntroAnimation onComplete={handleIntroComplete} />}

      {/* Main Page Header */}
      <Header />
      
      <main id="home" className="flex-1 focus:outline-none" tabIndex={-1}>
        {/* Section 1: Hero */}
        <Hero />

        {/* Section 2: Who Sagarvani serves / Use Cases */}
        <UseCases />

        {/* Section 3: Before → Sagarvani → Outcome */}
        <DecisionNarrative />

        {/* Section 4: Connected Ocean Ecosystem */}
        <ConnectedEcosystem />

        {/* Section 5: Sagarvani Intelligence Voyage */}
        <IntelligenceVoyage />

        {/* Section 6: Evidence & Exploration */}
        <EvidenceExploration />

        {/* Section 7: Scenario Replay Presentation */}
        <ScenarioReplay />

        {/* Section 8: Maps, Marine Exploration & Insights */}
        <MapExploration />

        {/* Section 9: Sagarvani Ocean Roadmap */}
        <OceanRoadmap />

        {/* Section 10: Origin Story & Coastal Community Relevance */}
        <CommunityImpact />

        {/* Section 11: Frequently Asked Questions */}
        <FaqSection />

        {/* Section 12: Closing Call to Action */}
        <ClosingCta />
      </main>

      {/* Editorial Ocean Footer */}
      <Footer />
    </div>
  );
}
