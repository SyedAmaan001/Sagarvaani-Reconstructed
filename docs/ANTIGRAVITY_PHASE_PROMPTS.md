- `# Sagarvani — Antigravity Phase Prompts` 

```
## How to use this file
```

`1. Open the actual Sagarvani workspace in Antigravity.` 

`2. Provide the approved UX specification, supplied design archive, and `docs/FRONTEND_IMPLEMENTATION_HANDOFF.md`.` 

`3. Paste **Phase 0 only**.` 

`4. Review the audit before allowing code changes.` 

`5. Use one phase prompt at a time. Do not ask Antigravity to implement the entire document in one pass.` 

`6. At every gate, explicitly approve the next phase.` 

- `# PHASE 0 — Read-only repository and backend audit` 

```
This is audit-only. Do not implement the frontend yet.
```

```
Read the approved UX specification and frontend handoff. Inspect the existing
project and backend source directly. Do not guess the stack, routing, component
library, asset paths, request schema or response schema.
```

```
Report:
```

`1. Actual workspace root and whether the design archive has been extracted.` 

`2. Frontend framework/version, package manager, entry point, route definitions and page structure.` 

`3. Existing component library, CSS/design system, fonts, themes and reusable components.` 

`4. Existing scroll/animation libraries.` 

`5. Exact asset folders and which named artwork files exist.` 

`6. Existing tests, linting, scripts, environment files and current build status.` 

`7. Existing frontend-to-backend communication and configuration.` 

```
Inspect actual FastAPI route definitions, Pydantic models, configuration,
catalog/run access and OpenAPI. Verify query and run-status routes. Identify
real input fields, output fields, enums, error semantics and whether progress
events are exposed.
```

```
For each item, mark **verified**, **partially available**, or **not available**:
```

- `Answer text/status.` 

- `Data mode/source mode.` 

- `Evidence/source metadata, timestamp and units.` 

- `Run ID, task results, decision trace.` 

- `Validation and recovery outcomes.` 

- `Release-policy state/reasons.` 

- `Geographic coordinates suitable for a genuine map.` 

```
Create `docs/FRONTEND_REPO_AUDIT.md` with the inventory, contract summary, asset
coverage, current build/test results, risks and recommended work order.
```

```
Do not change application code, routes, dependencies, package manifests,
environment files, backend logic or assets. Do not implement Phase 1.
```

```
**Stop and wait for approval.**
```

```
# PHASE 1 — Home page, hero and opening sequence
```

```
Implement **only** the entry experience and homepage hero. Use the actual
```

```
project structure discovered in Phase 0.
```

```
Include:
```

- `Approved header/navigation shell and accessible website-language control.` 

- `Supplied hero artwork selected after checking the full-resolution image/crop.` 

- `Approved headline/supporting copy, primary “Ask Sagarvani” CTA and secondary` 

- `“Explore the ocean” CTA.` 

- `Trust statement only if factually grounded.` 

- `Responsive desktop and mobile layout.` 

- `Design tokens and readable typography.` 

- `“A light across the ocean” opening sequence.` 

# `Sequence:` 

`1. Warm ivory/pale-sea field.` 

`2. Supplied waves enter from one side.` 

`3. Supplied boat enters from the opposite side with gentle bobbing.` 

`4. One soft, non-strobing lamp flash/beam.` 

`5. Beam reveals the actual homepage hero.` 

```
Aim for 1.6–2.0 seconds and approximately 2.2 seconds maximum. Load the hero
behind the animation. Include keyboard-accessible **Skip intro**, respect
`prefers-reduced-motion`, and bypass animation if artwork/JavaScript fails. No
autoplay sound. Do not replay on internal route changes.
```

```
Constraints:
```

- `Use supplied art only; no replacement imagery.` 

- `No dashboard/login/map or backend query integration yet.` 

- `Audit existing animation dependencies before adding any.` 

- `Do not change backend.` 

```
At the gate, check desktop/mobile appearance, skip, reduced-motion, focus order,
fallback, asset loading, and existing build/tests. Report changed files and
actual results.
```

```
**Stop after Phase 1 and wait for approval.**
```

- `# PHASE 2 — Audience and outcomes` 

```
Implement only the second public content stage. If the application is a long
landing page, make these sections within its existing structure; do not invent
routes without cause.
```

```
Include:
```

- `Fishers/coastal communities.` 

- `Marine researchers.` 

- `Coastal authorities.` 

- `Maritime operators.` 

- `Before → evidence checked → outcome explanation.` 

- `Short benefit statements, supplied artwork, keyboard/touch-friendly actions.` 

```
The outcome must allow either a supported answer or an explanation that evidence
is insufficient. Do not invent testimonials, impact statistics, safety
guarantees, logos, or claims that every group has a functional dedicated backend
service.
```

```
Reuse Phase 1 components and tokens. At the gate, check layout, reading order,
accessible actions, contrast, navigation and build/tests.
```

```
**Stop after Phase 2 and wait for approval.**
```

```
# PHASE 3 — How Sagarvani works and Intelligence Voyage
```

```
Implement only the workflow explanation:
```

- `Connected Ocean Ecosystem, labelled as an illustrative concept.` 

- `Gather → Validate → Recover if needed → Decide.` 

- `Plain-language explanation of evidence collection, comparability/freshness, bounded recovery and independent release-policy gate.` 

- `Intelligence-network concept diagram.` 

- `Supplied boat-and-coast imagery.` 

```
The recovery path must return to validation and must never bypass the release
gate.
```

```
Until connected to verified runtime traces, label diagrams “System concept” or
“Illustrative workflow.” No fake agent execution, fake data flows, task
completion or backend progress. Motion must have a tap/keyboard and reduced-
motion alternative. Do not implement new runtime agents or duplicate backend
orchestration in the frontend.
```

