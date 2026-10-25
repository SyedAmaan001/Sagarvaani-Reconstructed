```
# Sagarvani Frontend Implementation Handoff
```

```
**Status:** Implementation handoff
```

```
**Design baseline:** `Sagarvani_Accessible_UX_Animation_Spec_v2`, the three
approved visual boards, and supplied marine artwork.
**Implementation rule:** Inspect the existing repository before choosing or
changing its structure.
```

```
## 1. Product and design objective
```

```
Build Sagarvani as a welcoming, accessible marine companion, not a uniformly
dark technical dashboard.
```

```
Use the supplied ukiyo-e-inspired marine artwork, warm ivory surfaces, indigo
and lapis illustration tones, azure interactive emphasis, icy-blue highlights,
and readable typography. Detailed artwork belongs at story moments; forms,
instructions, and evidence summaries should remain calm and readable.
```

# `Approved palette:` 

- `Icy Blue: `#AED5F5`` 

- `Azure Blue: `#367ADF`` 

- `Fresh Sky: `#4FACE5`` 

- `French Blue: `#394988`` 

- `Charcoal Blue: `#353A4C`` 

- `Warm Ivory: `#EDE4D2`` 

```
Use only artwork supplied in `Sagarvani-Design Reconstruction.zip`. Preserve
original filenames. Create derivatives only when necessary for cropping,
responsive layout, accessibility, or performance. Do not generate, retrieve, or
substitute replacement illustrations.
```

# `## 2. Mandatory repository audit` 

```
Before modifying code, inspect the supplied design-reconstruction project and
backend repository.
```

# `Record:` 

- `Actual workspace root and archive extraction location.` 

- `Frontend framework/version, package manager, entry point, routes, and current page structure.` 

- `Existing component library, CSS/design system, fonts, themes, and reusable components.` 

- `Existing scroll and animation libraries.` 

- `Exact asset folders and which supplied artwork files exist.` 

- `Existing tests, linting, scripts, environment files, and current build status. - Existing API client, environment-variable naming, CORS setup, and backend URL configuration.` 

- `Actual backend routes, request models, response models, error semantics, and OpenAPI schema.` 

```
Use the existing architecture where sound. Do not scaffold a replacement
application, duplicate the frontend, replace package manifests, or install an
animation framework before checking what exists.
```

```
If the ZIP differs from this handoff, report the discrepancy and preserve the
working source. Do not invent missing pieces.
```

```
## 3. Known backend capabilities and limits
```

```
The current prototype is reported to contain a FastAPI backend, typed contracts,
Open-Meteo marine/weather gateways, an evidence catalog and artifact store, a
```

```
guarded FSM/task harness, evidence validation, bounded recovery, and an
independent release policy.
```

```
Reported API paths:
```

- ``GET /health`` 

- ``POST /api/orca/query`` 

- ``GET /api/runs/{run_id}`` 

```
These are candidates, not permission to assume the request/response shapes.
Verify each route, HTTP method, request model, response model, error semantics,
and status codes in the actual source/OpenAPI.
```

```
Known limitations:
```

```
- Official-warning, marine-protected-area, and vessel-limit checks may remain
`NOT_EVALUABLE` until authoritative data and review requirements are met.
- The optional Laya selector is disabled by default. Actual model inference has
not been verified. Do not claim it is active unless runtime evidence proves it.
- The offline demo runner uses fixtures to demonstrate acquisition, source
failure, recovery, and abstention. These are demonstrations, not live marine
conditions.
```

```
- Legacy NetCDF/AltiKa material is historical/replay data, not a current
forecast.
```

```
- The frontend must not convert insufficient, conflicting, blocked, or withheld
results into a positive safety recommendation.
```

```
## 4. Capability matrix
```

- `| Feature | Decision |` 

- `|---|---|` 

- `| Homepage, hero, navigation, supplied artwork | Build now |` 

- `| Opening animation, skip, reduced-motion fallback | Build now |` 

- `| Use cases and explanation of evidence validation/recovery | Build now |` 

- `| Text-based Ask Sagarvani | Connect after verifying the actual query contract | | Marine/weather results | Display only fields actually returned, with source/time/data-mode details when available |` 

