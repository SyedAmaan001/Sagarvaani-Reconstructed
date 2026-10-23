# Sagarvani / ORCA — Post-Audit Architecture Decisions & Build Plan

**Prepared:** 23 October 2026  
**Basis:** `Sagarvani_Outstanding_Verification_Report.md` (read-only audit dated 23 October 2026)  
**Immediate context:** Internal build day Saturday, 24 October; finalist event Sunday, 25 October 2026.

## 1. Decision summary

The audit is directionally useful. Adopt the smallest coherent architecture that makes one end-to-end path truthful and testable. Do not use this report as permission to claim that Sagarvani can safely approve real vessel departures. The threshold values, authority coverage, source permissions, and operational safety behaviour remain unvalidated.

### Adopt for the MVP

1. **One canonical backend path.** Route user requests through one pipeline; retire or adapt the competing orchestrator only after mapping callers and existing behaviours.
2. **Guarded state machine.** Explicit states, legal transitions, timeout/cancellation handling, terminal outcomes and a bounded recovery count.
3. **Task DAG.** Fetch independent evidence in parallel; keep dependencies explicit and prevent cycles within one acquisition attempt.
4. **Evidence registry plus local run artifacts.** Start with filesystem artifacts and SQLite metadata. A vector database or Redis is not justified for the first demonstrator.
5. **Deterministic evidence validator and release gate.** Models may suggest an allow-listed recovery action or draft an explanation; they cannot override validation or the final policy gate.
6. **Bounded, targeted recovery.** At most two recovery attempts is a reasonable initial engineering cap to test, not a scientifically proven optimal value. Every attempt must target a documented evidence gap and show progress or terminate.
7. **One backend decision, two presentation projections.** Field/Community and Professional/Analysis views must render the same evidence, warnings and decision status.
8. **Truthful source/mode labels.** Distinguish live forecast, official warning, historical archive, static reference layer, synthetic fixture and unavailable data.

### Defer

- Laya weights/fine-tuning until deterministic baseline tests exist.
- Redis, vector databases, broad agent frameworks, Copernicus integration and production broadcast queues.
- Real SMS/WhatsApp dispatch in the demo environment. Mock the provider; keep alert routes disabled unless access-controlled and explicitly enabled.
- Claims of patent novelty, patentability, or guaranteed safe navigation pending qualified review.

## 2. Corrections and caveats to the audit report

These items should be addressed before turning the audit’s recommendations into code or external claims.

### A. Marine limits are placeholders until validated

The report proposes freshness TTLs, vessel sea-keeping limits, cyclone buffers and other thresholds, but also lists expert validation as an unresolved gate. Treat every proposed value as **UNAPPROVED CONFIGURATION** until a qualified marine-domain reviewer approves its scope and assumptions. Do not show `GO_APPROVED`, a numeric “safety score”, or operational “Stay Ashore” advice derived solely from those proposed values. For the hackathon, label the prototype as demonstrative decision support and clearly show when an authoritative warning feed or validated threshold is unavailable.

### B. The worked timestamp example is inconsistent

The report's sample request is for 05:00 IST on 24 October 2026, but the stated `valid_time_utc` is `2026-10-23T20:00:00Z`, equivalent to 01:30 IST on 24 October—not 05:00 IST. The requested target time would be `2026-10-23T23:30:00Z`. Treat the walkthrough numbers as illustrative until request parameters and source timestamps are captured and checked mechanically.

### C. The Bhuvan inventory does not contain the proposed MPA geometries

The audit reports that the local Bhuvan folder contains documentation PDFs only, with no GeoJSON, shapefile or GeoTIFF geometry. The architecture must not claim a functioning MPA geofence until a verified and licensed geometry dataset is actually available, versioned and tested. Otherwise, mark geofence evidence `UNAVAILABLE` and do not infer “clear”.

### D. Do not infer that the ocean-current files are synthetic

The audit establishes that the files are old/dated, lack global attributes and have insufficient lineage for operational use. That is enough to classify them as historical/unverified fixtures, but does not by itself prove they are synthetic. Preserve this distinction in the UI and evidence catalog.

### E. `RFC 5737` does not define phone-number test ranges

RFC 5737 concerns IPv4 address blocks used in documentation, not E.164 telephone numbers. Do not substitute a made-up but plausible phone number in the test. Remove outbound dispatch from automated tests by injecting a mocked SMS/WhatsApp provider. Keep the route disabled in development/demo mode unless authenticated, rate-limited and deliberately enabled.

### F. An SSL failure does not prove that a government root CA is missing

The reported INCOIS TLS failure needs certificate-chain inspection before installing any additional trust root. Never disable TLS verification (`verify=False`) as a workaround. Use the normal verified certificate store, document the certificate issuer/chain and confirm the correct remediation from an authoritative source before modifying trust settings.

### G. “Deterministic” requires a defined boundary

