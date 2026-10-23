# Sagarvani — Hackathon Guide

**Goal:** a concise guide the whole team can study in roughly two hours. Replace every implementation-specific placeholder with facts verified in `ENGINEERING_LOGBOOK.md` before presenting. Never describe planned features as completed.

## 1. The pitch

**One sentence:** Sagarvani turns fragmented marine information into context-specific, evidence-backed decision support—and shows when the evidence needs to be checked again before it responds.

**30-second version:** Marine decisions can depend on weather forecasts, ocean conditions, fishing advisories and geospatial constraints that come from different sources and use different timestamps, units and formats. Sagarvani coordinates relevant sources, tracks the provenance and validity of the evidence, detects gaps or conflicts, and performs bounded, targeted recovery. If evidence remains insufficient, it says so instead of fabricating reassurance. The same underlying result can be presented in a simple Field/Community view or a detailed Professional/Analysis view.

## 2. What makes the architecture meaningful

Do not say “we used multiple agents” as the whole contribution. Explain the system's responsibilities:

1. **Guarded FSM:** owns request states, guards, budgets and terminal outcomes.
2. **Task DAG / R2 harness:** schedules independent acquisition tasks and executes typed tasks with timeouts and traceable results.
3. **Evidence critic:** validates schema, units, time, location, freshness and lineage where metadata allows.
4. **R3 bounded recovery:** selects a targeted permitted action for a diagnosed gap, executes it, then revalidates; it stops when the budget is exhausted or progress fails.
5. **R1 Laya adapter:** optional typed-decision selector for the allow-listed recovery actions. Rules are the baseline; Laya is evaluated against them and cannot decide release.
6. **Independent release policy:** can pass, block or declare a check non-evaluable. A missing source is not proof that no hazard exists.
7. **Evidence trace:** exposes the source, relevant time, attempted action, recovery result and reason for withholding a conclusion.

**Novelty wording:** position this as our proposed technical contribution and evaluation hypothesis. Do not claim nobody else does it, and do not claim patentability without a proper prior-art and professional IP review.

## 3. The three refactors

- **R1 — Laya decision adapter:** experiments with a structured decision engine to select among safe, allow-listed recovery actions. It is not the marine forecaster and does not calculate hazard probabilities.
- **R2 — Agent harness:** typed task handoffs, state/checkpoint, permissions, timeouts, bounded retries, idempotency where needed and an auditable run trace.
- **R3 — Bounded decision-aware recovery:** uses the exact validator gap to pick the next action, checks progress, prevents repeated futile work and abstains when unresolved.

## 4. Demo script — use only verified behaviour

### 4.0 Deterministic Backend Demo Runner (Offline CLI)

To demonstrate the full decision pipeline immediately without network connectivity, API keys, or frontend dependencies, run:

```bash
cd backend
uv run python -m scripts.demo_runner
```

This runs three offline scenarios in an isolated temporary environment:
1. **Nominal Evidence Acquisition:** Queries `POST /api/orca/query` for Malpe coordinates. Retrieves 6 parameters (wave height, wave direction, wave period, wind speed, wind direction, wind gusts) with Open-Meteo attribution. Verifies on-disk SHA-256 artifacts. Shows independent release policy strictly withholding departure clearance (`NOT_EVALUABLE`) because official IMD/INCOIS bulletins and MPA geometries remain unintegrated.
2. **Truthful Source Failure:** Simulates marine gateway failure. Proves that the API returns a truthful `PARTIAL` status with 3 weather parameters and `GAP_MARINE_SOURCE_ERROR`—never generating synthetic or hallucinatory wave data. Overall release verdict: `BLOCK`.
3. **Bounded Recovery & Honest Abstention:** (a) Simulates a missing parameter and proves that bounded recovery (R3) triggers `retry_with_backoff`, recovers the missing parameter, and reaches `SUCCEEDED`; (b) Simulates an irrecoverable gap and proves that recovery executes `abstain_and_log`, terminates on cycle 1 (max budget: 2), and reaches `EXHAUSTED`.

*Note on Frontend Demarcation:* This demo runner exercises the core decision-intelligence backend directly. The separate Next.js presentation layer (Phase 8) remains paused pending user delivery of updated frontend design documents.

### Step 1: Ask a realistic question

Use a pilot-coast question that gives a specific location and forecast-valid time. Do not imply that a prototype can authorise a real departure.

### Step 2: Show the task plan

Explain which independent data tasks the request needs and which ones can run concurrently. Show task states/results only if this is implemented in the current build.

### Step 3: Show evidence provenance

