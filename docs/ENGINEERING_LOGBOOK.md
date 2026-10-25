# Sagarvani — Engineering Logbook

**This is a living implementation record.** Antigravity must update it during actual work. Do not fill in planned functions as though they already exist. Keep entries concise; link to source files, commits and test output where possible.

## 1. Current status

- Overall state: `COMPLETE`
- Active phase: `Phases 6, 7 & 8 — Operational Dashboard, Real Backend Integration, End-to-End QA & Final Release Readiness (COMPLETE)` (Acceptance Gate: `PASS / FULL PROTOTYPE VERIFIED`)
- Last updated: 2026-10-25 06:25 IST
- Branch / commit: `master`
- Last verified test command and result:
  - Backend Unit/Integration Tests: `uv run pytest -v` → 168 passed, 2 skipped, 0 failed (100% offline coverage, zero alert dispatch).
  - Frontend Build & TypeScript: `npm run build` → Next.js 16.4.3 (Turbopack) clean compilation in 994ms, prerendered all 4 routes (`/`, `/_not-found`, `/dashboard`, `/login`).
  - Code Quality & Linting: `npm run lint` → ESLint passed with 0 errors, 0 warnings.
  - Live Canonical Query Verification: `POST /api/orca/query` executed against live Open-Meteo marine and weather gateways; returned `status=COMPLETED`, `policy_verdict=NOT_EVALUABLE` (honest independent safety hold), 6 physical evidence items with CC BY 4.0 attribution, valid windows, and quality flags.
  - End-to-End Browser Subagent QA: Automated browser verification on `http://localhost:3000` verifying full query flow, tab switching (Advisory, Evidence Records, Release Policy Gate with expanded checks, FSM Trace & Lineage), presentation mode switching (Field View vs Analysis View), two-way navigation, and `/login` disabled credentials banner. 0 console errors, 0 failed requests.
- Main blocker: None. All 8 phases of Sagarvani Reconstructed have successfully passed their acceptance gates.
- Next action: Platform ready for demonstration and domain review.

## 2. Decision record — WHY

- **ID / timestamp:** DEC-20261025-22
- **Type:** release / phase-8-final-release-readiness
- **Context or trigger:** User directive authorizing sequential execution of Phases 6, 7, and 8 in an uninterrupted run for final release readiness.
- **Evidence and source references:** Full repository inspection; `backend/src/backend/main.py`; `frontend/src/app/dashboard/page.tsx`; `frontend/src/app/login/page.tsx`; `frontend/src/app/page.tsx`; `frontend/src/components/Navigation.tsx`; `frontend/src/components/Footer.tsx`; `frontend/src/components/Hero.tsx`; `docs/BUILD_PLAYBOOK.md`; `docs/MASTER_BLUEPRINT.md`; `AGENTS.md`.
- **Files inspected & verified:**
  - `frontend/src/app/dashboard/page.tsx`: Full operational cockpit with live Open-Meteo gateway retrieval, 8 stakeholder roles, dual presentation modes, 4 tabs (Advisory, Evidence, Policy, Diagnostics), illustrative marine cartography, and honest offline instructions.
  - `frontend/src/app/login/page.tsx`: Presentation-only preview with permanently disabled inputs and explicit notice that authentication is not available.
  - `frontend/src/app/page.tsx`: Complete long-form editorial landing page with all 12 approved public sections, original Ukiyo-e woodblock artwork, and honest status notices.
  - `frontend/src/components/Navigation.tsx`, `Hero.tsx`, `Footer.tsx`: Unified navigation linking between `/`, `/login`, and `/dashboard`.
- **Verification outcomes:**
  - Backend: 168 tests passed, 2 skipped, 0 failed.
  - Frontend: `npm run lint` clean (0 errors, 0 warnings), `npm run build` clean (4 static routes generated).
  - E2E Integration: Real Open-Meteo query returns 6 live physical evidence items; policy gate unilaterally vetos release (`NOT_EVALUABLE`) due to unintegrated official warnings and MPA boundaries.
  - Browser QA: Verified via browser subagent across desktop, tablet, and mobile; zero horizontal overflow; zero console errors.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "The backend remains the sole authority for marine evidence... Never turn blocked, withheld, conflicting, failed or NOT_EVALUABLE outcomes into a positive marine-safety recommendation."
- **Action result:** Phase 8 complete. Full release readiness achieved with zero unverified claims or fake data.
- **Status:** verified

---

- **ID / timestamp:** DEC-20261025-21
- **Type:** verification / phase-7-end-to-end-integration-qa
- **Context or trigger:** Full end-to-end integration and QA testing across live backend (`http://localhost:8000`) and Next.js frontend (`http://localhost:3000`).
- **Evidence and source references:** Playwright automated browser subagent recording `phase678_e2e_qa`; live network requests to `/health` and `/api/orca/query`; DOM inspection across all routes.
- **Actions executed:**
  1. Booted backend daemon with `uv run uvicorn backend.main:app --port 8000`. Verified `/health` returned HTTP 200 OK (`version: 0.1.0`).
  2. Booted Next.js production server daemon with `npm run start` on port 3000. Verified `/`, `/login`, and `/dashboard` returned HTTP 200 OK.
  3. Browser subagent navigated to `/dashboard`, verified `API Online (0.1.0)` health badge, and submitted live decision query for Malpe Harbour.
  4. Verified response: `status=COMPLETED`, `data_mode=LIVE_FORECAST`, `overall_verdict=NOT_EVALUABLE`.
  5. Inspected Evidence Records tab: verified 6 physical evidence items with Open-Meteo attribution, valid windows, and quality flags.
  6. Inspected Release Policy Gate tab: verified all mandatory checks, expanded `CHECK OFFICIAL WARNINGS` displaying detailed explanation of missing authority feeds.
  7. Inspected FSM Trace & Lineage tab: verified execution metrics and 0 recovery cycles.
  8. Toggled Presentation Mode switcher to Analysis View: verified scientific parameter breakdown table and upstream lineage audit.
  9. Tested Platform Home navigation and verified `/login` presentation-only state.
- **Validator result:** All automated assertions passed with 0 console errors and 0 broken assets.
- **Status:** verified

---

- **ID / timestamp:** DEC-20261025-20
- **Type:** implementation / phase-6-operational-dashboard-real-backend-integration
- **Context or trigger:** User authorized Phase 6 implementation of the operational decision workspace at `/dashboard` connected to canonical ORCA backend.
- **Evidence and source references:** Board 02 (Operational Dashboard) and Board 03 (Components) layout specifications; `backend/src/backend/main.py`; `backend/src/backend/models/`; `frontend/src/lib/api.ts`.
- **Files created/modified:**
  - Created `frontend/src/app/dashboard/page.tsx` with Newsreader serif headings, warm ivory surfaces, and accessible layout.
  - Updated `frontend/src/components/Navigation.tsx` adding Cockpit link to navigation bar and mobile drawer.
  - Updated `frontend/src/components/Hero.tsx` linking "Ask Sagarvani" CTA to `/dashboard`.
  - Updated `frontend/src/components/Footer.tsx` adding Operational Cockpit link and Phase 6 badge.
- **Key capabilities implemented:**
  - Live probe and health check indicator for `GET /health`.
  - 8 canonical stakeholder role personas with descriptive safety envelopes.
  - Coordinate & target location inputs with quick port presets (Malpe, Chennai, Kochi, Paradip).
  - Real async execution via `POST /api/orca/query` using typed `CanonicalQueryRequest`.
  - Honest offline handling displaying exact terminal launch instructions without fabricating measurements.
  - Dual presentation modes: Field & Community Advisory vs Professional Analysis & Lineage.
  - Detailed Evidence Records inspection view with units, sources, and quality flags.
  - Independent Release Policy Gate viewer with expandable check breakdowns.
  - FSM Trace & Diagnostics panel tracking run status, trace ID, and recovery cycles.
- **Status:** verified

---

- **ID / timestamp:** DEC-20261025-19
- **Type:** correction / phase-5-authentication-status-wording
- **Context or trigger:** User directive (2026-10-25 05:32 IST): Replace all statements promising authentication "coming soon in Phase 6" with honest messaging: "Authentication is not available in the current prototype. Future availability has not yet been confirmed." Preserve disabled inputs, accessibility, artwork, and navigation. Run lint and build and record actual results.
- **Evidence and source references:** User Phase 5 Final Wording Correction directive; inspection of `frontend/src/app/login/page.tsx` (five locations containing Phase 6 delivery promises identified: handleSubmit notice string, banner heading, banner body, submit button label, architecture box heading).
- **Files changed:** `frontend/src/app/login/page.tsx` — five targeted wording changes only. No other files modified.
- **Specific changes made:**
  - `handleSubmit` notice: `"Authentication service is coming soon in Phase 6..."` → `"Authentication is not available in the current prototype. Future availability has not yet been confirmed. Real credentials cannot be entered or processed."`
  - Banner heading: `"Authentication Coming Soon in Phase 6"` → `"Authentication Not Available in Current Prototype"`
  - Banner body: removed sentence `"Live session handling and role cockpits will be implemented in Phase 6."` → replaced with `"Authentication is not available in the current prototype. Future availability has not yet been confirmed."`
  - Submit button label: `"Sign In (Planned for Phase 6)"` → `"Sign In (Not Available in Prototype)"`
  - Architecture box heading: `"Future Role-Gated Architecture (Phase 6)"` → `"Planned Role-Gated Architecture (Not Yet Implemented)"`
- **Chosen action:** Deterministic targeted wording correction. No auth endpoints, session handling, user tables, packages, or sign-in logic added. Phase 6 roadmap (dashboard and verified backend integration) unchanged.
- **Selector:** deterministic rules / editorial policy
- **Reason encoded in policy:** AGENTS.md: "No synthetic fallback may impersonate a successful live advisory... Never invent values... Marine risk thresholds are unapproved until supported by authoritative guidance."
- **Action result:** Wording correction applied cleanly. `npm run lint`: exit 0, 0 errors, 0 warnings. `npm run build`: exit 0, TypeScript clean, all three routes prerendered as static content.
- **Validator result after action:** Lint and build both pass with zero errors.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 6 (operational dashboard, verified backend query `/api/orca/query` and health `/health` integration, GIS maps, and role-specific cockpits) awaits authorization; (b) Authentication is not available; future availability has not been confirmed; (c) Speech synthesis and regional dialect models remain unintegrated (labeled Coming Soon).
- **Code references and tests:** `frontend/src/app/login/page.tsx` (wording changes only), `npm run lint`, `npm run build`.
- **Status:** verified

---

- **ID / timestamp:** DEC-20261025-18
- **Type:** implementation / phase-5-login-page-and-authentication-readiness
- **Context or trigger:** User approved Phase 4 and authorized implementation of Phase 5 only: (1) Audit repository for authentication endpoints, user models, token handling, session persistence, and security configuration; (2) Implement `/login` page consistent with Sagarvani visual identity; (3) Honest availability messaging (if no authentication backend exists, implement presentation-only page with clear "Authentication coming soon" notice; do not accept or transmit real passwords; disable credential fields; do not fabricate session state); (4) Provide accessible focus states and clear navigation back to the homepage.
- **Evidence and source references:** User Phase 5 directive; repository audit of `backend/src/backend/main.py` (only `/health` and `/api/orca/query` exist; zero auth endpoints), `backend/src/backend/catalog/migrations.py` (only run, task, artifact, evidence, and catalog dataset tables; zero user/auth tables), and `frontend/package.json` (zero auth libraries installed); `AGENTS.md` truthfulness rules; Component Board 03 layout.
- **Options considered:** (1) Implement a mock client-side auth mechanism with simulated credentials; (2) Implement a presentation-only, accessibility-checked `/login` page with explicit truthful notices, inputs permanently disabled, two-way navigation, and original Ukiyo-e artwork.
- **Chosen action:** Option 2. Zero backend code or dependencies modified.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "No synthetic fallback may impersonate a successful live advisory."
- **Action result:** Phase 5 implementation complete. The `/login` route is live, truthful, and accessible. No passwords can be submitted.
- **Validator result after action:** All Phase 5 acceptance criteria satisfied. Playwright verification across Desktop/Tablet/Mobile passed.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 6 awaits authorization; (b) Speech synthesis remains unintegrated.
- **Code references and tests:** `frontend/src/app/login/page.tsx`, `frontend/src/components/Navigation.tsx`, `frontend/src/components/Footer.tsx`, `npm run build`, `npm run lint`, Playwright suite.
- **Status:** verified


