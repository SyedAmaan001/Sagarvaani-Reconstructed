"use client";

import React from "react";
import Image from "next/image";
import { HeartHandshake, Compass, BookOpen, AlertCircle } from "lucide-react";

export function CommunityImpact() {
  return (
    <section id="community" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Origin &amp; Purpose
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Origin Story &amp; Coastal Community Relevance
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Bridging the gap between dense numerical ocean models and the practical safety needs of artisanal fishers and coastal mariners.
          </p>
        </div>

        {/* Featured Sunrise Harbour Artwork */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[220px]">
            <Image
              src="/artwork/Ukiyo-e Sunrise Fishing Harbour.png"
              alt="Ukiyo-e woodblock style painting of a coastal fishing harbour at sunrise with fishing craft preparing for sea"
              fill
              className="object-cover object-center"
              sizes="100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/85 via-transparent to-transparent" />
            
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1 max-w-xl">
              <span className="px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)] text-[9px] uppercase tracking-wider font-mono">
                Illustrative Art — Coastal Community Archive
              </span>
              <h3 className="text-lg sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                Dawn Over the Coastal Landing
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-normal">
                Every dawn, coastal mariners make critical departure decisions based on limited and fragmented marine signals.
              </p>
            </div>
          </div>
        </div>

        {/* Narrative Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          
          {/* Column 1: The Information Divide */}
          <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg w-fit bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <Compass className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
                The Coastal Information Divide
              </h4>
              <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                India’s coastline spans over 7,500 kilometers and supports millions of livelihoods. While national agencies generate world-class meteorological and oceanographic models, outputs are frequently presented in technical tables or English bulletins that are difficult to interpret rapidly at sea.
              </p>
            </div>
            <div className="pt-3 border-t border-[var(--color-warm-ivory-dark)] text-[11px] text-[var(--color-charcoal-blue-muted)]">
              Core challenge: Transforming specialized metrics into intuitive vernacular guidance.
            </div>
          </div>

          {/* Column 2: The Sagarvani Vision */}
          <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg w-fit bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <BookOpen className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
                Evidence-Aware Architecture
              </h4>
              <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                Sagarvani was conceived as an open, defensible decision-intelligence platform. Instead of acting as an unconstrained generative chatbot, the architecture enforces finite-state-machine validation, bounded recovery, and deterministic safety release gates.
              </p>
            </div>
            <div className="pt-3 border-t border-[var(--color-warm-ivory-dark)] text-[11px] text-[var(--color-charcoal-blue-muted)]">
              Architectural principle: When evidence is insufficient, abstain rather than hallucinate safety.
            </div>
          </div>

          {/* Column 3: Intended Field Relevance */}
          <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg w-fit bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <HeartHandshake className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
                Intended Community Relevance
              </h4>
              <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                By synthesizing wave dynamics, wind vectors, and safety boundaries into honest visual summaries, the platform strives to assist community elders, boatmasters, and harbor coordinators before departure.
              </p>
            </div>
            <div className="pt-3 border-t border-[var(--color-warm-ivory-dark)] text-[11px] text-[var(--color-charcoal-blue-muted)]">
              Objective: Empathetic, accessible communication without compromising physical truth.
            </div>
          </div>

        </div>

        {/* Conceptual Field Scenario Notice */}
        <div className="p-5 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] flex items-start gap-3.5 text-xs text-[var(--color-charcoal-blue-muted)]">
          <AlertCircle className="w-5 h-5 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold text-[var(--color-charcoal-blue)]">
              Prototype Field Context Note:
            </span>
            <p>
              Descriptions of community use cases reflect the intended operational purpose of the Sagarvani project. The platform is currently a research and demonstration prototype. No real-world commercial pilots, verified partner endorsements, adoption figures, or lives-saved metrics are claimed.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
}