- `| Evidence/source details and decision trace | Display only fields exposed by verified APIs/catalog routes |` 

- `| Release-policy and `NOT_EVALUABLE` states | Show the actual outcome and reason where provided |` 

- `| Historical NetCDF/AltiKa | Historical/replay presentation only | | Offline demo scenarios | Clearly label `Illustrative demo / not live` or the actual fixture mode |` 

- `| Painted maps, satellite arcs, ship artwork | Illustrative visuals only | | Operational GIS map, accurate protected-area overlays, live vessel tracking | Coming Soon unless verified geographic services are connected |` 

- `| Official warnings, vessel-safety checks, protected-area checks, current PFZ guidance | Not verified as operational until integrated |` 

- `| Activity Terrain/live fishing-activity charts | Coming Soon unless meaningful verified time-series data exists |` 

- `| Login, accounts, saved insights, sign-out | Coming Soon unless actual authentication/persistence exists |` 

- `| File upload and document processing | Coming Soon until a real uploadprocessing contract is verified |` 

- `| Speech recognition, spoken answers, dialect support | Coming Soon until providers/capabilities and failure states are verified |` 

- `| Translated interface languages | Offer only completed, reviewed translations | | Notifications and alerts | Coming Soon until actual event and delivery services exist |` 

- `| Scenario replay using real data | Build only when its time axis, provenance, and playback semantics are real; otherwise label fixtures |` 

```
A visually complete page does not mean every backend-dependent control should be
```

```
operational.
```

# `## 5. Data truthfulness` 

```
The actual backend response and saved source metadata determine how evidence is
described.
```

```
The prototype has been reported to use data modes including `LIVE_FORECAST`,
`HISTORICAL_REPLAY`, and `TEST_FIXTURE`. Confirm the actual enum in source
before implementing labels.
```

# `Suggested meanings:` 

```
- **Live forecast:** only after a successful live adapter response; show source
and timestamp when available.
```

- `**Historical replay:** explicitly historical, with a relevant time range when known.` 

- `**Test fixture:** visibly controlled demo/test data, never presented as a current observation.` 

- `**Unavailable/source failed:** explain what could not be retrieved.` 

- `**Needs checking/conflicting/insufficient:** only when derived from the actual response or validation record.` 

- `**Withheld/not evaluable:** show the actual policy outcome and reason where available.` 

```
Do not derive status from evidence count, a timer, an illustration, a colour, or
a successful HTTP response alone.
```

# `## 6. Frontend-to-backend contract rules` 

`1. Keep backend URL configuration in the existing environment/configuration system. Identify the framework before selecting the environment-variable prefix.` 

```
2. Never expose backend secrets or private API keys in browser code.
```

`3. Build a small typed API client around actual request/response models. Do not scatter ad hoc API calls throughout page components.` 

```
4. Handle non-2xx responses, malformed data, timeouts, cancelled requests, and
unavailable backend.
```

```
5. Do not invent request properties, event streams, progress stages, or response
fields.
```

```
6. If no backend progress events exist, show one honest status message such as
âChecking the available informationâ¦â rather than pretending steps have
completed.
```

`7. Show source lineage, task outcomes, recovery trace, or policy explanations only when backed by real response fields or verified catalog/run endpoints.` 

`8. Preserve the backend's abstention and release-policy results.` 

`9. Keep frontend changes separate from backend logic. Any required backend contract change needs a documented proposal and explicit approval.` 

# `## 7. Public-site phase mapping` 

- `**Phase 1 â Home:** opening experience, header, hero, Ask CTA, Explore CTA.` 

- `**Phase 2 â Audience and outcomes:** use cases and before â evidence checked â` **�** `supported/withheld outcome.` 

- `**Phase 3 â How it works:** connected-ocean concept, Gather â Validate â` **�** `Recover â Decide, intelligence-network explanation.` 

- `**Phase 4 â Evidence and exploration:** evidence, scenario presentation, map preview, roadmap, community, FAQ, footer.` 

- `**Phase 5 â Login:** design-only until real authentication exists.` 

- `**Phase 6 â Workspace:** dashboard shell, Ask panel, actual evidence, actual policy states.` 

- `**Phase 7 â Integration:** end-to-end navigation, responsive/accessibility QA, real error states, acceptance tests.` 