- **ID / timestamp:** DEC-20261025-17
- **Type:** implementation / phase-4-evidence-exploration-roadmap-community-faq-footer
- **Context or trigger:** User approved Phase 3 and authorized implementation of Phase 4 only: (1) Evidence explanation and exploration (`EvidenceExploration.tsx`); (2) Scenario replay presentation (`ScenarioReplay.tsx`); (3) Maps, exploration and marine insights (`MapExploration.tsx`); (4) Ocean roadmap (`OceanRoadmap.tsx`); (5) Origin story and community impact (`CommunityImpact.tsx`); (6) FAQ accordion (`FaqSection.tsx`); (7) Closing call to action and complete ocean footer (`ClosingCta.tsx`, `Footer.tsx`).
- **Evidence and source references:** User Phase 4 directive; `AGENTS.md` rules and locked 30-component plan (Components 11, 13, 12/25, 14, 28, 18, 15, 16); `docs/Sagarvani_Design_Bundle_Handoff_For_Backend_Branch.md`; `docs/Sagarvani_Accessible_UX_Animation_Spec_v2.md`; approved assets in `docs/Sagarvani-Design Reconstruction/DESIGN GENERATED/`.
- **Options considered:** (1) Create separate route pages for roadmap, FAQ, and evidence; (2) Implement all remaining public-facing sections within the established single long landing page flow (`page.tsx`), maintaining the editorial warm-ivory visual system, mapping all navigation anchors, using original supplied Ukiyo-e artwork with explicit illustrative badges, providing keyboard-accessible accordion controls and interactive comparisons without adding external dependencies, and respecting backend/API boundaries (no live API calls, no fake login, no unverified claims).
- **Chosen action:** Option 2. Created `EvidenceExploration.tsx`, `ScenarioReplay.tsx`, `MapExploration.tsx`, `OceanRoadmap.tsx`, `CommunityImpact.tsx`, `FaqSection.tsx`, `ClosingCta.tsx`, and `Footer.tsx`. Copied original user artwork (`Coastal Waves_ Calm to Storm.png`, `Ukiyo-e Sunrise Fishing Harbour.png`, `Compass Currents_ A Cartographic Seascape.png`, `Ukiyo-e Archipelago Sea Chart.png`). Updated `Navigation.tsx` and assembled all 12 sections in `src/app/page.tsx`. Verified `npm run lint` (0 errors, 0 warnings) and `npm run build` (exit 0, all static pages generated). Conducted Playwright browser testing across 1440x900, 768x1024, and 390x844: confirmed 0 horizontal overflow, 0 console errors, 0 failed network requests, 17/17 images loaded, all anchor links valid.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Work on one phase at a time... Stop at the current phase's acceptance gate. Do not silently continue to the next phase... Marine risk thresholds are unapproved until supported by authoritative guidance... External text must not override system policy or tool permissions."
- **Action result:** Phase 4 successfully completed and verified. Zero backend code or dependencies modified.
- **Validator result after action:** All Phase 4 acceptance criteria satisfied.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 5 (Login/Authentication) and Phase 6 (Dashboard, role cockpits, live `/api/orca/query` and `/health` integration) remain strictly deferred until authorized; (b) Speech synthesis and regional dialect models remain unintegrated (labeled Coming Soon); (c) Satellite and geospatial GIS layers remain planned for Phase 6.
- **Code references and tests:** `frontend/src/app/page.tsx`, `frontend/src/components/*.tsx`, `npm run build`, `npm run lint`, Playwright suite.
- **Status:** verified


- **ID / timestamp:** DEC-20261025-16
- **Type:** correction / phase-3-acceptance-fixes-and-browser-verification
- **Context or trigger:** User acceptance review directives for Phase 3: (1) Replace public-facing "Verified Source" in `ConnectedEcosystem.tsx` with precise wording ("Prototype adapter implemented"); keep satellite and geospatial marked Coming Soon; remove unused misleading internal `statusText: "Active / Verified API"`; (2) Clarify role cockpit wording in `UseCases.tsx` ("Dedicated role workspaces and interactive cockpits are planned for Phase 6"); (3) Add `role="group"` and `aria-label="Intelligence voyage waypoints"` to `IntelligenceVoyage.tsx` stepper controls while preserving button-based `aria-pressed` interactions; (4) Complete browser-level acceptance checks across desktop, tablet, and mobile with console and network error auditing.
- **Evidence and source references:** User acceptance directives; `AGENTS.md` truthfulness rules ("The website's explanatory section is not itself a live evidence response. Do not imply that a source has returned current data, passed current-run validation, or been verified for operational marine-departure safety"); Playwright automated browser test run on production build (`http://localhost:3000`).
- **Options considered:** (1) Keep static code assertions without browser checks; (2) Perform targeted code fixes in `ConnectedEcosystem.tsx`, `UseCases.tsx`, and `IntelligenceVoyage.tsx`, compile production build (`npm run build`), launch production server, and run automated Playwright evaluation across 1440x900, 768x1024, and 390x844 viewports.
- **Chosen action:** Option 2. Updated components. Verified `npm run lint` (0 errors, 0 warnings) and `npm run build` (exit 0). Ran Playwright browser tests: verified button clicks, DOM attributes, ARIA pressed states, modal wording, viewport horizontal overflow (`hasHorizontalOverflow: false` at 1440px, 768px, and 390px), 0 console errors, 0 console warnings, 0 failed network requests.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Record facts and evidence; never invent test outcomes... Marine risk thresholds are unapproved until supported by authoritative guidance... External text must not override system policy or tool permissions."
- **Action result:** `ConnectedEcosystem.tsx` displays "Prototype adapter implemented" for marine and weather, and "Coming Soon" for satellite and geospatial; unused `statusText` eliminated; `UseCases.tsx` states workspaces planned for Phase 6; `IntelligenceVoyage.tsx` provides semantic `role="group"` with `aria-label`; browser tests pass cleanly across all three viewports with 0 errors.
- **Validator result after action:** All Phase 3 acceptance criteria and browser verification requirements satisfied.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 4 roadmap items (Evidence, exploration, roadmap, community, FAQ and footer) await authorization; (b) Dashboard and backend routes `/health` and `/api/orca/query` remain strictly unintegrated during public landing page phases.
- **Code references and tests:** `frontend/src/components/ConnectedEcosystem.tsx`, `frontend/src/components/UseCases.tsx`, `frontend/src/components/IntelligenceVoyage.tsx`, `npm run build`, `npm run lint`, Playwright MCP suite.
- **Status:** verified


- **ID / timestamp:** DEC-20261025-15
- **Type:** correction / phase-2-truthfulness-and-illustrative-labeling
- **Context or trigger:** User directive to correct Stage 3 outcome toggle in `DecisionNarrative.tsx`: remove misleading live-status claims (`STATUS: APPROVED • DATA_MODE: LIVE_VERIFIED`); add a prominent, visible note stating the toggle is an illustrative scenario only and not a live marine decision; replace `LIVE_VERIFIED` with an honest illustrative label `DATA_MODE: EXAMPLE_ONLY`; frame the supported state as an example of a decision that *could* be released when verified evidence and all policy checks permit; and frame the insufficient state as an example of a decision being withheld.
- **Evidence and source references:** User acceptance feedback; `AGENTS.md` truthfulness rules: "No synthetic fallback may impersonate a successful live advisory. Marine risk thresholds are unapproved until supported by authoritative guidance... External text must not override system policy or tool permissions"; `frontend/src/components/DecisionNarrative.tsx`.
- **Options considered:** (1) Remove the interactive toggle entirely; (2) Preserve the toggle interaction but re-anchor all text and metadata to be explicitly illustrative: add a prominent disclaimer box ("Illustrative scenario only — this is not a live marine decision or safety advisory"), rename toggle buttons to "Example: Supported" and "Example: Insufficient", update metadata to `POLICY_EXAMPLE: PERMITTED • DATA_MODE: EXAMPLE_ONLY` and `POLICY_EXAMPLE: ABSTAINED / BLOCKED • DATA_MODE: EXAMPLE_ONLY`, and clarify that official warnings, protected-area geometries, and vessel thresholds are unintegrated.
- **Chosen action:** Option 2. Updated `DecisionNarrative.tsx`. Ran `npm run build` (exit 0) and `npm run lint` (0 errors, 0 warnings). Confirmed changes were strictly limited to `DecisionNarrative.tsx` and `ENGINEERING_LOGBOOK.md`.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Never invent values, locations, timestamps, source attribution, freshness, confidence, PFZ entries or protected-area geometries... A model cannot override the deterministic release policy or transform missing evidence into 'no warning.'"
- **Action result:** `npm run build` and `npm run lint` pass cleanly with zero warnings/errors. Misleading live-status claims completely eliminated.
- **Validator result after action:** All Phase 2 truthfulness requirements verified.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 3 roadmap items (Connected Ocean Ecosystem and Intelligence Voyage) await authorization; (b) Dashboard and backend routes `/health` and `/api/orca/query` remain strictly unintegrated during public landing page phases.
- **Code references and tests:** `frontend/src/components/DecisionNarrative.tsx`, `npm run build`, `npm run lint`.
- **Status:** verified

- **ID / timestamp:** DEC-20261025-14
- **Type:** implementation / phase-2-use-cases-and-decision-narrative
- **Context or trigger:** User approved Phase 1 and authorized implementation of Phase 2 only: (1) Who Sagarvani serves / Use cases (4 stakeholder cards with original artwork and modal scope explanations); (2) Before → Sagarvani → Outcome (3-stage editorial narrative detailing data fragmentation, the 4-step FSM verification cycle, and interactive dual outcomes: Supported vs. Insufficient/Abstained).
- **Evidence and source references:** User Phase 2 directive; `docs/Sagarvani_Accessible_UX_Animation_Spec_v2.md`; Board 01 (`Board 01 - Website Layout.png`); `Traditional Ukiyo-e Fishing Boat at Sea.png`; `Ukiyo-e Maritime Research Voyage.png`; `Ukiyo-e Coastal Fishing Village Panorama-2.png`; `Ukiyo-e Research Ship in Stormy Seas.png`; `From Map Fragments to Lighthouse Bay.png`.
- **Options considered:** (1) Create separate route pages for each stakeholder role; (2) Integrate both sections directly into the single long-landing page flow (`src/app/page.tsx`) using modular components (`src/components/UseCases.tsx`, `src/components/DecisionNarrative.tsx`), preserve warm ivory editorial styling and design tokens, link stakeholder cards to modal role scope overviews that honestly state role cockpits integrate in Phase 6, and present the dual outcome state (Permitted vs. Abstained/Blocked) to demonstrate release policy veto authority without fabricating green success.
- **Chosen action:** Option 2. Created `UseCases.tsx` and `DecisionNarrative.tsx`. Copied original user artwork from `DESIGN GENERATED` to `frontend/public/artwork/`. Integrated into `page.tsx`. Verified interactive role scope dialogs and dual outcome toggle (Supported vs. Insufficient) on both desktop (1440x900) and mobile (390x844) via Playwright. Verified `npm run build` (exit 0) and `npm run lint` (0 errors, 0 warnings). Zero backend or legacy files modified.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Work on one phase at a time... Stop at the current phase's acceptance gate. Do not silently continue to the next phase... Marine risk thresholds are unapproved until supported by authoritative guidance... No synthetic fallback may impersonate a successful live advisory. Network/source failure must return a clear unavailable/partial/abstain state."
- **Action result:** `npm run build` passed with clean static page generation. `npm run lint` passed with 0 errors and 0 warnings. Verified on Playwright browser with 0 console errors.
- **Validator result after action:** All Phase 2 acceptance criteria satisfied.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 3 roadmap items (Connected Ocean Ecosystem and Intelligence Voyage) await authorization; (b) Dashboard and backend routes `/health` and `/api/orca/query` remain unintegrated during public site phases.
- **Code references and tests:** `frontend/src/components/UseCases.tsx`, `frontend/src/components/DecisionNarrative.tsx`, `frontend/src/app/page.tsx`, Playwright screenshots.
- **Status:** verified

- **ID / timestamp:** DEC-20261025-13
- **Type:** correction / phase-1-roadmap-consistency-fix
- **Context or trigger:** User directive to ensure complete roadmap consistency across Phase 1: remove inaccurate messages promising Ask Sagarvani or voice integration in Phase 3; label voice simply as "Coming Soon" without a phase promise; use a neutral message for the Ask Sagarvani CTA ("The interactive 'Ask Sagarvani' decision workspace is not yet available in the current prototype."); and strictly preserve the locked 7-phase roadmap.
- **Evidence and source references:** User acceptance feedback; `AGENTS.md` truthfulness rules; `frontend/src/components/Navigation.tsx`; `frontend/src/components/Hero.tsx`; `docs/Sagarvani-Design Reconstruction/DESIGN GENERATED/Traditional Ukiyo-e Fishing Boat at Sea.png`.
- **Options considered:** (1) Keep speculative phase numbers in UI notifications; (2) Remove all premature phase promises for voice and Ask Sagarvani: update `Navigation.tsx` so speech engine is labeled `Voice Coming Soon` / `Speech Engine (Coming Soon)` without promising a delivery phase; update `Hero.tsx` so Ask Sagarvani CTA displays a neutral message stating the workspace is not yet available in the current prototype; verify `npm run build` and `npm run lint`.
- **Chosen action:** Option 2. Updated `Navigation.tsx` and `Hero.tsx`. Verified build and lint checks pass cleanly with 0 errors and 0 warnings. Preserved the agreed 7-phase roadmap definitions:
  - Phase 1: Home and hero.
  - Phase 2: Audience/use cases and before → evidence checked → outcome.
  - Phase 3: Connected Ocean Ecosystem and Intelligence Voyage.
  - Phase 4: Evidence, exploration, roadmap, community, FAQ and footer.
  - Phase 5: Login.
  - Phase 6: Dashboard and verified backend integration.
  - Phase 7: End-to-end integration and QA.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Do not imply that selecting a language translates the interface or enables voice when it does not... Do not invent operational capabilities."
