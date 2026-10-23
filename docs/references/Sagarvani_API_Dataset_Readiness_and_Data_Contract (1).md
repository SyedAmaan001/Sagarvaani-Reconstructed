# Sagarvani — API, Dataset Readiness & Data Contract

**Version:** 1.0  
**Prepared:** 23 October 2026  
**Purpose:** Define what credentials and datasets are actually needed, what the audit says is already present, what to obtain next, and the canonical shape the backend should return to a later dashboard.

> This is a readiness checklist, not proof that any currently unconnected source is live. The prior audit was performed in the Windows workspace and must be re-confirmed by Antigravity against the exact checkout before changes. No secrets belong in this document or the repository.

## 1. The short answer

- **No third-party API key is required to start backend development.** Use offline test fixtures first, then add Open-Meteo's public marine/weather endpoints for a non-commercial prototype. The service documents no API key or sign-up for its free non-commercial API, with attribution and rate limits.
- **IMD access is a target, not a build blocker.** The official reference lists Port Warning, Sea Area Bulletin, Coastal Bulletin and Fishermen Warning endpoints. Confirm the actual registration, credential and/or IP-allow-list requirements for the team's use before calling the feed “connected”.
- **INCOIS PFZ advisory is a real official source but not necessarily a clean public JSON API.** Start by identifying current bulletin issue/validity and linking to it; only automate parsing after the structure and terms are checked.
- **INCOIS ERDDAP is public data discovery/access infrastructure, not a single guaranteed dataset.** Choose datasets one by one and validate certificate trust, variable names, unit, spatial/temporal coverage and update cadence. Do not turn off TLS verification.
- **The current local marine files are not cleared for live decision support.** Reuse them as labelled historical replay/parser fixtures until provenance is proven.
- **Laya can be evaluated locally without an inference API key.** A hosted inference provider would require its own account/token and has separate terms/cost; that is not required for the first adapter.

## 2. API credentials inventory

### 2.1 Needed now vs. later

| Service / credential | Needed to build first backend? | What to do | Notes |
|---|---:|---|---|
| **Open-Meteo Marine API** | **No key required** | Use a backend-only `httpx` gateway with request timeout, response validation, explicit units and attribution. Re-test during implementation. | Free API is for non-commercial use, has usage limits, and requires CC BY 4.0 attribution to Open-Meteo and relevant model providers. For commercial/promotional use, review/subcribe to the appropriate plan. |
| **Open-Meteo Weather API** | **No key required for free non-commercial API** | Use a separate weather endpoint for atmospheric variables (e.g. wind/weather) where needed. Keep its model/source provenance distinct from marine variables. | Do not assume a marine-wave response is an official wind-warning feed. |
| **IMD marine API / developer access** | Not a blocker for skeleton; required before claiming connected IMD feed | Ask/complete the official access process and verify documented credentials and any IP allow-list constraints. Store only the granted credential/config in backend secrets. | Do not invent an auth header or claim public endpoints need no authorization solely because the docs page is public. |
| **INCOIS PFZ** | No API key identified as necessary for first source inspection | Inspect official PFZ advisory, text advisory and WebGIS pages; record issue time, region/sector, valid-until metadata, source URL and retrieval time. Automate only if safely parseable. | Do not treat the static code list as current data. PFZ identifies probable aggregation zones, not guaranteed fish presence or safe routes. |
| **INCOIS ERDDAP** | Usually no API key for public catalog/data requests; verify per dataset | Test a small documented GET with certificate verification enabled. Inspect the real TLS chain if it fails. | Prior audit reported a certificate verification error on 23 Oct 2026. Do not use `verify=False`. |
| **MOSDAC username/password** | No, not for local historic files | Register only when a chosen satellite product is needed. Use `mdapi.py` + `config.json` outside git and download a small bounded sample. | MOSDAC's official download guide says download requires account credentials and `datasetId`; search/preview may not require login. These are login credentials, not a generic API key. |
| **Copernicus Marine account credentials** | No; defer | Create/use an account only after selecting a concrete dataset and value proposition. | Adds another source and tooling setup. It is useful later for model comparison, not required for first vertical slice. |
| **Laya API token** | **No for local inference** | Build `RecoverySelector` interface and rules implementation first; later install the model into a project-managed environment and test local inference. | Optional Hugging Face token only if the chosen download/hosting path requires it (e.g. gated/private resource or hosted inference). Never make it a core API dependency. |
| **Bhashini / Sarvam API credentials** | No; defer voice/translation | Consider only after backend outputs are evidence-grounded and the warning/uncertainty semantics are tested in target languages. | Not needed for the first backend. Translation must not weaken or omit a warning. |
| **Map tile provider token (e.g. MapTiler)** | No for backend; possibly later for frontend maps | Choose a tile provider only when frontend map implementation begins. Keep the provider token in frontend-appropriate restricted configuration if their terms require client use; do not treat MapLibre itself as a data source. | Prefer a suitable no-key tile source if usage and attribution terms fit. Do not depend on map tiles for a geofence safety check. |
| **Twilio SID/token or WhatsApp provider token** | **No—keep disabled** | Do not configure or call outbound alert dispatch in MVP. Replace provider with a mock/sandbox. | Audit reported unauthenticated alert routes and a tracked live recipient in a test. Do not execute old alert tests before remediation. Rotate any exposed/compromised credentials. |
| **Gemini / Claude / OpenAI API keys** | **No** | Set deterministic templates as default. Optional wording models can be evaluated later behind an interface, but they must not control policy. | Claude Pro subscription is not a project dependency; no build stage should block on its verification. |
| **Supabase / Redis / vector database credentials** | **No for this MVP unless code audit proves a required feature depends on one** | Start with local SQLite catalog and file artifacts. Inspect actual code before adding hosted services. | Do not add infrastructure merely because a README claims it exists. |

