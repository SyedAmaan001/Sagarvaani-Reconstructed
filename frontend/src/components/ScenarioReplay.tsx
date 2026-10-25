"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Compass, Wind, Waves, AlertTriangle, CheckCircle2, Info, Eye } from "lucide-react";

interface ScenarioState {
  id: string;
  label: string;
  sublabel: string;
  category: "Illustrative scenario — not live data";
  conditions: {
    waveHeight: string;
    wavePeriod: string;
    windVelocity: string;
    visibility: string;
  };
  policyOutcome: "Permitted" | "Withheld (High Risk)";
  explanation: string;
}

const SCENARIOS: ScenarioState[] = [
  {
    id: "calm",
    label: "Scenario A: Fair Weather Inshore",
    sublabel: "Benign morning swell",
    category: "Illustrative scenario — not live data",
    conditions: {
      waveHeight: "0.8 m",
      wavePeriod: "7.2 s",
      windVelocity: "11 kts NE",
      visibility: "Good (>10 km)",
    },
    policyOutcome: "Permitted",
    explanation:
      "Wave heights and wind gust vectors remain well within small-craft design envelopes. Deterministic policy permits craft departure with standard logged observation window.",
  },
  {
    id: "shift",
    label: "Scenario B: Pre-Frontal Wind Shift",
    sublabel: "Rising chop & direction reversal",
    category: "Illustrative scenario — not live data",
    conditions: {
      waveHeight: "2.1 m",
      wavePeriod: "5.4 s",
      windVelocity: "26 kts WSW (Gusting 32 kts)",
      visibility: "Moderate (~5 km in spray)",
    },
    policyOutcome: "Withheld (High Risk)",
    explanation:
      "Short wave period paired with steep 2.1m chop creates dangerous breaking waves near harbor sandbars. Departure clearance is withheld by automated safety gates.",
  },
  {
    id: "storm",
    label: "Scenario C: Squall / Monsoonal Surge",
    sublabel: "Severe cyclonic swell",
    category: "Illustrative scenario — not live data",
    conditions: {
      waveHeight: "4.3 m",
      wavePeriod: "11.8 s",
      windVelocity: "42 kts S (Gale warnings active)",
      visibility: "Poor (<1.5 km in torrential squall)",
    },
    policyOutcome: "Withheld (High Risk)",
    explanation:
      "Extreme sea state exceeds all artisanal vessel thresholds. Release policy strictly blocks departure. Even with incomplete sensor feeds, fail-safe rules hold absolute veto.",
  },
];

