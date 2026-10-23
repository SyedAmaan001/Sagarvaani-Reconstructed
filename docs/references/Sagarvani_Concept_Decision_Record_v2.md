# Sagarvani — Product Concept & Architecture Decision Record

**Version:** 2.0 — research-informed concept baseline  
**Prepared:** 23 October 2026  
**Status:** Recommended design baseline for team confirmation and implementation mapping  
**Purpose:** Finalise the product and technical direction before rewriting the wider IC’26 execution, design, Claude-instructions, stagewise and testing documents.

> This record combines the SIH submission, the SagarvaniComplete forensic audit, prior source research, and additional research on agent loops, Ralph loops, shared state and selective context handoffs. It defines the proposed target; it does not imply all target components are already implemented.

## 1. Executive decisions

1. **Product:** Keep Sagarvani as one unified, evidence-aware marine decision-intelligence platform serving all eight stakeholder profiles through one backend and two presentation modes: **Field / Community** and **Professional / Analysis**.
2. **Backend:** Repurpose proven algorithms, verified parsers, data-provider clients, geospatial assets and valuable UI components from SagarvaniComplete. Create one canonical request-to-advisory workflow instead of connecting the two competing existing orchestrators.
3. **Agent design:** Use a **typed chain with controlled fan-out/fan-in**. One task's structured result becomes the next task's input, but agents receive only the compact context and evidence references relevant to their assigned task. They do not receive every file or the full conversation by default.
4. **Shared data:** Build a shared, typed **Task State + Evidence/Artifact Store** with a searchable catalogue and per-run trace. A shared directory is useful for local datasets, fixtures, cached payloads and handoff artifacts; it is not a licence to load the entire folder into a model prompt. In deployed environments, persistent task state and large raw files should live in the appropriate database/object store, with the same reference-based interface.
5. **Runtime loop:** Implement a small, explicit **trigger → understand/context-compile → plan/execute → validate/critic → continue/recover/exit** loop. It must have tool allow-lists, time/cost/action budgets, duplicate/no-progress detection, and deterministic stop/release conditions.
6. **Ralph Wiggum loop:** Consider the Ralph Loop as a **Claude Code development technique** for isolated coding tasks with objective test criteria and a maximum iteration count. Do not embed the Ralph plugin into Sagarvani's live marine-decision runtime.
7. **Laya:** Keep Laya behind a replaceable decision-adapter interface. Run it only as an experiment against a rules-based fallback and the same labelled Sagarvani recovery cases. No model score becomes a marine hazard probability; Laya cannot override the release policy.
8. **Safety:** The deterministic release policy—not the LLM, Laya, a majority of agents or the UI mode—decides whether an advisory may be released. If required evidence remains insufficient, report uncertainty/unavailability, request clarification or escalate.
9. **Research/IP:** The candidate technical contribution remains a hypothesis: provenance-aware comparability and false-consensus checks linked to targeted, bounded evidence acquisition and an auditable release policy. Novelty/inventive step and the final brand name remain unresolved pending professional review.

## 2. Product definition

### Problem
Marine users need to combine relevant ocean conditions, forecasts, official warnings, geospatial constraints and related information for a specific place, time and activity. Evidence can be missing, stale, mismatched in location/time/units, contradictory, or correlated because several apparent sources depend on the same upstream feed.

### Solution
Sagarvani is a conversational marine decision-support platform that plans relevant data tasks, retrieves and normalises evidence, preserves source lineage, validates evidence quality and consistency, and seeks targeted additional evidence where a material gap blocks a defensible result. It produces an explainable, qualified advisory only when a separate deterministic policy permits it; otherwise it transparently asks for clarification, withholds the result, or escalates.

### Working pitch
**Sagarvani turns fragmented marine information into context-specific, evidence-backed decision support—and identifies when the evidence needs further checking before it responds.**

### Boundaries
Sagarvani is a decision-support system, not a guarantee that a trip is safe. It must not invent physical hazard probabilities, override official warnings, or present old/static/synthetic data as current observations. A Potential Fishing Zone is not a guaranteed catch prediction.

## 3. Users and unified experience

The current stakeholder explorer identifies eight profiles. Treat them all as first-class personas:

