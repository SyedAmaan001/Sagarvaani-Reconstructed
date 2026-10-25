"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Layers, Clock, AlertTriangle, FileCheck, HelpCircle } from "lucide-react";

interface EvidenceFacet {
  id: string;
  title: string;
  badge: string;
  badgeType: "prototype" | "planned";
  question: string;
  explanation: string;
  validationCheck: string;
  limitationRisk: string;
}

const EVIDENCE_FACETS: EvidenceFacet[] = [
  {
    id: "provenance",
    title: "Source Provenance & Boundaries",
    badge: "Prototype adapter implemented",
    badgeType: "prototype",
    question: "Where does marine evidence originate, and what are its boundaries?",
    explanation:
      "Evidence enters through typed gateway adapters connecting in-situ ocean buoys, numerical weather prediction models, and coastal observation networks. Every reading carries a designated source identifier and spatial resolution envelope.",
    validationCheck:
      "Coordinate boundary check verifies that query coordinates fall within the coastal domain; schema asserts required fields exist with valid typing.",
    limitationRisk:
      "A forecast grid cell (e.g., 0.25° × 0.25°) cannot resolve fine-grained bay turbulence or immediate surf-zone shoaling.",
  },
  {
    id: "temporal",
    title: "Temporal Lineage & Freshness",
    badge: "Prototype adapter implemented",
    badgeType: "prototype",
    question: "Why do issue times, valid times, and observation windows matter?",
    explanation:
      "Marine conditions change rapidly. Sagarvani strictly differentiates between when an observation was recorded, when a numerical model was run, when the forecast is valid, and when our engine retrieved it.",
    validationCheck:
      "Freshness verification rejects readings whose valid-time window has expired or whose observation timestamp is older than allowable operational tolerance.",
    limitationRisk:
      "Presenting a 12-hour-old wave forecast without an explicit timestamp can disguise an approaching sea swell or squall front.",
  },
  {
    id: "units",
    title: "Units & Physical Feasibility",
    badge: "Prototype adapter implemented",
    badgeType: "prototype",
    question: "How are metrics standardized and vetted for physical plausibility?",
    explanation:
      "Disparate gateways report in conflicting units (meters vs. feet, knots vs. m/s, millibars vs. hPa). The ingestion engine normalizes all units into standard scientific metrics and enforces strict physical bounds.",
    validationCheck:
      "Sensor bounds check asserts non-negative values (Significant Wave Height ≥ 0m, Wind Speed ≥ 0 kts, Wave Period between 1s and 30s).",
    limitationRisk:
      "Unnormalized units or corrupt negative readings passed into departure logic could trigger erroneous clearance.",
  },
  {
    id: "geospatial",
    title: "Jurisdictional & Boundary Limits",
    badge: "Coming Soon",
    badgeType: "planned",
    question: "Why are protected areas and port baselines essential to release policy?",
    explanation:
      "Marine decisions must account for Marine Protected Areas (MPAs), restricted shipping channels, and territorial borders. Sagarvani treats spatial boundary verification as a mandatory safety gate.",
    validationCheck:
      "Spatial polygon intersection checks candidate departure routes against certified maritime jurisdiction baselines.",
    limitationRisk:
      "Currently marked NOT_EVALUABLE in release policy because licensed, authoritative MPA geometry is not yet integrated into the repository.",
  },
];