- **Action result:** `npm run build` and `npm run lint` pass cleanly (0 errors, 0 warnings). Zero backend or legacy files touched.
- **Validator result after action:** All Phase 1 roadmap consistency requirements satisfied.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 2 roadmap items (use cases, narrative outcome stages) await authorization; (b) Dashboard and backend routes `/health` and `/api/orca/query` remain strictly unintegrated during public site phases.
- **Code references and tests:** `frontend/src/components/Navigation.tsx`, `frontend/src/components/Hero.tsx`, `npm run build`, `npm run lint`.
- **Status:** verified

- **ID / timestamp:** DEC-20261025-12
- **Type:** implementation / frontend-scaffold-tokens-navigation-hero
- **Context or trigger:** User approved Phase 0 audit and authorized Phase 1 implementation in `frontend/`: greenfield Next.js App Router scaffold, design tokens, responsive header/navigation, editorial hero, intro wave/vessel animation ("A light across the ocean"), and accessible keyboard/reduced-motion behaviors.
- **Evidence and source references:** `docs/FRONTEND_REPO_AUDIT.md`; `docs/Sagarvani_Accessible_UX_Animation_Spec_v2.md`; Board 01 (`Board 01 - Website Layout.png`); `Minimalist Indigo Ukiyo-e Seascape.png`; `layered-waves-haikei.svg`.
- **Options considered:** (1) Scaffold full multi-page application with dashboard routes; (2) Implement Phase 1 strictly within defined boundaries in `frontend/`: Next.js App Router, TypeScript, Tailwind CSS 4, minimal Framer Motion and Lucide icons, canonical palette tokens (`#EDE4D2`, `#353A4C`, `#394988`, `#367ADF`, `#4FACE5`, `#AED5F5`), Header with website and voice language selectors, Hero with candidate headline "A clearer view of our ocean", honest advisory disclaimers, Coming Soon action drawers, and the single-sequence "A light across the ocean" intro with Skip and reduced-motion fallback.
- **Chosen action:** Option 2. Initialized greenfield Next.js in `frontend/`. Configured Inter and Newsreader fonts in `layout.tsx` and design tokens in `globals.css`. Built `Header` in `src/components/Navigation.tsx`, `Hero` in `src/components/Hero.tsx`, and `IntroAnimation` in `src/components/IntroAnimation.tsx`. Copied original user assets to `public/artwork/`. Resolved React 19 cascading setState in effect and cleaned all unused imports.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Work on one phase at a time... Stop at the current phase's acceptance gate. Do not silently continue to the next phase... Marine risk thresholds are unapproved until supported by authoritative guidance... The public website must be warm, editorial and ocean-inspired. Do not turn it into a uniformly dark dashboard."
- **Action result:** `npm run build` succeeded with static page generation. `npm run lint` passed with 0 errors and 0 warnings. Server executed and verified via Node HTTP client with HTTP 200. Zero backend or legacy code modified.
- **Validator result after action:** All Phase 1 requirements verified.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Sections 2–8 of Board 01 (Use cases, Narrative, Ecosystem, Voyage, Living Network, Community, Footer) remain for Phase 2; (b) Dashboard and live API integration remain for Phase 3+.
- **Code references and tests:** `frontend/src/app/globals.css`, `frontend/src/app/layout.tsx`, `frontend/src/app/page.tsx`, `frontend/src/components/Navigation.tsx`, `frontend/src/components/Hero.tsx`, `frontend/src/components/IntroAnimation.tsx`.
- **Status:** verified

- **ID / timestamp:** DEC-20261025-11
- **Type:** audit / frontend-implementation-readiness
- **Context or trigger:** User initiated Phase 0 Frontend Repository Audit & Implementation Readiness ahead of phased frontend development. Visual assets provided in `Sagarvani-Design Reconstruction.zip` (Boards 01, 02, 03, 46 PNGs, Haikei SVGs).
- **Evidence and source references:** `docs/FRONTEND_REPO_AUDIT.md`; `docs/FRONTEND_IMPLEMENTATION_HANDOFF.md`; `docs/Sagarvani_Accessible_UX_Animation_Spec_v2.md`; `backend/main.py`; `backend/models/query.py`; `backend/models/enums.py`.
- **Options considered:** (1) Begin immediate Next.js scaffolding in `frontend/` along with the audit; (2) Strictly enforce Phase 0 as audit-only, inspecting workspace, design boards, artwork inventory, legacy incompatibilities, backend routes and Pydantic schemas, running the offline test suite to confirm backend health, producing `docs/FRONTEND_REPO_AUDIT.md`, and halting execution at the gate for user review.
- **Chosen action:** Option 2. Maintained strict gate discipline. Proved `frontend/` is greenfield. Confirmed all 46 PNG illustrations and Haikei SVGs exist on disk. Verified active backend endpoints (`GET /health`, `POST /api/orca/query`) and catalogued missing/unimplemented endpoints. Re-verified 100% offline backend test suite (168 passed, 0 failures). Documented capability matrix, "Coming Soon" feature list, risks, and exact Phase 1 file boundaries in `docs/FRONTEND_REPO_AUDIT.md`.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Work on one phase at a time... Stop at the current phase's acceptance gate. Do not silently continue to the next phase. Frontend implementation/design is a separate workstream and later must consume the canonical backend response."
- **Action result:** `docs/FRONTEND_REPO_AUDIT.md` written and committed to disk. Backend confirmed healthy (168 tests pass). Zero frontend code modified or generated during Phase 0.
- **Validator result after action:** All Phase 0 criteria satisfied. Zero network calls or external side effects.
- **Terminal outcome:** audit complete / gated
- **Remaining known gaps (documented, not invented):** (a) Components 1–6 in Sagarvani 30-component system require explicit alignment during shell scaffolding; (b) Location fallback must be handled client-side to prevent backend `ABSTAINED` verdict; (c) Navigational charting, alert dispatch, and radar feeds remain "Coming Soon" in frontend presentation.
- **Code references and tests:** `docs/FRONTEND_REPO_AUDIT.md`, `backend/main.py`, `backend/models/query.py`, `backend/tests/` (168 passed).
- **Status:** verified

- **ID / timestamp:** DEC-20261024-10
- **Type:** bugfix / data-provenance-truthfulness
- **Context or trigger:** User identified that Scenario 1 (mocked gateways, 100% offline) incorrectly reported `data_mode: LIVE_FORECAST`. This violates Sagarvani's data-provenance requirements: a fixture-backed run must never claim live-forecast provenance.
- **Evidence and source references:** User directive (checkpoint 12 correction request); `AGENTS.md` rule: "No synthetic fallback may impersonate a successful live advisory"; `backend/src/backend/models/enums.py` `DataMode.TEST_FIXTURE`.
- **Options considered:** (1) Override `data_mode` manually in the demo runner's result dict (surface fix only — main.py would still hardcode LIVE_FORECAST); (2) Fix `_build_evidence_response` in `main.py` to derive `data_mode` from the actual evidence records (lowest-fidelity propagates: `TEST_FIXTURE` < `HISTORICAL_REPLAY` < `LIVE_FORECAST`), and also change `_make_dummy_evidence` default to `TEST_FIXTURE`.
- **Chosen action:** Option 2. In `main.py::_build_evidence_response`, compute `derived_mode = min(evidence records, key=priority)` where `TEST_FIXTURE` has the lowest priority value (0) and therefore always wins over `LIVE_FORECAST` (3). Changed `_make_dummy_evidence` default from `DataMode.LIVE_FORECAST` to `DataMode.TEST_FIXTURE`. Added inline assertions in each scenario function. Added 4 regression tests in `test_demo_runner.py`: two asserting `data_mode != LIVE_FORECAST`, two asserting `data_mode == TEST_FIXTURE`.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** Fixture evidence carries `TEST_FIXTURE` mode; the response builder must not upgrade it to `LIVE_FORECAST`. The mode is derived from the evidence, not from the count of parameters retrieved.
- **Action result:** Demo runner output now explicitly shows `TEST_FIXTURE (fixture — not a live gateway call)` for both Scenario 1 and Scenario 2. Full test suite: 168 passed (was 164), 2 skipped, 0 failed.
- **Validator result after action:** `uv run python -m scripts.demo_runner` → exit 0, both scenarios report `TEST_FIXTURE`. `uv run pytest -v` → 168 passed, 2 skipped.
- **Terminal outcome:** passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 8 Frontend integration is pending user design documents; (b) Official IMD/INCOIS bulletins and MPA geometries remain unintegrated (`NOT_EVALUABLE`).
- **Code references and tests:** `backend/src/backend/main.py` (`_build_evidence_response`), `backend/scripts/demo_runner.py` (`_make_dummy_evidence`, scenario functions), `backend/tests/test_demo_runner.py` (4 new regression tests).
- **Status:** verified

- **ID / timestamp:** DEC-20261024-09
- **Type:** implementation / backend-deterministic-demo-runner
- **Context or trigger:** User directive to pause Phase 8 frontend integration while design documents are prepared, and to implement a standalone, deterministic backend demo runner (`backend/scripts/demo_runner.py`) exercising the canonical API, guarded FSM, bounded recovery, and release veto authority offline.
- **Evidence and source references:** User request A1; `AGENTS.md` verification and safety rules; `docs/BUILD_PLAYBOOK.md` Phase 7; `backend/src/backend/main.py`.
- **Options considered:** (1) Create an ad-hoc shell script or curl commands against a live running server; (2) Create a typed, self-contained Python demo runner (`backend/scripts/demo_runner.py`) that uses `fastapi.testclient.TestClient(app)` with dependency overrides, runs inside an isolated temporary directory with a clean SQLite catalog and artifact store, executes 3 distinct scenarios (nominal acquisition with release veto, source failure handling, bounded recovery with no-progress termination), and add dedicated unit tests in `tests/test_demo_runner.py`.
- **Chosen action:** Option 2. Implemented `backend/scripts/demo_runner.py` and `backend/tests/test_demo_runner.py`. Configured isolated temporary directories to prevent polluting production or development SQLite databases (`sagarvani.db`) and artifact storage. Verified 100% offline execution with zero network access and zero external side effects.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Default execution must be fully offline... Use temporary artifact storage and SQLite databases for isolated demo runs... Clearly distinguish mocked evidence from genuinely live Open-Meteo forecasts."
- **Action result:** Demo runner executed with exit code 0 across all 3 scenarios. Full test suite: 164 passed, 2 skipped, 0 failed in 13.22s.
- **Validator result after action:** All 3 demo scenarios verified. Release policy strictly preserves `NOT_EVALUABLE` and `BLOCK` safety vetoes.
- **Terminal outcome:** continued / passed gate
- **Remaining known gaps (documented, not invented):** (a) Phase 8 Frontend integration is pending user design documents; (b) Official IMD/INCOIS bulletins and MPA geometries remain unintegrated (`NOT_EVALUABLE`).
- **Code reference and tests:** `backend/scripts/demo_runner.py`, `backend/tests/test_demo_runner.py`, `backend/pyproject.toml`.
- **Status:** verified



- **ID / timestamp:** DEC-20261024-08
- **Type:** verification / phase-7-demo-acceptance-and-bugfix
- **Context or trigger:** Phase 7 end-to-end verification across 10 mandatory operational scenarios and resolution of SQLite cascade deletion bug during run finalization.
- **Evidence and source references:** `docs/BUILD_PLAYBOOK.md` Phase 7; `AGENTS.md` verification rules; `docs/MASTER_BLUEPRINT.md` Section 3.
- **Options considered:** (1) Rely only on unit test coverage from Phases 1–6 without dedicated end-to-end scenario validation; (2) Implement comprehensive 27-test end-to-end verification suite (`tests/test_phase7_verification.py`) covering all 10 mandatory scenarios, resolve SQLite `INSERT OR REPLACE` cascade bug in `CatalogService.record_run`, rigorously document Laya runtime status (adapter implemented & tested; live inference unverified in offline environment), and produce a truthful demo acceptance matrix.
- **Chosen action:** Option 2. Created `backend/tests/test_phase7_verification.py` validating location validation, happy path linkages, source failure permutations, malformed payloads, temporal/freshness/lineage checks, bounded recovery behaviors, DAG resilience, storage failure safety, Laya fallbacks, and release policy veto authority. Fixed SQLite `INSERT OR REPLACE INTO runs` by upgrading to `INSERT INTO runs (...) ON CONFLICT(run_id) DO UPDATE SET ...` to prevent SQLite foreign key cascade deletion of `fsm_transitions` when `runs` is updated.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "The complete request-to-response path must be verified... Error, partial-data, timeout and bounded-recovery behaviour must be demonstrated by tests... A model—including Laya—cannot override the deterministic release policy or transform missing evidence into 'no warning.'"
- **Action result:** 27 Phase 7 tests pass. Full test suite: 160 passed, 2 skipped, 0 failed in 6.96s.
- **Validator result after action:** Phase 7 acceptance gate passed. All 10 scenarios confirmed. Safety gates strictly maintain `NOT_EVALUABLE` when mandatory official inputs are unintegrated.
- **Terminal outcome:** continued / passed gate
- **Remaining known gaps (documented, not invented):** (a) Official IMD/INCOIS feeds unintegrated → `CHECK_OFFICIAL_WARNINGS = NOT_EVALUABLE`; (b) Marine protected area geometries unverified → `CHECK_MARINE_PROTECTED_AREAS = NOT_EVALUABLE`; (c) Vessel operational limits uncertified → `CHECK_VESSEL_LIMITS = NOT_EVALUABLE`; (d) Real Laya model checkpoint inference is opt-in and NOT VERIFIED in the offline development environment (requires PyTorch wheel and weights ~1.5GB); fallback path and adapter contract are verified.
- **Code reference and tests:** `backend/src/backend/catalog/service.py`, `backend/tests/test_phase7_verification.py`, `backend/src/backend/main.py`
- **Status:** verified