### 2.2 Suggested backend environment variables

Use an ignored local `.env` with no values committed, plus a safe `.env.example` containing placeholders only:

```dotenv
APP_ENV=development
CORS_ALLOWED_ORIGINS=http://localhost:3000
EVIDENCE_ROOT=artifacts/runs
SQLITE_PATH=artifacts/sagarvani.sqlite3
RUN_DEADLINE_SECONDS=12
GATEWAY_TIMEOUT_SECONDS=6
N_MAX_RECOVERY=2
LAYA_SELECTOR_ENABLED=false
NARRATIVE_PROVIDER=template
OPEN_METEO_MARINE_ENABLED=true
OPEN_METEO_WEATHER_ENABLED=true
IMD_ENABLED=false
INCOIS_ERDDAP_ENABLED=false
PFZ_ADVISORY_ENABLED=false
MOSDAC_DOWNLOAD_ENABLED=false
COPERNICUS_MARINE_ENABLED=false
VOICE_PROVIDER=disabled
OUTBOUND_ALERTS_ENABLED=false

# Add only after access is granted; exact IMD auth format must follow its agreement/docs.
# IMD_API_KEY=
# MOSDAC_USERNAME=
# MOSDAC_PASSWORD=
# COPERNICUSMARINE_SERVICE_USERNAME=
# COPERNICUSMARINE_SERVICE_PASSWORD=
# BHASHINI_API_KEY=
# SARVAM_API_KEY=
# HF_TOKEN=   # optional; not a requirement for local, public model inference
# MAPTILER_API_KEY=  # only if selected when frontend maps are built
```

**Secret handling:** never paste keys into Antigravity prompts, source files, screenshots, tickets, reports or frontend bundles. Do not print `.env`. Ensure `.env`, provider config files, model credentials and downloaded private data are gitignored. Backend-only credentials stay on the server. Test with mocked providers.

## 3. Dataset inventory: what the audit says already exists

These findings were reported by the supplied audit and must be reconfirmed before relying on file paths or counts.