1. Fishermen and coastal crews.
2. Marine and port operators.
3. Researchers and ocean scientists.
4. Disaster management and safety teams.
5. Aquaculture and marine-farming operators.
6. Coastal tourism and recreation operators.
7. Offshore energy and marine industry.
8. Marine policy and conservation stakeholders.

### Two presentation modes, one source of truth

- **Field / Community View:** mobile-first, low-clutter, accessible wording, key conditions and official warnings, concise evidence cards, map and clear next steps. Language/voice affordances appear only where actually connected and tested.
- **Professional / Analysis View:** layered maps, filters, time series, source/lineage explorer, data-quality flags, scenario comparisons, trace inspection and report/export capabilities.

A role/profile selector configures defaults, suggested tasks, terminology, widgets and information density. Users can switch modes. Both modes use the same APIs, evidence, execution state and release policy. A display toggle is not authorisation; backend permissions govern restricted data/actions.

A unified MVP means one application, one evidence model, one request/trace contract, one canonical backend pipeline, and truthful capability states. It does not mean all specialised workflows for all eight personas must be complete immediately. Mark capabilities **live/verified**, **limited**, **historical**, **demo-only**, or **planned** according to what is actually implemented and tested.

## 4. Relationship to the SIH architecture

The SIH slide already proposed access channels, interpreter, Main Orchestrator, Planner, Reasoning/Validation Agent, Visualizer and six specialist agents. It includes a return path on inconsistent/conflicting/low-confidence output. The target preserves that product idea.

What is being made more precise is the feedback/control mechanism:

- One canonical request-to-decision pipeline, rather than separate conflicting orchestration paths.
- Typed task contracts and structured result envelopes.
- Durable/shared task state separated from the small working context sent to a model.
- Evidence identity and upstream-source lineage so correlated outputs are not mistaken for independent corroboration.
- Validation failures become machine-readable codes and evidence gaps.
- A controller chooses a targeted corrective action within a bounded budget instead of blindly rerunning all agents.
- Laya may select an eligible recovery action but cannot create facts or authorise release.
- A separate deterministic release gate prevents the critic, planner or renderer from bypassing safety requirements.
- The frontend reads the backend's actual result and traces; it never converts API failure to a synthetic success.

## 5. Proposed architecture

### A. Request and context compiler
Parse the request into a schema: intent, user profile, location/geometry, valid time window, activity/vessel constraints where relevant, requested output and missing required fields. Validate coordinates/time/units. Ask the user for clarification where needed. Do not allow an LLM to fabricate missing fields silently.

### B. Planner and task graph
Create a small typed task graph. Independent evidence acquisition tasks can run in parallel; dependent tasks run sequentially. The plan declares each task's input contract, required fields, allowed tools, dependencies, timeout/budget and acceptance criteria. Do not force a linear serial chain where safe parallel work is possible.

### C. Agent harness
The harness is the control plane around execution. It owns run/task IDs, state transitions, allowed tool registry, timeout and retry budgets, cancellation, idempotency, task scheduling, trace events, error propagation and termination. A “specialist agent” may be ordinary Python/domain code, a retrieval adapter, a numerical function, or an LLM-assisted step. Do not create a separate LLM agent where a deterministic function is better.

### D. Data gateway and specialised domain tools
Adapters expose explicit queries such as `get_weather(location, time_window, variables)`, `get_pfz(area, valid_time)`, `get_official_warnings(area, time_window)`, `get_restricted_zones(geometry)`, and `get_netcdf_subset(dataset_id, bbox, time, variables)`. Data access stays in backend tools; raw data files are not pasted wholesale into LLM context.

### E. Shared evidence and artifact state
Keep durable state separate from per-call prompt context. The shared state contains user/run metadata, task statuses, evidence records, source health, lineage links, allowed action set, remaining budgets, validation findings and terminal status.

Recommended local development layout (adapt to actual project conventions):

```text
workspace/
  data_catalog/          # metadata/index of accessible datasets; not a copy of all data
  fixtures/              # labelled synthetic test inputs; never treated as live
  cache/                 # bounded cached provider responses, with expiry and attribution
  artifacts/<run_id>/    # larger derived artefacts, GeoJSON, charts, extracted subsets
  traces/<run_id>.jsonl  # append-only structured workflow events
  handoffs/<run_id>/     # small typed task-result envelopes / review artifacts
```

