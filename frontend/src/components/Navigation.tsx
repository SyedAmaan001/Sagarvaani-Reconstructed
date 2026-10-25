"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Compass, Globe, Volume2, Menu, X, ArrowRight, Info, Lock } from "lucide-react";

interface HeaderProps {
  onAskClick?: () => void;
  onExploreClick?: () => void;
}

interface LanguageOption {
  code: string;
  label: string;
  native: string;
  status: "active" | "coming_soon";
}

const WEBSITE_LANGUAGES: LanguageOption[] = [
  { code: "en", label: "English", native: "English", status: "active" },
  { code: "hi", label: "Hindi", native: "हिन्दी", status: "coming_soon" },
  { code: "or", label: "Odia", native: "ଓଡ଼ିଆ", status: "coming_soon" },
  { code: "ta", label: "Tamil", native: "தமிழ்", status: "coming_soon" },
  { code: "bn", label: "Bengali", native: "বাংলা", status: "coming_soon" },
];

const VOICE_LANGUAGES: LanguageOption[] = [
  { code: "none", label: "Speech Engine (Coming Soon)", native: "Voice Engine", status: "coming_soon" },
  { code: "en", label: "English Speech", native: "English", status: "coming_soon" },
  { code: "hi", label: "Hindi Speech", native: "हिन्दी", status: "coming_soon" },
  { code: "kn", label: "Kannada Speech", native: "ಕನ್ನಡ", status: "coming_soon" },
  { code: "ta", label: "Tamil Speech", native: "தமிழ்", status: "coming_soon" },
  { code: "te", label: "Telugu Speech", native: "తెలుగు", status: "coming_soon" },
];