```
These are implementation phases, not automatically new routes. Inspect the app
```

```
and preserve the existing route structure unless the design and active project
plan require otherwise.
```

# `## 8. Artwork rules` 

```
Inspect full-resolution images before final cropping. Maintain a manifest with
original filename, target page/component, crop/position, alt text, and
illustrative/live distinction.
```

```
Candidate uses:
```

- ``Minimalist Indigo Ukiyo-e Seascape.png` â opening atmosphere.` 

- ``Flowing Indigo Waves on Cream Paper.png` â opening wave layer.` 

- ``Ukiyo-e Fishing Boat Wave Cycle.png` â inspect/crop a boat frame for the intro.` 

- ``Ukiyo-e Seascape with Sailboat.png` or `Panoramic Ukiyo-e Wave Seascape.png` â hero.` 

- ``From Map Fragments to Lighthouse Bay.png` â evidence journey.` 

- ``Ukiyo-e Coastal Village with Satellite Arcs.png` and `Compass Currents_ A Cartographic Seascape.png` â ecosystem concept.` 

- ``Ukiyo-e Voyage to the Lighthouse.png` â Intelligence Voyage.` 

- ``Vintage Japanese Maritime Emblem Collection.png` â future avatar/emblem reference only if account support exists.` 

```
Every painted map, satellite arc, or vessel illustration is illustrative, not a
live GIS layer or tracking source. Label visuals wherever they could be mistaken
for actual geography or observations.
```

# `## 9. Opening animation` 

```
Implement âA light across the oceanâ inside the existing page-load/hero
experience.
```

```
Sequence: warm ivory/pale-sea field â supplied waves sweep in â supplied boat
enters from the opposite side â one soft lamp flash/beam â beam reveals the
homepage hero.
```

```
Requirements:
```

- `Target approximately 1.6â2.0 seconds, around 2.2 seconds maximum.` 

- `Load the hero behind the animation.` 

- `Visible, keyboard-accessible **Skip intro** control.` 

- ``prefers-reduced-motion` bypass or minimal fade.` 

- `No autoplay sound or repeated flashing.` 

- `No focus trap. Do not replay on internal route changes.` 

- `Direct hero fallback if JavaScript, artwork, or animation fails.` 

- `Prefer transform/opacity and avoid expensive canvas/shader effects.` 

- `Reuse existing animation dependencies after audit.` 

# `## 10. Dashboard states` 

```
Every interactive data feature needs appropriate states:
```

- `**Idle:** clear input and one main action.` 

- `**Loading:** prevent duplicate submissions; use honest progress.` 

- `**Success:** actual answer and available evidence.` 

- `**Partial evidence:** identify the gap if the backend reports it.` 

- `**Withheld/not evaluable:** explain the actual policy outcome.` 

- `**Source failure:** identify unavailable source; do not fabricate fallback advice.` 

- `**API/backend error:** readable message and retry where safe.` 

- `**Illustrative demo:** explicit distinction from live data.` 

```
Voice, upload, save, download, notification, or map controls must not appear
```

# `operational when they are not.` 

```
## 11. Accessibility and motion
```

- `Use actual HTML text, not text baked into art.` 

- `Provide visible keyboard focus and logical focus order.` 

- `Give controls accessible names and expanded/collapsed states.` 

- `Pair status colour with text and an icon.` 

- `Provide text/list alternatives to map-only information.` 

- `Aim for touch targets around 44â48 CSS pixels where practical.` 

- `Test mobile layouts, enlarged text, contrast, and screen-reader announcements.` 

- `Respect reduced-motion preferences.` 

- `Voice must never be the only way to submit or understand an answer.` 

```
## 12. End-of-phase gate
```

```
At the end of every phase, report:
```

`1. Files created/changed.` 

`2. Dependencies added/avoided and reasons.` 

`3. Commands run and actual results.` 

`4. Tests/build/lint results.` 

`5. Backend mismatches discovered.` 

`6. Features intentionally marked Coming Soon.` 

`7. Desktop/mobile screenshots or concise visual findings.` 

`8. Acceptance criteria passed and not passed.` 

```
Stop after the requested phase. Do not begin the next phase until the user
reviews the result and explicitly approves continuation.
```