The actual large source files may stay in their managed data directories or move to object storage later. The catalogue points to them by ID/path/URL and metadata. Agents do not receive unrestricted filesystem access; they use scoped, allow-listed retrieval tools. One shared store is the source of truth—agents should pass evidence/artifact IDs rather than creating divergent copies of the same evidence.

### F. Typed agent-to-agent chain

Every handoff should be a typed object, not an unconstrained prose dump. Suggested envelope:

```json
{
  "run_id": "...",
  "task_id": "...",
  "task_type": "weather_evidence",
  "status": "completed|partial|failed|needs_clarification",
  "summary": "Compact task result for the next stage",
  "result": {"...": "schema-validated values only"},
  "evidence_refs": ["evidence-id-1"],
  "artifact_refs": ["artifact-id-1"],
  "lineage_refs": ["source-record-id-1"],
  "quality_flags": ["..."],
  "errors": [],
  "eligible_next_actions": ["..."],
  "trace_ref": "..."
}
```

Schema details should be specialised for each result type. Do not use a generic `confidence: 0.94` field unless it has a defined meaning and calibration evidence. The next task receives the previous structured result and relevant evidence references; if it needs more information, it asks a controlled retrieval tool for a narrow subset.

Example chain (with fan-out/fan-in):

1. Interpreter → validated request context.
2. Planner → task graph and dependencies.
3. Marine, weather and geospatial tools → run independent queries in parallel where appropriate.
4. Evidence normaliser → canonical evidence records in shared state.
5. Comparability/provenance validator → typed pass/fail findings and unresolved gaps.
6. Recovery controller → eligible next action.
7. Laya adapter or rule policy → selects one eligible action; controller validates it.
8. Harness executes only that action/tool and appends new evidence.
9. Validator checks the updated state; bounded loop repeats only if useful.
10. Deterministic release gate → response renderer for Field or Professional View.

The chain passes **minimal summaries plus references**. A researcher-oriented analysis task can ask for an aggregated time series; a risk task can ask for a compact subset for one location/time; neither receives every source file by default. NetCDF/GeoJSON/large CSV files are processed by backend parsers and query functions; the LLM receives only the required, provenance-bearing slices or derived statistics.

### G. Evidence envelope and lineage
Each evidence record should include where applicable: evidence ID; provider/product/dataset; source URL or identifier; parent/upstream lineage IDs; variable/value/unit; geometry or point/grid; spatial and temporal resolution; observed/forecast/advisory/historical/derived/synthetic classification; retrieval, issue/observation and valid times; quality/availability flags; transformation history; attribution/licence.

A query-time generated timestamp is not an observation timestamp. Multiple agents querying one upstream source should be recorded as correlated lineage, not independent confirmations. Validate comparability before comparing values.

### H. Recovery policy, Laya and critic

Allowed actions are a bounded vocabulary such as:

- `REQUERY_SOURCE` — retry transient faults only;
- `QUERY_ALTERNATIVE_SOURCE` — only when a semantically comparable and permitted source exists;
- `RECOMPUTE` — recompute from valid available evidence;
- `EVALUATE_ALTERNATIVE_TIME` — retrieve and validate the data for an alternate window before presenting it;
- `ASK_USER` — resolve missing/ambiguous context;
- `ESCALATE` — request qualified human review;
- `WITHHOLD` / `STOP` — terminate without issuing an unsupported advisory.

Laya receives the compact failure/validation state plus the currently eligible actions. Its output is schema-validated and checked against current state, allow-list, policy and budgets. If unavailable, invalid or not useful in evaluation, deterministic rules remain the working fallback.

A critic is not a free-form second opinion that votes on safety. Deterministic validators handle measurable conditions first. A separate LLM critic may be used for bounded semantic checks such as whether an explanation cites the evidence it claims to use, whether required fields are addressed, or whether a result contradicts the request; its findings become validation signals, not permission to override the deterministic release gate.

## 6. Loop integration decision

