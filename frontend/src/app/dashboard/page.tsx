"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  Compass,
  ArrowLeft,
  Send,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  WifiOff,
  Loader2,
  ChevronDown,
  ChevronUp,
  Database,
  ShieldAlert,
  BarChart3,
  MapPin,
  RefreshCw,
  Lock,
  ExternalLink,
  Sliders,
  FileText,
  AlertCircle,
} from "lucide-react";
import {
  checkHealth,
  submitQuery,
  type CanonicalQueryResponse,
  type CanonicalQueryRequest,
  type StakeholderRole,
  type PresentationMode,
  type ApiError,
  type OverallGateVerdict,
  type RunStatus,
} from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

type QueryState =
  | { phase: "idle" }
  | { phase: "loading" }
  | { phase: "success"; response: CanonicalQueryResponse }
  | { phase: "error"; error: ApiError };

type BackendStatus =
  | { phase: "checking" }
  | { phase: "online"; version: string; app: string }
  | { phase: "offline"; message: string };

const STAKEHOLDER_OPTIONS: { value: StakeholderRole; label: string; desc: string }[] = [
  {
    value: "fisherman_community",
    label: "Artisanal & Small-Craft Fisher",
    desc: "Swell window, wave-period cautions, and high-contrast coastal safety summaries.",
  },
  {
    value: "port_operator",
    label: "Port Officer & Maritime Authority",
    desc: "Vessel transit thresholds, berthing wave envelopes, and harbour surge telemetry.",
  },
  {
    value: "scientist_researcher",
    label: "Marine Scientist & Oceanographer",
    desc: "Full evidence parameter matrices, sensor lineage, and model run provenance.",
  },
  {
    value: "disaster_management",
    label: "Disaster Management Authority",
    desc: "Coastal storm surge indicators, squall envelopes, and civil defense advisories.",
  },
  {
    value: "aquaculture_farmer",
    label: "Aquaculture & Mariculture Farmer",
    desc: "Sea surface temperature, cage stress factors, and sheltered bay dynamics.",
  },
  {
    value: "coastal_tourism",
    label: "Coastal Tourism & Water Sports",
    desc: "Beach bathing safety, surf conditions, and nearshore wind hazards.",
  },
  {
    value: "offshore_industry",
    label: "Offshore Industry & Tug Fleet",
    desc: "Deepwater wave regimes, significant wave height matrices, and operational windows.",
  },
  {
    value: "marine_conservation",
    label: "Marine Conservation & Protected Waters",
    desc: "Ecosystem boundary compliance and environmental monitoring lineage.",
  },
];

const PRESET_QUERIES = [
  {
    title: "Malpe Artisanal Fleet",
    query: "Is it safe for a motorized artisanal canoe to fish near Malpe harbour today?",
    lat: 13.35,
    lon: 74.70,
    name: "Malpe Harbour, Karnataka",
    role: "fisherman_community" as StakeholderRole,
  },
  {
    title: "Chennai Port Inbound",
    query: "What are the significant wave heights and wind gusts for berthing at Chennai Port?",
    lat: 13.08,
    lon: 80.28,
    name: "Chennai Port, Tamil Nadu",
    role: "port_operator" as StakeholderRole,
  },
  {
    title: "Kochi Oceanographic Analysis",
    query: "Provide comprehensive marine and meteorological evidence for Kochi coastal waters.",
    lat: 9.96,
    lon: 76.24,
    name: "Kochi Harbour, Kerala",
    role: "scientist_researcher" as StakeholderRole,
  },
  {
    title: "Paradip Surge Assessment",
    query: "Evaluate coastal squall and wave surge risks for small craft near Paradip Port.",
    lat: 20.26,
    lon: 86.61,
    name: "Paradip Port, Odisha",
    role: "disaster_management" as StakeholderRole,
  },
];

function formatVerdictBadge(verdict: OverallGateVerdict) {
  if (verdict === "PASS") {
    return {
      bg: "bg-emerald-50 text-emerald-900 border-emerald-300",
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />,
      text: "GATE PERMITTED (PASS)",
    };
  }
  if (verdict === "BLOCK") {
    return {
      bg: "bg-red-50 text-red-900 border-red-300",
      icon: <XCircle className="w-4 h-4 text-red-600 shrink-0" />,
      text: "GATE VETOED (BLOCK)",
    };
  }
  return {
    bg: "bg-amber-50 text-amber-950 border-amber-300",
    icon: <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" />,
    text: "INDEPENDENT SAFETY HOLD (NOT_EVALUABLE)",
  };
}