export function ScenarioReplay() {
  const [activeScenario, setActiveScenario] = useState<ScenarioState>(SCENARIOS[0]);

  return (
    <section id="scenario-replay" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory-light)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Comparative Analysis
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Scenario Replay Presentation
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Comparing ocean conditions across varying weather states demonstrates how guarded rules respond to rising wave heights, gust shifts, and safety boundaries.
          </p>
        </div>

        {/* Featured Panoramic Sea State Artwork */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[220px]">
            <Image
              src="/artwork/Coastal Waves_ Calm to Storm.png"
              alt="Ukiyo-e woodblock illustration showing progression of coastal waves from calm swells to turbulent stormy surf"
              fill
              className="object-cover object-center"
              sizes="100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/85 via-transparent to-transparent" />
            
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1 max-w-xl">
              <span className="px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)] text-[9px] uppercase tracking-wider font-mono">
                Illustrative Sea Progression
              </span>
              <h3 className="text-lg sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                Calm Seas to Storm Surges
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-normal">
                Illustrative scenario only — not live telemetry or current hazardous conditions.
              </p>
            </div>
          </div>
        </div>

        {/* Notice on Distinguishing Scenarios */}
        <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] flex items-start gap-3 text-xs text-[var(--color-charcoal-blue-muted)]">
          <Info className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold text-[var(--color-charcoal-blue)]">
              Evaluation Clarification:
            </span>
            <p>
              In production, Sagarvani will distinguish <strong>Historical Observation</strong> (past buoy records), <strong>Live Forecast</strong> (active model run), and <strong>Illustrative Scenario</strong> (synthetic teaching case). The comparative states below are strictly illustrative scenarios demonstrating policy boundaries.
            </p>
          </div>
        </div>

        {/* Interactive Scenario Selector & Metrics Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Scenario Buttons */}
          <div className="lg:col-span-5 space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
              Select Marine Scenario
            </span>
            <div className="space-y-2.5" role="group" aria-label="Marine scenario comparison">
              {SCENARIOS.map((sc) => {
                const isSelected = activeScenario.id === sc.id;
                return (
                  <button
                    key={sc.id}
                    type="button"
                    onClick={() => setActiveScenario(sc)}
                    aria-pressed={isSelected}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-200 flex flex-col space-y-1.5 ${
                      isSelected
                        ? "border-[var(--color-azure-blue)] bg-[var(--color-warm-ivory)] shadow-sm ring-1 ring-[var(--color-azure-blue)]/30"
                        : "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] hover:bg-[var(--color-warm-ivory)]"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-serif font-bold text-[var(--color-french-blue)]">
                        {sc.label}
                      </h4>
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                        Illustrative
                      </span>
                    </div>
                    <p className="text-xs text-[var(--color-charcoal-blue-muted)]">
                      {sc.sublabel}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Scenario Details & Guard Evaluation Card */}
          <div className="lg:col-span-7 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-6 sm:p-8 space-y-6 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--color-warm-ivory-dark)] pb-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
                  {activeScenario.category}
                </span>
                <h3 className="text-xl sm:text-2xl font-serif font-bold text-[var(--color-french-blue)]">
                  {activeScenario.label}
                </h3>
              </div>
              <div className="flex items-center gap-1.5 self-start sm:self-center px-3 py-1 rounded-full text-xs font-semibold border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)]">
                <Eye className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                <span>Simulated Inspection</span>
              </div>
            </div>

            {/* Simulated Parameter Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                <span className="text-[10px] font-semibold text-[var(--color-charcoal-blue-muted)] uppercase tracking-wider flex items-center gap-1">
                  <Waves className="w-3 h-3 text-[var(--color-azure-blue)]" /> Wave Height
                </span>
                <p className="text-sm font-bold font-mono text-[var(--color-french-blue)]">
                  {activeScenario.conditions.waveHeight}
                </p>
              </div>

              <div className="p-3 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                <span className="text-[10px] font-semibold text-[var(--color-charcoal-blue-muted)] uppercase tracking-wider flex items-center gap-1">
                  <Compass className="w-3 h-3 text-[var(--color-azure-blue)]" /> Wave Period
                </span>
                <p className="text-sm font-bold font-mono text-[var(--color-french-blue)]">
                  {activeScenario.conditions.wavePeriod}
                </p>
              </div>

              <div className="p-3 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                <span className="text-[10px] font-semibold text-[var(--color-charcoal-blue-muted)] uppercase tracking-wider flex items-center gap-1">
                  <Wind className="w-3 h-3 text-[var(--color-azure-blue)]" /> Wind Velocity
                </span>
                <p className="text-sm font-bold font-mono text-[var(--color-french-blue)]">
                  {activeScenario.conditions.windVelocity}
                </p>
              </div>

              <div className="p-3 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-1">
                <span className="text-[10px] font-semibold text-[var(--color-charcoal-blue-muted)] uppercase tracking-wider">
                  Visibility
                </span>
                <p className="text-sm font-bold font-mono text-[var(--color-french-blue)]">
                  {activeScenario.conditions.visibility}
                </p>
              </div>
            </div>

            {/* Policy Release Outcome */}
            <div className={`p-4 rounded-xl border space-y-2 ${
              activeScenario.policyOutcome === "Permitted"
                ? "border-emerald-200 bg-emerald-50/60 text-emerald-950"
                : "border-amber-200 bg-amber-50/60 text-amber-950"
            }`}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                  {activeScenario.policyOutcome === "Permitted" ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Release Policy Status: Permitted (Illustrative)</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      <span>Release Policy Status: Withheld / Blocked (Illustrative)</span>
                    </>
                  )}
                </span>
              </div>
              <p className="text-xs leading-relaxed">
                {activeScenario.explanation}
              </p>
            </div>

            <p className="text-[11px] text-[var(--color-charcoal-blue-muted)] italic">
              Notice: Operational historical replay requires calibrated hindcast data and certified harbor boundaries, planned for Phase 6.
            </p>
          </div>

        </div>

      </div>
    </section>
  );
}