### Adopt an application-specific bounded control loop

Use this lifecycle:

**TRIGGER → CONTEXT UNDERSTANDING → PLAN → EXECUTE ONE ELIGIBLE STEP → VALIDATE/CRITIQUE → (RECOVER / ASK / ESCALATE / RELEASE / STOP).**

- **Trigger:** new user request or a task event that needs recovery (timeout, unavailable source, stale/missing evidence, schema failure, material contradiction, provenance/comparability failure).
- **Context understanding:** compile the minimum current request state, task status, evidence refs, past actions and budgets needed for this decision.
- **Execution protocol:** select and execute one permitted action through the harness; record inputs, outputs, side effects and trace IDs.
- **Critic/validator:** run deterministic validation; optionally run a narrowly scoped semantic critic. Return typed issues, not just a prose critique.
- **Continuation:** continue only when a permitted action can plausibly reduce a material unresolved gap and budgets remain.
- **Successful exit:** required evidence and deterministic release-policy checks pass; render a qualified advisory with limitations.
- **Blocked exit:** critical evidence remains unavailable/conflicting, a clarification is needed, an action is ineligible, a budget expires, the next action repeats without progress, or a source/tool fails irrecoverably. Return uncertainty/unavailable status or escalate.

Guardrails for every loop: max action/iteration count; per-tool and overall wall-clock budget; request/API/cost budget; tool allow-list and schema validation; timeouts; idempotency and duplicate-side-effect checks; no-progress fingerprint detection; safe cancellation; prompt-injection defence for retrieved text; audit trace. Numeric limits should be configuration values calibrated through the benchmark, not invented marine thresholds. For the IC’26 prototype a small default recovery budget (for example, no more than two recovery actions) can be tested, but must remain configurable.

### Queue-trigger-guardrail-termination pattern

Use a queue/event-oriented loop only for work that is genuinely asynchronous or long-running: scheduled dataset ingestion, expensive historical analytics or later alert/subscription workflows. Trigger on a queued job or source update; guard by job state, permissions, idempotency, backoff and budgets; terminate on completed, failed, cancelled, stale/dead-letter or expired jobs. Do not add a queue/worker infrastructure just for the synchronous hackathon request flow if one in-process state machine is sufficient.

### How Ralph Loop fits

“Ralph Wiggum” is an iterative **coding-agent** technique: repeatedly feed the same task prompt to Claude Code, rely on changes/tests/Git artifacts as persistent state, and stop on a completion condition or maximum iterations. Anthropic's official plugin documents `/ralph-loop`, `--completion-promise` and `--max-iterations`; its documentation warns to use a maximum iteration cap because an impossible task can keep looping.

Use it only for small, testable implementation tasks where success is objectively verifiable—for example, implement the `EvidenceEnvelope` schema plus unit tests, or bind one map component to a known backend contract. Keep a human reviewing diffs, protect the Git working tree, run tests each iteration, set a low iteration cap, and do not use automatic permission-bypass options. Do not run a broad “build all of Sagarvani” Ralph loop. Ralph is a development workflow, not a runtime marine-recovery algorithm.

## 7. Data/API integration strategy

Prioritise source adapters that give us defensible provenance and actual structured data. Verify the exact endpoint, access terms, schema, update cadence, location/time coverage, rate limits and production reachability per feature before calling it live.

### Priority 1 — official warnings and core marine products
- **IMD public API reference:** investigate coastal/sea-area/port/fishermen warnings, district/subdivision warnings, cyclone information and lightning. Keep official warnings separate from general model forecasts.
- **INCOIS PFZ advisories and Ocean State Forecast:** establish the exact supported structured access path; do not assume the public WebGIS implies a public unrestricted REST API.
- **INCOIS ERDDAP:** inspect current catalogue/dataset metadata and test subset requests for the exact relevant product/variable/time/region.

