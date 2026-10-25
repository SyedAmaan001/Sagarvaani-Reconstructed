"use client";

import React from "react";
import Image from "next/image";
import { Map, Layers, Navigation, AlertCircle, Sparkles } from "lucide-react";

export function MapExploration() {
  return (
    <section id="map-exploration" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Spatial Intelligence
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Maps, Marine Exploration &amp; Insights
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Geographic context transforms raw weather predictions into meaningful operational boundaries. Explore how coastal bathymetry, currents, and zones intersect.
          </p>
        </div>

        {/* Illustrative Map Preview Composition */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[260px]">
            <Image
              src="/artwork/Ukiyo-e Oceanographic Archipelago Map.png"
              alt="Ukiyo-e woodblock style cartographic archipelago sea chart with depth contours and coastal soundings"
              fill
              className="object-cover object-center"
              sizes="100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/85 via-[var(--color-charcoal-blue)]/20 to-transparent" />
            
            {/* Top Status Pill */}
            <div className="absolute top-4 left-4 sm:top-6 sm:left-6">
              <span className="px-3 py-1 rounded-md bg-[var(--color-charcoal-blue)]/90 backdrop-blur-xs text-[10px] uppercase tracking-wider font-mono text-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)]/40">
                Illustrative Cartography — Geographic GIS Integration in Progress
              </span>
            </div>

            {/* Bottom Caption Overlay */}
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1.5 max-w-xl">
              <h3 className="text-xl sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                Coastal Archipelagos &amp; Bathymetric Contours
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-relaxed">
                Illustrative marine chart. Paintings are not used as live GIS layers, vessel positions, or official sanctuary boundaries.
              </p>
            </div>
          </div>
        </div>

        {/* 3 Spatial Domain Insight Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1: Coastal Baselines */}
          <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-3">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <Navigation className="w-5 h-5" />
              </div>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                Coming Soon
              </span>
            </div>
            <h4 className="text-base font-serif font-bold text-[var(--color-french-blue)]">
              Coastal Shoreline &amp; Harbor Geometry
            </h4>
            <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
              Calculates vessel distance to safe harbor, port breakwaters, and nearshore shoals to evaluate emergency return windows.
            </p>
          </div>

          {/* Card 2: Marine Protected Areas */}
          <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-3">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <Layers className="w-5 h-5" />
              </div>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                Coming Soon
              </span>
            </div>
            <h4 className="text-base font-serif font-bold text-[var(--color-french-blue)]">
              Marine Sanctuaries &amp; No-Take Zones
            </h4>
            <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
              Spatial release policy will gate potential fishing advisories, strictly withholding routing inside protected ecological boundaries.
            </p>
          </div>

          {/* Card 3: Interactive Exploration Cockpit */}
          <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-3">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-french-blue)]">
                <Map className="w-5 h-5" />
              </div>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                Phase 6 Scope
              </span>
            </div>
            <h4 className="text-base font-serif font-bold text-[var(--color-french-blue)]">
              Interactive GIS Map Workspace
            </h4>
            <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
              A vector map cockpit with bathymetric layers, coordinate inspector, and regional wave heatmaps is scheduled for the Phase 6 dashboard.
            </p>
          </div>

        </div>

        {/* Activity Terrain Notice Card */}
        <div className="p-5 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[var(--color-azure-blue)]" />
              <h4 className="text-sm font-serif font-bold text-[var(--color-french-blue)]">
                Activity Terrain &amp; Spectrum Profiles
              </h4>
            </div>
            <p className="text-xs text-[var(--color-charcoal-blue-muted)] max-w-2xl">
              Numerical wave energy spectra and live vessel telemetry will render as interactive charts only when connected to verified live sensor feeds. Unverified charts are omitted to avoid misrepresenting real marine conditions.
            </p>
          </div>

          <div className="shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs text-[var(--color-charcoal-blue-muted)]">
            <AlertCircle className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
            <span>Telemetry Charts Gated</span>
          </div>
        </div>

      </div>
    </section>
  );
}