The state controller and rules can be deterministic for fixed, recorded inputs, code version and policy version. Live API responses, remote timeouts and third-party model outputs are not inherently deterministic. Persist the exact request parameters, retrieval time, raw response/artifact hash, parser version, ruleset version and final transition trace to support reproducibility.

### H. The 60-case pilot cannot establish real-world safety

The proposed 60 cases (five per class) are a useful engineering regression set, not proof of a sufficiently low real-world hazard rate. Report the sample size, class-wise results, false-release count and limitations. A zero-violation result on this pilot must not be described as proof that the product is safe for navigation.

### I. Separate observation time, issue time, model run time and forecast valid time

A forecast retrieved now for tomorrow is not “stale” merely because its valid time is in the future; a recently downloaded old forecast can still be stale. Store at least `retrieved_at`, `issued_at` or `model_run_at` when available, `valid_time`, provider and time zone. Apply source-specific freshness rules to the correct timestamp. Treat the report's TTL suggestions as configurable proposals, not universal rules.

## 3. Saturday build plan — the smallest credible vertical slice

Do not attempt a full repository rewrite in one session. First make the demo truthful, then demonstrate the concept on one coastal query.

### Phase 0 — safety/integrity lock (first)

- Inspect the exact current route and frontend error paths before editing.
- Remove/disable real outbound SMS/WhatsApp dispatch from demo/test flows; replace provider calls with mocks.
- Remove the silent fallback that fabricates a safe advisory when the backend fails. Show an explicit unavailable/error state instead.
- Restrict CORS to intended development origins and ensure any alert route is disabled by default or protected by authentication and rate limits.
- Check Git status and diff before and after each change. Do not print `.env` or secret values. Rotate secrets only if there is evidence they were exposed or committed.
- Do not run the existing HTTP test script unless its dispatch path has been made incapable of sending real messages.

**Exit gate:** Backend failure cannot produce a successful-looking advisory; demo tests cannot dispatch messages; no secrets or personal phone numbers appear in output/diffs.

### Phase 1 — one canonical request path

- Map frontend requests and backend route handlers, then select `/api/orca/query` as the canonical path if that matches current callers.
- Do not delete the second orchestration implementation immediately. First route the active caller through the canonical path, add tests, and mark the unused path as deprecated only when references are confirmed.
- Define typed request/response models with `run_id`, user query, persona, display mode, location/time context, evidence references, warnings, source mode and terminal status.
- Keep missing location, ambiguous target time or missing required context as a clarification outcome; do not silently invent values.

**Exit gate:** One integration test proves that the frontend's free-form request reaches the canonical backend and receives the actual backend result or explicit error.

### Phase 2 — evidence-first one-query demo

Use one Malpe-area test scenario and a small allow-list of sources:

- Open-Meteo marine forecast may be used as a clearly attributed **secondary forecast**. The marine API documentation calls for attribution to both Open-Meteo and DWD; confirm displayed attribution against the actual variables/model returned.
- Existing MOSDAC files are historical/unverified material only, not current observations.
- Do not claim an operational INCOIS/IMD warning integration unless the exact data endpoint, access and received payload have been verified. A source being listed in a plan is not evidence that ingestion is working.
- Do not claim MPA geofence results while the actual geometry is absent or unverified.

For every evidence item, store its origin, parameter, unit, coordinates/spatial coverage, retrieval time, issue/model-run time when available, forecast/observation valid time, data class, raw artifact path/hash, parser version and quality warnings.

**Exit gate:** A reviewer can click/read the source and see the actual source and timestamps; old files are rejected or labelled historical; missing evidence cannot be represented as a clear/safe result.

### Phase 3 — guarded validation and bounded recovery

Implement a small state machine with explicit terminal statuses, for example:

`REQUESTED → CONTEXT_VALIDATED → TASK_GRAPH_READY → EVIDENCE_ACQUISITION → EVIDENCE_VALIDATION → RELEASE_CHECK`

From validation, route to exactly one of:

- `RECOVERY_PLANNING` for a recoverable and decision-relevant gap;
- `CLARIFICATION_REQUIRED` when user context is insufficient;
- `ABSTAIN_INSUFFICIENT_EVIDENCE` when the required evidence cannot be established;
- `UPSTREAM_UNAVAILABLE` on a provider failure;
- `UNSAFE_UNDER_APPROVED_POLICY` only when a real, approved policy rule has been triggered;
- `RESPONSE_READY` only when the release conditions pass.

Use a rules-based allow-list first. A recovery attempt must name the detected gap, action, expected evidence improvement, outcome and next transition. If the same action repeats or there is no measurable improvement, stop. Recovery limits and timeout budgets must compose; one extended retry must not violate the total request deadline.

**Exit gate:** Unit tests cover valid transition, illegal transition, stale data, missing required source, malformed payload, repeat/no-progress, timeout and abstention paths.