- **ID / timestamp:** DEC-20261024-07
- **Type:** implementation / laya-decision-adapter-r1
- **Context or trigger:** Phase 6 implementation of Laya Decision Adapter (R1) as an optional, feature-gated recovery action selector.
- **Evidence and source references:** `docs/BUILD_PLAYBOOK.md` Phase 6; `docs/MASTER_BLUEPRINT.md` Sections 3.2, 4.2; `docs/DATA_AND_QUALITY.md` Sections 1, 8; Hugging Face model card `convaiinnovations/laya` (ModernBERT-large, 421M params, Apache 2.0).
- **Options considered:** (1) Hardcode mandatory dependency on heavyweight PyTorch/transformers packages and allow arbitrary string outputs from model; (2) Implement optional, feature-gated `LayaRecoverySelector` (R1) with pure lazy importing, selecting exclusively from the closed `PERMITTED_ACTIONS` allow-list via typed choice question schema, backed by rule-based fallback on timeout (3.0s), missing package, or unapproved choice, recording auditable `SelectorTraceEntry` in SQLite.
- **Chosen action:** Option 2. Implemented `LayaRecoverySelector` in `backend/src/backend/engine/laya_adapter.py`. Enhanced `RuleBasedRecoverySelector` with trace logging. Created Migration 4 in `migrations.py` adding `selector_traces` table and indexes. Updated `CatalogService` and `RecoveryController`. Added 30 comprehensive tests including 10-case comparative benchmark (`test_comparative_case_evaluation`), release policy independence, cycle/no-progress guards, SQLite persistence, and opt-in live inference.
- **Selector:** Laya (optional decision selector) / Rule-based fallback
- **Reason encoded in policy:** AGENTS.md: "Recovery must use an allow-list, a finite budget (initial design: at most two recovery cycles), and no-progress/repeated-action checks. Rules are the baseline selector. Laya is an optional, feature-flagged recovery-action selector only... A model—including Laya—cannot override the deterministic release policy or transform missing evidence into 'no warning.'"
- **Action result:** 30 Phase 6 tests pass in `tests/test_laya_adapter.py`. Full test suite: 133 passed, 2 skipped (live sources), 0 failed in 10.92s.
- **Validator result after action:** Phase 6 acceptance gate passed. Laya output validated strictly against allow-list; release policy maintains veto authority.
- **Terminal outcome:** continued / passed gate
- **Remaining known gaps (documented, not invented):** (a) PyTorch/transformers runtime wheel (~1.5GB+) is an optional runtime dependency; (b) Live inference opt-in via `RUN_LIVE_LAYA_TESTS=1`; (c) Release policy maintains `NOT_EVALUABLE` on safety gates.
- **Code reference and tests:** `backend/src/backend/engine/laya_adapter.py`, `backend/src/backend/engine/recovery.py`, `backend/src/backend/models/recovery.py`, `backend/src/backend/catalog/migrations.py`, `backend/src/backend/catalog/service.py`, `backend/tests/test_laya_adapter.py`
- **Status:** verified

 
- **ID / timestamp:** DEC-20261024-06
- **Type:** implementation / evidence-validator-recovery-release-policy
- **Context or trigger:** Phase 5 implementation of deterministic evidence validator, bounded recovery controller (R3), and independent release policy.
- **Evidence and source references:** `docs/BUILD_PLAYBOOK.md` Phase 5; `docs/MASTER_BLUEPRINT.md` Sections 3.3, 4.4; `docs/DATA_AND_QUALITY.md` Sections 2–5; `AGENTS.md` Engineering constraints and safety rules.
- **Options considered:** (1) Simple threshold-based Python functions without typed checks or audit trails; (2) Full deterministic validator (`EvidenceValidator`) producing typed `ValidationCheckItem` and `IdentifiedGap` objects, bounded `RecoveryController` with strict ≤2-cycle budget and gap fingerprinting, and independent `ReleasePolicy` with unilateral veto authority and `NOT_EVALUABLE` default for missing mandatory safety inputs.
- **Chosen action:** Option 2. Implemented `EvidenceValidator` covering 7 check families: structure/physical range (`CHECK_STRUCTURE`, `CHECK_PHYSICAL_RANGE`), unit recognition (`CHECK_UNITS`), temporal relevance and freshness (`CHECK_TEMPORAL_RELEVANCE`, `CHECK_FRESHNESS`), spatial coverage (`CHECK_SPATIAL_COVERAGE`), attribution and artifact integrity (`CHECK_ATTRIBUTION`, `CHECK_ARTIFACT_INTEGRITY`), shared upstream lineage (`CHECK_SHARED_LINEAGE`), and core marine sufficiency (`CHECK_CORE_EVIDENCE`). Implemented `RecoveryController` with `compute_gap_fingerprint`, allow-list enforcement (`PERMITTED_ACTIONS`), no-progress detection, and revalidation after each cycle. Implemented `ReleasePolicy` with mandatory `CHECK_OFFICIAL_WARNINGS`, `CHECK_MARINE_PROTECTED_AREAS`, `CHECK_VESSEL_LIMITS`, and `CHECK_EVIDENCE_ADEQUACY` checks — all three safety checks return `NOT_EVALUABLE` until authoritative data sources are integrated. Added `record_policy_checks`, `get_policy_checks`, `record_recovery_trace`, `get_recovery_trace` methods and `close()` to `CatalogService`. Added `pytest-asyncio` for async recovery tests. Added `asyncio_mode = "auto"` to `pyproject.toml`.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Marine risk thresholds are unapproved until supported by authoritative guidance and domain-expert review. Do not claim certified safety, operational navigation guidance, or validated evacuation advice. A model—including Laya—cannot override the deterministic release policy or transform missing evidence into 'no warning.'"
- **Action result:** 29 Phase 5 tests pass in `tests/test_validator_recovery_policy.py`. Full regression suite: 104 passed, 1 skipped (live network), 0 failed in 3.34s.
- **Validator result after action:** Phase 5 acceptance gate passed. Safety verdict `NOT_EVALUABLE` maintained correctly for all missing mandatory inputs.
- **Terminal outcome:** continued / passed gate
- **Remaining known gaps (documented, not invented):** (a) IMD/INCOIS official warning bulletin not integrated → `CHECK_OFFICIAL_WARNINGS = NOT_EVALUABLE`; (b) No verified marine protected area geometry source → `CHECK_MARINE_PROTECTED_AREAS = NOT_EVALUABLE`; (c) No domain-expert-reviewed vessel operational limits → `CHECK_VESSEL_LIMITS = NOT_EVALUABLE`.
- **Code reference and tests:** `backend/src/backend/engine/validator.py`, `backend/src/backend/engine/recovery.py`, `backend/src/backend/engine/policy.py`, `backend/src/backend/catalog/service.py`, `backend/tests/test_validator_recovery_policy.py`
- **Status:** verified

- **ID / timestamp:** DEC-20261024-05
- **Type:** architecture / execution-harness-and-fsm
- **Context or trigger:** Phase 4 implementation of R2 — typed task harness, guarded deterministic FSM, and dependency-aware DAG.
- **Evidence and source references:** `docs/BUILD_PLAYBOOK.md` Phase 4; `docs/MASTER_BLUEPRINT.md` Sections 3.2, 4.2; `AGENTS.md` Work protocol & Engineering constraints.
- **Options considered:** (1) Keep monolithic sequential procedural calls inside the route handler; (2) Introduce external workflow engines (e.g. Celery, Airflow, Temporal, LangGraph); (3) Build self-contained, typed, in-process deterministic FSM (`RunFSM`) with explicit allow-list transitions, terminal state enforcement, and wall-clock deadline guard, paired with a Kahn's-algorithm validated DAG (`TaskDAG`) and wave-based concurrent execution harness (`ExecutionHarness`) bounded by `asyncio.Semaphore` and task/run deadlines.
- **Chosen action:** Option 3. Implemented `RunFSM` with states `REQUESTED`, `CONTEXT_VALIDATED`, `TASK_GRAPH_READY`, `EVIDENCE_ACQUISITION`, `EVIDENCE_VALIDATION`, `RECOVERY_PLANNING`, `SAFETY_GATE_CHECK`, `RELEASED`, `ABSTAINED`, `BLOCKED`, `FAILED`, `TIMED_OUT`. Implemented `TaskDAG` with duplicate ID, cycle, and self-loop rejection, calculating topological execution waves. Implemented `ExecutionHarness` executing independent tasks concurrently while skipping tasks whose prerequisites fail or time out. Wired into `POST /api/orca/query` and added migration 2 for `fsm_transitions` SQLite audit logging.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Keep the initial MVP small: FastAPI, Pydantic, SQLite/local artifacts, typed task contracts, guarded FSM, task DAG, evidence validation, bounded recovery and offline tests. Do not add Redis, a vector DB or a large agent framework without a demonstrated requirement... A model—including Laya—cannot override the deterministic release policy."
- **Action result:** 51 comprehensive tests added in `tests/test_fsm_dag_harness.py`. All 75 tests across Phases 1–4 pass offline in 2.45s with zero regressions.
- **Validator result after action:** Phase 4 acceptance gate passed.
- **Terminal outcome:** continued / passed gate
- **Code reference and tests:** `backend/src/backend/engine/` (`fsm.py`, `dag.py`, `harness.py`), `backend/src/backend/catalog/migrations.py`, `backend/src/backend/main.py`, `backend/tests/test_fsm_dag_harness.py`
- **Status:** verified

- **ID / timestamp:** DEC-20261024-04
- **Type:** implementation / data-catalog-and-storage
- **Context or trigger:** Phase 3 implementation of path-safe, bounded raw response artifact store and repeatable SQLite metadata migrations.
- **Evidence and source references:** `docs/BUILD_PLAYBOOK.md` Phase 3; `docs/MASTER_BLUEPRINT.md` Sections 3.1, 4.3; `docs/DATA_AND_QUALITY.md` Sections 2 & 4.
- **Options considered:** (1) Write artifacts directly with uncontrolled filenames and use arbitrary SQLite queries; (2) Implement path-safe, bounded, atomic JSON artifact store (`ArtifactStore`) with SHA-256 checksums, versioned SQLite migrations (`apply_migrations`), thread-safe metadata service (`CatalogService`), and dataset registry (`catalog_known_datasets`) that explicitly flags historical NetCDF and test fixtures so they cannot masquerade as live.
- **Chosen action:** Option 2. Implemented `ArtifactStore` with strict alphanumeric regex and max byte caps. Implemented versioned SQLite schema for runs, tasks, artifacts, evidence, and catalog datasets. Integrated into query endpoint and registered legacy MOSDAC NetCDF files as `HISTORICAL_REPLAY`.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Store bounded raw response artifacts under a run-specific directory and metadata in SQLite... Mark old NetCDF/SAR files as historical/replay fixtures unless metadata and provenance independently establish otherwise."
- **Action result:** 24 offline tests pass across contracts, gateways, artifact store, and SQLite persistence. Every piece of forecast evidence traces to an on-disk artifact reference with an exact SHA-256 checksum.
- **Validator result after action:** Phase 3 acceptance gate passed.
- **Terminal outcome:** continued / passed gate
- **Code reference and tests:** `backend/src/backend/catalog/`, `backend/src/backend/main.py`, `backend/tests/test_evidence_catalog.py`
- **Status:** verified

- **ID / timestamp:** DEC-20261024-03
- **Type:** implementation / data-adapter
- **Context or trigger:** Phase 2 implementation of Open-Meteo Marine and Weather gateways.
- **Evidence and source references:** `docs/BUILD_PLAYBOOK.md` Phase 2; `docs/DATA_AND_QUALITY.md` Section 3; official Open-Meteo API documentation and terms.
- **Options considered:** (1) Reuse legacy `processors/weather_processor.py` (which used synchronous `requests` without typed evidence normalization or schema validation); (2) Build typed gateways using `httpx`, bounded timeouts, small retries, array validation, coordinate grid offset detection, and strict normalization into `EvidenceRecord`.
- **Chosen action:** Option 2. Implemented `OpenMeteoMarineGateway` and `OpenMeteoWeatherGateway` under `backend/src/backend/gateways/`. Created deterministic offline fixtures under `backend/tests/fixtures/`. Connected gateways to canonical `POST /api/orca/query` endpoint with truthful failure handling and release policy strictly `NOT_EVALUABLE`.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Open-Meteo may serve as the first explicitly attributed forecast adapter. Do not label its data as INCOIS or IMD data... No synthetic fallback may impersonate a successful live advisory."
- **Action result:** 17 offline tests passed with zero network calls. Opt-in live test (`RUN_LIVE_SOURCE_TESTS=1`) passed, verifying real Open-Meteo connectivity for coordinates (13.35, 74.70).
- **Validator result after action:** Phase 2 acceptance gate passed.
- **Terminal outcome:** continued / passed gate
- **Code reference and tests:** `backend/src/backend/gateways/`, `backend/src/backend/main.py`, `backend/tests/test_open_meteo_gateways.py`
- **Status:** verified

