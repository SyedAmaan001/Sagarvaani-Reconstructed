/**
 * Sagarvani Reconstructed - Frontend API Client
 *
 * Typed wrapper for canonical backend endpoints:
 *   GET  /health
 *   POST /api/orca/query
 *
 * Rules (AGENTS.md):
 * - Never simulate success on network/API error.
 * - Never invent evidence values, timestamps, or policy verdicts.
 * - All enum values mirror the backend enums exactly.
 * - Connection failure returns ApiError, not fabricated data.
 */

const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Enums — exact mirrors of backend/models/enums.py
// ---------------------------------------------------------------------------
export type RunStatus =
  | "COMPLETED" | "PARTIAL" | "SOURCE_UNAVAILABLE"
  | "INSUFFICIENT_EVIDENCE" | "CLARIFICATION_REQUIRED"
  | "BLOCKED" | "FAILED" | "TIMED_OUT";

export type DataMode =
  | "LIVE_FORECAST" | "LIVE_OBSERVATION" | "HISTORICAL_REPLAY"
  | "TEST_FIXTURE" | "NOT_AVAILABLE";

export type GateCheckOutcome = "PASS" | "BLOCK" | "NOT_EVALUABLE";
export type OverallGateVerdict = "PASS" | "BLOCK" | "NOT_EVALUABLE";

export type StakeholderRole =
  | "fisherman_community" | "port_operator" | "scientist_researcher"
  | "disaster_management" | "aquaculture_farmer" | "coastal_tourism"
  | "offshore_industry" | "marine_conservation";

export type PresentationMode = "field_community" | "professional_analysis";

export type RecoveryActionType =
  | "retry_with_backoff" | "expand_spatial_radius" | "extend_temporal_window"
  | "switch_fallback_provider" | "load_historical_analog"
  | "request_user_clarification" | "abstain_and_log";

// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------
export interface GeoLocation {
  lat: number;
  lon: number;
  location_name?: string | null;
}

export interface QueryContext {
  location?: GeoLocation | null;
  departure_time?: string | null;
  vessel_type?: string | null;
  operating_radius_km?: number | null;
  language?: string;
}

export interface CanonicalQueryRequest {
  query: string;
  session_id?: string | null;
  stakeholder_role: StakeholderRole;
  presentation_mode: PresentationMode;
  context_override?: QueryContext | null;
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------
export interface EvidenceRecord {
  evidence_id: string;
  source_id: string;
  source_name: string;
  product_id: string;
  parameter: string;
  value: number | string | Record<string, unknown>;
  unit: string;
  location: GeoLocation;
  observed_at?: string | null;
  issued_at?: string | null;
  model_run_at?: string | null;
  valid_from?: string | null;
  valid_to?: string | null;
  retrieved_at: string;
  data_mode: DataMode;
  quality_flags: string[];
  lineage_parent_ids: string[];
  source_url: string;
  attribution: string;
  artifact_ref?: string | null;
  schema_version: string;
}

export interface PolicyCheckItem {
  check_name: string;
  outcome: GateCheckOutcome;
  details: string;
  basis: string;
}

export interface PolicyAudit {
  overall_verdict: OverallGateVerdict;
  checks: PolicyCheckItem[];
  explanation: string;
}

export interface MarineWarningItem {
  warning_code: string;
  severity: string;
  message: string;
  source: string;
}

export interface IdentifiedGap {
  gap_code: string;
  description: string;
  affected_parameter?: string | null;
  suggested_action?: RecoveryActionType | null;
}

export interface RecoveryTraceEntry {
  cycle: number;
  selector: string;
  action: RecoveryActionType;
  target_gap: IdentifiedGap;
  parameters_applied: Record<string, unknown>;
  outcome: string;
  fallback_reason?: string | null;
  timestamp: string;
}

export interface FieldCommunityProjection {
  headline: string;
  advisory_text: string;
  caution_flags: string[];
}

export interface ProfessionalAnalysisProjection {
  scientific_summary: string;
  parameter_breakdown: Record<string, { value: unknown; unit?: string }>;
  lineage_audit: string[];
}

export interface CanonicalQueryResponse {
  run_id: string;
  trace_id: string;
  status: RunStatus;
  data_mode: DataMode;
  query: string;
  extracted_context?: QueryContext | null;
  evidence: EvidenceRecord[];
  warnings: MarineWarningItem[];
  gaps: IdentifiedGap[];
  recovery_trace: RecoveryTraceEntry[];
  policy_audit: PolicyAudit;
  summary_text: string;
  field_view?: FieldCommunityProjection | null;
  professional_view?: ProfessionalAnalysisProjection | null;
  timestamp: string;
  disclaimer: string;
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  timestamp: string;
  disclaimer: string;
}

// ---------------------------------------------------------------------------
// Error handling — never substitute fabricated data for these
// ---------------------------------------------------------------------------
export type ApiErrorKind =
  | "NETWORK_UNREACHABLE" | "BACKEND_ERROR" | "VALIDATION_ERROR" | "TIMEOUT";

export interface ApiError {
  kind: ApiErrorKind;
  message: string;
  status?: number;
}

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: ApiError };

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------
const DEFAULT_TIMEOUT_MS = 30_000;

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Health check — GET /health */
export async function checkHealth(): Promise<ApiResult<HealthResponse>> {
  try {
    const res = await fetchWithTimeout(`${BACKEND_BASE_URL}/health`, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) {
      return {
        ok: false,
        error: {
          kind: "BACKEND_ERROR",
          message: `Backend returned HTTP ${res.status}`,
          status: res.status,
        },
      };
    }
    const data = (await res.json()) as HealthResponse;
    return { ok: true, data };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      return { ok: false, error: { kind: "TIMEOUT", message: "Health check timed out." } };
    }
    return {
      ok: false,
      error: {
        kind: "NETWORK_UNREACHABLE",
        message: `Backend unreachable at ${BACKEND_BASE_URL}. Start the backend server first.`,
      },
    };
  }
}

