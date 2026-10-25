"use client";

/**
 * Sagarvani — Authentication Context
 *
 * Provides Supabase auth state (user, session, accessToken) to the entire
 * React tree.  All auth operations go through this context so that
 * components never import supabase directly.
 *
 * Security notes (AGENTS.md):
 *  - accessToken is the signed-in user JWT; it MUST be sent to the backend
 *    in Authorization: Bearer <token>.
 *  - The publishable key is NOT a user credential.
 *  - No secrets are stored here.
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { User, Session, AuthError } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export type AuthUser = User;

export interface AuthState {
  user: AuthUser | null;
  session: Session | null;
  /** Raw JWT for Authorization: Bearer header.  Null when signed out. */
  accessToken: string | null;
  loading: boolean;
  /** Supabase user_metadata.stakeholder_role, if set at signup */
  userRole: string | null;
}

export interface AuthActions {
  signIn: (
    email: string,
    password: string
  ) => Promise<{ error: AuthError | Error | null }>;
  signUp: (
    email: string,
    password: string,
    stakeholderRole?: string
  ) => Promise<{ error: AuthError | Error | null; requiresConfirmation: boolean }>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export type AuthContextValue = AuthState & AuthActions;

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------
const AuthContext = createContext<AuthContextValue | null>(null);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  const accessToken = session?.access_token ?? null;
  const userRole =
    (user?.user_metadata?.stakeholder_role as string | undefined) ?? null;

  // Restore session on mount and listen for auth changes.
  useEffect(() => {
    let mounted = true;

    // Get current session immediately (restored from localStorage).
    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSession(data.session);
      setUser(data.session?.user ?? null);
      setLoading(false);
    });

    // Subscribe to future auth events (sign in, sign out, token refresh, etc.).
    const { data: sub } = supabase.auth.onAuthStateChange((_event, newSession) => {
      if (!mounted) return;
      setSession(newSession);
      setUser(newSession?.user ?? null);
      setLoading(false);
    });

    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  // ---------------------------------------------------------------------------
  // Auth operations
  // ---------------------------------------------------------------------------
  const signIn = useCallback(
    async (email: string, password: string) => {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      return { error };
    },
    []
  );

  const signUp = useCallback(
    async (email: string, password: string, stakeholderRole?: string) => {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: stakeholderRole ? { stakeholder_role: stakeholderRole } : undefined,
        },
      });
      // If the user object has no identities, the email is already registered.
      const requiresConfirmation =
        !error && !!data.user && !data.session;
      return { error, requiresConfirmation };
    },
    []
  );

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const refreshSession = useCallback(async () => {
    const { data } = await supabase.auth.refreshSession();
    setSession(data.session);
    setUser(data.session?.user ?? null);
  }, []);

  const value: AuthContextValue = {
    user,
    session,
    accessToken,
    loading,
    userRole,
    signIn,
    signUp,
    signOut,
    refreshSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>.");
  }
  return ctx;
}
