"use client";

import React from "react";
import Image from "next/image";
import { CheckCircle2, Clock, Anchor, ShieldCheck } from "lucide-react";

interface Milestone {
  phase: string;
  title: string;
  status: "Completed" | "Current Gate" | "Planned";
  description: string;
  deliverables: string[];
}

const MILESTONES: Milestone[] = [
  {
    phase: "Phase 1",
    title: "Scaffold, Tokens & Navigation",
    status: "Completed",
    description: "Next.js App Router scaffold, ocean-inspired warm ivory design tokens, responsive header, and introductory voyage animation.",
    deliverables: ["Editorial navigation with status controls", "Hero section with advisory notice", "Accessible reduced-motion fallback"],
  },
  {
    phase: "Phase 2",
    title: "Audience & Decision Narrative",
    status: "Completed",
    description: "Multi-domain stakeholder use cases and the 3-stage Before → Sagarvani → Outcome framework with dual illustrative outcome states.",
    deliverables: ["4 stakeholder role overviews", "Dual-outcome toggle (Supported vs. Insufficient)", "Failsafe abstention logic explained"],
  },
  {
    phase: "Phase 3",
    title: "Connected Ecosystem & Voyage",
    status: "Completed",
    description: "Multi-domain observation networks overview and the 4-stage Intelligence Voyage decision track with explicit verification guards.",
    deliverables: ["4 information domains with adapter status", "Interactive waypoint tracker (Gather → Validate → Recover → Decide)", "Deterministic release policy gate"],
  },
  {
    phase: "Phase 4",
    title: "Evidence, Exploration & Community",
    status: "Current Gate",
    description: "Transparent evidence exploration, scenario comparisons, visual ocean roadmap, community origin narrative, and editorial FAQ.",
    deliverables: ["Evidence quality dimensions", "Illustrative scenario comparison", "Accessible FAQ and ocean footer"],
  },
  {
    phase: "Phase 5",
    title: "Authentication & Access Control",
    status: "Planned",
    description: "Secure role-based login for coastal operators, port officers, and marine researchers without exposing private credentials.",
    deliverables: ["Secure session handling", "Role authorization gates", "Auditable credential controls"],
  },
  {
    phase: "Phase 6",
    title: "Dashboard & Verified Backend Integration",
    status: "Planned",
    description: "Direct integration with backend query API (/api/orca/query), live service health monitoring (/health), role-specific cockpits, and GIS maps.",
    deliverables: ["Verified backend data binding", "Stakeholder cockpit views", "Certified GIS spatial overlays"],
  },
  {
    phase: "Phase 7",
    title: "End-to-End QA & Future Horizons",
    status: "Planned",
    description: "Cross-system verification, offline resilience, and evaluation of multi-dialect Indian speech synthesis for artisanal fishers.",
    deliverables: ["Comprehensive QA test suite", "Regional speech dialect evaluation", "Authoritative port bulletin ingestion"],
  },
];

export function OceanRoadmap() {
  return (
    <section id="roadmap" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory-light)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Project Trajectory
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Sagarvani Ocean Roadmap
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Our progressive journey from audited architectural foundation to a fully verified, evidence-aware decision intelligence platform.
          </p>
        </div>

        {/* Panoramic Sea Chart Banner */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[220px]">
            <Image
              src="/artwork/Ukiyo-e Archipelago Sea Chart.png"
              alt="Ukiyo-e woodblock style archipelago navigation chart showing progressive nautical waypoints"
              fill
              className="object-cover object-center"
              sizes="100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/85 via-transparent to-transparent" />
            
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1 max-w-xl">
              <span className="px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)] text-[9px] uppercase tracking-wider font-mono">
                Illustrative Voyage Chart
              </span>
              <h3 className="text-lg sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                Plotting the Safe Course
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-normal">
                Structured in sequential gates. Each milestone must pass rigorous verification before subsequent phases unlock.
              </p>
            </div>
          </div>
        </div>

        {/* Sequential Milestone Voyage Track */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
              Voyage Milestones (Phase 1 through Phase 7)
            </span>
            <span className="text-xs font-mono text-[var(--color-azure-blue)]">
              ACTIVE STAGE: PHASE 4
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {MILESTONES.map((m) => {
              const isCompleted = m.status === "Completed";
              const isCurrent = m.status === "Current Gate";

              return (
                <div
                  key={m.phase}
                  className={`p-6 rounded-2xl border transition-all duration-200 flex flex-col justify-between space-y-4 ${
                    isCurrent
                      ? "border-[var(--color-azure-blue)] bg-[var(--color-warm-ivory)] shadow-md ring-2 ring-[var(--color-azure-blue)]/30"
                      : isCompleted
                      ? "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)]"
                      : "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)]/60 opacity-90"
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
                        {m.phase}
                      </span>
                      {isCompleted ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>Completed</span>
                        </span>
                      ) : isCurrent ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-100 text-[var(--color-french-blue)] animate-pulse">
                          <Anchor className="w-3 h-3 text-[var(--color-azure-blue)]" />
                          <span>Current Gate</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                          <Clock className="w-3 h-3" />
                          <span>Planned</span>
                        </span>
                      )}
                    </div>

                    <h4 className="text-base font-serif font-bold text-[var(--color-french-blue)]">
                      {m.title}
                    </h4>

                    <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                      {m.description}
                    </p>
                  </div>

                  {/* Deliverables List */}
                  <div className="pt-3 border-t border-[var(--color-warm-ivory-dark)] space-y-1.5 text-xs text-[var(--color-charcoal-blue)]">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
                      Core Outcomes:
                    </span>
                    <ul className="space-y-1">
                      {m.deliverables.map((item) => (
                        <li key={item} className="flex items-start gap-1.5 text-[11px]">
                          <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-azure-blue)] mt-1 shrink-0" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Roadmap Integrity Notice */}
        <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] flex items-start gap-3 text-xs text-[var(--color-charcoal-blue-muted)]">
          <ShieldCheck className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
          <p>
            <strong>Integrity Assurance:</strong> Sagarvani advances one phase at a time under strict acceptance review. Unimplemented features are never claimed as active until verified against backend data models and safety release gates.
          </p>
        </div>

      </div>
    </section>
  );
}