/** Canonical query — POST /api/orca/query */
export async function submitQuery(
  req: CanonicalQueryRequest,
  accessToken?: string | null
): Promise<ApiResult<CanonicalQueryResponse>> {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (accessToken) {
      headers["Authorization"] = `Bearer ${accessToken}`;
    }
    const res = await fetchWithTimeout(
      `${BACKEND_BASE_URL}/api/orca/query`,
      {
        method: "POST",
        headers,
        body: JSON.stringify(req),
        cache: "no-store",
      }
    );
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const body = await res.json() as { detail?: unknown };
        if (body?.detail) detail = String(body.detail);
      } catch { /* ignore */ }
      return { ok: false, error: { kind: "BACKEND_ERROR", message: detail, status: res.status } };
    }
    const data = (await res.json()) as CanonicalQueryResponse;
    return { ok: true, data };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      return { ok: false, error: { kind: "TIMEOUT", message: "Query timed out after 30 s." } };
    }
    return {
      ok: false,
      error: {
        kind: "NETWORK_UNREACHABLE",
        message: `Backend unreachable at ${BACKEND_BASE_URL}. Start the backend server first.`,
      },
    };
  }
}

// ---------------------------------------------------------------------------
// Auth verification — GET /api/auth/me
// ---------------------------------------------------------------------------
export interface AuthMeResponse {
  user_id: string;
  email: string | null;
  role: string;
}

/**
 * Verifies that the backend can validate the signed-in user's access token.
 * The token MUST be the Supabase session access_token, not the publishable key.
 */
export async function getMe(
  accessToken: string
): Promise<ApiResult<AuthMeResponse>> {
  try {
    const res = await fetchWithTimeout(`${BACKEND_BASE_URL}/api/auth/me`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      cache: "no-store",
    });
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const body = (await res.json()) as { detail?: unknown };
        if (body?.detail) detail = String(body.detail);
      } catch { /* ignore */ }
      return { ok: false, error: { kind: "BACKEND_ERROR", message: detail, status: res.status } };
    }
    const data = (await res.json()) as AuthMeResponse;
    return { ok: true, data };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      return { ok: false, error: { kind: "TIMEOUT", message: "Auth check timed out." } };
    }
    return {
      ok: false,
      error: {
        kind: "NETWORK_UNREACHABLE",
        message: `Backend unreachable at ${BACKEND_BASE_URL}.`,
      },
    };
  }
}