### Priority 2 — supplementary forecasts and scientific products
- **Open-Meteo Marine API:** practical supplementary hourly wave/swell/current/SST forecast source. Label provider/model attribution exactly and respect the provider's stated accuracy/usage limits; not an official IMD/INCOIS warning substitute.
- **MOSDAC API:** authenticate and select exact dataset IDs/products; retain source/file dates and licences.
- **Copernicus Marine Toolbox:** useful for selected historical/reanalysis products and subset downloads; verify account requirements, update cadence and intended use.
- **Existing local MOSDAC NetCDF:** retain the verified parser; use files with actual dates and coverage. Historical data is useful for offline evaluation and science views, not false real-time claims.
- **GIS:** use appropriately licensed machine-readable geometries for calculations. WMS is display imagery, not replacement geometry for deterministic route/geofence checks.

### Data remediation
Replace fabricated SST/chlorophyll, artificial timestamps, hard-coded confidence, synthetic tide curves and expired live-path PFZ entries with verified adapters or clearly labelled fixtures. Source outages must remain unavailable states—not green/safe defaults. Every value displayed should link back to an evidence record and its provenance.

## 8. Evaluation plan for the proposed contribution

Use identical versioned examples, snapshots, prompts/schemas and time/cost budgets to compare:

- **B0:** current repository behaviour as audited;
- **B1:** fixed bounded retry;
- **B2:** structured evidence + deterministic validation + targeted rule-based recovery;
- **B3:** same as B2, but Laya selects among eligible recovery actions;
- **Ablations:** remove lineage checks, targeted action selection or other proposed mechanisms to see what contributes.

Test stale/missing/conflicting data, incompatible units/times/locations, correlated duplicate evidence, unavailable API, malformed payload, ambiguous query, untrusted-source prompt injection and critical official warnings. Keep historical expert-labelled cases, synthetic fault injection and live API smoke tests separately labelled.

Measure at least: critical-policy violation rate on the defined suite; appropriate withholding/abstention; useful evidence yield; recovery success on eligible failures; redundant/no-progress query rate; action selection accuracy; trace completeness; p50/p95 latency; cost per task. Report sample size and limits. Synthetic tests demonstrate mechanism behaviour, not real-world marine safety. If Laya does not beat the rules baseline, keep the adapter boundary and use rules.

## 9. Recommended additions

Adopt now as architectural requirements:

1. **Evidence lineage / false-consensus detection.** Track upstream dataset lineage and comparability before interpreting agreement.
2. **Source health and honest degradation.** Expose available/stale/failing/unknown source status; never convert failure into safe.
3. **Replayable test harness and traces.** Capture request, versions, tool calls, evidence refs, validation findings, recovery choices, budgets and terminal state.
4. **Selective context retrieval.** Agents obtain only needed data through narrow tools; no full-folder or full-history context by default.
5. **Typed handoff contracts.** Schema validation at every agent boundary; reject malformed/unpermitted results.
6. **Deterministic release policy.** Independent and testable; the LLM/Laya/critic cannot override it.
7. **Role-adaptive UI backed by one API.** The Field/Professional toggle changes layout and task defaults, never evidence or release rules.
8. **Human review and correction capture.** Critical/unresolved cases can escalate; feedback is recorded with provenance for later evaluation.

Defer unless actual requirements demand them: another agent framework, vector database, fine-tuning Laya, a new predictive marine model, broad satellite-image analysis, background notifications and message queues for synchronous requests.

## 10. Security, IP and naming boundaries

- Do not make live alert/notification endpoints publicly callable without authentication, rate limits, consent and explicit authority; omit alert sending from the weekend MVP unless properly secured.
- Do not log raw credentials, unnecessary personal data or sensitive location histories. Apply least privilege to data and tools.
- Treat all retrieved webpages/dataset text as untrusted input; source content cannot alter tool permissions or policy.
- Never publicly claim a patent is pending/granted, or claim novelty/inventive step, unless verified by the team/IP professional.
- INCOIS previously used “Sagar Vani” as the name of an ocean-information dissemination system. The product name requires separate trademark/positioning review; the technical architecture should be brand-independent.

## 11. Still-pending verification (research is not a substitute for testing)

