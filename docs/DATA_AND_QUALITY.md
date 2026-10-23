# Sagarvani — Data, APIs and Quality

This file is the source of truth for API-access readiness, dataset status, evidence fields and quality/security gates. **Credentials are tracked here by requirement and status only; never put actual secrets in Markdown or source code.** Reconfirm all legacy inventory findings inside the reconstructed workspace before use.

## 1. Credential and service checklist

| Service | Key/account needed? | Priority | Rule / current action |
|---|---|---:|---|
| Open-Meteo Marine and Weather | No API key for eligible free non-commercial use | P0 | CONNECTED & TESTED (Phase 2). CC BY 4.0 attribution required: "Marine weather data by Open-Meteo.com". Non-commercial tier limits apply (up to 10,000 calls/day). |
| INCOIS PFZ | No generic key identified for public advisory pages; machine-readable access still needs verification | P0/P1 | Inspect official page; preserve issue/validity info. Do not claim integration until tested. |
| IMD developer API | Confirm official registration and auth requirements | P1 | Pursue institutional access; never guess key format. |
| INCOIS ERDDAP | Public catalog endpoints may be accessible without an API key | P1 | Validate specific dataset, TLS chain and licensing. Never set `verify=False`. A TLS failure alone does not prove which CA is missing. |
| MOSDAC | Account credentials for protected downloads | P2 | Use only for selected product downloads; do not copy legacy secrets. |
| Copernicus Marine | Service account for toolbox/data access | P2 | Defer until the core Indian coastal MVP works. |
| Laya local checkpoint | No hosted inference key for local inference | P1 experiment | IMPLEMENTED & TESTED (Phase 6). Apache 2.0 licence. Checkpoint: `convaiinnovations/laya` (ModernBERT-large, 421M). Gated behind `ENABLE_LAYA_SELECTOR=false`. Strict allow-list validation and fail-closed deterministic fallback to `RuleBasedRecoverySelector`. Real in-process model execution opt-in via `RUN_LIVE_LAYA_TESTS=1`. |
| Bhashini/Sarvam | Provider credentials if we select hosted speech/translation | Later | Not required for initial backend. |
| Map tile provider | Depends on provider selected during frontend work | Frontend phase | MapLibre does not mandate a particular paid provider. |
| Twilio/WhatsApp | Not needed for MVP | Disabled | Mock all dispatch; do not send real notifications during development/demo. |
| Claude/Gemini/OpenAI | Not required for deterministic backend foundation | Not required | Do not make Claude Pro verification or any one hosted LLM a project dependency. |

Potential local environment variables should be added only when needed, for example `OPEN_METEO_BASE_URL`, `IMD_API_KEY`, `MOSDAC_USERNAME`, `MOSDAC_PASSWORD`, `COPERNICUSMARINE_SERVICE_USERNAME`, `COPERNICUSMARINE_SERVICE_PASSWORD`, `BHASHINI_API_KEY`, `SARVAM_API_KEY`, and `MAPTILER_API_KEY`. Use an ignored local `.env` and a safe `.env.example` containing placeholder names only. Never print secret values.

## 2. Existing dataset inventory (reported by the previous audit; reconfirm locally)

| Asset | Reported state | Allowed use now | Not allowed without further verification |
|---|---|---|---|
| `MOSDAC/Global Ocean Surface Current/` | Five NetCDF files with U/V current variables and dates between Jan–Jun 2026; global attributes reported empty | Cataloged in Phase 3 as `HISTORICAL_REPLAY` / test fixtures with SHA-256 checksums and quality flags | Treating as verified current live ocean state or calling the data synthetic solely because global attributes are empty |
| `MOSDAC/Indian Mainland Coastal Product/` | SARAL/AltiKa files dated Jun–Jul 2016 (deleted in working copy, cycle 035 directory remains) | Historical analysis/parser fixtures with explicit observation dates | Treating as current sea state |
| `Bhuvan NRSC – LULC 2024–25/` | Two documentation PDFs; no geometries were found in the audit | Reference documentation only | MPA/route clearance claims; obtain and verify actual geometry first |
| `IMD/IMD.txt` | Empty file | None until populated by a verified source | Claiming an IMD warning check ran |
| Static PFZ registry | Reported entries dated 2026-09-04 | Historical UI fixture only, clearly labelled expired | Presenting entries as current PFZ advisories |
| Open-Meteo offline fixtures | `open_meteo_marine_sample.json`, `open_meteo_weather_sample.json` | Cataloged in Phase 3 as `TEST_FIXTURE` with SHA-256 checksums | Presenting as live forecast |