function formatRunStatus(status: RunStatus) {
  const styles: Record<RunStatus, { bg: string; text: string }> = {
    COMPLETED: { bg: "bg-emerald-100 text-emerald-900 border-emerald-300", text: "COMPLETED" },
    PARTIAL: { bg: "bg-amber-100 text-amber-950 border-amber-300", text: "PARTIAL EVIDENCE" },
    SOURCE_UNAVAILABLE: { bg: "bg-slate-100 text-slate-800 border-slate-300", text: "SOURCE UNAVAILABLE" },
    INSUFFICIENT_EVIDENCE: { bg: "bg-orange-100 text-orange-950 border-orange-300", text: "INSUFFICIENT EVIDENCE" },
    CLARIFICATION_REQUIRED: { bg: "bg-blue-100 text-blue-900 border-blue-300", text: "CLARIFICATION REQUIRED" },
    BLOCKED: { bg: "bg-red-100 text-red-900 border-red-300", text: "RELEASE BLOCKED" },
    FAILED: { bg: "bg-red-100 text-red-900 border-red-300", text: "EXECUTION FAILED" },
    TIMED_OUT: { bg: "bg-slate-100 text-slate-800 border-slate-300", text: "TIMED OUT" },
  };
  return styles[status] ?? { bg: "bg-slate-100 text-slate-800 border-slate-300", text: status };
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, accessToken, userRole, signOut } = useAuth();

  // Operational state
  const [stakeholderRole, setStakeholderRole] = useState<StakeholderRole>("fisherman_community");
  const [presentationMode, setPresentationMode] = useState<PresentationMode>("field_community");
  const [queryText, setQueryText] = useState("Is it safe for a motorized artisanal canoe to fish near Malpe harbour today?");
  const [lat, setLat] = useState("13.35");
  const [lon, setLon] = useState("74.70");
  const [locationName, setLocationName] = useState("Malpe Harbour, Karnataka");

  // Query and backend state
  const [queryState, setQueryState] = useState<QueryState>({ phase: "idle" });
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({ phase: "checking" });
  const [activeTab, setActiveTab] = useState<"advisory" | "evidence" | "policy" | "diagnostics">("advisory");
  const [expandedPolicyCheck, setExpandedPolicyCheck] = useState<string | null>(null);

  // Health check handler
  const performHealthCheck = useCallback(async () => {
    setBackendStatus({ phase: "checking" });
    const res = await checkHealth();
    if (res.ok) {
      setBackendStatus({
        phase: "online",
        version: res.data.version || "0.1.0",
        app: res.data.app || "Sagarvani Decision Core",
      });
    } else {
      setBackendStatus({
        phase: "offline",
        message: res.error.message || "Backend unreachable at http://localhost:8000",
      });
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    checkHealth().then((res) => {
      if (!isMounted) return;
      if (res.ok) {
        setBackendStatus({
          phase: "online",
          version: res.data.version || "0.1.0",
          app: res.data.app || "Sagarvani Decision Core",
        });
      } else {
        setBackendStatus({
          phase: "offline",
          message: res.error.message || "Backend unreachable at http://localhost:8000",
        });
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  // Handle Query Submission
  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryText.trim()) return;

    setQueryState({ phase: "loading" });

    const parsedLat = parseFloat(lat);
    const parsedLon = parseFloat(lon);

    const payload: CanonicalQueryRequest = {
      query: queryText.trim(),
      stakeholder_role: stakeholderRole,
      presentation_mode: presentationMode,
      context_override: {
        location: {
          lat: isNaN(parsedLat) ? 13.35 : parsedLat,
          lon: isNaN(parsedLon) ? 74.70 : parsedLon,
          location_name: locationName.trim() || undefined,
        },
      },
    };

    const res = await submitQuery(payload, accessToken);
    if (res.ok) {
      setQueryState({ phase: "success", response: res.data });
      // Keep user on the relevant tab or default to advisory
    } else {
      setQueryState({ phase: "error", error: res.error });
    }
  };

  const applyPreset = (preset: typeof PRESET_QUERIES[0]) => {
    setQueryText(preset.query);
    setLat(preset.lat.toString());
    setLon(preset.lon.toString());
    setLocationName(preset.name);
    setStakeholderRole(preset.role);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-warm-ivory)] text-[var(--color-charcoal-blue)] selection:bg-[var(--color-icy-blue)] selection:text-[var(--color-charcoal-blue)]">
      
      {/* Top Workspace Header */}
      <header className="sticky top-0 z-30 w-full border-b border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)]/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Brand & Return Navigation */}
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="group flex items-center gap-1.5 text-xs font-semibold text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded-lg px-2 py-1"
              aria-label="Return to public homepage"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
              <span className="hidden sm:inline">Platform Home</span>
            </Link>

            <span className="text-[var(--color-warm-ivory-dark)]">|</span>

            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[var(--color-french-blue)] flex items-center justify-center text-[var(--color-warm-ivory)] shadow-xs">
                <Compass className="w-4 h-4" />
              </div>
              <div className="flex flex-col">
                <span className="text-base font-serif font-bold text-[var(--color-french-blue)] leading-tight">
                  Sagarvani
                </span>
                <span className="text-[10px] uppercase font-mono tracking-wider text-[var(--color-charcoal-blue-muted)] leading-none">
                  Cockpit
                </span>
              </div>
            </div>
          </div>

          {/* Center: Live Gateway Health Badge */}
          <div className="flex items-center gap-2">
            {backendStatus.phase === "checking" && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-xs text-[var(--color-charcoal-blue-muted)]">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-[var(--color-azure-blue)]" />
                <span className="hidden md:inline">Probing Gateway...</span>
              </div>
            )}
            {backendStatus.phase === "online" && (
              <button
                type="button"
                onClick={performHealthCheck}
                className="group flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-300 text-emerald-950 text-xs font-medium hover:bg-emerald-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600"
                title="Backend online. Click to refresh status."
              >
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
                <span className="font-mono text-[11px]">API Online ({backendStatus.version})</span>
                <RefreshCw className="w-3 h-3 text-emerald-700 opacity-60 group-hover:rotate-180 transition-transform" />
              </button>
            )}
            {backendStatus.phase === "offline" && (
              <button
                type="button"
                onClick={performHealthCheck}
                className="group flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 border border-amber-300 text-amber-950 text-xs font-medium hover:bg-amber-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-600"
                title="Backend offline. Click to retry connection."
              >
                <WifiOff className="w-3.5 h-3.5 text-amber-700 shrink-0" />
                <span className="hidden sm:inline font-mono text-[11px]">Backend Offline</span>
                <RefreshCw className="w-3 h-3 text-amber-700 opacity-70 group-hover:rotate-180 transition-transform" />
              </button>
            )}
          </div>

          {/* Right: Presentation Mode Toggle & Auth State */}
          <div className="flex items-center gap-3">
            {/* View Mode Segment Switcher */}
            <div className="inline-flex rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setPresentationMode("field_community")}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  presentationMode === "field_community"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-xs"
                    : "text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)]"
                }`}
              >
                Field View
              </button>
              <button
                type="button"
                onClick={() => setPresentationMode("professional_analysis")}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  presentationMode === "professional_analysis"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-xs"
                    : "text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)]"
                }`}
              >
                Analysis View
              </button>
            </div>

            {/* Auth State Indicator */}
            {user ? (
              <div className="hidden lg:flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-emerald-300 bg-emerald-50 text-xs text-emerald-900">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="font-mono truncate max-w-[120px]" title={user.email ?? ""}>
                    {user.email ?? "Operator"}
                  </span>
                  {userRole && (
                    <span className="ml-1 px-1.5 py-0.5 rounded bg-emerald-100 text-[10px] font-semibold uppercase tracking-wide border border-emerald-200">
                      {userRole.replace(/_/g, " ")}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={async () => { await signOut(); router.push("/login"); }}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-md border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-xs text-[var(--color-charcoal-blue-muted)] hover:border-red-300 hover:text-red-700 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
                >
                  <Lock className="w-3 h-3" />
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-xs text-[var(--color-charcoal-blue-muted)] hover:border-[var(--color-azure-blue)] hover:text-[var(--color-charcoal-blue)] transition-colors"
              >
                <Lock className="w-3 h-3" />
                <span>Sign In</span>
              </Link>
            )}
          </div>

        </div>
      </header>

      {/* Prototype Governance Notice Banner */}
      <div className="w-full bg-amber-50/80 border-b border-amber-200 py-2 px-4 text-xs text-amber-950">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0" />
            <span>
              <strong>Operational Workspace Preview:</strong> Queries execute against the canonical ORCA FSM and Open-Meteo marine/weather gateways. Missing authoritative sources enforce an independent safety hold.
            </span>
          </div>
          <span className="font-mono text-[10px] uppercase text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
            Phase 6 • Real Backend Wire
          </span>
        </div>
      </div>

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column (5 Cols): Query Formulation & Stakeholder Controls */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Query Form Box */}
            <section
              aria-labelledby="query-controls-heading"
              className="p-5 sm:p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-xs space-y-5"
            >
              <div className="flex items-center justify-between border-b border-[var(--color-warm-ivory-dark)] pb-3">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-[var(--color-french-blue)]" />
                  <h2 id="query-controls-heading" className="text-sm font-serif font-bold uppercase tracking-wider text-[var(--color-french-blue)]">
                    Query &amp; Envelope Setup
                  </h2>
                </div>
                <span className="text-[10px] font-mono uppercase bg-[var(--color-warm-ivory)] px-2 py-0.5 rounded border border-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue-muted)]">
                  FSM / ORCA DAG
                </span>
              </div>

              <form onSubmit={handleQuerySubmit} className="space-y-4">
                
                {/* Stakeholder Role Dropdown */}
                <div className="space-y-1">
                  <label htmlFor="stakeholder-select" className="block text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]">
                    Stakeholder Persona
                  </label>
                  <select
                    id="stakeholder-select"
                    value={stakeholderRole}
                    onChange={(e) => setStakeholderRole(e.target.value as StakeholderRole)}
                    className="w-full px-3 py-2 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-xs text-[var(--color-charcoal-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)]"
                  >
                    {STAKEHOLDER_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                  <p className="text-[11px] text-[var(--color-charcoal-blue-muted)] leading-tight">
                    {STAKEHOLDER_OPTIONS.find((o) => o.value === stakeholderRole)?.desc}
                  </p>
                </div>

                {/* Location & Coordinates Input */}
                <div className="space-y-2 pt-1">
                  <div className="flex items-center justify-between">
                    <label htmlFor="location-name-input" className="block text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]">
                      Target Coastal Location
                    </label>
                    <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] font-mono">
                      WGS-84 Decimal
                    </span>
                  </div>
                  <input
                    id="location-name-input"
                    type="text"
                    value={locationName}
                    onChange={(e) => setLocationName(e.target.value)}
                    placeholder="e.g. Malpe Harbour, Karnataka"
                    className="w-full px-3 py-2 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-xs text-[var(--color-charcoal-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)]"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label htmlFor="lat-input" className="block text-[10px] font-medium text-[var(--color-charcoal-blue-muted)] mb-0.5">
                        Latitude (°N)
                      </label>
                      <input
                        id="lat-input"
                        type="number"
                        step="0.0001"
                        value={lat}
                        onChange={(e) => setLat(e.target.value)}
                        className="w-full px-3 py-1.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-xs font-mono text-[var(--color-charcoal-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)]"
                      />
                    </div>
                    <div>
                      <label htmlFor="lon-input" className="block text-[10px] font-medium text-[var(--color-charcoal-blue-muted)] mb-0.5">
                        Longitude (°E)
                      </label>
                      <input
                        id="lon-input"
                        type="number"
                        step="0.0001"
                        value={lon}
                        onChange={(e) => setLon(e.target.value)}
                        className="w-full px-3 py-1.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-xs font-mono text-[var(--color-charcoal-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)]"
                      />
                    </div>
                  </div>
                </div>

                {/* Natural Language Query Text */}
                <div className="space-y-1.5 pt-1">
                  <label htmlFor="query-textarea" className="block text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]">
                    Inquiry / Decision Question
                  </label>
                  <textarea
                    id="query-textarea"
                    rows={3}
                    value={queryText}
                    onChange={(e) => setQueryText(e.target.value)}
                    placeholder="Ask about swell, wind shifts, or operational safety..."
                    className="w-full px-3 py-2 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-xs text-[var(--color-charcoal-blue)] leading-relaxed focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)] resize-none"
                  />
                </div>

                {/* Submit Action Button */}
                <button
                  type="submit"
                  disabled={queryState.phase === "loading"}
                  className="w-full py-3 px-4 rounded-xl bg-[var(--color-french-blue)] hover:bg-[var(--color-azure-blue)] text-[var(--color-warm-ivory)] font-medium text-xs sm:text-sm shadow-sm transition-all flex items-center justify-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {queryState.phase === "loading" ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Executing FSM &amp; Open-Meteo Retrieval...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Execute Query &amp; Evaluate Gate</span>
                    </>
                  )}
                </button>
              </form>

              {/* Quick Preset Buttons */}
              <div className="space-y-2 pt-2 border-t border-[var(--color-warm-ivory-dark)]">
                <span className="block text-[10px] font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)]">
                  Quick Port &amp; Fleet Presets
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {PRESET_QUERIES.map((preset) => (
                    <button
                      key={preset.title}
                      type="button"
                      onClick={() => applyPreset(preset)}
                      className="text-left p-2.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] hover:border-[var(--color-azure-blue)] hover:bg-[var(--color-icy-blue-light)] transition-colors group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-[var(--color-french-blue)] group-hover:text-[var(--color-azure-blue)]">
                          {preset.title}
                        </span>
                        <MapPin className="w-3 h-3 text-[var(--color-charcoal-blue-muted)] group-hover:text-[var(--color-azure-blue)]" />
                      </div>
                      <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] line-clamp-1 mt-0.5">
                        {preset.name}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

            </section>

            {/* Illustrative Ocean Map Surface */}
            <section
              aria-label="Coastal Marine Cartography Context"
              className="rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] p-3 shadow-xs space-y-3"
            >
              <div className="relative aspect-[16/10] w-full rounded-xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)]">
                <Image
                  src="/artwork/Ukiyo-e Oceanographic Archipelago Map.png"
                  alt="Ukiyo-e Oceanographic Archipelago Map showing coastal bathymetry, current contours, and navigational depth lines"
                  fill
                  className="object-cover object-center"
                  sizes="(max-width: 1024px) 100vw, 40vw"
                />
                
                {/* Location Marker Overlay */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="flex flex-col items-center">
                    <div className="w-6 h-6 rounded-full bg-[var(--color-azure-blue)]/80 border-2 border-[var(--color-warm-ivory)] flex items-center justify-center text-[var(--color-warm-ivory)] shadow-lg animate-bounce">
                      <MapPin className="w-3.5 h-3.5" />
                    </div>
                    <span className="mt-1 px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)]/90 text-[10px] font-mono text-[var(--color-warm-ivory)] shadow-md">
                      {lat}°N, {lon}°E
                    </span>
                  </div>
                </div>

                <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-[var(--color-charcoal-blue)]/80 text-[9px] font-mono uppercase text-[var(--color-warm-ivory)]">
                  Illustrative Marine Cartography — GIS Layers In Progress
                </div>
              </div>

              <div className="px-1 text-[11px] text-[var(--color-charcoal-blue-muted)] flex items-center justify-between">
                <span>Coordinates: {lat}°N, {lon}°E</span>
                <span>Spatial Window: Coastal Nearshore (25km)</span>
              </div>
            </section>

          </div>

          {/* Right Column (7 Cols): Operational Display Stage */}
          <div className="lg:col-span-7 space-y-6">

            {/* Tab Navigation for Query Outcomes */}
            <div className="flex items-center gap-1 border-b border-[var(--color-warm-ivory-dark)] pb-2 overflow-x-auto">
              <button
                type="button"
                onClick={() => setActiveTab("advisory")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "advisory"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-xs"
                    : "text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-light)]"
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Decision &amp; Advisory</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("evidence")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "evidence"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-xs"
                    : "text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-light)]"
                }`}
              >
                <Database className="w-3.5 h-3.5" />
                <span>Evidence Records</span>
                {queryState.phase === "success" && (
                  <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-[var(--color-warm-ivory)] text-[var(--color-french-blue)] font-mono">
                    {queryState.response.evidence.length}
                  </span>
                )}
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("policy")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "policy"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-xs"
                    : "text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-light)]"
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Release Policy Gate</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("diagnostics")}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "diagnostics"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-xs"
                    : "text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-light)]"
                }`}
              >
                <BarChart3 className="w-3.5 h-3.5" />
                <span>FSM Trace &amp; Lineage</span>
              </button>
            </div>

            {/* STAGE A: Idle State */}
            {queryState.phase === "idle" && (
              <div className="p-8 sm:p-10 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] flex items-center justify-center text-[var(--color-french-blue)] mx-auto shadow-xs">
                  <Compass className="w-6 h-6 stroke-[1.5]" />
                </div>
                <div className="space-y-1.5 max-w-md mx-auto">
                  <h3 className="text-xl font-serif font-bold text-[var(--color-french-blue)]">
                    Ready for Marine Query Execution
                  </h3>
                  <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                    Select a target coastal zone and submit an operational question. Queries route through the guarded ORCA DAG, gathering real meteorological and marine forecasts, performing strict data validation, and checking the independent release gate.
                  </p>
                </div>
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => applyPreset(PRESET_QUERIES[0])}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--color-azure-blue)] hover:underline"
                  >
                    <span>Load sample query: Malpe Artisanal Fleet →</span>
                  </button>
                </div>
              </div>
            )}

            {/* STAGE B: Loading State */}
            {queryState.phase === "loading" && (
              <div className="p-10 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-center space-y-5">
                <div className="w-12 h-12 rounded-full bg-[var(--color-icy-blue-light)] border border-[var(--color-azure-blue)]/30 flex items-center justify-center text-[var(--color-azure-blue)] mx-auto animate-pulse">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
                <div className="space-y-2 max-w-md mx-auto">
                  <h3 className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
                    Executing Deterministic Marine Workflow
                  </h3>
                  <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                    Retrieving Open-Meteo marine and weather forecasts, validating temporal windows, computing physical boundary checks, and applying the independent release policy gate.
                  </p>
                </div>
                <div className="flex items-center justify-center gap-2 text-[10px] uppercase font-mono text-[var(--color-charcoal-blue-muted)]">
                  <span>DAG Step: Concurrent Retrieval</span>
                  <span>•</span>
                  <span>FSM State: VALIDATING</span>
                </div>
              </div>
            )}

            {/* STAGE C: Error / Offline State */}
            {queryState.phase === "error" && (
              <div className="p-6 sm:p-8 rounded-2xl border border-red-200 bg-red-50/70 text-red-950 space-y-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <h3 className="text-base font-serif font-bold text-red-900">
                      Backend Gateway Execution Notice
                    </h3>
                    <p className="text-xs text-red-900/90 leading-relaxed">
                      {queryState.error.message}
                    </p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-white/80 border border-red-200 space-y-2 text-xs">
                  <span className="font-semibold text-red-950 block">
                    How to start the Sagarvani Backend Server:
                  </span>
                  <p className="text-[11px] text-red-900 leading-relaxed">
                    Open a terminal in the project root and start the FastAPI service with UV:
                  </p>
                  <pre className="p-2.5 rounded bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto select-all">
                    cd backend; uv run uvicorn backend.main:app --port 8000
                  </pre>
                  <p className="text-[10px] text-red-800 italic pt-1">
                    Truthfulness guarantee: Sagarvani will never invent synthetic weather or fabricate an advisory response when the backend is offline.
                  </p>
                </div>

                <div className="flex items-center gap-3 pt-1">
                  <button
                    type="button"
                    onClick={performHealthCheck}
                    className="px-3 py-1.5 rounded-lg bg-red-100 hover:bg-red-200 text-red-900 font-medium text-xs transition-colors flex items-center gap-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Re-check Health</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setQueryState({ phase: "idle" })}
                    className="text-xs text-red-800 hover:underline"
                  >
                    Reset Query Form
                  </button>
                </div>
              </div>
            )}

            {/* STAGE D: Success State (Canonical Response Received) */}
            {queryState.phase === "success" && (
              <div className="space-y-6 animate-in fade-in duration-200">
                
                {/* 1. Overall Release Policy Banner (Paramount Gate) */}
                {(() => {
                  const verdict = queryState.response.policy_audit.overall_verdict;
                  const vStyle = formatVerdictBadge(verdict);
                  return (
                    <div className={`p-4 sm:p-5 rounded-2xl border ${vStyle.bg} space-y-3`}>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-current/15 pb-2">
                        <div className="flex items-center gap-2">
                          {vStyle.icon}
                          <span className="text-xs font-bold uppercase tracking-wider">
                            {vStyle.text}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/70 border border-current/20">
                            {formatRunStatus(queryState.response.status).text}
                          </span>
                          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/70 border border-current/20">
                            {queryState.response.data_mode}
                          </span>
                        </div>
                      </div>

                      <p className="text-xs leading-relaxed">
                        {queryState.response.policy_audit.explanation}
                      </p>

                      <div className="text-[11px] flex items-center justify-between pt-1 opacity-80">
                        <span>Run ID: <code className="font-mono">{queryState.response.run_id}</code></span>
                        <span>Trace ID: <code className="font-mono">{queryState.response.trace_id.slice(0, 16)}...</code></span>
                      </div>
                    </div>
                  );
                })()}

                {/* TAB 1: Decision & Advisory */}
                {activeTab === "advisory" && (
                  <div className="space-y-6">
                    {/* View Projection Content */}
                    {presentationMode === "field_community" ? (
                      <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-4">
                        <div className="flex items-center justify-between border-b border-[var(--color-warm-ivory-dark)] pb-3">
                          <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)]">
                            Field &amp; Community Advisory
                          </span>
                          <span className="text-[10px] font-mono text-[var(--color-charcoal-blue-muted)]">
                            Artisanal Safety Orientation
                          </span>
                        </div>

                        {queryState.response.field_view ? (
                          <div className="space-y-3">
                            <h4 className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
                              {queryState.response.field_view.headline}
                            </h4>
                            <p className="text-xs sm:text-sm text-[var(--color-charcoal-blue)] leading-relaxed">
                              {queryState.response.field_view.advisory_text}
                            </p>

                            {queryState.response.field_view.caution_flags.length > 0 && (
                              <div className="pt-2 space-y-2">
                                <span className="text-[11px] font-bold uppercase tracking-wider text-amber-900 block">
                                  Safety Cautions:
                                </span>
                                <ul className="space-y-1.5">
                                  {queryState.response.field_view.caution_flags.map((flag, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-xs text-amber-950 bg-amber-50/70 p-2 rounded-lg border border-amber-200">
                                      <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                                      <span>{flag}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-xs text-[var(--color-charcoal-blue)] leading-relaxed">
                            {queryState.response.summary_text}
                          </p>
                        )}
                      </div>
                    ) : (
                      <div className="p-6 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-4">
                        <div className="flex items-center justify-between border-b border-[var(--color-warm-ivory-dark)] pb-3">
                          <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)]">
                            Professional Analysis &amp; Lineage Audit
                          </span>
                          <span className="text-[10px] font-mono text-[var(--color-charcoal-blue-muted)]">
                            Scientific Breakdown
                          </span>
                        </div>

                        {queryState.response.professional_view ? (
                          <div className="space-y-4">
                            <p className="text-xs sm:text-sm text-[var(--color-charcoal-blue)] leading-relaxed">
                              {queryState.response.professional_view.scientific_summary}
                            </p>

                            <div className="space-y-2">
                              <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)] block">
                                Physical Parameter Breakdown
                              </span>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                {Object.entries(queryState.response.professional_view.parameter_breakdown).map(
                                  ([k, v]) => (
                                    <div key={k} className="p-2.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)]">
                                      <span className="text-[10px] font-mono text-[var(--color-charcoal-blue-muted)] uppercase block">
                                        {k.replace(/_/g, " ")}
                                      </span>
                                      <span className="text-sm font-semibold text-[var(--color-french-blue)]">
                                        {String(v.value)} {v.unit ?? ""}
                                      </span>
                                    </div>
                                  )
                                )}
                              </div>
                            </div>

                            {queryState.response.professional_view.lineage_audit.length > 0 && (
                              <div className="space-y-1.5 pt-2">
                                <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-charcoal-blue-muted)] block">
                                  Upstream Lineage &amp; Model Provenance:
                                </span>
                                <ul className="space-y-1">
                                  {queryState.response.professional_view.lineage_audit.map((lin, idx) => (
                                    <li key={idx} className="text-[11px] font-mono text-[var(--color-charcoal-blue)] bg-[var(--color-warm-ivory)] px-2.5 py-1.5 rounded border border-[var(--color-warm-ivory-dark)]">
                                      {lin}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-xs text-[var(--color-charcoal-blue)] leading-relaxed">
                            {queryState.response.summary_text}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Official Marine Disclaimer Notice */}
                    <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-[11px] text-[var(--color-charcoal-blue-muted)] space-y-1">
                      <span className="font-semibold text-[var(--color-charcoal-blue)] block">
                        Official Safety &amp; Legal Disclaimer:
                      </span>
                      <p>{queryState.response.disclaimer}</p>
                    </div>
                  </div>
                )}

                {/* TAB 2: Evidence Records Catalog */}
                {activeTab === "evidence" && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]">
                        Canonical Evidence Records ({queryState.response.evidence.length})
                      </span>
                      <span className="text-[10px] font-mono text-[var(--color-charcoal-blue-muted)]">
                        Immutable SQLite Metadata Wire
                      </span>
                    </div>

                    {queryState.response.evidence.length === 0 ? (
                      <div className="p-6 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] text-center text-xs text-[var(--color-charcoal-blue-muted)]">
                        No evidence records returned for this query.
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {queryState.response.evidence.map((ev, idx) => (
                          <div
                            key={ev.evidence_id || idx}
                            className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-2 hover:border-[var(--color-azure-blue)]/50 transition-colors"
                          >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-[var(--color-warm-ivory-dark)] pb-2">
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-bold text-[var(--color-french-blue)]">
                                  {ev.parameter.replace(/_/g, " ").toUpperCase()}
                                </span>
                                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] text-[var(--color-charcoal-blue)]">
                                  {String(ev.value)} {ev.unit}
                                </span>
                              </div>
                              <span className="text-[10px] font-mono text-[var(--color-charcoal-blue-muted)]">
                                Source: {ev.source_name}
                              </span>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-[var(--color-charcoal-blue)]">
                              <div>
                                <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Attribution:</span>
                                <span>{ev.attribution}</span>
                              </div>
                              <div>
                                <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Retrieved At:</span>
                                <span className="font-mono text-[10px]">{new Date(ev.retrieved_at).toLocaleString()}</span>
                              </div>
                              {ev.valid_from && (
                                <div>
                                  <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Valid Window:</span>
                                  <span className="font-mono text-[10px]">{ev.valid_from} → {ev.valid_to ?? "ongoing"}</span>
                                </div>
                              )}
                              <div>
                                <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Quality Flags:</span>
                                <div className="flex flex-wrap gap-1 mt-0.5">
                                  {ev.quality_flags.map((q, qIdx) => (
                                    <span key={qIdx} className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                                      {q}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            </div>

                            <div className="pt-1 flex items-center justify-between text-[10px] text-[var(--color-charcoal-blue-muted)] border-t border-[var(--color-warm-ivory-dark)]">
                              <span>Evidence ID: <code className="font-mono">{ev.evidence_id}</code></span>
                              <a
                                href={ev.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-[var(--color-azure-blue)] hover:underline"
                              >
                                <span>Source Endpoint</span>
                                <ExternalLink className="w-2.5 h-2.5" />
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 3: Release Policy Gate Detail */}
                {activeTab === "policy" && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] space-y-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)] block">
                        Independent Release Policy Evaluation
                      </span>
                      <p className="text-xs text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                        The release policy operates independently from all LLMs and heuristic adapters. Any check evaluating to <code>BLOCK</code> or <code>NOT_EVALUABLE</code> acts as an immediate safety hold, preventing unverified marine clearance.
                      </p>
                    </div>

                    <div className="space-y-2">
                      {queryState.response.policy_audit.checks.map((check) => {
                        const isExpanded = expandedPolicyCheck === check.check_name;
                        return (
                          <div
                            key={check.check_name}
                            className="p-3 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-2"
                          >
                            <button
                              type="button"
                              onClick={() => setExpandedPolicyCheck(isExpanded ? null : check.check_name)}
                              className="w-full flex items-center justify-between text-left focus:outline-none"
                            >
                              <div className="flex items-center gap-2">
                                {check.outcome === "PASS" ? (
                                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                                ) : check.outcome === "BLOCK" ? (
                                  <XCircle className="w-4 h-4 text-red-600 shrink-0" />
                                ) : (
                                  <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" />
                                )}
                                <span className="text-xs font-semibold text-[var(--color-charcoal-blue)]">
                                  {check.check_name.replace(/_/g, " ").toUpperCase()}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span
                                  className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                                    check.outcome === "PASS"
                                      ? "bg-emerald-50 text-emerald-900 border-emerald-300"
                                      : check.outcome === "BLOCK"
                                      ? "bg-red-50 text-red-900 border-red-300"
                                      : "bg-amber-50 text-amber-950 border-amber-300"
                                  }`}
                                >
                                  {check.outcome}
                                </span>
                                {isExpanded ? (
                                  <ChevronUp className="w-4 h-4 text-[var(--color-charcoal-blue-muted)]" />
                                ) : (
                                  <ChevronDown className="w-4 h-4 text-[var(--color-charcoal-blue-muted)]" />
                                )}
                              </div>
                            </button>

                            {isExpanded && (
                              <div className="pt-2 text-[11px] text-[var(--color-charcoal-blue)] space-y-1.5 border-t border-[var(--color-warm-ivory-dark)]">
                                <p><strong>Details:</strong> {check.details}</p>
                                <p className="text-[10px] text-[var(--color-charcoal-blue-muted)]">
                                  <strong>Legal / Policy Basis:</strong> {check.basis}
                                </p>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* TAB 4: FSM Execution Trace & Diagnostics */}
                {activeTab === "diagnostics" && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-3">
                      <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)] block">
                        FSM Workflow Execution Summary
                      </span>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                        <div className="p-2.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)]">
                          <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Run Status:</span>
                          <span className="font-mono font-semibold">{queryState.response.status}</span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)]">
                          <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Data Mode:</span>
                          <span className="font-mono font-semibold">{queryState.response.data_mode}</span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)]">
                          <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Evidence Items:</span>
                          <span className="font-mono font-semibold">{queryState.response.evidence.length}</span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)]">
                          <span className="text-[10px] text-[var(--color-charcoal-blue-muted)] block">Recovery Cycles:</span>
                          <span className="font-mono font-semibold">{queryState.response.recovery_trace.length} / 2</span>
                        </div>
                      </div>
                    </div>

                    {/* Identified Gaps */}
                    {queryState.response.gaps.length > 0 && (
                      <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/70 space-y-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-amber-950 block">
                          Identified Evidence Gaps ({queryState.response.gaps.length})
                        </span>
                        <ul className="space-y-1.5 text-xs text-amber-950">
                          {queryState.response.gaps.map((gap, gIdx) => (
                            <li key={gIdx} className="p-2 rounded bg-white/70 border border-amber-200">
                              <span className="font-mono font-bold text-[11px] block">{gap.gap_code}: {gap.description}</span>
                              {gap.suggested_action && (
                                <span className="text-[10px] text-amber-800">
                                  Suggested Action: <code>{gap.suggested_action}</code>
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Recovery Trace */}
                    {queryState.response.recovery_trace.length > 0 && (
                      <div className="p-4 rounded-xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] space-y-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-french-blue)] block">
                          Bounded Recovery Trace
                        </span>
                        <div className="space-y-2 text-xs">
                          {queryState.response.recovery_trace.map((rec, rIdx) => (
                            <div key={rIdx} className="p-2.5 rounded-lg bg-[var(--color-warm-ivory)] border border-[var(--color-warm-ivory-dark)] space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-[var(--color-french-blue)]">
                                  Cycle {rec.cycle}: {rec.action}
                                </span>
                                <span className="text-[10px] font-mono text-[var(--color-charcoal-blue-muted)]">
                                  Selector: {rec.selector}
                                </span>
                              </div>
                              <p className="text-[11px] text-[var(--color-charcoal-blue)]">Outcome: {rec.outcome}</p>
                              {rec.fallback_reason && (
                                <p className="text-[10px] text-amber-800">Fallback: {rec.fallback_reason}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Warnings */}
                    {queryState.response.warnings.length > 0 && (
                      <div className="p-4 rounded-xl border border-red-200 bg-red-50/70 space-y-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-red-950 block">
                          System Warnings ({queryState.response.warnings.length})
                        </span>
                        <ul className="space-y-1 text-xs text-red-950">
                          {queryState.response.warnings.map((w, wIdx) => (
                            <li key={wIdx} className="p-2 rounded bg-white/70 border border-red-200">
                              <span className="font-bold">{w.warning_code}</span> ({w.severity}): {w.message}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  </div>
                )}

              </div>
            )}

          </div>

        </div>
      </main>

      {/* Operational Cockpit Footer */}
      <footer className="w-full border-t border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] py-6 px-4 text-xs text-[var(--color-charcoal-blue-muted)] mt-12">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-[var(--color-french-blue)]" />
            <span>Sagarvani Decision Intelligence • Phase 6 Operational Workspace</span>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <Link href="/" className="hover:text-[var(--color-azure-blue)] transition-colors">
              Platform Home
            </Link>
            <span>•</span>
            <Link href="/login" className="hover:text-[var(--color-azure-blue)] transition-colors">
              Sign In (Preview)
            </Link>
            <span>•</span>
            <Link href="/#roadmap" className="hover:text-[var(--color-azure-blue)] transition-colors">
              Roadmap
            </Link>
            <span>•</span>
            <Link href="/#faq" className="hover:text-[var(--color-azure-blue)] transition-colors">
              FAQ
            </Link>
          </div>
        </div>
      </footer>

    </div>
  );
}
