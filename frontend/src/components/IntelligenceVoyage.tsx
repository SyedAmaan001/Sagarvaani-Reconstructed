"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Compass, ShieldCheck, RefreshCw, CheckCircle2, AlertOctagon, Anchor } from "lucide-react";

interface Waypoint {
  step: number;
  id: string;
  title: string;
  shortLabel: string;
  summary: string;
  detail: string;
  guards: string[];
  failureAction: string;
  icon: React.ElementType;
}

const WAYPOINTS: Waypoint[] = [
  {
    step: 1,
    id: "gather",
    title: "1. Gather Available Evidence",
    shortLabel: "Gather",
    summary: "Acquires marine and atmospheric parameters from verified gateways.",
    detail: "Collects wave height, wind velocity, and barometric forecasts for the requested coastal location. Does not invent missing readings.",
    guards: ["Target coordinate bounded within coastal envelope", "Gateway response adheres to typed Pydantic evidence contract"],
    failureAction: "Marks missing parameter and initiates bounded recovery selector.",
    icon: Anchor,
  },
  {
    step: 2,
    id: "validate",
    title: "2. Validate Quality & Lineage",
    shortLabel: "Validate",
    summary: "Examines timestamps, units, sensor bounds, and source credibility.",
    detail: "Distinguishes observation time from forecast-valid time and retrieval time. Checks physical viability (e.g. wave height >= 0, wind speed >= 0).",
    guards: ["Observation freshness within tolerance", "Coordinate precision matches resolution bounds", "Lineage includes verifiable source_id"],
    failureAction: "Flags invalid evidence; triggers recovery cycle or sets status to UNVERIFIED.",
    icon: Compass,
  },
  {
    step: 3,
    id: "recover",
    title: "3. Bounded Recovery Cycle",
    shortLabel: "Recover",
    summary: "Executes restricted fallbacks with finite retry budget and no-progress checks.",
    detail: "Allows at most two recovery attempts using pre-approved fallback rules. If no new evidence is acquired, execution terminates cleanly to avoid infinite loops.",
    guards: ["Maximum 2 recovery cycles enforced", "No-progress detection halts repetitive actions", "Never bypasses release policy"],
    failureAction: "Terminates recovery loop; marks run as INSUFFICIENT_EVIDENCE.",
    icon: RefreshCw,
  },
  {
    step: 4,
    id: "decide",
    title: "4. Apply Release Policy Gate",
    shortLabel: "Decide",
    summary: "Deterministic safety checks hold final veto over all released advisories.",
    detail: "A generative model cannot override deterministic release policies. If official bulletins or vessel limits are missing, the system strictly outputs NOT_EVALUABLE or ABSTAINED.",
    guards: ["Departure safety limits enforced", "Official warning gates hold veto authority", "Auditable policy log preserved in catalog"],
    failureAction: "Withholds departure clearance; outputs honest explanatory reason.",
    icon: ShieldCheck,
  },
];

