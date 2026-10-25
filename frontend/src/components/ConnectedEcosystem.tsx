"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Waves, Wind, Satellite, MapPin, CheckCircle2, Clock } from "lucide-react";

interface DomainInfo {
  id: string;
  title: string;
  subtitle: string;
  status: "prototype_adapter" | "extension_planned";
  metrics: string[];
  description: string;
  provenanceNote: string;
  icon: React.ElementType;
}

const DOMAINS: DomainInfo[] = [
  {
    id: "marine",
    title: "Marine & Wave Observations",
    subtitle: "In-situ & forecast wave states",
    status: "prototype_adapter",
    metrics: ["Significant Wave Height (SWH)", "Mean Wave Period", "Sea Surface Temperature"],
    description: "Captures wave dynamics and swell dispersion models. Values require verifiable observation and issue timestamps before being released to decision logic.",
    provenanceNote: "Open-Meteo Marine / INCOIS OSF gateway format.",
    icon: Waves,
  },
  {
    id: "weather",
    title: "Weather & Wind Fields",
    subtitle: "Atmospheric vectors & gust hazards",
    status: "prototype_adapter",
    metrics: ["10m Wind Speed & Gusts", "Wind Direction Vectors", "Barometric Pressure"],
    description: "Monitors cyclonic circulation, localized squalls, and coastal wind gradients. Wind speed thresholds are bound directly to small-craft operational limits.",
    provenanceNote: "Open-Meteo Weather / IMD bulletin mapping.",
    icon: Wind,
  },
  {
    id: "satellite",
    title: "Satellite Observations",
    subtitle: "Thermal & chlorophyll overlays",
    status: "extension_planned",
    metrics: ["Sea Surface Chlorophyll", "Ocean Frontal Gradients", "Thermal Composite Anomaly"],
    description: "Synoptic sea surface imagery provides broad environmental context for potential fishing zone (PFZ) analysis once certified high-resolution pipelines are integrated.",
    provenanceNote: "Requires verified spatial geometry pipeline (Coming Soon).",
    icon: Satellite,
  },
  {
    id: "geospatial",
    title: "Geospatial & Coastal Context",
    subtitle: "Jurisdictions & bathymetry",
    status: "extension_planned",
    metrics: ["Coastal Water Baselines", "Marine Protected Area (MPA) Boundaries", "Port Harbor Geometry"],
    description: "Spatial boundaries prevent advisories from recommending activities inside marine sanctuaries or restricted maritime traffic channels.",
    provenanceNote: "Requires certified GIS boundary licensing (Currently NOT_EVALUABLE in release policy).",
    icon: MapPin,
  },
];

export function ConnectedEcosystem() {
  const [activeDomain, setActiveDomain] = useState<DomainInfo>(DOMAINS[0]);

  return (
    <section id="evidence" className="relative w-full py-16 md:py-24 bg-[var(--color-warm-ivory)] border-t border-[var(--color-warm-ivory-dark)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
            Connected Architecture
          </div>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
            Connected Ocean Ecosystem
          </h2>
          <p className="text-base sm:text-lg text-[var(--color-charcoal-blue-muted)] leading-relaxed">
            Sound marine intelligence cannot rely on a single isolated sensor. Sagarvani connects disparate meteorological, oceanographic, and geospatial information domains into a verifiable decision framework.
          </p>
        </div>

        {/* Hero Artwork Composition */}
        <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-sm">
          <div className="relative aspect-[21/9] sm:aspect-[2.4/1] w-full min-h-[220px]">
            <Image
              src="/artwork/Ukiyo-e Coastal Village with Satellite Arcs.png"
              alt="Ukiyo-e coastal landscape with subtle cartographic satellite arcs connecting ocean observations"
              fill
              className="object-cover object-center"
              sizes="100vw"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/80 via-transparent to-transparent" />
            
            <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-6 text-[var(--color-warm-ivory)] space-y-1 max-w-xl">
              <span className="px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)] text-[9px] uppercase tracking-wider font-mono">
                Illustrative Marine Cartography
              </span>
              <h3 className="text-lg sm:text-2xl font-serif font-bold text-[var(--color-warm-ivory)]">
                Observation Networks & Synoptic Linkages
              </h3>
              <p className="text-xs sm:text-sm text-[var(--color-warm-ivory)]/90 leading-normal">
                Disparate sources are aligned along common spatial coordinates and verified timestamps before policy evaluation.
              </p>
            </div>
          </div>
        </div>

        {/* 4 Information Domains Grid & Interactive Detail Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Domain Selection Tabs / Cards */}
          <div className="lg:col-span-6 space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
              Select an Information Domain
            </span>
            <div className="space-y-3">
              {DOMAINS.map((domain) => {
                const Icon = domain.icon;
                const isSelected = activeDomain.id === domain.id;
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => setActiveDomain(domain)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-200 flex items-start gap-4 ${
                      isSelected
                        ? "border-[var(--color-azure-blue)] bg-[var(--color-warm-ivory-light)] shadow-sm ring-1 ring-[var(--color-azure-blue)]/30"
                        : "border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] hover:bg-[var(--color-warm-ivory-light)] hover:border-[var(--color-azure-blue)]/50"
                    }`}
                  >
                    <div
                      className={`p-2.5 rounded-lg shrink-0 ${
                        isSelected
                          ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)]"
                          : "bg-[var(--color-warm-ivory-dark)]/60 text-[var(--color-charcoal-blue)]"
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>

                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-serif font-bold text-[var(--color-french-blue)] truncate">
                          {domain.title}
                        </h4>
                        {domain.status === "prototype_adapter" ? (
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                            Prototype adapter implemented
                          </span>
                        ) : (
                          <span className="text-[10px] uppercase font-medium tracking-wider px-2 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                            Coming Soon
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[var(--color-charcoal-blue-muted)]">
                        {domain.subtitle}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Domain Detail Card */}
          <div className="lg:col-span-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] p-6 space-y-6 shadow-xs">
            <div className="flex items-start justify-between border-b border-[var(--color-warm-ivory-dark)] pb-4">
              <div className="space-y-1">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--color-azure-blue)]">
                  Domain Profile
                </span>
                <h4 className="text-xl font-serif font-bold text-[var(--color-french-blue)]">
                  {activeDomain.title}
                </h4>
              </div>
              <div className="p-2 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)]">
                <activeDomain.icon className="w-6 h-6 text-[var(--color-french-blue)]" />
              </div>
            </div>

            <p className="text-sm text-[var(--color-charcoal-blue)] leading-relaxed">
              {activeDomain.description}
            </p>

            {/* Metrics List */}
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
                Primary Monitored Metrics
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {activeDomain.metrics.map((m) => (
                  <div
                    key={m}
                    className="flex items-center gap-2 p-2 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs text-[var(--color-charcoal-blue)]"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-[var(--color-azure-blue)] shrink-0" />
                    <span>{m}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Provenance & Gate Notice */}
            <div className="p-3.5 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] space-y-1.5 text-xs text-[var(--color-charcoal-blue-muted)]">
              <div className="flex items-center gap-1.5 font-semibold text-[var(--color-charcoal-blue)]">
                <Clock className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                <span>Lineage & Policy Status</span>
              </div>
              <p>{activeDomain.provenanceNote}</p>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