- **ID / timestamp:** DEC-20261024-02
- **Type:** architecture / contract-definition
- **Context or trigger:** Phase 1 implementation of canonical request, evidence, task, and response contracts.
- **Evidence and source references:** `docs/MASTER_BLUEPRINT.md` Sections 3.3, 5; `docs/DATA_AND_QUALITY.md` Section 4 & 5.
- **Options considered:** (1) Reuse legacy `ChatRequest` from legacy `main.py`; (2) Build monolithic dictionary response; (3) Build strict Pydantic v2 domain models with versioned contracts, distinct temporal semantics (`observed_at`, `issued_at`, `valid_from`, `retrieved_at`), explicit release policy audit checks (`PASS`, `BLOCK`, `NOT_EVALUABLE`), and a truthful fallback if context is missing.
- **Chosen action:** Option 3. Created `backend/src/backend/models/` (`enums.py`, `evidence.py`, `task.py`, `recovery.py`, `query.py`).
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md: "Use stable schemas, explicit enums and versioned contracts. Keep source timestamps and units. Distinguish observation time, issue/model-run time, forecast-valid time and retrieval time."
- **Action result:** Implemented `GET /health` and `POST /api/orca/query` in FastAPI. Missing location returns `CLARIFICATION_REQUIRED` with `GAP_MISSING_LOCATION` and `NOT_EVALUABLE` policy verdict. 8 offline tests pass.
- **Validator result after action:** Phase 1 acceptance gate passed.
- **Terminal outcome:** continued / passed gate
- **Code reference and tests:** `backend/src/backend/main.py`, `backend/src/backend/models/`, `backend/tests/test_canonical_contracts.py`
- **Status:** verified

- **ID / timestamp:** DEC-20261024-01
- **Type:** safety / architecture
- **Context or trigger:** Phase 0 Workspace Preservation and Safety Lockdown.
- **Evidence and source references:** Legacy `test_api_endpoints.py` line 43-44 contained hardcoded live recipient phone number invoking real Twilio alert endpoints. `DashboardClient.tsx` lines 211-231 contained client-side mock fallback fabricating a successful advisory on backend failure.
- **Options considered:** (1) Run legacy test suites directly; (2) Remove or sanitize legacy directly; (3) Preserve `legacy/` intact, initialize root `.gitignore` to block accidental leak of secrets/cache/artifacts, create safe `.env.example`, and ban execution of legacy alert tests.
- **Chosen action:** Option 3. Legacy reference is preserved intact under `legacy/Sagrvani Complete/`. Root repository initialized with strict `.gitignore` and `.env.example`. Test scripts invoking external dispatch (`test_api_endpoints.py`, `test_all.py`) flagged and quarantined from execution.
- **Selector:** deterministic rules / policy
- **Reason encoded in policy:** AGENTS.md safety rule: "Never execute tests or scripts that could dispatch real SMS, WhatsApp messages, email, voice calls or alerts. Replace provider calls with mocks and prove tests cannot dispatch externally before running relevant test paths."
- **Action result:** Workspace root initialized with Git, zero credentials exposed, no alerts dispatched, safety hazards catalogued.
- **Validator result after action:** Passed Phase 0 safety gate.
- **Terminal outcome:** recovered / passed gate
- **Code reference and tests:** `.gitignore`, `.env.example`, `legacy/Sagrvani Complete/`
- **Status:** verified

## 3. Runtime workflow — HOW THE REQUEST MOVES

Antigravity maintains this section against the implemented code, not only the target blueprint.

- **Canonical entry point(s):**
  - `GET /health` -> `HealthResponse` (`backend/src/backend/main.py:health_check`)
  - `POST /api/orca/query` -> `CanonicalQueryResponse` (`backend/src/backend/main.py:canonical_orca_query`)
- **Actual states and legal transitions:** Full deterministic lifecycle (`REQUESTED`, `CONTEXT_VALIDATED`, `TASK_GRAPH_READY`, `EVIDENCE_ACQUISITION`, `EVIDENCE_VALIDATION`, `RECOVERY_PLANNING`, `SAFETY_GATE_CHECK`, `RELEASED`, `ABSTAINED`, `BLOCKED`, `FAILED`, `TIMED_OUT`) enforced by `RunFSM` (`backend/src/backend/engine/fsm.py`). Missing location yields `CLARIFICATION_REQUIRED` and transitions to `ABSTAINED`.
- **Task DAG:** Implemented via `TaskDAG` (`backend/src/backend/engine/dag.py`) validating acyclicity and calculating topological execution waves.
- **Task harness:** Implemented via `ExecutionHarness` (`backend/src/backend/engine/harness.py`) executing concurrent tasks bounded by `max_task_concurrency` semaphore and wall-clock deadlines, with automatic prerequisite failure skipping.
- **Evidence validation:** Implemented via `EvidenceValidator` (`backend/src/backend/engine/validator.py`) executing 7 check families: structure, physical ranges, units, temporal relevance/freshness, spatial coverage, lineage, and attribution.
- **Recovery loop:** Implemented via `RecoveryController` (`backend/src/backend/engine/recovery.py`) with strict ≤2 cycle budget, gap fingerprinting, and no-progress detection. Recovery selector supports deterministic `RuleBasedRecoverySelector` and optional `LayaRecoverySelector` (R1, `backend/src/backend/engine/laya_adapter.py`) selecting from closed `PERMITTED_ACTIONS` allow-list.
- **Release policy:** Implemented via `ReleasePolicy` (`backend/src/backend/engine/policy.py`) with unilateral veto authority. Mandatory checks `CHECK_OFFICIAL_WARNINGS`, `CHECK_MARINE_PROTECTED_AREAS`, `CHECK_VESSEL_LIMITS`, and `CHECK_EVIDENCE_ADEQUACY` are always evaluated.
- **Fallback/abstention behaviour:** When required location context is missing or mandatory safety inputs are unintegrated, endpoint returns truthful status, gaps, and `NOT_EVALUABLE` overall policy verdict. No fake clearances or mock advisories are ever generated.
- **Differences from `MASTER_BLUEPRINT.md`:** None.

## 4. Code execution — WHAT CALLS WHAT

Keep this as an accurate call-chain map. Add actual function names and file paths only after verifying them in source.

| Layer | Actual file / function | Input contract | Output contract | Side effects | Tests |
|---|---|---|---|---|---|
| HTTP API / health | `backend/src/backend/main.py:health_check` | None | `HealthResponse` | None | `tests/test_canonical_contracts.py:test_health_check_endpoint` |
| Canonical Query API | `backend/src/backend/main.py:canonical_orca_query` | `CanonicalQueryRequest` | `CanonicalQueryResponse` | Bounded raw JSON artifact saved & run recorded in SQLite | `tests/test_canonical_contracts.py`, `tests/test_open_meteo_gateways.py`, `tests/test_evidence_catalog.py`, `tests/test_fsm_dag_harness.py`, `tests/test_validator_recovery_policy.py`, `tests/test_laya_adapter.py` |
| Request/context validation | Pydantic validation via `CanonicalQueryRequest`, `QueryContext`, `GeoLocation` | Request JSON | Validated Pydantic Models | 422 on invalid schema | `tests/test_canonical_contracts.py:test_query_invalid_payload_validation_error` |
| Planner / task DAG | `backend/src/backend/engine/dag.py:TaskDAG` | `List[TaskContract]` | Topological waves / Execution plan | Rejects cycles, self-loops, duplicate IDs | `tests/test_fsm_dag_harness.py:TestTaskDAG` |
| Task harness / FSM | `backend/src/backend/engine/fsm.py:RunFSM` & `harness.py:ExecutionHarness` | Tasks & Gateways | `HarnessResult` & `List[TaskResult]` | Concurrency semaphore, deadlines, FSM transitions | `tests/test_fsm_dag_harness.py` |
| Source gateways | `backend/src/backend/gateways/open_meteo_*.py` | Coordinates | `EvidenceRecord` | Network GET (bounded timeout/retries) | `tests/test_open_meteo_gateways.py` |
| Evidence catalog/store | `backend/src/backend/catalog/artifact_store.py` & `service.py` | Run, Tasks, Artifacts, Evidence, Traces | Relative Path / Checksum / SQLite Rows | Local atomic JSON files / SQLite | `tests/test_evidence_catalog.py`, `tests/test_validator_recovery_policy.py`, `tests/test_laya_adapter.py` |
| Validator/critic | `backend/src/backend/engine/validator.py:EvidenceValidator` | `List[EvidenceRecord]`, context | `ValidationResult`, `List[IdentifiedGap]` | Verifies 7 check families, artifact checksums, physical ranges | `tests/test_validator_recovery_policy.py:TestEvidenceValidator` |
| Recovery controller (R3) | `backend/src/backend/engine/recovery.py:RecoveryController` | `List[IdentifiedGap]`, context | `RecoveryResult`, `List[RecoveryTraceEntry]` | Enforces ≤2 cycles, allow-list, no-progress detection | `tests/test_validator_recovery_policy.py:TestBoundedRecovery` |
| Laya decision adapter (R1) | `backend/src/backend/engine/laya_adapter.py:LayaRecoverySelector` | `IdentifiedGap`, history | `ValidatedAction`, `SelectorTraceEntry` | Pure lazy import, timeout fallback, allow-list validation, SQLite audit | `tests/test_laya_adapter.py` |
| Independent release policy | `backend/src/backend/engine/policy.py:ReleasePolicy` | Evidence, gaps, context | `PolicyAudit` (`PASS`/`BLOCK`/`NOT_EVALUABLE`) | Mandatory safety checks; unilateral veto authority | `tests/test_validator_recovery_policy.py:TestIndependentReleasePolicy`, `tests/test_laya_adapter.py:TestReleasePolicyIndependence` |
| Response projection/formatting | `backend/src/backend/main.py` | Context, Verdict, Evidence | `FieldCommunityProjection` / `ProfessionalAnalysisProjection` | None | `tests/test_canonical_contracts.py`, `tests/test_open_meteo_gateways.py`, `tests/test_fsm_dag_harness.py` |
## 5. Phase journal

### 2026-10-24 — Phase 0: Workspace Preservation and Safety Lockdown
- Goal and expected behaviour: Inspect workspace tree, Git state, legacy source code, routes, orchestrators, gateways, secret-handling, alert dispatch risks, and frontend failure fallbacks. Confirm safety gates without executing unsafe side effects or printing secrets.
- Files inspected:
  - `AGENTS.md`, `README.md`, `docs/MASTER_BLUEPRINT.md`, `docs/BUILD_PLAYBOOK.md`, `docs/DATA_AND_QUALITY.md`, `docs/ENGINEERING_LOGBOOK.md`, `docs/HACKATHON_GUIDE.md`
  - `legacy/Sagrvani Complete/backend/main.py`
  - `legacy/Sagrvani Complete/backend/services/alert_service.py`
  - `legacy/Sagrvani Complete/backend/test_api_endpoints.py`
  - `legacy/Sagrvani Complete/backend/test_all.py`
  - `legacy/Sagrvani Complete/backend/processors/weather_processor.py`
  - `legacy/Sagrvani Complete/backend/processors/marine_products.py`
  - `legacy/Sagrvani Complete/backend/gateway/marine_data_gateway.py`
  - `legacy/Sagrvani Complete/frontend/src/lib/api/orca.ts`
  - `legacy/Sagrvani Complete/frontend/src/components/dashboard/DashboardClient.tsx`
  - `legacy/Sagrvani Complete/Bhuvan  NRSC – LULC 2024–25/`
  - `legacy/Sagrvani Complete/IMD/`
  - `legacy/Sagrvani Complete/MOSDAC/`
- Files changed:
  - `.gitignore` (created at workspace root to protect `.env`, secrets, caches, node_modules, and run artifacts)
  - `.env.example` (created at workspace root with placeholder template and safety flags)
  - `docs/ENGINEERING_LOGBOOK.md` (updated with Phase 0 status and findings)
- Summary of code changes: Initialized clean root git tracking, added strict safety `.gitignore`, added safe `.env.example` template with `ENABLE_EXTERNAL_DISPATCH=false`, documented all legacy risks.
- Exact commands/tests run:
  - `git status` (workspace root: confirmed not a git repo initially)
  - `git status` (legacy folder: inspected main branch, uncommitted deletions of legacy 2016 coastal products noted)
  - `git init` (workspace root: initialized clean root repo)
  - `uv --version` (verified uv 0.12.15 is installed and available)
  - `git status` (workspace root: confirmed tracking and gitignore functioning)
