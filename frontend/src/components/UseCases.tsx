"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Anchor, Compass, Building2, Navigation2, ArrowRight, X, AlertCircle } from "lucide-react";

interface Stakeholder {
  id: string;
  role: string;
  headline: string;
  message: string;
  detail: string;
  imageSrc: string;
  imageAlt: string;
  icon: React.ElementType;
}

const STAKEHOLDERS: Stakeholder[] = [
  {
    id: "fishers",
    role: "Fishers & Coastal Communities",
    headline: "Understand conditions before you plan a trip.",
    message: "Understand available marine and weather information to help plan informed decisions.",
    detail: "Artisanal craft operators and shore communities require plain-language advisories on wave height, wind shifts, and tidal patterns without deciphering complex synoptic forecast charts.",
    imageSrc: "/artwork/Traditional Ukiyo-e Fishing Boat at Sea.png",
    imageAlt: "Traditional ukiyo-e artisanal fishing vessel navigating coastal swells",
    icon: Anchor,
  },
  {
    id: "researchers",
    role: "Marine Researchers",
    headline: "Explore evidence from disparate ocean sources.",
    message: "Explore evidence from different sources and understand its provenance and limitations.",
    detail: "Ocean scientists and academic investigators can trace observation timestamps, sensor provenance, confidence metrics, and discrepancy flags across public satellite and meteorological models.",
    imageSrc: "/artwork/Ukiyo-e Maritime Research Voyage.png",
    imageAlt: "Scientific maritime survey vessel traversing open ocean waters in woodblock print aesthetic",
    icon: Compass,
  },
  {
    id: "authorities",
    role: "Coastal Authorities",
    headline: "Review evidence for coastal safety and planning.",
    message: "Review available evidence to support coastal planning and assessment.",
    detail: "Port masters, disaster mitigation cells, and local administration review cross-validated ocean indicators, environmental alerts, and jurisdictional boundaries ahead of public advisories.",
    imageSrc: "/artwork/Ukiyo-e Coastal Fishing Village Panorama-2.png",
    imageAlt: "Panoramic coastal inlet with settlement, harbour breakwater, and ocean approaches",
    icon: Building2,
  },
  {
    id: "operators",
    role: "Maritime Operators",
    headline: "Evaluate conditions before operational maneuvers.",
    message: "Review available conditions and evidence before operational decisions.",
    detail: "Tug operators, coastal barge pilots, and commercial harbour logistics review wave forecasts, current drift, and verified advisory release verdicts before scheduled transit windows.",
    imageSrc: "/artwork/Ukiyo-e Research Ship in Stormy Seas.png",
    imageAlt: "Commercial maritime vessel maintaining station in agitated sea conditions",
    icon: Navigation2,
  },
];

export function UseCases() {
  const [selectedStakeholder, setSelectedStakeholder] = useState<Stakeholder | null>(null);

  return (
    <section id="use-cases" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-12 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Stakeholder Roles
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Who Sagarvani serves
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Different coastal stakeholders face different operational risks. Sagarvani adapts its presentation while maintaining identical verifiable evidence under the hood.
          </p>
        </div>

        {/* Four Stakeholder Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {STAKEHOLDERS.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.id}
                className="group flex flex-col justify-between rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] overflow-hidden shadow-xs hover:shadow-md hover:border-[var(--color-azure-blue)] transition-all duration-200"
              >
                <div>
                  {/* Artwork Container */}
                  <div className="relative aspect-[16/10] w-full overflow-hidden bg-[var(--color-warm-ivory)]">
                    <Image
                      src={item.imageSrc}
                      alt={item.imageAlt}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
                      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 25vw"
                    />
                    <div className="absolute top-3 left-3 w-8 h-8 rounded-lg bg-[var(--color-warm-ivory)]/90 backdrop-blur-xs flex items-center justify-center text-[var(--color-french-blue)] shadow-xs">
                      <Icon className="w-4 h-4" />
                    </div>
                  </div>

                  {/* Text Content */}
                  <div className="p-5 space-y-2.5">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-azure-blue)]">
                      {item.role}
                    </span>
                    <h3 className="text-lg font-serif font-bold text-[var(--color-charcoal-blue)] leading-snug group-hover:text-[var(--color-french-blue)] transition-colors">
                      {item.headline}
                    </h3>
                    <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                      {item.message}
                    </p>
                  </div>
                </div>

                {/* Card Action */}
                <div className="px-5 pb-5 pt-2">
                  <button
                    type="button"
                    onClick={() => setSelectedStakeholder(item)}
                    className="w-full flex items-center justify-between text-xs font-semibold px-3.5 py-2.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-[var(--color-charcoal-blue)] hover:border-[var(--color-azure-blue)] hover:text-[var(--color-azure-blue)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] transition-colors"
                  >
                    <span>View role scope</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Modal / Explanatory Drawer for Stakeholder Detail */}
        {selectedStakeholder && (
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="stakeholder-modal-title"
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-200"
          >
            <div className="relative w-full max-w-lg rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-6 shadow-2xl space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-azure-blue)]">
                    Role Overview
                  </span>
                  <h3 id="stakeholder-modal-title" className="text-2xl font-serif font-bold text-[var(--color-french-blue)] mt-1">
                    {selectedStakeholder.role}
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedStakeholder(null)}
                  className="p-1.5 rounded-lg text-[var(--color-charcoal-blue-muted)] hover:bg-[var(--color-warm-ivory-dark)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                  aria-label="Close role scope dialog"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <p className="text-sm text-[var(--color-charcoal-blue)] leading-relaxed">
                {selectedStakeholder.detail}
              </p>

              {/* Truthful Prototype Notice */}
              <div className="p-3 rounded-lg bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] flex items-start gap-2.5 text-xs text-[var(--color-charcoal-blue-muted)]">
                <AlertCircle className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
                <p>
                  <strong>Prototype Status:</strong> Role-specific view configurations are established in backend data contracts. Dedicated role workspaces and interactive cockpits are planned for Phase 6.
                </p>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={() => setSelectedStakeholder(null)}
                  className="px-4 py-2 rounded-lg bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] text-xs font-medium hover:bg-[var(--color-azure-blue)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] transition-colors"
                >
                  Close overview
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </section>
  );
}
