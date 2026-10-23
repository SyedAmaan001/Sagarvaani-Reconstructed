# Antigravity Prompt — Sagarvani Outstanding Verification & Loop Architecture Research

## Mission
Act as a senior systems architect, marine-data integration researcher, agent-workflow researcher, and QA auditor. Research and verify the remaining open design questions for Sagarvani/ORCA before implementation. Produce a rigorous, evidence-backed Markdown report that the team can use to finalise the concept and later update the architecture and implementation documents.

This is a **research and verification task only**. We are not asking you to implement the architecture or alter the project in this run.

## Product context — treat as the current working definition
Sagarvani is one unified conversational marine decision-intelligence platform for eight stakeholder profiles found in the existing website:
1. Fishermen and coastal crews
2. Marine and port operators
3. Researchers and scientists
4. Disaster management and safety teams
5. Aquaculture and marine farming
6. Coastal tourism and recreation
7. Offshore energy and industry
8. Marine policy and conservation

The product should offer two presentation modes over the same underlying backend and evidence:
- **Field / Community View:** simpler, mobile-first, plain-language and warning-focused.
- **Professional / Analysis View:** denser maps, charts, comparisons, filters and evidence details.

Changing persona or display mode must not change the source evidence or weaken the release/safety policy.

The proposed technical focus to investigate is **evidence-aware, bounded recovery for marine advisory generation**. The working architecture includes a shared evidence/artifact store, typed task handoffs, selective data access, a stateful execution harness, a Laya decision adapter considered experimentally, a bounded recovery controller, and a deterministic release policy. Treat all proposed features as unverified until evidence confirms implementation.

The existing repository is the local SagarvaniComplete workspace. A previous audit report stated that it contains two disconnected orchestration paths, simulated frontend paths, some synthetic/stale marine values, working offline geospatial routing/safety/ranking/NetCDF components, and critical alert endpoint risks. Re-verify only where necessary; do not blindly assume that report's findings are still current. The intended strategy is to build a clean coherent implementation while selectively repurposing valuable code, not to repair everything or discard all existing code indiscriminately.

The three intended refactors are:
- **R1 — Laya decision adapter:** optional selection among an allow-list of recovery actions; benchmark against deterministic rules and, if feasible, a general LLM. Laya must not estimate real marine hazard probability or override release policy.
- **R2 — Agent harness:** bounded, observable execution with task contracts, selective context/file/data access, state, permissions, retries, timeouts, duplicate-action protection, and trace events.
- **R3 — Bounded decision-aware recovery:** use failed validation state and unresolved evidence gaps to choose targeted next actions, revalidate, and terminate/abstain when necessary.

## Strict operating and safety rules
1. **Do not modify the repository.** No edits, deletes, renames, formatting, new files within the repository, dependency installs, package upgrades, migrations, branch switches, resets, pushes, deployments, or configuration changes.
2. Do not invoke any endpoint or script that can send real SMS/WhatsApp/voice messages, change user data, incur usage fees, trigger alerts, or otherwise cause an external side effect. Do not run existing HTTP test scripts without inspecting their calls first.
3. Never print, quote, copy or include secrets or credentials. Do not show `.env` values, API keys, usernames/passwords, tokens, personal phone numbers or private contact information. If a secret-related issue is found, report only a redacted risk description and file path. Avoid echoing secret variable values in terminal output.
4. Do not call authenticated, paid or account-scoped APIs. Public read-only GET requests may be attempted only when documented, low-volume and clearly safe; use one small request per candidate endpoint, short timeouts, and no bulk downloads. If access terms, side effects or safety are unclear, do not call the endpoint; report the uncertainty and its official documentation instead.
5. Do not download large datasets or model checkpoints, install Laya, or incur API/model costs. You may inspect existing local data and installed packages. You may run already-supported offline tests if they are safe and do not modify the repository; explain exactly what was run.
6. Treat README claims, source comments, benchmark tables, diagrams and docs as claims until supported. Distinguish source-inspected, independently corroborated, safe-read-only-tested, offline-tested, runtime-verified and unverified.
7. Do not claim marine safety, patent novelty, inventive step, API availability, or model suitability without specific evidence. Do not invent performance measurements.
8. You may use internet research if available. Prefer official documentation, original papers and primary repositories. Include title, publisher/authors where available, publication/update date where available, access date, exact URL, and a short note about what the source does and does not establish. Mark conflicting or inaccessible sources.
9. Save a single new report **outside the repository** if local tooling permits, e.g. `Sagarvani_Outstanding_Verification_Report.md`. If that is not possible, return the complete report in your response. Do not create or modify files under the project root.

# Part A — Research appropriate agent-loop patterns

Research and compare candidate loop/workflow patterns rather than assuming one of the user-provided examples is automatically best. Include at least the following:

1. **Deterministic finite-state machine / guarded workflow loop** — explicit states, valid transitions, guards, retry budgets and terminal states.
2. **Plan-and-execute / task-graph with conditional replanning** — plan dependencies, execute independent tasks in parallel, and replan only when results or failures require it.
3. **ReAct-style tool-use loop** — alternate a structured next action with tool execution and observations. Do not expose or store hidden chain-of-thought; persist tool/action/result summaries and evidence instead.
4. **Evaluator-optimizer / generator-critic loop** — evaluate a candidate output against explicit criteria and perform bounded correction where the evaluator can reliably judge quality.
5. **Reflexion / episodic feedback loop** — record concise failure lessons for subsequent test episodes or development, without letting unvalidated reflections silently alter marine safety policy in production.
6. **Event-driven queue-worker loop** — trigger, enqueue, execute under permissions and budgets, retry transient faults, ensure idempotency, support cancellation and dead-letter/terminal failure. Assess whether this is needed now or only for asynchronous ingestion/alerts.
7. **Ralph Loop / iterative coding-agent loop** — verify its exact semantics and limits from the official Anthropic plugin/docs and primary technique source. Treat it as a development workflow, not automatically as a runtime Sagarvani loop.
8. Any other relevant pattern supported by credible literature that materially improves this design (e.g. supervisor-worker DAG, saga/workflow orchestration, checkpoint/resume). Include only if there is a clear Sagarvani use case.

Research primary sources such as:
- ReAct paper: https://arxiv.org/abs/2210.03629
- Reflexion paper: https://arxiv.org/abs/2303.11366
- Anthropic Building Effective Agents / architecture patterns: https://www.anthropic.com/engineering/building-effective-agents
- Anthropic evaluator-optimizer cookbook: https://platform.claude.com/cookbook/patterns-agents-evaluator-optimizer
- Google ADK loop workflow documentation: https://adk.dev/agents/workflow-agents/loop-agents/
- Official Anthropic Ralph Loop plugin: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop
- LangGraph persistence/durable execution docs if proposing LangGraph.

For each pattern, report:
- Core idea and authoritative source.
- What part of Sagarvani it fits.
- Benefits and costs/risks.
- Failure and termination behaviour.
- Whether to ADOPT NOW, ADAPT, DEFER, or REJECT for the first coherent implementation.
- Evidence and reasoning behind that decision.

**Required conclusion:** Recommend one composite loop architecture, not a collection of overlapping loops. Explain the outer state controller, normal task execution, critic/validation, targeted recovery, terminal states and which patterns are development-only or asynchronous-only.

Investigate and draw the likely control sequence, for example (change if research supports a better design):
`REQUESTED -> CONTEXT_VALIDATED -> TASK_GRAPH_READY -> EVIDENCE_ACQUISITION -> EVIDENCE_VALIDATION -> (RELEASE_CHECK | RECOVERY_PLANNING | CLARIFICATION | ESCALATION | ABSTAIN | ERROR | TIMEOUT) -> TERMINAL`.
Define guards and allowed transitions; do not leave termination to a model's free-form judgment.

# Part B — Shared evidence store, context, and selective agent handoffs

Research and recommend a concrete model for sharing context without giving every agent every file.

Examine the distinction between:
- Shared task/run state (small structured metadata and state transitions).
- Evidence catalogue/data registry (dataset identity, variables, spatial coverage, time coverage, units, source, license/access terms, refresh schedule, freshness policy and file pointers).
- Evidence/artifact store (large source files, downloaded response snapshots when permitted, filtered subsets, GeoJSON, chart artifacts, result files).
- Append-only run trace/provenance (actor/task, evidence IDs, source/parent lineage, timestamps, action, result, errors, model/prompt/schema/policy version).
- Handoff messages (typed outputs with references instead of embedded giant context blobs).

Recommend a **minimal first implementation** appropriate for the existing Python/FastAPI and Next.js stack. Do not require a new vector database, Redis, cloud object store or agent framework unless the need is demonstrated. Consider whether file-based local storage + JSON/SQLite/Postgres and explicit IDs is sufficient initially.

Define a typed handoff contract, at least with:
- `run_id`, `task_id`, `parent_task_id`, `status`, `input_refs`, `evidence_refs`, `output_schema_version`, `result`, `warnings`, `failure_code`, `source_lineage`, `started_at`, `finished_at`, `trace_ref`.
- Safe treatment of untrusted text in data-source content and prompt injection.
- Minimum data access per agent, path allow-lists, file-size/format limits, time/space/variable filters, read-only access where possible and audit logging.

