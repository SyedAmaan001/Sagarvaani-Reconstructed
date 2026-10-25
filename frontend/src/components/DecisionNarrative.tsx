"use client";

import React, { useState } from "react";
import Image from "next/image";
import { CheckCircle2, AlertTriangle, Layers, ShieldAlert, RefreshCw, FileText } from "lucide-react";

export function DecisionNarrative() {
  const [activeOutcome, setActiveOutcome] = useState<"supported" | "insufficient">("supported");

  return (
    <section id="how-it-works" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory-light)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Decision Integrity
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Before → Sagarvani → Outcome
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            How marine decision intelligence moves from unverified, fragmented observations into verified, policy-governed releases—or honest abstentions.
          </p>
        </div>

        {/* 3-Stage Editorial Narrative Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          
          {/* Stage 1: Before Sagarvani */}
          <div className="flex flex-col justify-between rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-6 shadow-xs space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-[var(--color-charcoal-blue)]/10 text-[var(--color-charcoal-blue)]">
                  Stage 01
                </span>
                <span className="text-xs text-[var(--color-charcoal-blue-muted)] font-medium">
                  The Problem
                </span>
              </div>

              <h3 className="text-2xl font-serif font-bold text-[var(--color-french-blue)]">
                Before Sagarvani
              </h3>

              <p className="text-sm text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                Critical marine information is scattered across incompatible port bulletins, regional weather websites, and raw satellite datasets. Fishers and operators face conflicting signals with no clear indication of sensor freshness or uncertainty.
              </p>

              {/* Supplied Illustration */}
              <div className="relative aspect-[16/10] w-full rounded-xl overflow-hidden border border-[var(--color-warm-ivory-dark)]">
                <Image
                  src="/artwork/From Map Fragments to Lighthouse Bay.png"
                  alt="Ukiyo-e cartographic rendering showing fragmented coastal maps and disparate observation lines"
                  fill
                  className="object-cover"
                  sizes="(max-width: 1024px) 100vw, 33vw"
                />
                <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)]/80 text-[9px] uppercase tracking-wider text-[var(--color-warm-ivory)] font-mono">
                  Illustrative Art — Disparate Data
                </div>
              </div>

              <ul className="space-y-2 pt-2 text-xs text-[var(--color-charcoal-blue)]">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-azure-blue)] mt-1.5 shrink-0" />
                  <span>Conflicting wave and wind predictions from uncalibrated sources.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-azure-blue)] mt-1.5 shrink-0" />
                  <span>Stale observations presented without explicit timestamps.</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Stage 2: What Sagarvani Does */}
          <div className="flex flex-col justify-between rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-6 shadow-xs space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-[var(--color-azure-blue)]/15 text-[var(--color-azure-blue)]">
                  Stage 02
                </span>
                <span className="text-xs text-[var(--color-charcoal-blue-muted)] font-medium">
                  The Core Engine
                </span>
              </div>

              <h3 className="text-2xl font-serif font-bold text-[var(--color-french-blue)]">
                What Sagarvani does
              </h3>

              <p className="text-sm text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                Rather than accepting raw values as truth, Sagarvani subjects every metric to an evidence-aware execution cycle governed by finite state machine guards.
              </p>

              {/* Four Architectural Steps */}
              <div className="space-y-3 pt-1">
                <div className="p-3 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                  <div className="flex items-center gap-2 text-xs font-bold text-[var(--color-french-blue)]">
                    <Layers className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                    <span>1. Gather Available Evidence</span>
                  </div>
                  <p className="text-[11px] text-[var(--color-charcoal-blue-muted)]">
                    Collects forecasts, buoy readings, and bathymetry from verified sources.
                  </p>
                </div>

                <div className="p-3 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                  <div className="flex items-center gap-2 text-xs font-bold text-[var(--color-french-blue)]">
                    <FileText className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                    <span>2. Validate Quality & Lineage</span>
                  </div>
                  <p className="text-[11px] text-[var(--color-charcoal-blue-muted)]">
                    Verifies temporal validity, bounds, coordinate precision, and source provenance.
                  </p>
                </div>

                <div className="p-3 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                  <div className="flex items-center gap-2 text-xs font-bold text-[var(--color-french-blue)]">
                    <RefreshCw className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                    <span>3. Bounded Recovery</span>
                  </div>
                  <p className="text-[11px] text-[var(--color-charcoal-blue-muted)]">
                    If an input fails, attempts targeted fallback cycles with strict no-progress checks.
                  </p>
                </div>

                <div className="p-3 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                  <div className="flex items-center gap-2 text-xs font-bold text-[var(--color-french-blue)]">
                    <ShieldAlert className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                    <span>4. Deterministic Release Policy</span>
                  </div>
                  <p className="text-[11px] text-[var(--color-charcoal-blue-muted)]">
                    Safety gates hold final veto authority. An AI model cannot bypass release policy.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Stage 3: The Outcome (Dual Reality) */}
          <div className="flex flex-col justify-between rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-6 shadow-xs space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-[var(--color-french-blue)]/15 text-[var(--color-french-blue)]">
                  Stage 03
                </span>
                <span className="text-xs text-[var(--color-charcoal-blue-muted)] font-medium">
                  Verified Outcome
                </span>
              </div>

              <h3 className="text-2xl font-serif font-bold text-[var(--color-french-blue)]">
                The outcome
              </h3>

              <p className="text-sm text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                A marine decision system must be honest. Sagarvani yields two distinct outcomes depending on whether evidence and policy checks are fully satisfied:
              </p>

              {/* Prominent Illustrative Disclaimer */}
              <div className="p-2.5 rounded-lg bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-[11px] text-[var(--color-charcoal-blue-muted)] leading-normal flex items-start gap-2">
                <span className="font-semibold text-[var(--color-french-blue)] shrink-0 uppercase tracking-wider text-[10px] px-1.5 py-0.5 rounded bg-[var(--color-french-blue)]/10">
                  Illustrative Scenario
                </span>
                <span>Illustrative scenario only — this is not a live marine decision or safety advisory.</span>
              </div>

              {/* Outcome Toggle Selector */}
              <div className="grid grid-cols-2 p-1 rounded-lg bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-medium">
                <button
                  type="button"
                  onClick={() => setActiveOutcome("supported")}
                  className={`py-2 px-3 rounded-md transition-all flex items-center justify-center gap-1.5 ${
                    activeOutcome === "supported"
                      ? "bg-[var(--color-warm-ivory)] text-[var(--color-french-blue)] font-bold shadow-xs border border-[var(--color-warm-ivory-dark)]"
                      : "text-[var(--color-charcoal-blue-muted)] hover:text-[var(--color-charcoal-blue)]"
                  }`}
                  aria-pressed={activeOutcome === "supported"}
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Example: Supported</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveOutcome("insufficient")}
                  className={`py-2 px-3 rounded-md transition-all flex items-center justify-center gap-1.5 ${
                    activeOutcome === "insufficient"
                      ? "bg-[var(--color-warm-ivory)] text-[var(--color-charcoal-blue)] font-bold shadow-xs border border-[var(--color-warm-ivory-dark)]"
                      : "text-[var(--color-charcoal-blue-muted)] hover:text-[var(--color-charcoal-blue)]"
                  }`}
                  aria-pressed={activeOutcome === "insufficient"}
                >
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Example: Insufficient</span>
                </button>
              </div>

              {/* Outcome Visual Display Card */}
              {activeOutcome === "supported" ? (
                <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 space-y-2.5 animate-in fade-in duration-200">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-900">
                      Illustrative: Supported Release
                    </span>
                  </div>
                  <p className="text-xs text-emerald-950 leading-relaxed">
                    Example of a decision that <em>could</em> be released when verified ocean observations, meteorological forecasts, and all mandatory policy checks permit it.
                  </p>
                  <div className="pt-1 text-[10px] font-mono text-emerald-800">
                    POLICY_EXAMPLE: PERMITTED • DATA_MODE: EXAMPLE_ONLY
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/60 space-y-2.5 animate-in fade-in duration-200">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span className="text-xs font-bold uppercase tracking-wider text-amber-900">
                      Illustrative: Decision Withheld
                    </span>
                  </div>
                  <p className="text-xs text-amber-950 leading-relaxed">
                    Example of a decision being withheld when mandatory bulletins, spatial boundary checks, or vessel thresholds are missing, uncalibrated, or contradictory.
                  </p>
                  <div className="pt-1 text-[10px] font-mono text-amber-800">
                    POLICY_EXAMPLE: ABSTAINED / BLOCKED • DATA_MODE: EXAMPLE_ONLY
                  </div>
                </div>
              )}

              <p className="text-[11px] text-[var(--color-charcoal-blue-muted)] italic pt-1">
                Notice: Withholding a decision when safety evidence is absent is an intentional safeguard, not an error.
              </p>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