```
At the gate, verify understandable flow, recovery path, policy gate and mobile
clarity. Run relevant tests/build.
```

```
**Stop and wait for approval.**
```

```
# PHASE 4 — Evidence, exploration and public information
```

```
Implement only:
```

- `Evidence/source explanation.` 

- `Marine map preview only with a verified geographic service; otherwise an illustrative, clearly labelled preview.` 

- `Scenario replay only with verified historical data or explicitly labelled fixtures.` 

- `Roadmap/community/origin content based on approved facts.` 

- `FAQ and footer with working links only.` 

```
Rules:
```

- `Ukiyo-e map paintings/satellite arcs are not geographic data or live observations.` 

- `Do not fabricate timestamps, weather values, fishing activity, vessel locations, warnings or source freshness.` 

- `Do not add new marine data sources in this phase.` 

- `Do not show Activity Terrain unless meaningful verified time-series data exists.` 

- `Mark future items Proposed or Coming Soon.` 

```
At the gate, check truthful labels, links, content accuracy, mobile layout,
accessibility and image loading. Run build/tests.
```

```
**Stop and wait for approval.**
```

```
# PHASE 5 — Login page
```

```
Build the login page visually only unless Phase 0 verified a working
```

```
authentication backend.
```

```
Include consistent branding, responsive form layout, proper labels, validation
presentation and keyboard focus.
```

```
Do not invent OAuth or credential endpoints, send credentials to a marine query
endpoint, store raw passwords, or fabricate a successful login. If
authentication is unavailable, label it Coming Soon and provide a route back to
the public site. Show only methods verified as implemented.
```

```
At the gate, verify that no credentials are sent to unsupported endpoints. Test
accessibility and responsive design.
```

```
**Stop and wait for approval.**
```

```
# PHASE 6 — Marine intelligence dashboard and verified API integration
```

```
The backend remains the authority for evidence, validation, recovery and release
decisions.
```

```
## Step A — Revalidate API contract
```

```
Check actual FastAPI source/OpenAPI and verify each route, method,
request/response model, status codes and error shape. Candidate paths previously
reported are `GET /health`, `POST /api/orca/query`, and `GET /api/runs/{run_id}
`; verify before use.
```

```
## Step B — Workspace
```

```
Build the approved shell:
```

- `Left navigation/stakeholder view.` 

- `Central map or clear selected-area representation.` 

- `Right Ask/evidence panel.` 

- `Expandable decision trace, source lineage and release-policy panel.` 

- `Text/list alternative to map-only information.` 

- `Simple default and denser Professional/Analysis view. Both must share the same evidence and release policy.` 

```
## Step C — Ask Sagarvani
```

- `Text input and suggested questions.` 

- `Send only fields permitted by the verified request schema.` 

- `Honest loading, duplicate-submit protection and input preservation where feasible.` 

- `Render actual output fields.` 

- `Display available evidence details only when present.` 

- `Specific API errors, no canned marine recommendation replacing a failure.` 

```
## Step D — Evidence/policy
```

```
Display actual evidence, provenance, timestamps, validation, recovery, run/task
and release-policy fields where exposed by verified routes.
```

```
Preserve blocked, withheld, conflicting and `NOT_EVALUABLE` states. Do not infer
safety from evidence count, green colour or successful HTTP status.
```

```
If real progress events do not exist, use one truthful status message, not a
fake multi-stage progress indicator.
```

```
## Step E — Maps and unavailable capabilities
```

```
Only enable genuine geographic layers with verified coordinates, source,
attribution and freshness semantics. Otherwise use a labelled illustrative
panel.
```

```
Do not claim live vessel tracking, PFZ, protected-area overlays or official-
warning integration unless those sources are verified and implemented.
```

```
Voice, upload, saved insights, alerts, profile persistence and advanced charts
stay Coming Soon unless the audit verified their service contracts.
```

```
## Acceptance gate
```

```
Test:
```

`1. Successful query with available data.` 

`2. Source failure/partial evidence.` 

`3. Backend/API error.` 

`4. Withheld or `NOT_EVALUABLE`.` 

`5. Test fixture with a clear demo label.` 

`6. Historical data, if used, labelled historical.` 

`7. Mobile layout and accessible keyboard flow.` 

```
Do not weaken policy or change backend without explicit approval. Report actual
outcomes.
```

```
**Stop and wait for approval.**
```

```
# PHASE 7 — End-to-end integration, QA and release readiness
```

```
This is integration/hardening, not a new feature phase.
```

```
Verify:
```

- `Navigation and page journeys.` 

- `Shared tokens, typography and components.` 

- `Correct artwork paths, crops, alt text and load performance.` 

- `Intro skip/reduced-motion/fallback.` 

- `Accurate data-mode and source labels.` 

- `Query/source failure/partial evidence/withheld/unavailable states.` 

- `API errors, timeout/cancellation and duplicate submissions.` 

- `No non-functional controls presented as working.` 

- `Keyboard, screen reader, contrast, enlarged text, reduced motion and touchtarget behaviour.` 

- `Desktop/tablet/mobile layouts.` 

- `Existing tests, lint, production build and accessibility checks.` 

```
Do not implement authentication, voice, upload, GIS, warnings, PFZ or
notifications solely to make a checklist look complete. Do not add overlapping
animation frameworks or change backend policy as part of styling.
```

```
Create `docs/FRONTEND_ACCEPTANCE_REPORT.md` with completed phases, real working
features, Coming Soon features, commands/results, desktop/mobile screenshots or
findings, known backend limitations and tasks requiring approval.
```

```
**Stop after the report. Do not start new features automatically.**
```

