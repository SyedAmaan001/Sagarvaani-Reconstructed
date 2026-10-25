"use client";

/**
 * Sagarvani — Operator Login & Sign-Up Page
 *
 * Functional Supabase authentication form.
 * Preserves the existing artwork, header/footer, colour tokens and typography.
 *
 * AGENTS.md rules enforced:
 *  - No fake/simulated authentication — real Supabase signIn/signUp.
 *  - Email confirmation required (mailer_autoconfirm: false) → user notified.
 *  - Redirect to /dashboard only after a verified Supabase session.
 *  - Error states are honest (wrong password, unconfirmed email, etc.).
 *  - No secret keys in browser code.
 */

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  Compass,
  ArrowLeft,
  Lock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Mail,
  Eye,
  EyeOff,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const STAKEHOLDER_ROLES = [
  { value: "fisherman_community",  label: "Artisanal & Small-Craft Fisher" },
  { value: "port_operator",        label: "Port Officer & Maritime Authority" },
  { value: "scientist_researcher", label: "Marine Scientist & Oceanographer" },
  { value: "disaster_management",  label: "Disaster Management Coordinator" },
  { value: "aquaculture_farmer",   label: "Aquaculture Farmer" },
  { value: "coastal_tourism",      label: "Coastal Tourism Operator" },
  { value: "offshore_industry",    label: "Offshore Industry Professional" },
  { value: "marine_conservation",  label: "Marine Conservation Officer" },
];

