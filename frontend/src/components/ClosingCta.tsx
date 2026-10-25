"use client";

import React, { useState } from "react";
import Image from "next/image";
import { ArrowUp, AlertCircle, Sparkles } from "lucide-react";

interface ClosingCtaProps {
  onAskClick?: () => void;
}

export function ClosingCta({ onAskClick }: ClosingCtaProps) {
  const [notice, setNotice] = useState<string | null>(null);

  const handleAsk = () => {
    if (onAskClick) {
      onAskClick();
    } else {
      setNotice("The interactive 'Ask Sagarvani' decision workspace integrates into the Phase 6 dashboard.");
    }
  };

  const handleScrollTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <section className="relative w-full py-20 md:py-32 bg-[var(--color-warm-ivory)] overflow-hidden border-t border-[var(--color-warm-ivory-dark)]">
      {/* Decorative Wave Border at top */}
      <div className="absolute top-0 inset-x-0 h-4 pointer-events-none opacity-40">
        <Image
          src="/artwork/wave-haikei.svg"
          alt=""
          fill
          className="object-cover object-top"
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="relative rounded-3xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-lg">
          
          {/* Background Oceanic Artwork */}
          <div className="relative aspect-[21/9] sm:aspect-[2.6/1] w-full min-h-[320px]">
            <Image
              src="/artwork/Ukiyo-e Lighthouse Among Stormy Waves.png"
              alt="Ukiyo-e woodblock painting of an ocean beacon guiding vessels through turbulent seas to safety"
              fill
              className="object-cover object-center"
              sizes="100vw"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[var(--color-charcoal-blue)]/95 via-[var(--color-charcoal-blue)]/80 to-[var(--color-charcoal-blue)]/60" />

            {/* Content Overlay */}
            <div className="absolute inset-0 p-8 sm:p-12 md:p-16 flex flex-col justify-between text-[var(--color-warm-ivory)]">
              <div className="space-y-4 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)]/10 backdrop-blur-xs border border-[var(--color-warm-ivory)]/20 text-xs font-mono uppercase tracking-wider text-[var(--color-warm-ivory)]">
                  <Sparkles className="w-3.5 h-3.5 text-[var(--color-fresh-sky)]" />
                  <span>Return to the Ocean</span>
                </div>

                <h2 className="text-3xl sm:text-4xl md:text-5xl font-serif font-bold text-[var(--color-warm-ivory)] leading-tight">
                  Clearer seas ahead.
                </h2>

                <p className="text-sm sm:text-base text-[var(--color-warm-ivory)]/90 leading-relaxed max-w-xl">
                  By anchoring marine decisions to verified data, explicit uncertainty, and deterministic safety rules, Sagarvani charts a safer course for ocean communities.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="pt-6 flex flex-wrap items-center gap-4">
                <button
                  type="button"
                  onClick={handleAsk}
                  className="px-6 py-3 rounded-xl bg-[var(--color-fresh-sky)] hover:bg-[var(--color-azure-blue)] text-[var(--color-charcoal-blue)] hover:text-[var(--color-warm-ivory)] font-semibold text-sm shadow-sm transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] active:scale-95"
                >
                  Ask Sagarvani
                </button>

                <button
                  type="button"
                  onClick={handleScrollTop}
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-[var(--color-warm-ivory)]/30 bg-[var(--color-warm-ivory)]/10 hover:bg-[var(--color-warm-ivory)]/20 text-[var(--color-warm-ivory)] font-medium text-sm backdrop-blur-xs transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                >
                  <ArrowUp className="w-4 h-4" />
                  <span>Back to top</span>
                </button>
              </div>
            </div>
          </div>

        </div>

        {/* Notice Drawer */}
        {notice && (
          <div
            role="status"
            className="mt-4 p-4 rounded-xl bg-[var(--color-warm-ivory-light)] border border-[var(--color-azure-blue)]/40 flex items-start justify-between gap-3 text-sm text-[var(--color-charcoal-blue)]"
          >
            <div className="flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
              <p>{notice}</p>
            </div>
            <button
              type="button"
              onClick={() => setNotice(null)}
              className="text-xs font-semibold px-2 py-1 rounded text-[var(--color-charcoal-blue-muted)] hover:text-[var(--color-charcoal-blue)]"
            >
              Dismiss
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
