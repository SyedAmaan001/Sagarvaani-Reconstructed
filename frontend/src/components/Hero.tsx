"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowRight, Compass, AlertCircle, Waves, Info } from "lucide-react";
import Image from "next/image";

interface HeroProps {
  onAskClick?: () => void;
  onExploreClick?: () => void;
}

export function Hero({ onExploreClick }: HeroProps) {
  const [comingSoonNotice, setComingSoonNotice] = useState<string | null>(null);

  const handleExplore = () => {
    if (onExploreClick) {
      onExploreClick();
    } else {
      setComingSoonNotice(
        "Ocean exploration sections (Use Cases and Narrative Stages) are rolling out in Phase 2."
      );
    }
  };

  return (
    <section className="relative w-full overflow-hidden bg-[var(--color-warm-ivory)] pt-8 pb-16 md:pt-16 md:pb-28">
      {/* Background Decorative Waves / Tone */}
      <div className="absolute inset-0 pointer-events-none opacity-40">
        <Image
          src="/artwork/layered-waves-haikei.svg"
          alt=""
          fill
          className="object-cover object-bottom"
          priority
        />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Editorial Headline & Copy */}
          <div className="lg:col-span-7 space-y-6 z-10">
            {/* Status Pill */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] shadow-xs">
              <span className="w-2 h-2 rounded-full bg-[var(--color-fresh-sky)] animate-pulse" />
              <span className="text-xs font-medium text-[var(--color-charcoal-blue)]">
                Evidence-Aware Marine Intelligence Platform
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold tracking-tight text-[var(--color-french-blue)] leading-[1.15]">
              A clearer view of our ocean.
            </h1>

            {/* Supporting Copy */}
            <p className="text-lg sm:text-xl text-[var(--color-charcoal-blue-muted)] leading-relaxed max-w-2xl font-normal">
              Marine observations, meteorological models, and coastal evidence brought together into honest, understandable advisories—designed for coastal communities, fishers, and ocean professionals.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-lg bg-[var(--color-french-blue)] hover:bg-[var(--color-azure-blue)] text-[var(--color-warm-ivory)] font-medium text-base shadow-sm transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] active:scale-95"
              >
                <span>Ask Sagarvani</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <button
                type="button"
                onClick={handleExplore}
                className="inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] hover:bg-[var(--color-warm-ivory)] text-[var(--color-charcoal-blue)] font-medium text-base transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
              >
                <Compass className="w-4 h-4 text-[var(--color-french-blue)]" />
                <span>Explore the ocean</span>
              </button>
            </div>

            {/* Honest Status Note */}
            <div className="pt-4 flex items-start gap-2.5 text-xs text-[var(--color-charcoal-blue-muted)] max-w-xl">
              <Info className="w-4 h-4 shrink-0 text-[var(--color-french-blue)] mt-0.5" />
              <p>
                <strong>Advisory notice:</strong> Prototype for demonstration and review. Marine-departure risk thresholds are subject to ongoing domain validation and do not replace certified port authority directives.
              </p>
            </div>

            {/* Coming Soon Alert Drawer */}
            {comingSoonNotice && (
              <div
                role="status"
                className="mt-4 p-4 rounded-lg bg-[var(--color-warm-ivory-light)] border border-[var(--color-fresh-sky)]/40 flex items-start justify-between gap-3 shadow-xs animate-in fade-in duration-200"
              >
                <div className="flex items-start gap-2.5">
                  <AlertCircle className="w-5 h-5 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
                  <p className="text-sm text-[var(--color-charcoal-blue)]">{comingSoonNotice}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setComingSoonNotice(null)}
                  className="text-xs font-semibold text-[var(--color-charcoal-blue-muted)] hover:text-[var(--color-charcoal-blue)] px-2 py-1 rounded"
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>

          {/* Right Column: Original Ukiyo-e Marine Illustration Card */}
          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md lg:max-w-none rounded-2xl overflow-hidden shadow-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] p-2">
              <div className="relative aspect-[4/3] w-full rounded-xl overflow-hidden">
                <Image
                  src="/artwork/Minimalist Indigo Ukiyo-e Seascape.png"
                  alt="Ukiyo-e woodblock style seascape showing rolling indigo waves and calm horizon"
                  fill
                  className="object-cover hover:scale-105 transition-transform duration-700 ease-out"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 40vw"
                  priority
                />

                {/* Subtle illustrative cartography badge */}
                <div className="absolute bottom-3 left-3 px-3 py-1 rounded-md bg-[var(--color-charcoal-blue)]/80 backdrop-blur-xs text-[10px] text-[var(--color-warm-ivory)] uppercase tracking-wider font-medium">
                  Illustrative Art — Sagarvani Archive
                </div>
              </div>

              {/* Caption Card */}
              <div className="p-4 flex items-center justify-between text-xs text-[var(--color-charcoal-blue)]">
                <div className="flex items-center gap-2">
                  <Waves className="w-4 h-4 text-[var(--color-french-blue)]" />
                  <span className="font-serif italic font-medium">Indian Ocean Horizon</span>
                </div>
                <span className="text-[11px] text-[var(--color-charcoal-blue-muted)] font-mono">
                  Bay of Bengal & Arabian Sea
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
