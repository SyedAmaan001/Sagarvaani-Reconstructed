# Sagarvani — Build Playbook

**Purpose:** A single staged execution plan for Antigravity. Complete one phase, show evidence, and stop at its gate before proceeding. This plan governs the backend first; the frontend design work remains separate until the backend contract is usable.

## Rules for every phase

1. Re-read `AGENTS.md` and the relevant sections of `MASTER_BLUEPRINT.md`.
2. Inspect the current branch, worktree and affected code before editing; preserve user changes.
3. Make the smallest necessary change and add/update offline tests.
4. Run only safe commands. Record exact test commands and actual outcomes in `ENGINEERING_LOGBOOK.md`.
5. Clearly label anything not run, blocked, assumed or only planned.
6. Stop after the current phase and report files inspected/changed, diff summary, tests, blockers and gate status.

## Phase 0 — Preserve workspace and safety lockdown

- Confirm the new reconstruction workspace paths and inspect Git status.
- Reconfirm the old audit findings against source: backend route paths, both orchestration paths, frontend call sites, CORS, alert dispatch, tests and secret handling.
- Keep the original Sagarvani Complete project intact under `legacy/`; do not blindly move files or copy `.env`, private credentials, virtual environments or `node_modules`.
- Disable/mock real alert dispatch in development/demo. Remove hard-coded real recipient data from tests safely. Do not run a test script until it is proven incapable of external dispatch.
- Restrict CORS to configured frontend origins. Remove fabricated “success” output on backend failure so failures are explicit.
- Do not change frontend design.

**Gate:** no test path can send real messages; backend/source failure cannot create a fake successful advisory; secrets are not printed; baseline branch/status is documented.

## Phase 1 — Canonical API and typed contracts

- Define/version request, response, evidence, task handoff, recovery action and error schemas using Pydantic.
- Establish one canonical query route, proposed as `POST /api/orca/query`, and a health route without secrets. Inspect compatibility needs before deprecating legacy paths.
- Define explicit statuses for complete/partial/unavailable, historical replay, test fixture, recovery, abstention and non-evaluable checks.
- Document units, timestamp semantics, validation errors and example fixtures in `DATA_AND_QUALITY.md`.

**Gate:** schema and request/response tests pass offline; missing context is explicit, not hallucinated.

## Phase 2 — First real evidence vertical slice

- Implement the Open-Meteo marine adapter with timeout, response/schema validation, correct attribution and actual valid-time fields.
- Add a redacted or non-sensitive fixture for offline tests; make live smoke tests opt-in and separate from normal CI/unit tests.
- Inspect the INCOIS PFZ page and access methods. Connect only if the data can be parsed and its issue/validity details preserved. Otherwise report `NOT_CONNECTED` with an official-source link.
- Do not label Open-Meteo data as IMD or INCOIS.

**Gate:** a request produces real, attributed evidence when available or a truthful unavailable/partial state; no fabricated measurements.

## Phase 3 — Evidence catalog, files and trace

- Store bounded raw response artifacts under a run-specific directory and metadata in SQLite.
- Record run/task/evidence IDs, source URL, retrieval time, parameter, units, valid time, source lineage where available, schema/parser version, quality flags, checksum and failure reason.
- Mark old NetCDF/SAR files as historical/replay fixtures unless metadata and provenance independently establish otherwise.

**Gate:** every displayed measurement links to an evidence record and raw artifact; replay material cannot masquerade as live.

## Phase 4 — Guarded FSM, harness and task DAG (R2)

- Implement explicit states and legal transitions.
- Add typed tasks, dependency graph, bounded concurrency, timeouts, run deadline, result caps and structured status outputs.
- Run independent retrievals concurrently; keep dependency-sensitive operations sequential. Failures become typed partial results, not silent success.

**Gate:** offline tests cover valid transitions, invalid transitions, DAG dependencies, timeout and task failure; no unbounded loop.

## Phase 5 — Validator, bounded recovery (R3) and release policy

- Validate schema, parameter/unit compatibility, spatial coverage, relevant valid time, freshness policy and source lineage/common-upstream duplication where known.
- Use a closed recovery-action allow-list. Start with deterministic rules. Initial design: at most two recovery cycles; detect repeated actions and no progress.
- Each action must name the gap it addresses. Revalidate after recovery.
- Keep a separate release policy with `PASS`, `BLOCK` or `NOT_EVALUABLE` for each configured check. Missing evidence is not a passed check.
- Do not claim protected-area clearance without verified boundary geometry or impose unreviewed vessel thresholds as official standards.

**Gate:** stale, missing or contradictory evidence either recovers transparently or leads to an explicit abstention/blocked state; a failed gate cannot produce “safe/go”.

## Phase 6 — Laya adapter (R1), experimental

- Define a selector interface with a `RuleBasedRecoverySelector` baseline first.
- Implement `LayaRecoverySelector` behind a feature flag. Laya may select only from allow-listed recovery actions; it cannot fetch arbitrary URLs, execute code or override release policy.
- Verify actual package/model/checkpoint/license/environment before claiming inference works. Download weights only when the baseline and adapter tests pass and time/resource budget allows.
- Compare rules and Laya on the same labelled offline cases; capture selector, action, result and fallback reason. Keep Laya disabled by default until evaluated.

**Gate:** model output is validated against the allowed enum; model load/timeout/invalid output falls back safely; no model can control the release gate. If inference is not run, report the adapter as implemented but model execution unverified.

## Phase 7 — Verification and demo acceptance

- Test nominal, stale evidence, conflicting inputs, duplicated upstream lineage, missing location, malformed payload, timeouts, prompt injection text and no-progress recovery.
- Begin with a small smoke-test subset; expand the planned 12 classes/60 cases as time and review allow. Do not imply this proves operational marine safety.
- Record real timings and actual pass/fail counts. Test live connectivity separately from deterministic offline tests.
- Perform a secret scan and verify no external alert dispatch can occur.

**Gate:** canonical backend behaviour, known limitations and test results are documented; all critical failures are explicit and truthful.

## Phase 8 — Handoff to frontend integration

This phase begins after backend contract and acceptance gates are reviewed. The separate frontend design work should use the same canonical evidence and decision in both views. Field/Community and Professional/Analysis modes may change presentation, not underlying evidence or release policy.

**Gate:** a sample backend response can be rendered without inventing measurements, status or provenance.

## What not to build early

Do not add Redis, a vector database, a complex agent framework, autonomous runtime Reflexion, open-ended ReAct orchestration, queue infrastructure, paid LLM dependence, mass messaging, or large model fine-tuning unless a verified requirement justifies it. Ralph Loop is a development-time coding technique only, never Sagarvani's runtime decision loop.

## Required phase-completion report

- Phase and gate: `PASS`, `BLOCKED` or `NOT RUN`.
- Files inspected and changed.
- Behaviour before/after and concise diff summary.
- Exact commands/tests and actual results.
- Any live API calls and their source/status (no secrets).
- Known risks, assumptions and next action.
- Confirmation no prohibited side effects occurred.