1. Confirm permission/rules for using the existing SIH project and for public technical disclosure.
2. Validate actual IMD endpoints and structured INCOIS PFZ/OSF access with safe read-only requests.
3. Inspect each local data file's date range, coordinates, resolution, variable names, units, licence and intended use.
4. Obtain domain review for evidence sufficiency and any operational thresholds.
5. Run the actual B0/B1/B2/B3 evaluation; Laya's benchmark alone cannot decide its usefulness.
6. Conduct a focused prior-art mapping around lineage-aware evidence comparability + targeted evidence acquisition + bounded loop + release gate, with the mentor/patent professional.
7. Verify the Sagarvani name before public launch.
8. Map every proposed requirement to actual repository files only after the team decides the canonical new project structure.

## 12. Research sources

- Anthropic, **Loop engineering: Getting started with loops** (30 June 2026): https://claude.com/resources/articles/getting-started-with-loops — distinguishes turn-based, goal-based and time-based loops; recommends explicit measurable stop conditions and limits.
- Anthropic, **Ralph Loop official plugin**: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop — documents same-prompt iteration, completion promise and maximum iteration cap.
- Geoffrey Huntley, **Ralph Wiggum as a software engineer**: https://ghuntley.com/ralph/ — source description of the coding-loop method; one small task per loop is a key guideline.
- Anthropic, **Effective harnesses for long-running agents**: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents — supports incremental task work and structured artifacts for context handoff between coding sessions.
- Anthropic, **Harness design for long-running application development** (24 March 2026): https://www.anthropic.com/research/harness-design-long-running-apps — planner/generator/evaluator, sprint contracts, file-based handoffs and hard evaluation thresholds.
- Google Developers Blog, **Architecting efficient context-aware multi-agent framework for production** (4 Dec 2025): https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/ — durable structured state separate from per-call working context; minimum context by default; explicit handoff slices.
- Microsoft Multi-agent Reference Architecture, **Context Engineering**: https://microsoft.github.io/multi-agent-reference-architecture/docs/context-engineering/Context-Engineering.html — minimise irrelevant content and maximise useful current context.
- Anthropic Claude Platform docs, **Manage tool context**: https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context — tool search, context editing, caching and programmatic tool calling to manage context bloat.
- IMD public API reference: https://api.imd.gov.in/public/api_reference.html
- INCOIS PFZ advisory: https://www.incois.gov.in/MarineFisheries/PfzAdvisory
- INCOIS PFZ WebGIS: https://incois.gov.in/MarineFisheries/PfzWebGis
- INCOIS Ocean State Forecast: https://www.incois.gov.in/site/services/osf.jsp
- INCOIS ERDDAP: https://erddap.incois.gov.in/erddap/index.html
- MOSDAC data-download API manual: https://www.mosdac.gov.in/downloadapi-manual
- Open-Meteo Marine API: https://open-meteo.com/en/docs/marine-weather-api
- Copernicus Marine Toolbox: https://help.marine.copernicus.eu/en/articles/7949409-copernicus-marine-toolbox-introduction
- Laya benchmark report: https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md
- Jev evaluation: https://arxiv.org/abs/2609.37647
- AgentBench: https://github.com/THUDM/AgentBench
- Holistic Agent Leaderboard: https://arxiv.org/abs/2510.11977
- OceanAI: https://arxiv.org/abs/2511.01019
- FloatChat: https://www.sciencedirect.com/science/article/pii/S1574954126003973
- Sensorium Arc: https://papers.neurips.cc/paper_files/paper/2025/hash/e37ba633f46635915994bd99db474305-Abstract-Creative_AI_Track.html

## 13. Final architecture decision summary

**Adopt:** one unified product and evidence model; two UI modes for all eight personas; canonical backend workflow; typed task handoffs; selective retrieval; shared state/evidence/artifact references; event-triggered bounded validate/recover loop; optional Laya action selector; deterministic release gate; replayable evaluation.

**Use Ralph Loop for:** small Claude Code implementation tasks only, with explicit acceptance tests, human-reviewed diffs and iteration caps.

**Do not adopt yet:** a new agent orchestration framework or a queue/worker system solely for the synchronous request path. Start with a lightweight explicit state machine. Add durable queue/worker infrastructure only when real asynchronous ingestion or long-running jobs require it.

**Freeze rule:** the next document set should be revised from this concept baseline. Final per-file implementation decisions are made only after mapping these contracts to the target clean project and validating available data sources.