Explain when chaining is appropriate and when independent tasks should run in parallel. Avoid a rigid serial chain where marine, weather and geospatial tasks have no dependency. The planner should create a task DAG with explicit dependency edges. Downstream tasks should receive output summaries and evidence references, then request only additional relevant fields/subsets through authorised tools.

Give one concrete example for a Malpe coastal use case showing exactly which evidence each task reads and what it passes forward; distinguish current available datasets from hypothetical future sources.

# Part C — Verify official API/data-source feasibility

Research and, where safe, verify exact data-access options for the following:
- IMD official APIs, especially port warnings, sea-area bulletins, coastal bulletins, fishermen warnings, cyclone tracks/wind/cones and relevant district/subdivision warnings.
- INCOIS official PFZ advisories, PFZ WebGIS, Ocean State Forecast, high-wave/small-vessel advisories and any documented structured/API/data-download access.
- INCOIS ERDDAP dataset catalogue, formats, griddap/tabledap access, relevant current datasets, temporal/spatial coverage and metadata.
- Open-Meteo weather/marine APIs as supplementary forecast providers, accurately attributed and with documented suitability limitations.
- MOSDAC product catalogue and data-download/API access, authentication/licence and whether current data can be accessed programmatically.
- Copernicus Marine catalogue/toolbox access if already relevant; do not install it.
- Existing local MOSDAC NetCDF and SAR files in the workspace.
- GIS/protected-area layers needed by the pilot and their official source/licence.

For each candidate dataset/API, return a table with:
1. Product/variables.
2. Official documentation and exact URL.
3. Access method (public documented GET, query/subset interface, registered credentials, manual download, not found/unclear).
4. Authentication or permissions, if documented (do not use stored credentials).
5. Format and schema examples from documentation.
6. Spatial/temporal coverage and update/freshness semantics.
7. Licence/attribution/redistribution constraints, if documented.
8. Whether a safe read-only test was actually run; exact request description (no secrets), HTTP/result summary, payload shape and timestamp if tested.
9. Failure modes/rate limits/operational caveats.
10. Recommended status: MVP source, secondary source, research-only, historical-only, synthetic-demo-only, or defer.

Do not infer an official API from a web page's existence. Distinguish an official advisory page/WebGIS from a documented machine-readable endpoint. Do not mislabel Open-Meteo values as INCOIS or IMD values. Do not treat static values or generated timestamps as live evidence.

# Part D — Verify local data inventory and freshness

Inspect only file metadata and a small representative sample when safe. For each local marine/satellite/GIS file or directory, provide:
- Path and format.
- Source identity inferred from file metadata/documentation (label as inferred if not confirmed).
- Actual time coverage / observation or file timestamp when available inside metadata.
- Variables, coordinate units, CRS, spatial extent and resolution if available.
- Whether any code uses the file today and which function/path accesses it.
- Whether it is suitable for current decision support, historical/replay evaluation, research-only analysis or demo-only use.
- Missing metadata, stale data risk, licence/attribution questions and recommended handling.

Pay particular attention to the previously reported current NetCDF files dated in 2026 versus the historical 2016 SARAL/AltiKa products; independently verify the actual metadata rather than repeating prior report values.

Do not read entire 500+ MB virtualenv or node_modules trees and do not ingest large binaries into prompts. Do not fabricate freshness rules; label proposed thresholds for domain review.

# Part E — Laya adapter and evaluation protocol

Inspect the repository and installed environment for any actual Laya implementation, model files, adapters, decision schemas, local tests or configuration. Cite exact files and line numbers. Do not download the model or install packages.

Research Laya's official repository and benchmark report, current checkpoint names, published license, runtime requirements, benchmark task definition, accuracy, calibration, option-order robustness, multilingual limitations, latency and the caveats about comparisons with Jev. Confirm all values against the source as available on the date of research. Also review the Jev paper only as a general decision-model comparison, not as proof of Laya or marine performance.

Propose a controlled experiment comparing:
- B0: current code path / recorded existing behaviour.
- B1: fixed bounded retry.
- B2: deterministic evidence-aware recovery rules.
- B3: same controller with Laya selecting from the same allow-listed action set.
- B4: optional ablations (e.g. disable lineage checks or targeted retrieval).

Define a small pilot labelled dataset of marine evidence-failure cases (suggest an initial sample size, but do not invent results): stale observation/forecast, conflicting wave/wind outputs, duplicate agents sharing upstream source, incompatible units or times, missing source, API timeout, malformed data, ambiguous location, critical official warning, prompt injection in retrieved text, no-progress retry and valid benign scenario. Specify labels, who should adjudicate critical ground truth, split/leakage controls, deterministic repeatability and metrics.

Metrics should include action accuracy per class, success/appropriate abstention, improper release against the policy test cases, useful evidence yield, redundant queries, no-progress loops, p50/p95 latency, cost and trace completeness. Keep physical hazard probability calibration separate from recovery-action scores. State which experiments can be executed without model downloads/API spend and which need team approval or a domain expert.