- Results: passed
- External access attempted and status: Zero external calls attempted. No tests run against live Twilio or live endpoints.
- Side-effect safety confirmation: Confirmed no real messages dispatched. Confirmed no secrets printed or committed.
- Remaining issues: Downstream official data connections (IMD, INCOIS PFZ, Bhuvan MPA geometries) remain unverified / non-evaluable for future phases.
- Gate: `PASS`
- Next permitted action: Proceed to Phase 1.

### 2026-10-24 — Phase 1: Canonical API and Typed Contracts
- Goal and expected behaviour: Set up Python project in `backend/` using `uv`, define versioned Pydantic models for queries, evidence, tasks, recovery, policy audits, and projections. Implement `GET /health` and `POST /api/orca/query`. Test offline validation, error handling, and serialization.
- Files inspected:
  - `backend/pyproject.toml`
  - `docs/BUILD_PLAYBOOK.md`
  - `docs/DATA_AND_QUALITY.md`
  - `docs/MASTER_BLUEPRINT.md`
- Files created/changed:
  - `backend/pyproject.toml` (initialized with dependencies: `fastapi`, `pydantic`, `uvicorn`, `httpx`, `pytest`)
  - `backend/src/backend/core/config.py` (configuration & CORS settings)
  - `backend/src/backend/models/enums.py` (core enums: `PASS`, `BLOCK`, `NOT_EVALUABLE`, `COMPLETED`, `PARTIAL`, `SOURCE_UNAVAILABLE`, `CLARIFICATION_REQUIRED`, `HISTORICAL_REPLAY`, `TEST_FIXTURE`)
  - `backend/src/backend/models/evidence.py` (`GeoLocation`, `EvidenceRecord` with distinct temporal semantics)
  - `backend/src/backend/models/task.py` (`TaskContract`, `TaskResult`)
  - `backend/src/backend/models/recovery.py` (`IdentifiedGap`, `RecoveryTraceEntry` with bounded cycle count)
  - `backend/src/backend/models/query.py` (`CanonicalQueryRequest`, `CanonicalQueryResponse`, `PolicyAudit`, `FieldCommunityProjection`, `ProfessionalAnalysisProjection`)
  - `backend/src/backend/models/__init__.py` (re-exports)
  - `backend/src/backend/main.py` (`FastAPI` app with `GET /health` and `POST /api/orca/query`)
  - `backend/tests/test_canonical_contracts.py` (8 offline pytest unit & integration tests)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status, decision record, call-chain map, and journal)
- Summary of code changes: Implemented full domain contract system in Pydantic v2. Endpoint enforces that missing spatial location yields `CLARIFICATION_REQUIRED` and `NOT_EVALUABLE` without fabricating fake data or fake clearances.
- Exact commands/tests run:
  - `uv init --app backend`
  - `uv add fastapi pydantic uvicorn httpx pytest`
  - `uv run pytest` -> `8 passed, 1 warning in 2.70s`
- Results: passed
- External access attempted and status: None. All tests ran offline with `TestClient`.
- Side-effect safety confirmation: Proven. No external dispatch, no fake data generated, zero secrets exposed.
- Remaining issues: Live marine data gateways are scheduled for Phase 2.
- Gate: `PASS`
- Next permitted action: Proceed to Phase 2.

### 2026-10-24 — Phase 2: First Real Evidence Vertical Slice
- Goal and expected behaviour: Implement typed Open-Meteo marine and weather gateways with schema validation, bounded timeouts, small retries, array checks, and evidence normalization. Ensure default test suite makes zero network calls and opt-in live tests are gated.
- Files inspected:
  - `docs/BUILD_PLAYBOOK.md` Phase 2
  - `docs/DATA_AND_QUALITY.md` Section 3
  - `backend/src/backend/main.py`
  - `backend/src/backend/core/config.py`
- Files created/changed:
  - `backend/src/backend/core/config.py` (added Open-Meteo base URLs and timeout settings)
  - `backend/src/backend/gateways/exceptions.py` (`GatewayError`, `GatewayTimeoutError`, `GatewayNetworkError`, `GatewayHTTPStatusError`, `GatewaySchemaValidationError`)
  - `backend/src/backend/gateways/open_meteo_marine.py` (`OpenMeteoMarineGateway`: wave height, direction, period)
  - `backend/src/backend/gateways/open_meteo_weather.py` (`OpenMeteoWeatherGateway`: wind speed, direction, gusts at 10m)
  - `backend/src/backend/gateways/__init__.py` (re-exports)
  - `backend/tests/fixtures/open_meteo_marine_sample.json` (deterministic offline marine fixture)
  - `backend/tests/fixtures/open_meteo_weather_sample.json` (deterministic offline weather fixture)
  - `backend/src/backend/main.py` (integrated gateways into `POST /api/orca/query` with truthful partial/unavailable handling and NOT_EVALUABLE release audit)
  - `backend/tests/test_open_meteo_gateways.py` (10 tests covering parsing, validation, timeouts, retries, 4xx errors, canonical endpoint integration, and opt-in live test)
  - `backend/tests/test_canonical_contracts.py` (updated to mock gateway failure mode)
  - `docs/DATA_AND_QUALITY.md` (updated Open-Meteo status to CONNECTED/TESTED with CC BY 4.0 terms)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status, DEC-20261024-03, and journal)
- Summary of code changes: Delivered complete first vertical slice. Open-Meteo responses are strictly normalized into `EvidenceRecord` without inventing missing observations or issue times. Release gate strictly evaluates as `NOT_EVALUABLE` since unapproved vessel thresholds and missing MPA shapefiles cannot authorize release.
- Exact commands/tests run:
  - `uv run pytest` -> `17 passed, 1 skipped in 0.95s` (all offline tests pass; zero network calls in default suite)
  - `uv run python -c "import os; os.environ['RUN_LIVE_SOURCE_TESTS']='1'; import pytest; sys_exit = pytest.main(['-v', '-k', 'test_live_open_meteo_gateways', 'tests/test_open_meteo_gateways.py']); exit(sys_exit)"` -> `1 passed in 2.74s` (live read-only Open-Meteo query confirmed for Malpe coordinates)
- Results: passed
- External access attempted and status: Live Open-Meteo GET request executed strictly during the opt-in live test (`RUN_LIVE_SOURCE_TESTS=1`). Response validated successfully.
- Side-effect safety confirmation: Proven. Read-only GET requests only. No alerts dispatched, no secrets exposed.
- Remaining issues: Run-specific artifact persistence and SQLite evidence catalog metadata scheduled for Phase 3.
- Gate: `PASS`
- Next permitted action: Proceed to Phase 3.

### 2026-10-24 — Phase 3: Evidence Catalog, Files and Trace
- Goal and expected behaviour: Implement path-safe, bounded, atomic ArtifactStore under `artifacts/runs/<run_id>/<task_id>.json`. Implement versioned, repeatable SQLite migrations and CatalogService for runs, tasks, artifacts, and evidence. Register historical NetCDF/SAR files with explicit `HISTORICAL_REPLAY` flags and checksums.
- Files inspected:
  - `legacy/Sagrvani Complete/MOSDAC/Global Ocean Surface Current/`
  - `legacy/Sagrvani Complete/MOSDAC/Indian Mainland Coastal Product/`
  - `backend/tests/fixtures/`
  - `docs/DATA_AND_QUALITY.md`
- Files created/changed:
  - `backend/src/backend/core/config.py` (added `artifacts_dir`, `sqlite_db_path`, `max_artifact_bytes` caps)
  - `.gitignore` (safeguarded `artifacts/`, `*.db`, `*.sqlite`, `*.sqlite3`)
  - `backend/src/backend/catalog/artifact_store.py` (`ArtifactStore`: atomic writes, regex path validation, max size checks, SHA-256 computation)
  - `backend/src/backend/catalog/migrations.py` (versioned SQLite schema migrations)
  - `backend/src/backend/catalog/service.py` (`CatalogService`: run, task, artifact, and evidence persistence)
  - `backend/src/backend/catalog/dataset_registry.py` (`catalog_known_datasets`: registers historical MOSDAC NetCDF as `HISTORICAL_REPLAY` and test fixtures as `TEST_FIXTURE`)
  - `backend/src/backend/catalog/__init__.py` (re-exports)
  - `backend/src/backend/main.py` (integrated raw artifact saving and metadata recording into `POST /api/orca/query`)
  - `backend/tests/test_evidence_catalog.py` (7 tests covering atomic writes, path safety, byte limits, migration idempotence, SQLite queries, and historical replay labeling)
  - `docs/DATA_AND_QUALITY.md` (updated dataset inventory table with Phase 3 status and checksums)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status, DEC-20261024-04, and journal)
- Summary of code changes: Implemented run-scoped artifact storage and metadata persistence. Every evidence record generated links to an on-disk JSON artifact with a verifiable SHA-256 hash. Legacy MOSDAC files are registered as `HISTORICAL_REPLAY` with empty-attribute warnings, preventing them from masquerading as live.
- Exact commands/tests run:
  - `uv run pytest -v` -> `24 passed, 1 skipped in 3.94s` (all offline tests pass)
- Results: passed
- External access attempted and status: Zero network calls. Offline fixtures used.
- Side-effect safety confirmation: Proven. No external dispatch, no secrets exposed, databases and artifact directories kept out of git.
- Remaining issues: Guarded FSM, task DAG, and execution harness scheduled for Phase 4.
- Gate: `PASS`
- Next permitted action: Proceed to Phase 4.

### 2026-10-24 — Phase 4: Guarded FSM, Harness and Task DAG (R2)
- Goal and expected behaviour: Implement typed task harness (R2), guarded deterministic FSM with explicit allow-list transitions, terminal state enforcement, and deadline guards. Implement dependency-aware Task DAG rejecting cycles, self-loops, and duplicate IDs while calculating topological execution waves. Implement ExecutionHarness executing independent tasks concurrently under bounded concurrency and timeouts while skipping tasks whose prerequisites fail. Integrate into canonical `POST /api/orca/query` and persist FSM transitions in SQLite.
- Files inspected:
  - `docs/BUILD_PLAYBOOK.md` Phase 4
  - `docs/MASTER_BLUEPRINT.md` Sections 3.2, 4.2
  - `backend/src/backend/main.py`
  - `backend/src/backend/core/config.py`
  - `backend/src/backend/catalog/migrations.py`
  - `backend/src/backend/catalog/service.py`
- Files created/changed:
  - `backend/src/backend/core/config.py` (added `run_deadline_seconds`, `max_task_concurrency`)
  - `backend/src/backend/engine/fsm.py` (`RunFSM`, `FSMState`, `ALLOWED_TRANSITIONS`, `TERMINAL_STATES`, `FSMTransitionEvent`, `IllegalTransitionError`, `TerminalStateError`, `DeadlineExceededError`)
  - `backend/src/backend/engine/dag.py` (`TaskDAG`, `TaskDAGError`, `DuplicateTaskIdError`, `CyclicDependencyError`, `SelfLoopError`, `UnknownDependencyError`, topological wave calculation)
  - `backend/src/backend/engine/harness.py` (`ExecutionHarness`, `HarnessResult`, `GatewayCallable`, bounded concurrency, timeout enforcement, dependency skipping)
  - `backend/src/backend/engine/__init__.py` (re-exports)
  - `backend/src/backend/catalog/migrations.py` (added Migration 2: `fsm_transitions` table with indexes)
  - `backend/src/backend/catalog/service.py` (`record_fsm_transitions`, `get_fsm_transitions`, run stub insertion for FK integrity)
  - `backend/src/backend/main.py` (wired FSM, DAG validation, and concurrent harness into `POST /api/orca/query` via `Depends(get_gateway_registry)`)
  - `backend/pyproject.toml` (configured `pythonpath = ["src"]`)
  - `backend/tests/test_fsm_dag_harness.py` (51 offline tests covering transitions, terminal states, deadlines, DAG cycle/loop detection, concurrency, prerequisite skipping, timeouts, endpoint integration, and regressions)
  - `backend/tests/test_evidence_catalog.py` (dynamically checked migration count against `MIGRATIONS`)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status, DEC-20261024-05, and journal)
- Summary of code changes: Delivered complete Phase 4 R2 task harness. All independent retrievals execute concurrently up to concurrency limits; prerequisites are strictly respected; cycles or invalid DAGs are rejected deterministically before task dispatch; FSM lifecycle transitions are auditable and persisted in SQLite.
- Exact commands/tests run:
  - `.venv\Scripts\python.exe -m pytest tests/test_fsm_dag_harness.py -v` -> `51 passed in 0.90s`
  - `.venv\Scripts\python.exe -m pytest -v` -> `75 passed, 1 skipped in 2.45s` (all offline tests pass)
- Results: passed
- External access attempted and status: Zero network calls. Fake and mocked gateways used for all offline tests.
- Side-effect safety confirmation: Proven. No real alert dispatch, no secrets exposed, no unapproved external calls.
- Remaining issues: Phase 5 evidence validation, closed recovery actions (R3), and release gate policy.
- Gate: `PASS`
- Next permitted action: Stop at Phase 4 gate and request user authorization to proceed to Phase 5 (Validator, bounded recovery (R3) and release policy).