| Existing asset | Reported content | Status | Reuse decision |
|---|---|---|---|
| `MOSDAC/Global Ocean Surface Current/` | Five NetCDF files; `U`/`V` current components on a 0.25-degree global grid; dates between Jan and Jun 2026; global attributes reportedly empty | **Unverified provenance / historical or test fixture** | Keep for parser tests, stale-data detection and replay. Do not show as a live MOSDAC observation without authentic product metadata and source proof. |
| `MOSDAC/Indian Mainland Coastal Product/` | SARAL/AltiKa NetCDF altimetry files from June–July 2016 | **Historical archive** | Reuse to test NetCDF parsing and data visualisation; label as a 2016 historical observation. |
| `Bhuvan NRSC – LULC 2024–25/` | Two PDF technical documents; no usable polygon GeoJSON/shapefile/GeoTIFF reportedly present | **Documentation only, not geospatial geometry** | Use docs to discover relevant products. Obtain and validate actual GIS layer before showing spatial exclusion checks. |
| `IMD/IMD.txt` | Empty file | **No dataset** | Do not reference as a warning dataset. |
| Static PFZ list in code | Four entries reported, dated 4 Sep 2026 | **Stale / not verified as live** | Remove from the live path. It may be moved to a clearly labelled test fixture if useful for UI/regression tests. |
| Frontend map/scenario/voice fixtures | Hard-coded coordinates, timers and preset interactions reported in audit | **Demo fixtures, not live evidence** | Reuse visuals and interaction patterns, but replace data binding later. Do not call them real telemetry or actual recorded voice input. |
| SST/chlorophyll/tide outputs | Several computed from constants/formulas or synthetic time fields according to audit | **Synthetic** | Do not use as measured ocean conditions. Keep only if useful as explicitly labelled test fixtures. |

## 4. Datasets to obtain or verify next

### P0 — required for a defensible backend prototype

1. **Open-Meteo Marine forecast responses** (API data, not a downloaded static dataset): wave height, wave direction, wave period and supported related variables for one defined pilot coast. Capture the exact request parameters, units, response timestamp and model/source metadata.
2. **Open-Meteo atmospheric weather responses** (separate API product as required): relevant wind and weather variables with their own source/provider metadata. Do not merge data products without keeping the source lineage.
3. **One current official INCOIS PFZ advisory record** for the pilot region, including original URL, sector/landing centre, issue date/time, valid-until date/time, and any coordinates explicitly stated by the advisory. If the content cannot be reliably parsed, save a permitted source snapshot/reference and mark the feed `MANUAL_REFERENCE` or `NOT_CONNECTED`, rather than pretending automated ingestion works.
4. **One verified official marine warning example** from IMD if authorized access can be obtained. Prioritize one documented endpoint (e.g. Port Warning, Sea Area Bulletin or Coastal Bulletin), not all 20+ APIs. If access cannot be secured for the demo, return `UNAVAILABLE_NOT_CONNECTED` and link to the official source; never synthesize “no warning”.
5. **A small verified geospatial pilot layer** only if the first backend slice claims route/protected-area intersection. It needs actual polygon geometry and metadata: source, release/version, retrieval date, CRS, feature identifiers, boundary effective date if available, license and checksum. A map image or a list of sanctuary names is insufficient.
6. **Offline validation fixtures:** create labelled JSON cases for fresh data, stale observation, timestamp mismatch, malformed schema, timeout, duplicate upstream lineage, unit/coordinate mismatch, ambiguous location, prompt injection in bulletin text, no-progress recovery and insufficient evidence. Synthetic test scenarios are allowed only when labelled `TEST_FIXTURE` and never reused as live observations.

### P1 — obtain after first vertical slice works

- **INCOIS ERDDAP scientific dataset subset:** inspect the current catalog and select a specific SST/chlorophyll, current or buoy dataset only after confirming variables, geographical coverage, time resolution, update rate, licensing/attribution and working certificate verification. ERDDAP supports gridded `griddap` and tabular `tabledap` access and multiple formats; its catalog is not proof that a particular needed variable is available or current.
- **MOSDAC satellite product subset:** select a concrete product through the MOSDAC catalogue (`datasetId`), register and download only a small pilot sample if needed. For the hackathon, existing archive files may be enough for offline parser demonstrations.
- **Protected-area boundaries:** first search for authoritative Indian government/agency boundaries, and compare with a traceable global protected-area source (e.g. UNEP-WCMC/IUCN Protected Planet/WDPCA) if its applicable download/use terms permit the intended use. Check geometry and national designation records; global data is a research candidate, not by itself a legally authoritative navigation restriction layer.
- **Bathymetry and tide data:** not needed for the first demo. Add only when a concrete feature needs it and an appropriate authoritative dataset and datum/time conventions are identified.

