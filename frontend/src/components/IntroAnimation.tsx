"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Compass } from "lucide-react";

interface IntroAnimationProps {
  onComplete: () => void;
}

export function IntroAnimation({ onComplete }: IntroAnimationProps) {
  const [phase, setPhase] = useState<"init" | "waves" | "boat" | "flash" | "reveal">("init");
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    // Check if user prefers reduced motion
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mediaQuery.matches) {
      onComplete();
      return;
    }

    const t1 = setTimeout(() => setPhase("waves"), 150);
    const t2 = setTimeout(() => setPhase("boat"), 650);
    const t3 = setTimeout(() => setPhase("flash"), 1100);
    const t4 = setTimeout(() => setPhase("reveal"), 1450);
    const t5 = setTimeout(() => onComplete(), 1950);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
    };
  }, [onComplete]);

  // Fallback direct to hero if images fail
  if (imageError) {
    onComplete();
    return null;
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Sagarvani Brand Introduction: A light across the ocean"
      className={`fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-[var(--color-warm-ivory)] transition-opacity duration-500 ${
        phase === "reveal" ? "opacity-0 pointer-events-none" : "opacity-100"
      }`}
    >
      {/* Skip Button */}
      <div className="absolute top-6 right-6 z-50">
        <button
          type="button"
          onClick={onComplete}
          className="px-4 py-2 text-xs font-semibold uppercase tracking-wider bg-[var(--color-warm-ivory-light)] text-[var(--color-charcoal-blue)] border border-[var(--color-warm-ivory-dark)] rounded-full shadow-sm hover:bg-[var(--color-french-blue)] hover:text-[var(--color-warm-ivory)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] transition-colors"
          aria-label="Skip introductory animation"
        >
          Skip intro
        </button>
      </div>

      {/* Ocean Horizon Field */}
      <div className="relative w-full h-full flex flex-col justify-end">
        {/* Sky / Atmospheric Mist */}
        <div className="absolute inset-0 bg-gradient-to-b from-[var(--color-warm-ivory)] via-[var(--color-icy-blue-light)] to-[#AED5F5]/30 pointer-events-none" />

        {/* Central Lighthouse / Horizon Glow */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-none">
          <div className="w-16 h-16 rounded-full bg-[var(--color-warm-ivory)] shadow-[0_0_80px_rgba(79,172,229,0.35)] flex items-center justify-center border border-[var(--color-warm-ivory-dark)]">
            <Compass className="w-8 h-8 text-[var(--color-french-blue)] opacity-80" />
          </div>
          <span className="text-sm font-serif italic text-[var(--color-charcoal-blue-muted)] mt-4 tracking-wide">
            A clearer view of our ocean...
          </span>
        </div>

        {/* Waves Layer - sweeps in from left using supplied wave artwork */}
        <div
          className={`absolute bottom-0 left-0 right-0 h-64 md:h-80 w-full transition-transform duration-700 ease-out ${
            phase === "init" ? "translate-y-full opacity-0" : "translate-y-0 opacity-100"
          }`}
        >
          <div className="relative w-full h-full">
            <Image
              src="/artwork/layered-waves-haikei.svg"
              alt="Decorative ocean waves"
              fill
              className="object-cover object-top opacity-90"
              onError={() => setImageError(true)}
              priority
            />
          </div>
        </div>

        {/* Fishing Boat - enters from right using genuine supplied artwork with CSS bob */}
        <div
          className={`absolute bottom-28 md:bottom-36 right-10 md:right-32 w-36 md:w-52 h-24 md:h-36 transition-all duration-800 ease-out ${
            phase === "init" || phase === "waves"
              ? "translate-x-72 opacity-0"
              : "translate-x-0 opacity-100 animate-ocean-bob"
          }`}
        >
          <div className="relative w-full h-full rounded-lg overflow-hidden shadow-md border border-[var(--color-warm-ivory-dark)]/60 bg-[var(--color-warm-ivory-light)]">
            {/* Genuine user-supplied artwork crop: Traditional Ukiyo-e Fishing Boat at Sea.png */}
            <Image
              src="/artwork/Traditional Ukiyo-e Fishing Boat at Sea.png"
              alt="Supplied ukiyo-e fishing craft navigating coastal waves"
              fill
              className="object-cover object-center"
              onError={() => setImageError(true)}
              priority
            />
            {/* Soft lamp beacon dot positioned at vessel prow */}
            <div
              className={`absolute top-4 left-4 w-3.5 h-3.5 rounded-full transition-all duration-300 ${
                phase === "flash"
                  ? "bg-[#FFF8E7] shadow-[0_0_20px_#FFF8E7] scale-125"
                  : "bg-[var(--color-fresh-sky)] shadow-sm"
              }`}
            />
          </div>
        </div>

        {/* Single Lamp Beam Flash (CSS/SVG Light Sweep layered over boat art) */}
        {phase === "flash" && (
          <div
            className="absolute bottom-32 md:bottom-40 right-28 md:right-64 w-[500px] h-[300px] pointer-events-none origin-bottom-right animate-pulse transition-opacity duration-300 z-30"
            style={{
              background: "radial-gradient(ellipse at 100% 50%, rgba(255,248,225,0.75) 0%, rgba(79,172,229,0.35) 45%, rgba(237,228,210,0) 80%)",
              transform: "rotate(-15deg)",
            }}
          />
        )}
      </div>
    </div>
  );
}