### 2026-10-24 — Phase 5: Deterministic Evidence Validator, Bounded Recovery (R3), Independent Release Policy
- Goal and expected behaviour: Implement deterministic EvidenceValidator across 7 check families (structure, physical ranges, units, temporal relevance/freshness, spatial coverage, lineage, attribution). Implement bounded RecoveryController (R3) with strict ≤2-cycle budget, gap fingerprinting, allow-listed actions (`PERMITTED_ACTIONS`), and no-progress detection. Implement independent ReleasePolicy with unilateral veto authority and mandatory safety checks returning `NOT_EVALUABLE` until authoritative data sources are integrated.
- Files inspected:
  - `docs/BUILD_PLAYBOOK.md` Phase 5
  - `docs/MASTER_BLUEPRINT.md` Sections 3.3, 4.4
  - `docs/DATA_AND_QUALITY.md` Sections 2–5
  - `backend/src/backend/engine/`
  - `backend/src/backend/catalog/`
- Files created/changed:
  - `backend/src/backend/engine/validator.py` (`EvidenceValidator`, `ValidationCheckItem`, `ValidationResult`, physical ranges, unit parsing, temporal window checks, artifact checksum verification)
  - `backend/src/backend/engine/recovery.py` (`RecoveryController`, `RuleBasedRecoverySelector`, `compute_gap_fingerprint`, allow-list enforcement, no-progress termination)
  - `backend/src/backend/engine/policy.py` (`ReleasePolicy`, mandatory safety checks `CHECK_OFFICIAL_WARNINGS`, `CHECK_MARINE_PROTECTED_AREAS`, `CHECK_VESSEL_LIMITS`, `CHECK_EVIDENCE_ADEQUACY`, unilateral veto)
  - `backend/src/backend/catalog/migrations.py` (added Migration 3: `policy_checks` and `recovery_traces` tables and indexes)
  - `backend/src/backend/catalog/service.py` (`record_policy_checks`, `get_policy_checks`, `record_recovery_trace`, `get_recovery_trace`)
  - `backend/src/backend/main.py` (integrated validator, recovery controller, and release policy into `POST /api/orca/query`)
  - `backend/pyproject.toml` (added `pytest-asyncio`, configured `asyncio_mode = "auto"`)
  - `backend/tests/test_validator_recovery_policy.py` (29 comprehensive tests)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status and DEC-20261024-06)
- Summary of code changes: Implemented full deterministic validation pipeline, bounded recovery loop, and safety release gate. Missing official warning feeds, protected area shapefiles, and unapproved vessel thresholds strictly produce `NOT_EVALUABLE` safety verdicts.
- Exact commands/tests run:
  - `uv run pytest tests/test_validator_recovery_policy.py -v` -> `29 passed in 0.98s`
  - `uv run pytest -v` -> `104 passed, 1 skipped in 3.34s` (all offline tests pass)
- Results: passed
- External access attempted and status: Zero network calls. Offline fixtures used.
- Side-effect safety confirmation: Proven. No real alert dispatch, no secrets exposed, release policy enforces veto.
- Remaining issues: Phase 6 Laya decision adapter (R1).
- Gate: `PASS`
- Next permitted action: Proceed to Phase 6.

### 2026-10-24 — Phase 6: Laya Decision Adapter (R1)
- Goal and expected behaviour: Implement optional Laya decision adapter (`LayaRecoverySelector`) as R1 decision selector. Ensure pure lazy importing of dependencies so system runs fully offline without PyTorch/transformers. Strictly restrict model outputs to the closed `PERMITTED_ACTIONS` allow-list via typed choice question schemas. Enforce fallback to `RuleBasedRecoverySelector` on timeout (3.0s), missing package, or unapproved choice. Log structured `SelectorTraceEntry` in SQLite. Benchmark rules vs Laya across 10 comparative cases. Verify release gate independence.
- Files inspected:
  - `docs/BUILD_PLAYBOOK.md` Phase 6
  - `docs/DATA_AND_QUALITY.md` Sections 1, 8
  - Hugging Face model cards for `convaiinnovations/laya`
  - `backend/src/backend/engine/recovery.py`
  - `backend/src/backend/catalog/migrations.py`
- Files created/changed:
  - `backend/src/backend/core/config.py` (added `enable_laya_selector`, `laya_model_checkpoint`, `laya_timeout_seconds`)
  - `backend/src/backend/models/recovery.py` (`SelectorTraceEntry` schema with all audit fields; added `selector_trace` to `RecoveryTraceEntry`)
  - `backend/src/backend/models/__init__.py` (re-exports)
  - `backend/src/backend/engine/laya_adapter.py` (`LayaRecoverySelector`: lazy loading, threadpool timeout, typed question prompt, allow-list validation, rule fallback, selector trace creation)
  - `backend/src/backend/engine/recovery.py` (enhanced `RuleBasedRecoverySelector` with trace logging; updated `RecoveryController` to use `LayaRecoverySelector` when enabled)
  - `backend/src/backend/engine/__init__.py` (re-exports)
  - `backend/src/backend/catalog/migrations.py` (added Migration 4: `selector_traces` table and `idx_selector_run` index)
  - `backend/src/backend/catalog/service.py` (`record_selector_traces`, `get_selector_traces`, updated `record_run`)
  - `backend/tests/test_laya_adapter.py` (30 tests: baseline rules, feature gating, missing dependency fallback, timeout fallback, allow-list enforcement, 10-case comparative benchmark, controller cycle/no-progress limits, release gate independence, SQLite CRUD, endpoint integration, opt-in live test)
  - `docs/DATA_AND_QUALITY.md` (updated Section 1 and Section 8 with verified Laya checkpoint and Apache 2.0 provenance)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status, DEC-20261024-07, Section 3, Section 4, Section 5, and Risk Register O-06)
- Summary of code changes: Implemented complete Laya Decision Adapter (R1). The system defaults to deterministic rules with zero runtime overhead when `ENABLE_LAYA_SELECTOR=false`. When enabled, Laya decisions are strictly bounded to the allow-list and fail-closed to rules. Under no circumstances can Laya override the release policy or convert missing safety evidence into approval.
- Exact commands/tests run:
  - `uv run pytest tests/test_laya_adapter.py -v` -> `29 passed, 1 skipped in 2.65s`
  - `uv run pytest -v` -> `133 passed, 2 skipped in 10.92s` (100% offline, zero network calls, zero failures)
- Results: passed
- External access attempted and status: Zero network calls in default suite. Real model inference gated behind `RUN_LIVE_LAYA_TESTS=1`.
- Side-effect safety confirmation: Proven. No real alert dispatch, no secrets exposed, release policy maintains veto authority.
- Remaining issues: Phase 7 End-to-End Verification and Demo Acceptance.
- Gate: `PASS`
- Next permitted action: Proceed to Phase 7.

### 2026-10-24 — Phase 7: Verification and Demo Acceptance
- Goal and expected behaviour: Verify complete request-to-response path across 10 operational scenarios. Ensure run IDs, trace IDs, task IDs, evidence IDs, artifacts, SHA-256 hashes, FSM transitions, recovery traces, selector traces, and policy checks link consistently. Exercise error handling, partial-data handling, timeout resilience, bounded recovery, and release veto authority. Fix verified blockers (specifically SQLite cascade deletion bug in `record_run`). Confirm offline isolation (zero external HTTP calls) and accurately document Laya runtime status. Produce verified demo acceptance matrix with commands.
- Files inspected:
  - `docs/BUILD_PLAYBOOK.md` Phase 7
  - `backend/src/backend/catalog/service.py`
  - `backend/src/backend/engine/validator.py`
  - `backend/src/backend/engine/recovery.py`
  - `backend/src/backend/engine/policy.py`
  - `backend/tests/test_laya_adapter.py`
- Files created/changed:
  - `backend/src/backend/catalog/service.py` (fixed `record_run`: migrated from `INSERT OR REPLACE INTO runs` to `INSERT INTO runs (...) ON CONFLICT(run_id) DO UPDATE SET ...` to prevent cascading deletion of `fsm_transitions` when run stubs exist)
  - `backend/tests/test_phase7_verification.py` (created 27 comprehensive tests exercising all 10 mandatory operational scenarios)
  - `docs/ENGINEERING_LOGBOOK.md` (updated status, DEC-20261024-08, Phase 7 journal, demo acceptance matrix, risk register, exact run commands)
  - `docs/HACKATHON_GUIDE.md` (updated demo scenarios, startup/test commands, and limitations)
- Bugs fixed and regression evidence:
  - *Bug:* In SQLite with foreign keys enabled, `INSERT OR REPLACE INTO runs` executes a delete followed by an insert. Because child tables (`fsm_transitions`, `recovery_trace`, `policy_checks`) have `FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE`, final run persistence was inadvertently wiping out earlier FSM transitions recorded during the run.
  - *Fix:* Upgraded `CatalogService.record_run` to use `INSERT INTO runs (...) ON CONFLICT(run_id) DO UPDATE SET ...`. Verified by `test_full_successful_request_to_response_pipeline`, which now confirms all 6 state transitions (`CONTEXT_VALIDATED`, `TASK_GRAPH_READY`, `EVIDENCE_ACQUISITION`, `EVIDENCE_VALIDATION`, `SAFETY_GATE_CHECK`, `ABSTAINED`) are preserved in SQLite.
- Laya Verification Facts:
  - Adapter Implementation: `IMPLEMENTED` & `VERIFIED` (`LayaRecoverySelector` with lazy loading, allow-list validation, timeout fallback, SQLite audit).
  - Comparative Benchmark: Evaluated offline across 10 labeled test cases using injected deterministic `StubRouter` responses to verify schema compliance and allow-list validation.
  - Real Model Checkpoint Inference: `NOT VERIFIED` in local development environment. The checkpoint `convaiinnovations/laya` (ModernBERT-large backbone, 421M parameters, ~1.5GB weights) and `laya`/`torch` runtime packages are not installed in `.venv`. The opt-in test `test_live_laya_inference_smoke` is safely skipped. Fallback path to rules is 100% verified. Default selector remains deterministic rules.
- Exact commands/tests run:
  - `uv run pytest tests/test_phase7_verification.py -v` -> `27 passed, 1 warning in 1.16s`
  - `uv run pytest -v` -> `160 passed, 2 skipped, 1 warning in 6.96s` (100% offline, zero network calls, zero failures)
- Results: passed
- External access attempted and status: Zero network calls in default suite. Only offline mocks/fixtures used.
- Remaining issues: Phase 8 Frontend integration (pending user approval and design document delivery).
- Gate: `PASS`
- Next permitted action: Implement backend demo runner per user instruction.

### 2026-10-24 — Phase 7.5: Deterministic Backend Demo Runner
- Goal and expected behaviour: Build a standalone deterministic demo runner (`backend/scripts/demo_runner.py`) enabling live demonstration of the canonical FastAPI backend (`POST /api/orca/query`), guarded FSM, task harness, evidence validator, bounded recovery controller, and release veto policy in a 100% offline, isolated environment. Phase 8 Frontend integration is paused pending user delivery of updated frontend design documents.
- Files inspected:
  - `backend/src/backend/main.py` (canonical route `POST /api/orca/query` and `get_gateway_registry`)
  - `backend/src/backend/engine/policy.py` (veto hierarchy: BLOCK > NOT_EVALUABLE > PASS)
  - `backend/src/backend/catalog/service.py` (SQLite catalog)
  - `backend/tests/test_phase7_verification.py` (offline mock gateways and recovery fixtures)
- Files created/changed:
  - `backend/scripts/__init__.py` (package marker)
  - `backend/scripts/demo_runner.py` (deterministic CLI demo runner exercising Scenario 1: Nominal Acquisition & Policy Veto, Scenario 2: Source Failure & Truthful Partial State, and Scenario 3: Bounded Recovery & No-Progress Abstention in an isolated temporary environment)
  - `backend/tests/test_demo_runner.py` (4 unit tests verifying demo runner scenarios and execution)
  - `backend/pyproject.toml` (updated pytest `pythonpath` to `["src", "."]`)
  - `docs/ENGINEERING_LOGBOOK.md` (DEC-20261024-09, updated status, test metrics, and journal)
  - `docs/HACKATHON_GUIDE.md` (demo script commands, scenario descriptions, backend vs frontend demarcation)
- Key Behaviors Demonstrated:
  - *Scenario 1 (Nominal Evidence Acquisition):* Marine and weather mocked gateways succeed. 6 forecast parameters retrieved with Open-Meteo attribution. SHA-256 artifacts saved and linked. Release policy evaluates `CHECK_OFFICIAL_WARNINGS`, `CHECK_MARINE_PROTECTED_AREAS`, and `CHECK_VESSEL_LIMITS` as `NOT_EVALUABLE`. Final verdict: `NOT_EVALUABLE` (clearance strictly withheld). FSM transitions cleanly to `ABSTAINED`.
  - *Scenario 2 (Source Failure & Truthful Reporting):* Marine gateway fails. Weather succeeds. Status returns `PARTIAL` with 3 atmospheric parameters and `GAP_MARINE_SOURCE_ERROR`. No synthetic fallback is generated. Release policy evaluates `CHECK_EVIDENCE_ADEQUACY` as `BLOCK`. Final verdict: `BLOCK`.
  - *Scenario 3 (Bounded Recovery & Abstention):* (a) Missing wind speed is recovered via `retry_with_backoff` action, yielding 6 verified evidence items and `SUCCEEDED` outcome; (b) Irrecoverable data corruption selects `abstain_and_log`, terminates on cycle 1 (strictly within budget of 2), and yields `EXHAUSTED` outcome.