### P2 — not needed for the immediate build

- Copernicus Marine model/observation datasets for independent comparison.
- Separate SST/chlorophyll anomaly analysis, aerosol/pollution, or satellite-derived products.
- Vernacular audio/TTS/translation datasets/services.
- Full historical training corpus or marine-specific fine-tuning data for Laya.
- Fleet telemetry, user/vessel identities and alert-recipient lists. Do not gather personal or operational data unless a feature needs it and consent/security is in place.

## 5. Data quality and provenance required for each source

Every ingested item must carry metadata. At minimum:

- `evidence_id`, `source_id`, `source_name`, `source_url`, `product_id` or dataset ID.
- `parameter`, `value`, `unit`, `uncertainty` (only when provided/derivable by a documented method), `quality_flags`.
- `location`/spatial bounds and coordinate reference system, including longitude/latitude order.
- `observed_at`, `issued_at`, `valid_from`, `valid_to`, `retrieved_at` as distinct nullable times; don't invent missing times.
- `data_kind`: `LIVE_FORECAST`, `OFFICIAL_ADVISORY`, `OBSERVATION`, `HISTORICAL_ARCHIVE`, `TEST_FIXTURE`, or `UNKNOWN`.
- `upstream_provider`, model name/run/cycle if supplied, parent-source IDs when known; don't count two endpoints with the same upstream model run as independent sources.
- `license_or_terms_url`, required attribution, `sha256`, raw artifact reference and parser/schema version.
- Gateway result: `SUCCESS`, `PARTIAL`, `UNAVAILABLE`, `TIMEOUT`, `TLS_ERROR`, `PARSE_ERROR`, `STALE` or `UNVERIFIED`.

A fresh retrieval time is not the same as a fresh observation or a currently valid forecast. Missing provenance is a gap, not an invitation to fill in plausible metadata.

## 6. Example canonical evidence record

Illustrative schema only; the numeric values below are placeholders, not a live forecast:

```json
{
  "evidence_id": "ev_01JEXAMPLE",
  "source_id": "open_meteo_marine",
  "source_name": "Open-Meteo Marine API",
  "source_url": "https://open-meteo.com/en/docs/marine-weather-api",
  "product_id": "marine_forecast",
  "parameter": "wave_height",
  "value": 0.8,
  "unit": "m",
  "location": {"lat": 13.35, "lon": 74.70, "label": "pilot location"},
  "observed_at": null,
  "issued_at": null,
  "valid_from": "2026-10-24T00:00:00Z",
  "valid_to": "2026-10-24T01:00:00Z",
  "retrieved_at": "2026-10-23T18:00:00Z",
  "data_kind": "LIVE_FORECAST",
  "upstream_provider": "provider/model returned by the API",
  "quality_flags": [],
  "lineage_parent_ids": [],
  "license_or_terms_url": "https://open-meteo.com/en/terms",
  "attribution": "Open-Meteo and applicable underlying model provider",
  "sha256": "computed-from-raw-response",
  "artifact_ref": "artifacts/runs/<run_id>/<task_id>.json",
  "schema_version": "v1.0"
}
```

In real records, `valid_from`/`valid_to` must be derived from the source's actual forecast time and configured interval, not copied from this example. Use `null` if the source does not provide an issued or observation time.

## 7. Example canonical backend response for the future dashboard

Illustrative contract; no claim that the API has already been implemented:

```json
{
  "run_id": "run_example",
  "status": "PARTIAL_EVIDENCE",
  "data_mode": "MIXED",
  "query_context": {
    "persona_id": "fishermen",
    "display_mode": "field",
    "location": {"lat": 13.35, "lon": 74.70, "label": "Malpe, Karnataka"},
    "target_time": "2026-10-24T05:00:00+05:30"
  },
  "summary_text": "A marine forecast was retrieved, but the official warning feed and verified protected-area geometry are not connected. This is not a complete safety assessment.",
  "evidence": [],
  "warnings": [
    {"code": "OFFICIAL_WARNING_FEED_UNAVAILABLE", "severity": "HIGH", "message": "Official warning status could not be verified."},
    {"code": "MPA_BOUNDARIES_NOT_EVALUABLE", "severity": "MEDIUM", "message": "Protected-area intersection was not evaluated because verified geometry is unavailable."}
  ],
  "gaps": ["official_warning_status", "verified_geospatial_boundaries"],
  "recovery_trace": [
    {"cycle": 1, "action": "FETCH_OFFICIAL_WARNING", "selector": "RULES", "outcome": "UNAVAILABLE_NOT_CONNECTED"}
  ],
  "policy_audit": {
    "policy_version": "prototype-0.1",
    "gate_evaluated": false,
    "gate_passed": null,
    "checks_passed": [],
    "checks_failed": [],
    "checks_not_evaluable": ["official_warning_status", "protected_area_intersection"]
  },
  "projections": {
    "field_view": {"primary_message": "Some required information is unavailable. Do not treat this prototype output as a safety clearance."},
    "professional_view": {"charts": [], "map_layers": [], "evidence_trail": []}
  },
  "trace_id": "trace_example",
  "disclaimer": "Prototype decision support only; not an official or certified marine safety advisory."
}
```

The empty `evidence` array is intentional in this illustration: use actual evidence returned during execution, never invent response values merely to match this example. Never use a green “safe” state if an important check was not evaluable.

## 8. What the dashboard will eventually render from this contract

This is a frontend design contract, not a request to build the frontend before the backend is complete.

- **Header/status strip:** selected coast/location, requested valid time, run status, data mode, last retrieval time and connected/unavailable source indicators.
- **Map:** only data-backed locations and geometries. Render forecast points, verified PFZ coordinates, verified boundaries and routes as separate layers with source references. If a geometry feed is absent, label it “not connected”; never draw a fake protected-area layer.
- **Marine condition cards:** the supported parameters actually present in evidence, each with unit, valid time and source. Do not show an invented safety score.
- **Official notices panel:** issue time, region/port, validity and original bulletin link. Distinguish “no warning was returned by a connected feed” from “warning feed is unavailable”.
- **Evidence drawer:** filterable evidence records with source/product, value/unit, observed/issued/valid/retrieved time, quality flags, lineage and raw artifact reference.
- **Recovery timeline:** the validation gap, allowed action selected, selector type (rules or Laya), observed outcome, whether the gap changed, recovery cycle and terminal result. Store action summaries, not hidden chain-of-thought.
- **Time-series chart:** values indexed by source-valid time, with gaps and data-kind changes visible. Never combine unrelated sampling intervals without explicit resampling rules.
- **Field / Community projection:** plain-language summary, concise warnings, uncertainty and what could not be checked.
- **Professional / Analysis projection:** time series, map layers, evidence comparison, lineage and structured validation results.

Both modes must use the same canonical evidence and policy output. The presentation can change; the decision and evidence cannot.

## 9. Recommended workspace structure: preserve first, reuse selectively

Keep the existing `Sagarvani Complete` checkout untouched as the legacy reference until the reconstructed backend is tested. Avoid a sweeping migration and do not make the old unsafe endpoints public again.

```text
Sagarvani Reconstructed/
├── README.md
├── docs/
│   ├── Sagarvani_Complete_Engineering_Master_Blueprint.md
│   ├── Sagarvani_Outstanding_Verification_Report.md
│   ├── Sagarvani_Post_Audit_Decisions_and_Build_Plan.md
│   └── Sagarvani_API_Dataset_Readiness_and_Data_Contract.md
├── legacy/
│   └── <existing Sagrvani Complete folder, keep its actual name>/  # unchanged reference
├── backend/                         # canonical backend implementation first
│   ├── pyproject.toml               # managed with uv
│   ├── app/
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── controller/              # FSM
│   │   ├── planner/                  # task DAG
│   │   ├── harness/                  # budgets/timeouts/contracts
│   │   ├── gateways/                 # source-specific adapters
│   │   ├── evidence/                 # file store + SQLite catalog
│   │   ├── validators/
│   │   ├── recovery/                 # rules + optional Laya adapter
│   │   └── policy/                   # independent release gate
│   ├── artifacts/                   # local, ignored at least where sensitive/large
│   └── tests/
│       ├── fixtures/
│       ├── unit/
│       ├── integration/
│       └── contract/
├── data/
│   ├── catalog.yaml                 # product/source inventory, license, validity rules
│   ├── fixtures/                    # small, explicitly synthetic test cases
│   └── manifests/                   # inventory/hash/metadata for historic datasets
└── frontend/                        # later: migrate/reuse audited components
```