export function IntelligenceVoyage() {
  const [activeStep, setActiveStep] = useState<number>(1);

  const currentWaypoint = WAYPOINTS[activeStep - 1];

  return (
    <section id="voyage" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory-light)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Decision Journey
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Sagarvani Intelligence Voyage
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Follow the journey of a marine advisory through our guarded decision framework: from raw coastal inputs, across strict validation checks, through bounded recovery, and past the final release-policy gate.
          </p>
        </div>

        {/* Voyage Panoramic Landscape Card */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[220px]">
            <Image
              src="/artwork/Ukiyo-e Voyage to the Lighthouse.png"
              alt="Ukiyo-e panoramic coastal sea voyage with vessel navigating toward safe harbor lighthouse"
              fill
              className="object-cover object-center"
              sizes="100vw"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/85 via-transparent to-transparent" />
            
            {/* Voyage Status Narrative on Art */}
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1 max-w-xl">
              <span className="px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)] text-[9px] uppercase tracking-wider font-mono">
                Illustrative Voyage Narrative
              </span>
              <h3 className="text-lg sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                The Path to Safe Harbour
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-normal">
                Waypoint {activeStep} of 4: {currentWaypoint.shortLabel} — Guided by deterministic verification guards.
              </p>
            </div>
          </div>
        </div>

        {/* Interactive Waypoint Progression Track (Hybrid scroll & tap) */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
              Voyage Progression Track (Tap any waypoint to inspect)
            </span>
            <div className="text-xs font-mono text-[var(--color-azure-blue)]">
              STAGE {activeStep} / 4
            </div>
          </div>

          {/* Stepper Navigation */}
          <div
            role="group"
            aria-label="Intelligence voyage waypoints"
            className="grid grid-cols-2 sm:grid-cols-4 gap-3"
          >
            {WAYPOINTS.map((wp) => {
              const Icon = wp.icon;
              const isActive = activeStep === wp.step;
              const isPast = activeStep > wp.step;

              return (
                <button
                  key={wp.id}
                  type="button"
                  onClick={() => setActiveStep(wp.step)}
                  className={`p-3.5 rounded-xl border text-left transition-all duration-200 flex flex-col justify-between space-y-2 ${
                    isActive
                      ? "border-[var(--color-azure-blue)] bg-[var(--color-warm-ivory)] shadow-sm ring-1 ring-[var(--color-azure-blue)]/40"
                      : isPast
                      ? "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)]/70 hover:bg-[var(--color-warm-ivory)]"
                      : "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] hover:bg-[var(--color-warm-ivory)]"
                  }`}
                  aria-pressed={isActive}
                >
                  <div className="flex items-center justify-between w-full">
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
                        isActive
                          ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)]"
                          : isPast
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue)]"
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-[10px] font-mono uppercase text-[var(--color-charcoal-blue-muted)]">
                      Step 0{wp.step}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-xs font-serif font-bold text-[var(--color-french-blue)]">
                      {wp.shortLabel}
                    </h4>
                    <p className="text-[10px] text-[var(--color-charcoal-blue-muted)] truncate">
                      {wp.summary}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Waypoint Deep-Dive Card */}
        <div className="rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-6 md:p-8 space-y-6 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[var(--color-warm-ivory-dark)] pb-4">
            <div className="space-y-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-azure-blue)]">
                Waypoint Detail
              </span>
              <h3 className="text-2xl font-serif font-bold text-[var(--color-french-blue)]">
                {currentWaypoint.title}
              </h3>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={activeStep === 1}
                onClick={() => setActiveStep((prev) => Math.max(1, prev - 1))}
                className="px-3 py-1.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-xs text-[var(--color-charcoal-blue)] disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={activeStep === 4}
                onClick={() => setActiveStep((prev) => Math.min(4, prev + 1))}
                className="px-3 py-1.5 rounded-lg bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] text-xs font-medium hover:bg-[var(--color-azure-blue)] disabled:opacity-40"
              >
                Next Waypoint
              </button>
            </div>
          </div>

          <p className="text-sm sm:text-base text-[var(--color-charcoal-blue)] leading-relaxed">
            {currentWaypoint.detail}
          </p>

          {/* Guards & Failure Safeguards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            
            {/* Active Guards */}
            <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)] flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-[var(--color-azure-blue)]" />
                Guarded Verification Checks
              </span>
              <ul className="space-y-1.5 text-xs text-[var(--color-charcoal-blue)]">
                {currentWaypoint.guards.map((g) => (
                  <li key={g} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-azure-blue)] mt-1.5 shrink-0" />
                    <span>{g}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Failure Safeguard */}
            <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-900 flex items-center gap-1.5">
                <AlertOctagon className="w-4 h-4 text-amber-600" />
                If Conditions Fail
              </span>
              <p className="text-xs text-[var(--color-charcoal-blue)] leading-relaxed">
                {currentWaypoint.failureAction}
              </p>
              <p className="text-[11px] text-[var(--color-charcoal-blue-muted)] italic pt-1">
                Policy invariant: Missing evidence cannot be converted into “safe departure”.
              </p>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
