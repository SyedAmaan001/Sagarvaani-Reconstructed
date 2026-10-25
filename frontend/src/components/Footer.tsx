"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Compass, Shield } from "lucide-react";

export function Footer() {
  return (
    <footer className="relative w-full border-t border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-[var(--color-charcoal-blue)] overflow-hidden">
      {/* Decorative Wave Border Accent */}
      <div className="w-full h-2 relative opacity-30">
        <Image
          src="/artwork/Indigo Ukiyo-e Ocean Wave Border.png"
          alt=""
          fill
          className="object-cover object-center"
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
          
          {/* Brand Info */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[var(--color-french-blue)] flex items-center justify-center text-[var(--color-warm-ivory)] shadow-sm">
                <Compass className="w-5 h-5 stroke-[1.75]" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
                  Sagarvani
                </span>
                <span className="text-[10px] uppercase tracking-wider text-[var(--color-charcoal-blue-muted)] font-medium -mt-0.5">
                  Marine Intelligence Prototype
                </span>
              </div>
            </div>

            <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed max-w-sm">
              An open, defensible marine decision-intelligence prototype. Grounding ocean observations in physical verification, bounded recovery, and deterministic safety release gates.
            </p>

            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[11px] text-[var(--color-charcoal-blue)] font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>Phase 6 Active • Cockpit &amp; Verified Backend</span>
            </div>
          </div>

          {/* Navigation Links Column 1: Core Architecture */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)]">
              Architecture &amp; Journey
            </h4>
            <ul className="space-y-2 text-xs text-[var(--color-charcoal-blue-muted)]">
              <li>
                <a href="#home" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Platform Home
                </a>
              </li>
              <li>
                <a href="#use-cases" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Stakeholder Use Cases
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Before → Sagarvani → Outcome
                </a>
              </li>
              <li>
                <a href="#evidence" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Connected Ocean Ecosystem
                </a>
              </li>
              <li>
                <a href="#voyage" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Intelligence Voyage (4 Stages)
                </a>
              </li>
            </ul>
          </div>

          {/* Navigation Links Column 2: Deep Dive & Roadmap */}
          <div className="md:col-span-4 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)]">
              Exploration &amp; Project Info
            </h4>
            <ul className="space-y-2 text-xs text-[var(--color-charcoal-blue-muted)]">
              <li>
                <a href="#evidence-exploration" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Evidence Quality Dimensions
                </a>
              </li>
              <li>
                <a href="#scenario-replay" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Scenario Replay Comparisons
                </a>
              </li>
              <li>
                <a href="#map-exploration" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Maps &amp; Spatial Insights
                </a>
              </li>
              <li>
                <a href="#roadmap" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Ocean Roadmap (Phases 1–7)
                </a>
              </li>
              <li>
                <a href="#community" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Origin Story &amp; Community
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-[var(--color-azure-blue)] transition-colors">
                  Frequently Asked Questions
                </a>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-[var(--color-azure-blue)] transition-colors flex items-center gap-1.5 font-semibold text-[var(--color-french-blue)]">
                  <span>Operational Cockpit (Phase 6 Live)</span>
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-[var(--color-azure-blue)] transition-colors flex items-center gap-1.5 font-medium text-[var(--color-charcoal-blue-muted)]">
                  <span>Operator Sign In (Phase 5 Preview)</span>
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar: Palette Tokens & Notice */}
        <div className="pt-8 border-t border-[var(--color-warm-ivory-dark)] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[var(--color-charcoal-blue-muted)]">
          <p>© 2026 Sagarvani. Defensible marine decision-intelligence prototype.</p>
          
          <div className="flex items-center gap-3">
            <span className="font-mono text-[11px]">Design tokens: Warm Ivory • Azure • French Blue</span>
            <span>•</span>
            <span className="text-[11px]">Ukiyo-e Marine Archive</span>
          </div>
        </div>

        {/* Regulatory & Safety Prototype Disclaimer */}
        <div className="p-4 rounded-xl bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] flex items-start gap-3 text-[11px] text-[var(--color-charcoal-blue-muted)] leading-relaxed">
          <Shield className="w-4 h-4 text-[var(--color-french-blue)] shrink-0 mt-0.5" />
          <p>
            <strong>Advisory Notice:</strong> Sagarvani is an experimental prototype created for architectural demonstration and research. Marine departure limits are unapproved and do not substitute for certified port clearance directives or official maritime safety guidance.
          </p>
        </div>
      </div>
    </footer>
  );
}