### Preservation and reuse rules

- Do **not** delete or overwrite the original checkout to create the new structure. Keep the original as a rollback reference until the new project has a passing baseline.
- Prefer a Git clone or branch/worktree for versioned files. For the nested `legacy` snapshot, exclude `.env`, credentials, caches, `node_modules`, and virtual environments; preserve large local datasets by a documented copy/reference strategy rather than silently omitting them.
- Do not reuse a moved `.venv` or `node_modules`; recreate environments in the new location using the lockfile/package manifest. Never copy an old `.env` into the reconstructed root.
- Create a reuse register: file/module, what it does, test evidence, dependencies, known risks and decision (`REUSE`, `ADAPT`, `REPLACE`, `KEEP_LEGACY`). Likely reuse candidates include the NetCDF parser and geo utility only after contract/unit tests pass; do not blindly reuse the old orchestrator or fabricated evidence path.
- Backend first means the canonical schemas, gateway, evidence trace, FSM, bounded recovery, independent policy and tests are functional before wiring the old frontend to it. Keep frontend components and visual assets available for later integration.

## 10. Immediate sequence

1. Create the reconstruction workspace and copy the planning documents into `docs/`; preserve the legacy project without its secrets/caches.
2. Have Antigravity re-audit the exact new workspace paths, dependencies, actual dataset files and Git status. No destructive commands and no secret output.
3. Build schemas, local fixture tests and `GET /health` without external APIs.
4. Build and test the Open-Meteo gateway; record a redacted response fixture, source metadata and attribution.
5. Build evidence catalog/artifact storage and the FSM/task harness.
6. Add PFZ official source metadata and IMD adapter seams; enable a feed only after a safe response is verified.
7. Add validator and bounded recovery, then tests for stale data, duplicate lineage, timeout, no progress and abstention.
8. Add the Laya selector adapter behind a feature flag, then install/evaluate weights only after rules tests pass.
9. Connect the frontend after the canonical response is stable.

## 11. Official documentation links

- IMD API reference: https://api.imd.gov.in/public/api_reference.html
- INCOIS PFZ advisory: https://www.incois.gov.in/MarineFisheries/PfzAdvisory
- INCOIS PFZ text data: https://www.incois.gov.in/MarineFisheries/TextDataHome?mfid=1&request_locale=en
- INCOIS PFZ WebGIS: https://www.incois.gov.in/MarineFisheries/PfzWebGis
- INCOIS ERDDAP catalog: https://erddap.incois.gov.in/erddap/index.html
- Open-Meteo marine API: https://open-meteo.com/en/docs/marine-weather-api
- Open-Meteo terms: https://open-meteo.com/en/terms
- MOSDAC download API manual: https://www.mosdac.gov.in/downloadapi-manual
- MOSDAC dataset catalog: https://mosdac.gov.in/catalog-app/satellite.php
- Laya model family: https://huggingface.co/convaiinnovations/laya
- Laya source code and docs: https://github.com/NandhaKishorM/laya
- Copernicus Marine Toolbox: https://help.marine.copernicus.eu/en/articles/7949409-copernicus-marine-toolbox-introduction
- UNEP-WCMC / IUCN WDPCA service description: https://data-gis.unep-wcmc.org/server/rest/services/ProtectedPlanet/WDPCA/MapServer
- MapLibre GL JS: https://maplibre.org/maplibre-gl-js/docs/