## 3. Datasets / feeds to obtain or verify

### First end-to-end slice

1. **Open-Meteo Marine API** — wave height, period, direction and other supported fields; capture the exact returned units and forecast timestamps. Documentation: https://open-meteo.com/en/docs/marine-weather-api
2. **Open-Meteo Weather API** — relevant atmospheric values from its own endpoint and attribution. Documentation: https://open-meteo.com/
3. **INCOIS PFZ** — investigate https://www.incois.gov.in/MarineFisheries/PfzAdvisory, https://www.incois.gov.in/MarineFisheries/TextDataHome?mfid=1&request_locale=en and https://www.incois.gov.in/MarineFisheries/PfzWebGis. Only integrate when an actual advisory can be parsed and its location, issue date, validity and attribution retained.
4. **Offline fixtures** — save safe representative responses and build labelled failures for repeatable tests. Fixtures are `TEST_FIXTURE`, not `LIVE`.
5. **Protected-area geometry** — a real route/geofence feature requires an authoritative or appropriately licensed geometry file, source/edition/date, CRS, licence and verified spatial tests. Until then set the relevant check to `NOT_EVALUABLE`.

### Add only after the first slice

- IMD official developer marine/coastal warnings: https://api.imd.gov.in/public/api_reference.html
- INCOIS ERDDAP catalog and one-by-one dataset discovery: https://erddap.incois.gov.in/erddap/index.html
- Selected MOSDAC products: https://www.mosdac.gov.in/
- Copernicus Marine only if the selected task benefits from its data and account access is ready: https://marine.copernicus.eu/
- Voice/translation data/models only after the backend and dashboard contract stabilise.

For each candidate dataset, record exact product/dataset ID, source URL, license/terms, attribution, variables, units, CRS, spatial/temporal coverage, actual observation/issue/model-run/forecast-valid times, retrieval time, update cadence, known limitations, access test date, and `PLANNED` / `CONNECTED` / `VERIFIED` / `BLOCKED` status. Do not treat discovery of a web page as verification of an API.

## 4. Canonical evidence record

Every value displayed as evidence must trace to a typed record with fields equivalent to:

```json
{
  "evidence_id": "ev_<id>",
  "source_id": "open_meteo_marine",
  "source_name": "Open-Meteo Marine API",
  "product_id": "marine_forecast",
  "parameter": "wave_height",
  "value": 0.8,
  "unit": "m",
  "location": {"lat": 13.35, "lon": 74.70},
  "observed_at": null,
  "issued_at": null,
  "model_run_at": null,
  "valid_from": "source-returned timestamp",
  "valid_to": null,
  "retrieved_at": "recorded by Sagarvani",
  "data_mode": "LIVE_FORECAST",
  "quality_flags": [],
  "lineage_parent_ids": [],
  "source_url": "https://open-meteo.com/en/docs/marine-weather-api",
  "attribution": "source/provider attribution",
  "artifact_ref": "artifacts/runs/<run_id>/<task_id>.json",
  "schema_version": "v1.0"
}
```

The example measurement is illustrative, not a live reading. `observed_at`, `issued_at`, `model_run_at`, `valid_from` and `retrieved_at` represent different concepts; leave unavailable values null rather than inventing them. Store actual values returned by sources, not example placeholders.

## 5. Canonical API response: dashboard contract

The proposed `POST /api/orca/query` response should include:

- `run_id`, `trace_id`, `status`, `data_mode`, and context (location/time/persona).
- `evidence[]` with parameter, value, unit, time, source and provenance reference.
- `warnings[]` and `gaps[]` with stable codes and severity.
- `recovery_trace[]` with cycle, selector (`rules` or `laya`), allowed action, trigger gap, result and fallback reason.
- `policy_audit` with checks that passed, failed or were not evaluable.
- `summary_text`, plus optional `field_view` and `professional_view` projections from the same underlying evidence and policy result.

