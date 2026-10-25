"use client";

import React, { useState } from "react";
import { ChevronDown, ShieldAlert } from "lucide-react";

interface FaqItem {
  id: string;
  question: string;
  answer: string;
  category: "Architecture" | "Data & Policy" | "Prototype Capabilities";
}

const FAQS: FaqItem[] = [
  {
    id: "what-is-sagarvani",
    category: "Architecture",
    question: "What is Sagarvani?",
    answer:
      "Sagarvani is an evidence-aware marine decision-intelligence prototype. It connects oceanographic observations, numerical weather predictions, and coastal boundaries into clear, defensible advisories governed by deterministic verification guards and safety release policies.",
  },
  {
    id: "how-marine-weather-used",
    category: "Data & Policy",
    question: "How does Sagarvani use marine and weather information?",
    answer:
      "The platform ingests wave parameters (significant wave height, swell period, sea surface temperature) and atmospheric metrics (wind speed vectors, gusts, barometric pressure) through typed adapters. Rather than passing raw figures directly to users, it normalizes units, validates physical feasibility bounds, and tests readings against small-craft operational thresholds.",
  },
  {
    id: "evidence-quality-limitations",
    category: "Data & Policy",
    question: "How are evidence quality and limitations handled?",
    answer:
      "Every piece of evidence is evaluated for source provenance, observation timestamp, valid forecast window, and physical viability. If a sensor reports impossible negative values, or if a forecast window has expired, the reading is flagged as unverified and routed through bounded recovery rules.",
  },
  {
    id: "why-answer-withheld",
    category: "Data & Policy",
    question: "Why might an answer be withheld?",
    answer:
      "Withholding an answer is an intentional safety feature, not a software crash. If mandatory coastal inputs are missing, contradictory, or uncalibrated, or if a vessel safety threshold cannot be evaluated, Sagarvani outputs an explicit INSUFFICIENT_EVIDENCE or ABSTAINED status rather than synthesizing a false clearance.",
  },
  {
    id: "available-features",
    category: "Prototype Capabilities",
    question: "Which features are available in the current prototype?",
    answer:
      "The current prototype (Phases 1–4) includes the complete public editorial landing page: responsive ocean-inspired design system, stakeholder use-case overviews, the Before → Sagarvani → Outcome framework, Connected Ocean Ecosystem domain catalog, Intelligence Voyage 4-stage waypoint progression, comparative scenario replay, and the project roadmap.",
  },
  {
    id: "planned-integrations",
    category: "Prototype Capabilities",
    question: "Which data integrations are still planned?",
    answer:
      "Satellite thermal/chlorophyll layers, authoritative Marine Protected Area (MPA) GIS baselines, certified port authority bulletin ingest, and direct vessel tracking are currently unintegrated and scheduled for Phase 6 and future expansions.",
  },
  {
    id: "available-languages",
    category: "Prototype Capabilities",
    question: "Which website languages are available now?",
    answer:
      "English is currently the only active and verified website language. Additional regional languages (Hindi, Odia, Tamil, Bengali) are displayed in the language selector as Coming Soon and will be activated only after human translation review.",
  },
  {
    id: "voice-speech-status",
    category: "Prototype Capabilities",
    question: "Is voice input or spoken marine advisory synthesis available?",
    answer:
      "No. Spoken advisory synthesis across Indian dialects (Hindi, Kannada, Tamil, Telugu) is currently unintegrated and clearly marked as Coming Soon. No voice model or audio streaming API is connected in the current prototype.",
  },
  {
    id: "certified-safety-advice",
    category: "Data & Policy",
    question: "Does the prototype provide certified marine-departure safety advice?",
    answer:
      "No. Sagarvani is a technology prototype for demonstration, architectural review, and research. Marine departure risk thresholds have not undergone formal maritime authority certification and cannot replace official port clearances or Coast Guard directives.",
  },
  {
    id: "dashboard-availability",
    category: "Prototype Capabilities",
    question: "When will the interactive dashboard be available?",
    answer:
      "The interactive decision dashboard, live backend API query integration (/api/orca/query), and role-specific cockpits will be implemented in Phase 6 following completion of Phase 5 (Authentication).",
  },
];

export function FaqSection() {
  const [openIds, setOpenIds] = useState<string[]>(["what-is-sagarvani", "why-answer-withheld"]);

  const toggleFaq = (id: string) => {
    setOpenIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  return (
    <section id="faq" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory-light)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Clear Explanations
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Frequently Asked Questions
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Direct, verified answers regarding Sagarvani’s architecture, evidence standards, safety policies, and roadmap boundaries.
          </p>
        </div>

        {/* FAQ Accordion List */}
        <div className="space-y-3">
          {FAQS.map((faq, index) => {
            const isOpen = openIds.includes(faq.id);
            const contentId = `faq-content-${faq.id}`;
            const headerId = `faq-header-${faq.id}`;

            return (
              <div
                key={faq.id}
                className="rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] overflow-hidden transition-all duration-200"
              >
                <button
                  type="button"
                  id={headerId}
                  aria-expanded={isOpen}
                  aria-controls={contentId}
                  onClick={() => toggleFaq(faq.id)}
                  className="w-full p-5 text-left flex items-center justify-between gap-4 hover:bg-[var(--color-warm-ivory-light)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-[var(--color-azure-blue)]">
                      {String(index + 1).padStart(2, "0")}.
                    </span>
                    <h3 className="text-sm sm:text-base font-serif font-bold text-[var(--color-french-blue)]">
                      {faq.question}
                    </h3>
                  </div>

                  <div className={`p-1 rounded-md transition-transform duration-200 ${isOpen ? "rotate-180 text-[var(--color-azure-blue)]" : "text-[var(--color-charcoal-blue-muted)]"}`}>
                    <ChevronDown className="w-5 h-5" />
                  </div>
                </button>

                {isOpen && (
                  <div
                    id={contentId}
                    role="region"
                    aria-labelledby={headerId}
                    className="px-5 pb-5 pt-1 text-xs sm:text-sm text-[var(--color-charcoal-blue)] leading-relaxed border-t border-[var(--color-warm-ivory-dark)]/60 bg-[var(--color-warm-ivory-light)]/40"
                  >
                    <p>{faq.answer}</p>
                    <div className="pt-2 text-[10px] font-mono uppercase text-[var(--color-charcoal-blue-muted)]">
                      Domain: {faq.category}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Advisory Reminder */}
        <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] flex items-start gap-3 text-xs text-[var(--color-charcoal-blue-muted)]">
          <ShieldAlert className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
          <p>
            Have additional technical questions? Review our architectural contracts in the repository logbook and design specifications.
          </p>
        </div>

      </div>
    </section>
  );
}