Do not run a marine-safety LLM decision in production, fine-tune models, or claim that Laya is better based only on its own general benchmark.

# Part F — Frontend/backend MVP implications

Using the repository's current UI and API contracts, identify what needs to change to provide a unified eight-profile application with two display modes while preserving one backend and one release policy.

Define the smallest meaningful vertical slice:
- one natural-language query with validated location, time, user role and relevant vessel/activity context;
- source-backed marine/weather evidence;
- normalised evidence records and lineage;
- deterministic comparability/freshness validation;
- targeted recovery using rules, and Laya only if independently evaluated/available;
- explicit release/abstain/error response;
- frontend map/chart/evidence presentation using actual backend payloads;
- clear separation between live data, historical data and synthetic fixtures.

Identify API contract fields, loading/error/unavailable states and which UI features must not continue using local mock scenarios when live mode is selected. Do not design eight separate backends.

# Part G — Security and policy checks

Re-check the previous report's P0 risks without invoking side-effect endpoints:
- public SMS/WhatsApp endpoints and any default recipient;
- real phone numbers inside tracked tests;
- secrets handling (never expose values);
- silent UI success on backend error;
- permissive CORS;
- any release/advisory path that passes despite critical validation errors;
- data-source misattribution, fake timestamps and hard-coded confidence.

Report issues and remediation recommendations only. Do not make changes.

# Part H — Prior art and potential technical contribution (engineering research only)

Perform a targeted technical prior-art comparison for the specific combination under study:
- evidence lineage across agent/tool outputs and shared upstream sources;
- parameter-level comparability validation across units, spatial locations and valid times;
- selecting a targeted evidence acquisition action from an unresolved decision-relevant evidence gap;
- bounded recovery with no-progress checks and explicit terminal states;
- an independent, deterministic release policy.

Search papers, open-source systems and patents. Use Google Patents, WIPO PATENTSCOPE, IP India public search where accessible, Google Scholar/arXiv and primary project documentation. Include exact links, dates, closest overlapping elements, and the differences we still need to investigate. Do not infer novelty merely because no exact name match appears. Separate product differentiation from possible patent contribution. This is not a legal opinion; flag questions for a registered patent professional, including filing status, priority date, existing disclosures and whether later-added mechanisms can be included in an existing specification.

# Required final report format

## 1. Executive decisions
Use a table with: question, recommended decision, confidence (high/medium/low), evidence, remaining dependency.

## 2. Loop pattern comparison
Compare all relevant patterns and state exactly which are adopted for runtime, optional, deferred, or development-only.

## 3. Recommended composite architecture
Provide an ASCII/Mermaid diagram and define states, guards, action contracts, termination conditions and recovery limits. Identify the minimum first implementation and the future asynchronous extension.

## 4. Shared evidence, task graph and selective retrieval contracts
Define the store/catalogue/trace/handoff structures and show one concrete example of agent inputs/outputs and references. Explicitly state which files/data each step is permitted to access.

## 5. API/source feasibility matrix
One row per data product; exact official references, access method, findings, status and caveats.

## 6. Local data inventory/freshness findings
Path-by-path metadata and recommendations.

## 7. Laya assessment and experiment protocol
Actual local status, official benchmark facts, limitations, test cases, metrics and which work can be run safely now.

## 8. Unified eight-profile/two-mode UI implications
Backend API contract changes, truthful live/error/synthetic modes, and MVP slice.

## 9. Security/safety blockers
P0/P1/P2, with file/function evidence and no secret values.

## 10. Prior-art map and IP questions
Document-by-document comparison; no unsupported novelty or patentability statements.

## 11. Implementation decisions for team approval
A short numbered list: implement in first MVP, adapt later, explicitly defer, and reject.

## 12. Outstanding questions and acceptance gates
For every unresolved item, list owner type (team/domain expert/mentor/IP professional), evidence needed, and what must pass before implementation.

## 13. Source list
Primary sources first, each linked and annotated with the specific claim it supports and the access date. Use dates and direct URLs, not search-result snippets alone.

## 14. Test log and verification boundaries
Exact safe commands run, tests passed/failed/skipped, any safe public GETs attempted, environment limitations, and all work intentionally not performed.

## 15. Clear recommendation
End with the minimum defensible Sagarvani architecture and next three steps. Do not implement them in this run.

## Quality bar
- Every major claim must have an exact file/line reference or a credible external citation.
- Mark fact vs inference vs proposed decision.
- Include negative evidence and disagreements.
- Use no fabricated benchmark/API test results.
- Be specific to this local Sagarvani checkout and its existing code.
- No edits or implementation. Stop after delivering the report.