### Phase 4 — two presentation modes, one verdict

- Field/Community View: plain-language answer, key source/time, limitations, clear next step.
- Professional/Analysis View: evidence table, valid times/units, source lineage, missing/conflicting data and recovery trace.
- Both views must use the same canonical decision and policy result. Display mode can change explanatory detail, never the gate outcome.
- A backend outage must produce the same explicit unavailable status in either view—not fixture data disguised as live evidence.

**Exit gate:** One end-to-end scenario toggles views and confirms that verdict, warnings and evidence references remain identical.

## 4. Minimal demo acceptance checklist

- [ ] One end-to-end Malpe-area query works through the canonical route.
- [ ] Every displayed data value has a source, unit and relevant timestamp.
- [ ] The app distinguishes live forecast, official warning, historical archive, static layer, fixture and unavailable source.
- [ ] Historical/unknown-lineage currents cannot silently become current live evidence.
- [ ] Missing/unverified MPA geometry is explicitly unavailable, never assumed clear.
- [ ] Backend/API failure never yields a fabricated green/GO advisory.
- [ ] No SMS/WhatsApp test path can send a real message.
- [ ] Field and Professional views show the same underlying decision.
- [ ] A handful of automated regression tests cover success, source failure, stale data and abstention.
- [ ] The presentation states that this is a prototype and not a replacement for official warnings or local maritime authority guidance.

## 5. What not to spend the build day on

Do not download Laya's weights, fine-tune a decision model, add a vector DB, build all eight separate domain workflows, attempt to create a full live Indian marine-data ingestion pipeline, or claim patent novelty. Preserve those as research tracks after one reliable vertical slice is working.

## 6. Prompt to use in Antigravity

```text
You are working in the existing Sagarvani / ORCA repository. Use the uploaded
Sagarvani_Outstanding_Verification_Report.md and
Sagarvani_Post_Audit_Decisions_and_Build_Plan.md as architecture guidance, but
apply all caveats in the decision plan.

First inspect the current repository state, Git branch/status/diff, active frontend
API calls, backend route wiring, and the exact locations of the unsafe alert and
silent-fallback behaviours. Do not display or copy secrets from .env.

Work in small, verifiable steps for a hackathon prototype. Do not rewrite the
entire repository. Do not install packages, download model weights, call paid APIs,
send SMS/WhatsApp messages, invoke voice providers, or make live side-effecting
calls. Do not execute test_api_endpoints.py unless you have proven its outbound
provider has been replaced by a mock.

Step 1: propose a short plan with the exact files to change and tests to run.
Step 2: neutralize unsafe demo/test side effects and remove any frontend fallback
that fabricates a successful/safe advisory on backend failure. Backend failure must
show a real error/unavailable state.
Step 3: route one frontend query through one canonical backend path, selecting
/api/orca/query only after verifying actual callers. Do not delete legacy paths
until their references are mapped.
Step 4: add/repair typed evidence metadata and truthful source/status labels for a
single Malpe-area demonstration. Open-Meteo is a secondary forecast, local MOSDAC
files are historical/unverified only, and missing MPA geometry must be unavailable.
Do not invent INCOIS/IMD integrations or attach their names to data from another source.
Step 5: implement or refine only the minimal guarded state flow and rule-based
bounded recovery needed for this slice. Models cannot override the release gate.
Do not introduce unreviewed vessel thresholds or emit real operational GO approval.
Use explicit outcomes for clarification, insufficient evidence, upstream failure,
and unapproved demo policy.
Step 6: add focused tests for successful retrieval, backend/provider failure, stale
or unverified evidence, no-progress recovery and abstention. Do not assert that a
small regression set proves real-world marine safety.
Step 7: run safe local tests, inspect the final diff, check that no secrets or real
phone numbers are added, and report each command/result. If any step requires an
unavailable source credential, expert-approved limit, missing geometry, or other
unverified dependency, stop that feature and document it rather than faking it.

Before making edits, explain what you intend to change. Then implement one phase at
a time, test it, and report changed files, tests, remaining risks, and the exact
manual demo path. Never claim success for a test that was not run.
```

## 7. Evidence references

- Outstanding verification report: sections 1, 3–9 and 11–15. The report explicitly records the empty Bhuvan geometry inventory, stale/unknown-lineage local data, unsafe alert/fallback paths, deferred Laya integration and remaining domain-expert gates.
- IMD API reference: <https://api.imd.gov.in/public/api_reference.html>
- Open-Meteo marine API documentation and attribution: <https://open-meteo.com/en/docs/marine-weather-api>
- Laya typed-decision benchmark caveat: <https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md>

**Final decision:** Build evidence integrity, safe failure behaviour and one tested vertical slice before expanding the agent architecture. The originality of Sagarvani should be demonstrated through measured evidence-aware recovery—not by the number of agents or loops in a diagram.