export function Header({ onExploreClick }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [websiteLang, setWebsiteLang] = useState("English");
  const [langNotice, setLangNotice] = useState<string | null>(null);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [voiceMenuOpen, setVoiceMenuOpen] = useState(false);

  const handleSelectWebsiteLang = (lang: LanguageOption) => {
    if (lang.status === "active") {
      setWebsiteLang(lang.label);
      setLangNotice(null);
    } else {
      setLangNotice(`${lang.label} (${lang.native}) interface translations are in preparation and will be available once human-reviewed.`);
    }
    setLangMenuOpen(false);
  };

  const handleSelectVoiceLang = (lang: LanguageOption) => {
    setLangNotice(`Spoken marine advisory synthesis for ${lang.label} is currently unintegrated. Voice services are Coming Soon.`);
    setVoiceMenuOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full backdrop-blur-md bg-[var(--color-warm-ivory)]/90 border-b border-[var(--color-warm-ivory-dark)] transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Brand Logo & Name */}
            <div className="flex items-center gap-3">
              <a
                href="#home"
                className="group flex items-center gap-3 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded-lg p-1"
                aria-label="Sagarvani Home"
              >
                <div className="w-10 h-10 rounded-full bg-[var(--color-french-blue)] flex items-center justify-center text-[var(--color-warm-ivory)] shadow-sm group-hover:bg-[var(--color-azure-blue)] transition-colors">
                  <Compass className="w-6 h-6 stroke-[1.75]" />
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
                    Sagarvani
                  </span>
                  <span className="text-[11px] uppercase tracking-wider text-[var(--color-charcoal-blue-muted)] font-medium -mt-1">
                    Marine Intelligence
                  </span>
                </div>
              </a>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-6" aria-label="Main Navigation">
              <a
                href="#home"
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                Platform
              </a>
              <a
                href="#use-cases"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                Use cases
              </a>
              <a
                href="#how-it-works"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                How it works
              </a>
              <a
                href="#voyage"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                Voyage
              </a>
              <a
                href="#evidence"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                Evidence
              </a>
              <a
                href="#roadmap"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                Roadmap
              </a>
              <a
                href="#community"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                Community
              </a>
              <a
                href="#faq"
                onClick={onExploreClick}
                className="text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1"
              >
                FAQ
              </a>
              <Link
                href="/dashboard"
                className="text-sm font-semibold text-[var(--color-french-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded px-2 py-1 flex items-center gap-1"
              >
                <span>Cockpit</span>
                <span className="text-[10px] font-mono uppercase bg-[var(--color-french-blue)]/10 text-[var(--color-french-blue)] px-1.5 py-0.2 rounded">
                  Live
                </span>
              </Link>
            </nav>

            {/* Right Action / Controls */}
            <div className="hidden md:flex items-center gap-3">
              {/* Website Language Selector */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setLangMenuOpen(!langMenuOpen);
                    setVoiceMenuOpen(false);
                  }}
                  className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-md border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-[var(--color-charcoal-blue)] hover:border-[var(--color-azure-blue)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                  aria-expanded={langMenuOpen}
                  aria-label="Select website language"
                >
                  <Globe className="w-3.5 h-3.5 text-[var(--color-french-blue)]" />
                  <span>{websiteLang}</span>
                  <span className="text-[10px] text-[var(--color-charcoal-blue-muted)]">▾</span>
                </button>

                {langMenuOpen && (
                  <div className="absolute right-0 mt-1 w-56 rounded-md bg-[var(--color-warm-ivory-light)] shadow-lg ring-1 ring-black/5 py-1 z-50 border border-[var(--color-warm-ivory-dark)]">
                    <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)] border-b border-[var(--color-warm-ivory-dark)] flex items-center justify-between">
                      <span>Website Language</span>
                      <span className="text-[9px] lowercase font-normal">reviewed only</span>
                    </div>
                    {WEBSITE_LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        type="button"
                        onClick={() => handleSelectWebsiteLang(lang)}
                        className="w-full text-left px-3 py-1.5 text-xs text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)] hover:text-[var(--color-azure-blue)] transition-colors flex items-center justify-between"
                      >
                        <span>
                          {lang.label} <span className="text-[10px] text-[var(--color-charcoal-blue-muted)]">({lang.native})</span>
                        </span>
                        {lang.status === "active" ? (
                          <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-[var(--color-french-blue)]/10 text-[var(--color-french-blue)] font-semibold">Active</span>
                        ) : (
                          <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)] font-medium">Soon</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Voice Language Selector */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setVoiceMenuOpen(!voiceMenuOpen);
                    setLangMenuOpen(false);
                  }}
                  className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-md border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-[var(--color-charcoal-blue)] hover:border-[var(--color-azure-blue)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                  aria-expanded={voiceMenuOpen}
                  aria-label="Select spoken dialect"
                >
                  <Volume2 className="w-3.5 h-3.5 text-[var(--color-french-blue)]" />
                  <span>Voice: Soon</span>
                  <span className="text-[10px] text-[var(--color-charcoal-blue-muted)]">▾</span>
                </button>

                {voiceMenuOpen && (
                  <div className="absolute right-0 mt-1 w-64 rounded-md bg-[var(--color-warm-ivory-light)] shadow-lg ring-1 ring-black/5 py-1 z-50 border border-[var(--color-warm-ivory-dark)]">
                    <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)] border-b border-[var(--color-warm-ivory-dark)] flex items-center justify-between">
                      <span>Speech Engine</span>
                      <span className="text-[9px] text-[var(--color-azure-blue)] font-medium">Coming Soon</span>
                    </div>
                    {VOICE_LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        type="button"
                        onClick={() => handleSelectVoiceLang(lang)}
                        className="w-full text-left px-3 py-1.5 text-xs text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)] hover:text-[var(--color-azure-blue)] transition-colors flex items-center justify-between"
                      >
                        <span>{lang.label}</span>
                        <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">Unconnected</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Sign In Link (Phase 5) */}
              <Link
                href="/login"
                className="text-xs font-semibold px-3 py-1.5 rounded-md border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-[var(--color-charcoal-blue)] hover:border-[var(--color-azure-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] flex items-center gap-1.5"
              >
                <Lock className="w-3.5 h-3.5 text-[var(--color-french-blue)]" />
                <span>Sign In</span>
              </Link>

              {/* Primary Action Button */}
              <Link
                href="/dashboard"
                className="ml-1 inline-flex items-center gap-2 bg-[var(--color-french-blue)] hover:bg-[var(--color-azure-blue)] text-[var(--color-warm-ivory)] px-4 py-2 rounded-md font-medium text-sm shadow-sm transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] active:scale-95"
              >
                <span>Ask Sagarvani</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <div className="flex md:hidden items-center gap-2">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-md text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-dark)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] px-4 pt-3 pb-6 space-y-4">
            <nav className="flex flex-col space-y-2">
              <a
                href="#home"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                Platform
              </a>
              <a
                href="#use-cases"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                Use cases
              </a>
              <a
                href="#how-it-works"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                How it works
              </a>
              <a
                href="#voyage"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                Voyage
              </a>
              <a
                href="#evidence"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                Evidence
              </a>
              <a
                href="#roadmap"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                Roadmap
              </a>
              <a
                href="#community"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                Community
              </a>
              <a
                href="#faq"
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onExploreClick) onExploreClick();
                }}
                className="px-3 py-2 rounded-md text-base font-medium text-[var(--color-charcoal-blue)] hover:bg-[var(--color-icy-blue-light)]"
              >
                FAQ
              </a>
            </nav>

            <div className="pt-3 border-t border-[var(--color-warm-ivory-dark)] space-y-3">
              <div className="flex items-center justify-between text-xs text-[var(--color-charcoal-blue)]">
                <span className="font-medium flex items-center gap-1.5">
                  <Globe className="w-4 h-4 text-[var(--color-french-blue)]" /> Website Language:
                </span>
                <span className="px-2 py-1 rounded bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] font-medium">
                  English (Only active)
                </span>
              </div>

              <div className="flex items-center justify-between text-xs text-[var(--color-charcoal-blue)]">
                <span className="font-medium flex items-center gap-1.5">
                  <Volume2 className="w-4 h-4 text-[var(--color-french-blue)]" /> Spoken Dialect:
                </span>
                <span className="px-2 py-1 rounded bg-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)] font-medium">
                  Voice Coming Soon
                </span>
              </div>

              <div className="pt-2 space-y-2">
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full flex items-center justify-center gap-2 border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-[var(--color-charcoal-blue)] px-4 py-2.5 rounded-md font-medium text-sm shadow-xs hover:border-[var(--color-azure-blue)]"
                >
                  <Lock className="w-4 h-4 text-[var(--color-french-blue)]" />
                  <span>Operator Sign In (Preview)</span>
                </Link>

                <Link
                  href="/dashboard"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full flex items-center justify-center gap-2 bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] px-4 py-2.5 rounded-md font-medium text-sm shadow-sm"
                >
                  <span>Ask Sagarvani (Cockpit)</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Language Status Notice Banner */}
      {langNotice && (
        <div
          role="status"
          className="bg-[var(--color-icy-blue-light)] border-b border-[var(--color-fresh-sky)]/30 px-4 py-2.5 text-xs text-[var(--color-charcoal-blue)] flex items-center justify-between"
        >
          <div className="max-w-7xl mx-auto flex items-center gap-2">
            <Info className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0" />
            <span>{langNotice}</span>
          </div>
          <button
            type="button"
            onClick={() => setLangNotice(null)}
            className="text-xs font-semibold px-2 py-0.5 rounded hover:bg-[var(--color-warm-ivory)]"
          >
            Dismiss
          </button>
        </div>
      )}
    </>
  );
}