type Mode = "signin" | "signup";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading: authLoading, signIn, signUp } = useAuth();

  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState("fisherman_community");
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Redirect to dashboard if already signed in.
  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/dashboard");
    }
  }, [user, authLoading, router]);

  const clearMessages = () => {
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();
    setSubmitting(true);

    try {
      if (mode === "signin") {
        const { error } = await signIn(email, password);
        if (error) {
          if (error.message.toLowerCase().includes("email not confirmed")) {
            setErrorMsg(
              "Your email address has not yet been confirmed. " +
                "Please check your inbox and click the confirmation link, then try again."
            );
          } else if (
            error.message.toLowerCase().includes("invalid login") ||
            error.message.toLowerCase().includes("invalid credentials")
          ) {
            setErrorMsg("Incorrect email or password. Please try again.");
          } else {
            setErrorMsg(error.message);
          }
        } else {
          // Auth state change will trigger the useEffect redirect.
          setSuccessMsg("Signing in…");
        }
      } else {
        const { error, requiresConfirmation } = await signUp(email, password, role);
        if (error) {
          if (
            error.message.toLowerCase().includes("already registered") ||
            error.message.toLowerCase().includes("user already registered")
          ) {
            setErrorMsg(
              "An account with this email already exists. " +
                "Please sign in or use a different email."
            );
          } else {
            setErrorMsg(error.message);
          }
        } else if (requiresConfirmation) {
          setSuccessMsg(
            "Account created! Please check your email for a confirmation link. " +
              "Once confirmed, return here to sign in."
          );
        } else {
          setSuccessMsg("Account created and signed in. Redirecting…");
        }
      }
    } finally {
      setSubmitting(false);
    }
  };

  // Show loading state while checking existing session.
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-warm-ivory)]">
        <Loader2 className="w-8 h-8 animate-spin text-[var(--color-french-blue)]" />
      </div>
    );
  }

  // Already signed in — useEffect handles redirect; show brief message.
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-warm-ivory)]">
        <p className="text-[var(--color-charcoal-blue)] font-medium">
          Redirecting to dashboard…
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-warm-ivory)] selection:bg-[var(--color-icy-blue)] selection:text-[var(--color-charcoal-blue)] text-[var(--color-charcoal-blue)]">

      {/* Top Utility Bar */}
      <header className="w-full border-b border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)]/80 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link
            href="/"
            className="group flex items-center gap-2 text-xs sm:text-sm font-medium text-[var(--color-charcoal-blue)] hover:text-[var(--color-azure-blue)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded-lg p-1"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
            <span>Return to Sagarvani Home</span>
          </Link>
          <Link
            href="/"
            className="flex items-center gap-2.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)] rounded-lg p-1"
            aria-label="Sagarvani Home"
          >
            <div className="w-8 h-8 rounded-full bg-[var(--color-french-blue)] flex items-center justify-center text-[var(--color-warm-ivory)] shadow-xs">
              <Compass className="w-4 h-4 stroke-[2]" />
            </div>
            <span className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
              Sagarvani
            </span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 md:py-16 flex items-center justify-center">
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">

          {/* Left Column: Auth Form */}
          <div className="lg:col-span-6 space-y-6 max-w-xl mx-auto w-full">

            {/* Page Header */}
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-warm-ivory-light)] border border-[var(--color-warm-ivory-dark)] text-xs font-semibold text-[var(--color-french-blue)] uppercase tracking-wider">
                <Lock className="w-3.5 h-3.5 text-[var(--color-azure-blue)]" />
                <span>Operator Access</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-[var(--color-french-blue)]">
                {mode === "signin" ? "Operator Sign In" : "Create Operator Account"}
              </h1>
              <p className="text-sm text-[var(--color-charcoal-blue-muted)] leading-relaxed">
                Role-gated workspace access for coastal mariners, harbor authorities, and marine researchers.
              </p>
            </div>

            {/* Mode Switcher */}
            <div className="flex rounded-xl border border-[var(--color-warm-ivory-dark)] overflow-hidden bg-[var(--color-warm-ivory-light)] p-1 gap-1">
              <button
                type="button"
                onClick={() => { setMode("signin"); clearMessages(); }}
                className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                  mode === "signin"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-sm"
                    : "text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-dark)]/50"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setMode("signup"); clearMessages(); }}
                className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                  mode === "signup"
                    ? "bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] shadow-sm"
                    : "text-[var(--color-charcoal-blue)] hover:bg-[var(--color-warm-ivory-dark)]/50"
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Auth Form */}
            <form
              onSubmit={handleSubmit}
              className="p-6 sm:p-8 rounded-2xl border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] shadow-xs space-y-5"
            >

              {/* Email */}
              <div className="space-y-1.5">
                <label
                  htmlFor="email"
                  className="block text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]"
                >
                  Email Address
                </label>
                <div className="relative">
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    placeholder="operator@harbour.gov.in"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={submitting}
                    className="w-full pl-10 pr-3.5 py-2.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-sm text-[var(--color-charcoal-blue)] placeholder:text-[var(--color-charcoal-blue-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)] disabled:opacity-60"
                  />
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-charcoal-blue-muted)]" />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-1.5">
                <label
                  htmlFor="password"
                  className="block text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete={mode === "signin" ? "current-password" : "new-password"}
                    required
                    minLength={8}
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={submitting}
                    className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-sm text-[var(--color-charcoal-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)] disabled:opacity-60"
                  />
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-charcoal-blue-muted)]" />
                  <button
                    type="button"
                    onClick={() => setShowPassword((p) => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-charcoal-blue-muted)] hover:text-[var(--color-charcoal-blue)] focus:outline-none"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {mode === "signup" && (
                  <p className="text-[11px] text-[var(--color-charcoal-blue-muted)]">
                    Minimum 8 characters.
                  </p>
                )}
              </div>

              {/* Stakeholder Role (signup only) */}
              {mode === "signup" && (
                <div className="space-y-1.5">
                  <label
                    htmlFor="role-select"
                    className="block text-xs font-bold uppercase tracking-wider text-[var(--color-charcoal-blue)]"
                  >
                    Stakeholder Role
                  </label>
                  <select
                    id="role-select"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    disabled={submitting}
                    className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory)] text-sm text-[var(--color-charcoal-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--color-azure-blue)] disabled:opacity-60"
                  >
                    {STAKEHOLDER_ROLES.map((r) => (
                      <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                  </select>
                  <span className="text-[11px] text-[var(--color-charcoal-blue-muted)] block">
                    Selects default view filters and safety tolerance envelopes.
                  </span>
                </div>
              )}

              {/* Submit Button */}
              <div className="pt-1">
                <button
                  type="submit"
                  disabled={submitting || !email || !password}
                  className="w-full py-3 px-4 rounded-xl bg-[var(--color-french-blue)] text-[var(--color-warm-ivory)] font-semibold text-sm border border-[var(--color-french-blue)] hover:bg-[var(--color-azure-blue)] transition-colors flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-azure-blue)]"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>{mode === "signin" ? "Signing in…" : "Creating account…"}</span>
                    </>
                  ) : (
                    <>
                      <Lock className="w-4 h-4" />
                      <span>{mode === "signin" ? "Sign In" : "Create Operator Account"}</span>
                    </>
                  )}
                </button>
              </div>

              {/* Error Message */}
              {errorMsg && (
                <div
                  role="alert"
                  className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-2"
                >
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
                  <p>{errorMsg}</p>
                </div>
              )}

              {/* Success Message */}
              {successMsg && (
                <div
                  role="status"
                  className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-start gap-2"
                >
                  <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
                  <p>{successMsg}</p>
                </div>
              )}

              {/* Email confirmation note */}
              {mode === "signup" && !successMsg && !errorMsg && (
                <p className="text-[11px] text-center text-[var(--color-charcoal-blue-muted)]">
                  After registering, check your email for a confirmation link before signing in.
                </p>
              )}
            </form>

            {/* Back Link */}
            <div className="text-center pt-2">
              <Link
                href="/"
                className="text-xs font-medium text-[var(--color-azure-blue)] hover:underline inline-flex items-center gap-1"
              >
                <span>← Back to public homepage</span>
              </Link>
            </div>

          </div>

          {/* Right Column: Original Artwork & Architecture Preview */}
          <div className="lg:col-span-6 space-y-6">
            <div className="relative rounded-2xl overflow-hidden border border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] p-2 shadow-md">
              <div className="relative aspect-[4/3] w-full rounded-xl overflow-hidden">
                <Image
                  src="/artwork/From Map Fragments to Lighthouse Bay.png"
                  alt="Ukiyo-e cartographic rendering of a lighthouse safe harbour amidst rolling coastal currents"
                  fill
                  className="object-cover object-center"
                  sizes="(max-width: 1024px) 100vw, 50vw"
                  priority
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-charcoal-blue)]/80 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 px-2.5 py-1 rounded bg-[var(--color-charcoal-blue)]/90 text-[10px] uppercase font-mono text-[var(--color-warm-ivory)]">
                  Illustrative Art — Sagarvani Archive
                </div>
              </div>

              {/* Architecture Details Box */}
              <div className="p-6 space-y-4">
                <h2 className="text-lg font-serif font-bold text-[var(--color-french-blue)]">
                  Role-Gated Access Architecture
                </h2>
                <ul className="space-y-2.5 text-xs text-[var(--color-charcoal-blue)]">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
                    <span><strong>Role Isolation:</strong> Artisanal fishers receive high-contrast swell summaries; commercial operators access multi-day forecast envelopes.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
                    <span><strong>Auditable Telemetry:</strong> Every query retains an immutable trace ID, observation timestamp, and policy gate record in the metadata catalog.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[var(--color-azure-blue)] shrink-0 mt-0.5" />
                    <span><strong>Token-Verified Sessions:</strong> Supabase RS256 JWT access tokens are verified by the backend on every protected request — no publishable-key substitution.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

        </div>
      </main>

      {/* Minimal Editorial Footer */}
      <footer className="w-full border-t border-[var(--color-warm-ivory-dark)] bg-[var(--color-warm-ivory-light)] py-6 px-4 text-center text-xs text-[var(--color-charcoal-blue-muted)]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>© 2026 Sagarvani. Supabase-authenticated operator workspace.</p>
          <div className="flex items-center gap-2">
            <Link href="/" className="hover:text-[var(--color-azure-blue)] transition-colors">
              Platform Home
            </Link>
            <span>•</span>
            <Link href="/#faq" className="hover:text-[var(--color-azure-blue)] transition-colors">
              FAQ
            </Link>
            <span>•</span>
            <Link href="/#roadmap" className="hover:text-[var(--color-azure-blue)] transition-colors">
              Roadmap
            </Link>
          </div>
        </div>
      </footer>

    </div>
  );
}