- Exact commands/tests run:
  - `uv run python -m scripts.demo_runner` -> Exit code 0 (All 3 scenarios passed congruently)
  - `uv run pytest tests/test_demo_runner.py -v` -> `4 passed, 1 warning in 1.48s`
  - `uv run pytest -v` -> `164 passed, 2 skipped, 1 warning in 13.22s` (100% offline, zero network calls, zero failures)
- Results: passed
- External access attempted and status: Zero network calls. Isolated temporary database and artifacts used.
- Side-effect safety confirmation: Proven. No real alerts dispatched, no secrets exposed, departure clearance strictly withheld.
- Remaining issues: Phase 8 Frontend integration (pending user design documents and explicit approval).
- Gate: `PASS`
- Next permitted action: Await user authorization and design assets for Phase 8.

### Phase 7 Operational Scenario Verification Matrix

| # | Scenario | Component(s) Exercised | Expected Outcome | Actual Outcome & Test Reference | Status |
|---|---|---|---|---|---|
| 1 | Missing or invalid location | Request validator, FSM, Policy | Clarification required; never guess location | Status `CLARIFICATION_REQUIRED`, `GAP_MISSING_LOCATION`, policy `NOT_EVALUABLE`, FSM `ABSTAINED`. Lat > 90 produces 422. (`TestScenario1_LocationValidation`) | `CONFIRMED` |
| 2 | Both gateways succeed (Happy Path) | FSM, DAG, Harness, Gateways, Catalog, Validator, Policy | 6 forecast variables retrieved; linked to artifacts; auditable trace | Status `COMPLETED`, 6 evidence items, SHA-256 artifacts verified on disk, SQLite run and FSM transitions persisted. Policy `NOT_EVALUABLE`. (`TestScenario2_HappyPathBothGateways`) | `CONFIRMED` |
| 3 | Gateway failures (marine, weather, both) | Harness, Gateway error handling, FSM | Partial evidence or source unavailable; no fake success | Marine fail -> `PARTIAL` (3 items, `GAP_MARINE_SOURCE_ERROR`). Weather fail -> `PARTIAL` (3 items, `GAP_WEATHER_SOURCE_ERROR`). Both fail -> `SOURCE_UNAVAILABLE` (0 items). (`TestScenario3_SourceFailures`) | `CONFIRMED` |
| 4 | Malformed data & physical range limits | EvidenceValidator, physical range checks | Out-of-bounds readings flagged as critical | Wave height 55m -> `GAP_UNPHYSICAL_VALUE` (critical fail). Wind speed 800 km/h -> `GAP_UNPHYSICAL_VALUE`. Unrecognized units -> `GAP_UNKNOWN_UNIT`. (`TestScenario4_MalformedPayloadsAndValidation`) | `CONFIRMED` |
| 5 | Temporal freshness & lineage | EvidenceValidator, freshness & lineage rules | Stale forecasts and distant windows flagged; lineage tracked | Retrieval age >48h -> `GAP_STALE_EVIDENCE`. Horizon >7d -> `GAP_TEMPORAL_WINDOW_MISMATCH`. Lineage correctly audit-logged as ECMWF/DWD. (`TestScenario5_TemporalFreshnessLineage`) | `CONFIRMED` |
| 6 | Bounded recovery behaviors | RecoveryController (R3), allow-list, budget | Bounded to ≤2 cycles, no-progress termination, targeted recovery | Max 2 cycles strictly enforced. No-progress terminates on cycle 1 with `ABSTAIN_AND_LOG`. Targeted retry successfully clears gap. (`TestScenario6_BoundedRecoveryBehaviors`) | `CONFIRMED` |
| 7 | DAG & harness resilience | TaskDAG, ExecutionHarness | Detect invalid DAGs; skip failed prerequisites | Rejects cycles (`CyclicDependencyError`), self-loops, duplicate IDs (`DuplicateTaskIDError`). Child tasks skip on prerequisite failure. (`TestScenario7_DAGAndHarnessResilience`) | `CONFIRMED` |
| 8 | Storage & database failure safety | ArtifactStore, CatalogService | Storage errors do not crash HTTP response; corrupt artifacts caught | Corrupt/missing artifact flags `GAP_MISSING_ARTIFACT`. SQLite database lock/error does not crash API (returns 200 with completed run). (`TestScenario8_StorageAndCatalogFailureSafety`) | `CONFIRMED` |
| 9 | Laya selector gating & fallbacks | LayaRecoverySelector (R1), Rule fallback | Disabled by default; safe rule fallback on missing package/timeout/bad output | `ENABLE_LAYA_SELECTOR=False` uses rules. Missing `laya` package falls back. Unapproved action fails-closed to rules. Timeout (0.03s) falls back. (`TestScenario9_LayaGatingAndFallbackResilience`) | `CONFIRMED` |
| 10 | Independent release policy & veto | ReleasePolicy, FSM safety gate | Mandatory unintegrated checks cannot pass; FSM cannot transition to RELEASED | `CHECK_OFFICIAL_WARNINGS`, `CHECK_MARINE_PROTECTED_AREAS`, and `CHECK_VESSEL_LIMITS` strictly return `NOT_EVALUABLE`. `can_release` returns `False`. FSM cannot enter `RELEASED`. (`TestScenario10_ReleasePolicyIndependenceAndVeto`) | `CONFIRMED` |

### Demo Acceptance Matrix & Presentation Guide

| Scenario | Setup & Command | Data Source Mode | Expected Behavior | Actual Behavior & Test Evidence | Safe to Demo? | Visible Disclaimer |
|---|---|---|---|---|---|---|
| **Demo 1: Happy Path Marine Advisory (Primary)** | `POST /api/orca/query` with Malpe coordinates `{"location": {"lat": 13.35, "lon": 74.70}}` | `LIVE_FORECAST` (Open-Meteo) or offline fixtures | Retrieves 6 atmospheric & wave forecast parameters; validator checks ranges; policy audits gates; status `COMPLETED`. | 6 parameters returned with verified on-disk SHA-256 artifacts. `CHECK_OFFICIAL_WARNINGS`, `CHECK_MARINE_PROTECTED_AREAS`, and `CHECK_VESSEL_LIMITS` evaluate as `NOT_EVALUABLE`. Overall safety verdict: `NOT_EVALUABLE`. FSM transitions to `ABSTAINED`. | **YES** (Recommended) | **PROTOTYPE ONLY**: Official IMD/INCOIS bulletins and protected-area geometries not integrated. Operational departure clearance strictly withheld. |
| **Demo 2: Controlled Failure & Bounded Recovery (Secondary)** | `POST /api/orca/query` with transient weather gateway error | `TEST_FIXTURE` / mocked gateway | Gateway failure detected; `GAP_WEATHER_SOURCE_ERROR` flagged; recovery controller retries with backoff; revalidates. | Cycle 1 attempts `retry_with_backoff`. When recovered, evidence is merged and status is `COMPLETED`. If permanent, terminates at ≤2 cycles and abstains. Trace saved in SQLite. | **YES** (Recommended) | **RECOVERY DEMO**: Exercises bounded decision-aware recovery (R3) without external side effects or infinite loops. |
| **Demo 3: Missing Location Clarification** | `POST /api/orca/query` with query text only (no location) | None (`NOT_AVAILABLE`) | System detects missing location context; never hallucinates or guesses coordinates. | Returns status `CLARIFICATION_REQUIRED`, flags `GAP_MISSING_LOCATION`, policy verdict `NOT_EVALUABLE`, FSM transitions to `ABSTAINED`. | **YES** | **TRUTHFUL ABSTENTION**: System withholds analysis when spatial coordinates are absent. |
| **Demo 4: Physical Sanity Violation Rejection** | Query returning wave height 55m | `TEST_FIXTURE` | Validator flags physical range violation; halts release. | Validator fails `CHECK_PHYSICAL_RANGE` (`CRITICAL`), raises `GAP_UNPHYSICAL_VALUE`, policy blocks release. | **YES** | **SAFETY GUARD**: Bounded physical sanity filters reject sensor corruption or unphysical inputs. |

### Exact Commands to Start and Test the Backend

1. **Run full default offline test suite (160 tests):**
   ```powershell
   cd "backend"
   uv run pytest -v
   ```
2. **Run Phase 7 verification suite only (27 tests):**
   ```powershell
   cd "backend"
   uv run pytest tests/test_phase7_verification.py -v
   ```
3. **Run opt-in live Open-Meteo network test:**
   ```powershell
   cd "backend"
   $env:RUN_LIVE_SOURCE_TESTS="1"; uv run pytest -v -k test_live_open_meteo_gateways tests/test_open_meteo_gateways.py; Remove-Item Env:\RUN_LIVE_SOURCE_TESTS
   ```
4. **Start the FastAPI backend server:**
   ```powershell
   cd "backend"
   uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   API Documentation available at: `http://127.0.0.1:8000/docs`

## 6. Open issues and risk register

| ID | Issue | Severity | Owner | Evidence needed | Status / next step |
|---|---|---|---|---|---|
| O-01 | Reconfirm the legacy audit findings against current source | High | Antigravity | Paths, line references, safe tests | VERIFIED in Phase 0 |
| O-02 | Official IMD API access requirements | Medium | Team | Current documentation/access confirmation | Open / Planned for Phase 2+ |
| O-03 | Reliable machine-readable current PFZ advisory | High for PFZ feature | Team | Successful sample + validity/provenance fields | Open / Static candidates expired |
| O-04 | Verified protected-area geometries | High for geofence feature | Team | Source, licence, CRS, geometry tests | Open / Bhuvan folder only has PDFs |
| O-05 | Expert review of any marine limits/policy | Blocking for operational safety claims | Domain expert | Written/traceable review | Open / Prototype disclaimer strictly enforced |
| O-06 | Laya checkpoint and adapter runtime test | Experiment | Antigravity | Selected checkpoint, dependency/licence review, offline comparison | VERIFIED in Phase 6 & 7 / Adapter verified offline; real model inference NOT VERIFIED (weights not installed in environment) |

## 7. Documentation truth labels

Use these labels consistently:

- `PLANNED` — designed but not implemented.
- `IMPLEMENTED` — code exists; tests may still be missing.
- `TESTED` — specific tests ran; include commands/results.
- `VERIFIED` — behaviour independently checked against stated acceptance criteria.
- `CONNECTED` — source adapter exists and a connection was confirmed at a timestamp.
- `BLOCKED` — dependency/issue prevents completion.
- `NOT_EVALUABLE` — required evidence/configuration does not exist, so a check cannot be truthfully completed.


## 8. Phase 8.1 — Supabase Authentication & Real End-to-End Integration

### Date: 2026-10-25
### Status: VERIFIED & TESTED

#### Changes Implemented:
1. **Backend Auth Verification:**
   - Implemented `backend/src/backend/core/auth.py` with RS256 JWKS verification (`PyJWKClient`) against Supabase Auth endpoints.
   - Verified token claims (`sub`, `email`, `role`, `user_metadata`).
   - Integrated `get_current_user` and `get_optional_user` into `backend/src/backend/main.py`. Added `/api/auth/me` inspection route.
   - Added auth configuration in `backend/src/backend/core/config.py` (`supabase_url`, `supabase_jwks_url`, `require_query_auth`).
   - Added 6 unit/integration tests in `backend/tests/test_supabase_auth.py`.
   - Results: `174 passed, 2 skipped` full suite; `6/6 passed` auth tests.

2. **Frontend Supabase Auth & Context:**
   - Created `frontend/src/lib/supabase.ts` singleton client.
   - Implemented `frontend/src/context/AuthContext.tsx` providing `user`, `session`, `accessToken`, `userRole`, `signIn`, `signUp`, `signOut`.
   - Wrapped Next.js application in `AuthProvider` (`frontend/src/app/layout.tsx`).
   - Upgraded `frontend/src/app/login/page.tsx` from presentation-only to fully functional Supabase authentication (Sign In & Sign Up with email verification notice and stakeholder role metadata).
   - Upgraded `frontend/src/app/dashboard/page.tsx` with live operator authentication badge, sign out action, and authenticated query dispatch passing `Authorization: Bearer <token>`.
   - Fixed `.gitignore` to prevent improper ignoring of `frontend/src/lib/`.
   - Zero lint warnings (`npm run lint`), successful production build (`npm run build`).

3. **Database & Migrations:**
   - Created PostgreSQL migration `supabase/migrations/20261025000000_sagarvani_auth_rls.sql` providing `user_profiles` and `user_queries` tables with Row Level Security (RLS) policies and automatic profile creation trigger on signup.
   - Created root `.env.example` documenting all configuration keys safely without leaking secrets.

4. **Testing & Build Commands Executed:**
   - `uv run pytest --tb=short -q` -> 174 passed, 2 skipped, 0 failures.
   - `uv run pytest tests/test_supabase_auth.py -v` -> 6/6 passed.
   - `cd frontend && npm run lint` -> 0 errors, 0 warnings.
   - `cd frontend && npm run build` -> Compiled successfully, static pages generated.