Use explicit states such as `COMPLETE`, `PARTIAL`, `SOURCE_UNAVAILABLE`, `INSUFFICIENT_EVIDENCE`, `HISTORICAL_REPLAY`, `TEST_FIXTURE`, `BLOCKED` and `NOT_EVALUABLE` as appropriate. Final enum values must be versioned and consistent across backend, tests and future frontend. Do not fabricate a “GO”, green badge, safety score or “no warning” response when a source is absent.

## 6. Quality and testing

Start with a compact offline suite, then expand. Test at minimum:

- Valid schema and units; missing or malformed fields.
- Old observations vs future forecast valid times; timezone and coordinate validation.
- Gateway timeout, HTTP error, oversized response and bad JSON.
- Multiple endpoints that share the same upstream model/run (avoid false consensus).
- Stale/missing evidence, conflicting values and ambiguous location.
- External bulletin prompt-injection text treated strictly as untrusted content.
- Recovery repeats/no-progress; enforce the initial maximum of two recovery cycles.
- Laya invalid output, model unavailable and timeout; rules fallback operates.
- Release gate cannot be bypassed by model, formatter or frontend.
- Alert tests prove network dispatch is mocked and impossible in the test path.

A proposed 12-class/60-case dataset is a useful later pilot, but does not establish operational marine safety. Begin with a smoke case per class and mark ground-truth review as pending where domain experts have not adjudicated it. Report measured results, not desired targets.

## 7. Security and safety release checks

- No secrets, private recipient details or copied legacy `.env` values in Git or logs. Use a secret scanner before public release; scanning supplements manual/configuration controls.
- Explicit CORS origins; authorization/rate limits on any administrative action.
- No real SMS/WhatsApp dispatch during development or demo. Do not run unsafe alert scripts until mocked and reviewed.
- No TLS verification bypass. Diagnose certificate chains and trust configuration.
- No fabricated success response on backend/source failure.
- Every value keeps its source and temporal meaning; historical/replay/test fixture states are visible.
- No protected-area clearance without verified geometry. No operational vessel thresholds without authoritative basis and domain review.
- Release checks return `PASS`, `BLOCK` or `NOT_EVALUABLE`; a missing check never counts as passed.
- Do not claim safety certification, real-world operational readiness or patent novelty from a prototype test suite.

## 8. Resource-register selections

Keep the register short and decision-specific:

- **Laya (R174):** Retained as an optional, bounded recovery-action decision selector (R1); evaluated side-by-side with `RuleBasedRecoverySelector`.
  - Repository: `convaiinnovations/laya` (Hugging Face / GitHub `NandhaKishorM/laya`).
  - Licence: Apache 2.0.
  - Architecture: Non-autoregressive System 1 decision engine executing discrete choice inference over typed question schemas.
  - Primary checkpoint: ModernBERT-large backbone (421M parameters, 512 context tokens).
  - Multilingual checkpoint: mmBERT-base (322M parameters, 1024 context tokens, 100+ languages).
  - Runtime constraints: Gated behind `ENABLE_LAYA_SELECTOR=false` by default. Pure lazy import. Fail-closed fallback to `RuleBasedRecoverySelector` on missing package, timeout (default 3.0s), or unapproved action.
  - Gate independence: Has zero access to release policy checks, cannot estimate physical hazard probabilities, and cannot overturn `NOT_EVALUABLE` or `BLOCK` verdicts.
  - Status: `IMPLEMENTED`, `TESTED` (all 30 offline tests pass; opt-in live model execution test available via `RUN_LIVE_LAYA_TESTS=1`).
- **Open Knowledge Format idea (R014):** adapt trust metadata such as `status`, `verified` and `stale_after` for documents/data sources; no knowledge-graph installation required.
- **TruffleHog (R017):** optional secret scan before public repository release; does not replace secret hygiene.
- **Cloudflare security-audit skill (R016):** optional one-time review if compatible with the current Antigravity setup.
- **Vectara HHEM (R183):** optional offline experiment for checking whether generated wording is supported by evidence. Never treat its score as a physical safety gate.
- **Silero VAD / faster-whisper / Indic Parler-TTS:** defer to frontend/voice phase; no dependency for backend readiness.

The MENS resource register is a candidate list, not proof that every listed project is compatible, actively maintained, licensed for our intended use or appropriate for Sagarvani. Verify before installation.