export function EvidenceExploration() {
  const [activeFacet, setActiveFacet] = useState<EvidenceFacet>(EVIDENCE_FACETS[0]);

  return (
    <section id="evidence-exploration" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Evidence Transparency
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Evidence &amp; Exploration
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Every marine advisory released by Sagarvani is rooted in verifiable evidence. Understand how observations are sourced, validated, and bounded before policy evaluation.
          </p>
        </div>

        {/* Featured Cartographic Art Composition */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[220px]">
            <Image
              src="/artwork/Ukiyo-e Ocean Layers Map.png"
              alt="Ukiyo-e woodblock style cartographic layers illustrating bathymetry, ocean surface, and observation lines"
              fill
              className="object-cover object-center"
              sizes="100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/85 via-transparent to-transparent" />
            
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1 max-w-xl">
              <span className="px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)] text-[9px] uppercase tracking-wider font-mono">
                Illustrative Cartography — Ocean Layers
              </span>
              <h3 className="text-lg sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                The Anatomy of Marine Evidence
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-normal">
                Disparate meteorological, oceanographic, and geospatial data layers must be cross-verified before contributing to any decision.
              </p>
            </div>
          </div>
        </div>

        {/* Interactive Evidence Facets Tabs & Inspection Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Facet Buttons */}
          <div className="lg:col-span-5 space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
              Core Dimensions of Evidence Quality
            </span>
            <div className="space-y-2.5" role="tablist" aria-label="Evidence quality dimensions">
              {EVIDENCE_FACETS.map((facet) => {
                const isSelected = activeFacet.id === facet.id;
                return (
                  <button
                    key={facet.id}
                    type="button"
                    role="tab"
                    id={`facet-tab-${facet.id}`}
                    aria-selected={isSelected}
                    aria-controls={`facet-panel-${facet.id}`}
                    onClick={() => setActiveFacet(facet)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-200 flex flex-col space-y-1.5 ${
                      isSelected
                        ? "border-[var(--color-azure-blue)] bg-[var(--color-warm-ivory-light)] shadow-sm ring-1 ring-[var(--color-azure-blue)]/30"
                        : "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] hover:bg-[var(--color-warm-ivory-light)]"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-serif font-bold text-[var(--color-french-blue)]">
                        {facet.title}
                      </h4>
                      {facet.badgeType === "prototype" ? (
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          {facet.badge}
                        </span>
                      ) : (
                        <span className="text-[10px] uppercase font-medium tracking-wider px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                          {facet.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[var(--color-charcoal-blue-muted)] line-clamp-1">
                      {facet.question}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Facet Deep-Dive Detail Panel */}
          <div
            id={`facet-panel-${activeFacet.id}`}
            role="tabpanel"
            aria-labelledby={`facet-tab-${activeFacet.id}`}
            className="lg:col-span-7 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] p-6 sm:p-8 space-y-6 shadow-xs"
          >
            <div className="flex items-start justify-between border-b border-[var(--color-warm-ivory-dark)] pb-4">
              <div className="space-y-1">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-azure-blue)]">
                  Evidence Dimension
                </span>
                <h3 className="text-xl sm:text-2xl font-serif font-bold text-[var(--color-french-blue)]">
                  {activeFacet.title}
                </h3>
              </div>
              <div className="p-2.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <Layers className="w-5 h-5" />
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-[var(--color-charcoal-blue)] flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0" />
                <span>{activeFacet.question}</span>
              </h4>
              <p className="text-sm text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                {activeFacet.explanation}
              </p>
            </div>

            {/* Validation Check Box */}
            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-1.5">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-900 uppercase tracking-wider">
                <FileCheck className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Deterministic Quality Verification</span>
              </div>
              <p className="text-xs text-emerald-950 leading-relaxed">
                {activeFacet.validationCheck}
              </p>
            </div>

            {/* Limitation & Safeguard Box */}
            <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/50 space-y-1.5">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-900 uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
                <span>Operational Limitation &amp; Guardrail</span>
              </div>
              <p className="text-xs text-amber-950 leading-relaxed">
                {activeFacet.limitationRisk}
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2 text-[11px] text-[var(--color-charcoal-blue-muted)]">
              <Clock className="w-3.5 h-3.5 text-[var(--color-french-blue)] shrink-0" />
              <span>
                Prototype Policy Rule: Missing, stale, or out-of-bounds evidence results in an honest abstention, never a synthetic guess.
              </span>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