Display at least one actual, attributed live forecast if a source connection is available. Show parameter, unit, source and valid time. Identify any historical fixture separately.

### Step 4: Demonstrate a controlled failure

Use an offline fixture with a stale timestamp, missing schema field or failed gateway. Show the validator finding the exact gap. Do not induce unsafe external side effects.

### Step 5: Show the recovery loop

Show the permitted action, selector (rules or Laya only if inference was actually verified), outcome and revalidation result. If recovery does not close the gap, show an honest abstention.

### Step 6: Show the response projections

When the frontend integration (Phase 8) is authorized, switch between Field/Community and Professional/Analysis views while explaining that the underlying evidence and policy result remain the same.

### Step 7: State limitations plainly

Name unconnected official sources, missing geometry, unvalidated limits or unverified Laya runtime. Do not claim certified marine safety. Direct real decisions to official bulletins and competent authorities.

## 5. Likely judge questions

**Why not just ask an LLM?**
Because generated wording should not be responsible for deciding whether evidence is fresh, comparable or sufficient. Deterministic validators and a separate release policy constrain the result; a model may help select a next action but cannot override the gate.

**Why Laya instead of another LLM?**
Laya is intended for structured decisions over typed options rather than general text generation. We are testing whether it improves recovery-action selection versus deterministic rules. It is an experiment, not an assumed performance win.

**What are the loops?**
The guarded FSM controls the overall lifecycle; the DAG manages dependent/parallel tasks; the critic detects the gap; R3 runs bounded targeted recovery. ReAct-like tool use is restricted, Reflexion is offline-only, queue-workers are deferred, and Ralph Loop is a development technique—not runtime Sagarvani architecture.

**What happens when an API fails?**
The gateway emits a typed failure, the validator marks the affected evidence unavailable, recovery can try an allowed alternative within its budget, and the release policy blocks or abstains if evidence remains insufficient. The UI must not invent a successful advisory.

**Are the data live?**
Say precisely which adapter successfully fetched a source, at what retrieval time, and the data's actual valid/observation time. Historical NetCDF/SAR data and test fixtures are labelled separately.

**How do you prevent false consensus?**
Track source lineage and common upstream product/model-run identifiers where the provider exposes them. If lineage is unavailable, mark it unknown; do not claim independence merely because two URLs differ.

**Is this safe for real fishermen to use?**
It is a prototype, not certified marine safety service. Operational use would need authoritative feeds, validated data/licences, expert-approved vessel-specific policy, relevant governance and field evaluation.

**What is the model accuracy or safety score?**
Report only measured results on a disclosed dataset with test counts, ground-truth provenance and limitations. Do not invent a confidence or accuracy number. A small software test set is not proof of real-world safety.

**Is it patentable?**
We have a technical contribution hypothesis. Novelty, inventive step, eligibility, prior art, public disclosure and ownership require qualified review; we do not claim a legal conclusion.

## 6. A-to-Z quick glossary

- **API gateway/adapter:** source-specific code that fetches/parses a provider response.
- **Artifact:** saved raw response or derived file for a run.
- **DAG:** directed acyclic graph of tasks and dependencies.
- **Evidence:** a typed source-backed observation, forecast or advisory with provenance/time.
- **FSM:** finite-state machine that limits legal transitions.
- **Freshness:** whether the source's time/validity metadata meets a documented product-specific rule.
- **Harness:** controlled executor for tasks, permissions, deadlines, retries and logging.
- **Lineage:** source ancestry, such as the model or upstream run behind an item.
- **Laya selector:** optional component returning an allowed typed action; not the final safety authority.
- **No-progress guard:** stops recovery when the attempt repeats work or fails to reduce the identified gap.
- **R1/R2/R3:** Laya adapter / task execution harness / bounded decision-aware recovery.
- **Release gate:** independent policy that blocks or abstains when required evidence/checks fail.
- **Trace:** structured sequence of states, tasks, inputs, evidence references, actions and outcomes—not hidden chain-of-thought.
- **Valid time:** period the source data describes; distinct from the time Sagarvani retrieved it.

## 7. Claims checklist before presenting

- [ ] Did this exact source work during the recorded test?
- [ ] Is it attributed to the true provider?
- [ ] Is its timestamp/validity shown correctly?
- [ ] Is Laya inference actually run, or is only the adapter implemented?
- [ ] Did we run the tests we cite, and are the results accurately reported?
- [ ] Are unavailable feeds and non-evaluable geofence checks explicit?
- [ ] Are examples labelled `TEST_FIXTURE` or `HISTORICAL_REPLAY` when appropriate?
- [ ] Does the team describe this as a prototype rather than certified safety advice?
