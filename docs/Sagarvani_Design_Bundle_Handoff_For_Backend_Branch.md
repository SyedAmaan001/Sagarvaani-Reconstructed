# Sagarvani — Design Bundle Interpretation & Handoff for the Backend/Implementation Branch

**Purpose:** Give the other ChatGPT/Antigravity branch the context needed to correctly use `Sagarvani-Design Reconstruction.zip` alongside its existing backend, repository context and implementation prompt.

**This is a supplementary design handoff, not a replacement for the active prompt in the other branch.** Keep that branch’s current requirements, safety constraints, build phases and backend decisions. Incorporate this document as the design-source interpretation layer.

---

## 1. What the ZIP actually contains

The archive `Sagarvani-Design Reconstruction.zip` is not just a folder of images. It combines five different kinds of material, and they must not be confused:

| Archive path | What it is | How the implementation branch should use it |
|---|---|---|
| `Sagarvani-Design Reconstruction/Intial design language for iteration/` | The three preferred original design boards | Treat these as the current layout and information-architecture baseline. Preserve their coverage and hierarchy while improving accessibility. The folder name really is spelled `Intial`; do not assume it is a typo when resolving the path. |
| `Sagarvani-Design Reconstruction/DESIGN GENERATED/` | 46 original user-generated illustrations | These are the actual visual assets to use. Match the image to the relevant page/section by filename and inspect it visually before placing it. Do not generate substitute imagery. |
| `Sagarvani-Design Reconstruction/design elements/` | Selected UI component code references, typography candidates, Haikei assets and Recraft SVG artwork | Use these to guide specific UI patterns and illustration assets. Adapt them to the existing project and accessibility requirements rather than pasting all code blindly. |
| `Sagarvani-Design Reconstruction/maritime reverse engineeer for sagarvani/` | REA research on maritime.sh: screenshots, captured DOM/accessibility tree/CSS tokens/network log, analysis and preliminary mapping | Use it as the primary design-inspiration evidence. Learn from the site's composition, interaction patterns and responsive behaviour; do not copy maritime.sh branding or content. |
| `Sagarvani-Design Reconstruction/Sagarvani-Files-To-Share/` | Engineering blueprint, concept decisions, API/data-readiness contract, build plan, resource register, package snapshot and prior prompts/reports | Use it to understand product and technical constraints. It does not prove every described feature is implemented in the current repository. Verify the actual checkout in the other branch. |

### Important distinction

- **The three boards** specify the desired structure and broad presentation.
- **The 46 illustrations** provide the real visual assets.
- **The design-element references** show possible implementations/effects.
- **The maritime.sh REA folder** explains what was researched and why the design inspiration was selected.
- **The engineering files and live repository** determine technical requirements and what is actually supported.

A board section is not automatically a new component, and a supplied UI snippet is not automatically a new top-level component. The user's existing 30-component plan remains locked.

---

## 2. The three preferred boards — preserve their detail

Use these exact source files in the archive as the baseline:

1. `Intial design language for iteration/Sagarvani_Visual_Board_01_Website_REVISED.png`
2. `Intial design language for iteration/Sagarvani_Visual_Board_02_Dashboard_REVISED.png`
3. `Intial design language for iteration/Sagarvani_Visual_Board_03_Components_REVISED.png`

### Board 1 — public-facing website

Preserve the full public website journey, including:

- Hero section and public navigation
- Stakeholder/use-case cards
- Before → Sagarvani → Outcome explanation
- Connected Ocean Ecosystem
- “From data to decisions” evidence workflow
- Intelligence Voyage
- Living Intelligence Network
- Scenario Replay
- Maps, exploration and marine insights
- Roadmap, origin story and community impact
- FAQ, closing experience and complete footer

The website may be composed as a long-form public experience, with individual pages/routes where already intended by the active implementation prompt. Do not delete sections simply to make the board look cleaner. If route/section ownership is ambiguous, keep the section inventory and mark the routing decision for the implementation branch to resolve against its current plan.

### Board 2 — operational workspace/dashboard

Preserve:

- App header and search/navigation
- Left workspace navigation
- Stakeholder view/switcher
- Main ocean map area
- Map layers and map actions
- Contextual radial marking menu, with standard accessible alternatives
- Wind → waves treatment
- Activity Terrain, only when meaningful data exists
- Active Evidence panel
- Ask Sagarvani panel
- Decision trace
- Source lineage/provenance
- Release policy
- Account/profile access
- Supporting states below the main workspace: login/account, AI text loading, voice/files and boat loader

Keep the Field/Community view simple by default and offer a Professional/Analysis view for users who need denser data. Switching the display mode must not change the underlying evidence or weaken the deterministic release/safety policy.

### Board 3 — component and interaction inventory

Keep the reference's full pattern coverage, including:

- Login/authentication, account menu and avatar picker
- File upload
- AI text loading and detailed AI state loading
- AI voice states
- Boat loader
- Empty/failure states
- Evidence status
- Search and filters
- Attach evidence
- Notifications
- Sticky navigation
- Stakeholder switcher
- Marking menu
- Activity Terrain
- Wind as waves
- Map overlays
- Scroll-to-photos
- Layered waves
- Scroll Wave Field and Tidal Stipple experiments
- Image sequence / guided voyage / scenario replay
- Responsive navigation
- Site-wide acceptance/release criteria

These are supporting interaction patterns mapped into the existing 30 components. They must not be treated as a new 30+ component list.

---

## 3. Original illustration inventory: 46 files

All files below are inside `Sagarvani-Design Reconstruction/DESIGN GENERATED/`. Suggested use is a mapping inferred from the filename and contact sheet; inspect the actual image before implementation. Preserve the original filename and file quality.

| Exact filename | Best-fit use to evaluate |
|---|---|
| `Coastal Waves_ Calm to Storm.png` | Scenario comparison or calm-to-turbulent conditions visual |
| `Compass Currents_ A Cartographic Seascape.png` | Evidence journey / validation motif |
| `Flowing Indigo Waves on Cream Paper.png` | Light-background current pattern or section background |
| `From Map Fragments to Lighthouse Bay.png` | Before → Sagarvani → Outcome story |
| `Hokusai-Inspired Stormy Fishing Waters.png` | Storm-state editorial/story visual; avoid implying a real current warning |
| `Indigo Ukiyo-e Ocean Wave Border.png` | Horizontal section/footer ornament |
| `Indigo Ukiyo-e Wave on Ivory Paper.png` | Light-background wave artwork |
| `Indigo Waves on Parchment.png` | Subtle background or light divider |
| `Japanese Nautical Woodblock Icon Sheet.png` | Source for reviewing/cropping decorative maritime symbols; recreate functional icons as accessible UI icons where appropriate |
| `Maritime Chronicles in Four Panels.png` | Community/origin/story section or narrative sequence |
| `Minimalist Indigo Ukiyo-e Seascape.png` | Quiet hero/empty-state/light section background |
| `Panoramic Ukiyo-e Wave Seascape.png` | Hero, intro animation backdrop or public-site wide panel |
| `Stormy Indigo Waves Under Swirling Skies.png` | High-energy scenario/story panel |
| `Sunlit Ukiyo-e Coastal Archipelago.png` | Light hero, community or coastal map/story section |
| `Three Detailed Boats from Above.png` | Map vessel silhouette reference; inspect crop/contrast/alpha before use |
| `Topographic Ocean Wave Engraving.png` | Activity Terrain / data-texture illustration, marked illustrative unless backed by real data |
| `Traditional Ukiyo-e Fishing Boat at Sea.png` | Fishing-vessel asset reference; assess how to layer/crop before using in animation |
| `Tranquil Ukiyo-e Sea Ripples.png` | Calm-state background / gentle section transition |
| `Turbulent Indigo Ukiyo-e Waves.png` | Scenario / challenging-sea illustration, not a live hazard display |
| `Ukiyo-e Archipelago Sea Chart.png` | Coastal map-art surface (illustrative, not navigation data) |
| `Ukiyo-e Boat Amidst Curling Waves.png` | Voyage/boat illustration |
| `Ukiyo-e Boat Amidst Stormy Waves.png` | Storm scenario illustration |
| `Ukiyo-e Coastal Fishing Village Panorama-2.png` | Hero, village/community story or intro backdrop |
| `Ukiyo-e Coastal Seascape Vignettes.png` | Use-case/story-card image source |
| `Ukiyo-e Coastal Village with Satellite Arcs.png` | Connected Ocean Ecosystem / satellite-observation story |
| `Ukiyo-e Coastal Vista with Satellite.png` | Evidence ecosystem / observation story |
| `Ukiyo-e Currents Around Island Shores.png` | Map/current background or current-flow story |
| `Ukiyo-e Currents in Indigo and Gold.png` | Decorative current pattern / evidence journey motif |
| `Ukiyo-e Fishing Boat on Indigo Waves.png` | Fishing vessel story or boat illustration source |
| `Ukiyo-e Fishing Boat Wave Cycle.png` | Potential loader sprite/frame-sheet source; verify frame layout before attempting animation |
| `Ukiyo-e Fishing Village at Dawn-1.png` | Sunrise Fishing Harbour/use-case or community story |
| `Ukiyo-e Indigo Wave Border.png` | Horizontal separator/footer ornament |
| `Ukiyo-e Lighthouse Among Stormy Waves.png` | Voyage destination / uncertainty story; avoid needless danger imagery in default view |
| `Ukiyo-e Maritime Research Voyage.png` | Researcher use case / research vessel scene |
| `Ukiyo-e Ocean Currents and Coastal Isles.png` | Map/current illustration |
| `Ukiyo-e Ocean Layers Map.png` | Layered evidence explanation / evidence-layer panel |
| `Ukiyo-e Ocean Waves and Distant Isles.png` | Light hero / section panorama |
| `Ukiyo-e Oceanographic Archipelago Map.png` | Coastal mapping and connected ecosystem illustration |
| `Ukiyo-e Research Ship in Stormy Seas.png` | Research-vessel scene / scenario illustration |
| `Ukiyo-e Seascape Beneath Billowing Clouds.png` | Darker horizon / architectural story section |
| `Ukiyo-e Seascape with Sailboat.png` | Light coastal panorama / opening sequence alternative |
| `Ukiyo-e Sunrise Fishing Harbour.png` | Fisher-community use case / sunrise hero art |
| `Ukiyo-e Tidal Islands and Whirlpools.png` | Ocean-current/map illustration |
| `Ukiyo-e Underwater Reef and Fish School.png` | Marine-life/fisheries content where relevant |
| `Ukiyo-e Voyage to the Lighthouse.png` | Intelligence Voyage destination sequence |
| `Vintage Japanese Maritime Emblem Collection.png` | Candidate avatar/emblem crop source; confirm crops work at small size |

### Asset rules

- The filenames are meaningful clues; they do not remove the need to visually inspect the actual image.
- Do not use an illustration as a real map tile, data chart, source icon, warning or live observation unless the content is actually backed by the relevant service.
- If the PNG is not transparent, do not pretend it is an isolated object. Use it as a contained scene/crop, or use the supplied Recraft SVGs if they fit.
- Do not generate additional images. Animation may be drawn in CSS/SVG/canvas around the supplied art, but no substitute image should be created.
- Keep a proper asset manifest mapping each placed asset to its exact source path and component/page.

---

## 4. `design elements/` — the exact references and how to treat them

The folder contains 30 entries: selected reference DOCX files, supplied SVG/PNG assets, and Recraft SVG variants. The DOCX files include code examples and implementation details; read them, but do not paste everything directly into the repository.

### Kokonut UI references

| Source file in `design elements/` | User decision / target behaviour | Implementation guardrail |
|---|---|---|
| `ai text loading.docx` | **Required** | Plain-language loading state. The animation may have changing words, but accessible status text must remain stable and stages must not claim work that the backend is not doing. |
| `ai state loading.docx` | Use/adapt | Show actual agent/workflow stages when the backend exposes them. The example includes looping demo steps if `steps` are omitted; do not allow the demo loop to represent a live request. |
| `ai voice.docx` | Planned/required experience | Make voice first-class, but verify microphone permission, speech-to-text and text-to-speech capabilities in the current backend/provider before calling it functional. Provide text fallback. |
| `loader.docx` | Adapt | Replace the circular/ring concept with the supplied boat artwork and a frontend animation. No new AI-generated ship. |
| `account menu kokonut ui.docx` | Use with login/account page | Wire it to real auth/profile state; do not show invented account data in production. |
| `avatar picker.docx` | Use with account experience | User wants an avatar picker. Prefer the supplied maritime emblem artwork over the sample's randomly generated face avatars, unless the user explicitly approves human avatars. |
| `file upload.docx` | Conditional | The sample simulates upload if no `onUpload` handler is provided. Do not ship simulated completion. First verify backend endpoint, permitted file types, size limits, authentication, persistence and processing. |
| `activity terrain kokonut ui.docx` | Explore for map/data side | It expects a numerical series (e.g., daily values). Only render a meaningful terrain if real time-series data exists; otherwise show a clearly labelled empty/unavailable state or omit the panel. |
| `wind component kokonut ui.docx` | Adapt to waves/current lines | Use as a restrained decorative current field only if it remains readable and performant; do not present the decorative field as real wind data. |
| `marking menu.docx` | Explore for dashboard/map tools | Optional shortcut for contextual map actions. All actions must remain available through conventional accessible buttons/menu; never make radial selection the only control path. |

### Haikei assets (provided originals)

- `layered-waves-haikei.svg` and `.png`
- `stacked-waves-haikei.png`
- `wave-haikei.svg` and `.png`

Use these selectively as section separators, light/dark transitions and subtle backgrounds. Prefer the supplied SVG where suitable. Ensure foreground text maintains contrast. Do not stack multiple moving wave effects at once.

### Supplied Recraft SVGs

- `recraft 1.1.svg`
- `recraft 1.2.svg`
- `recraft 2/side-profile-illustration-of-a-larger-modern-coast.svg`
- `recraft 2/side-profile-illustration-of-a-larger-modern-coast (1).svg`
- `recraft 2/side-profile-illustration-of-a-medium-oceanographi.svg`
- `recraft 2/side-profile-illustration-of-a-medium-oceanographi (1).svg`
- `recraft 2/side-profile-illustration-of-a-small-traditional-w.svg`
- `recraft 2/side-profile-illustration-of-a-small-traditional-w (1).svg`
- `recraft 3/precise-editorial-maritime-technical-atlas-illustr.svg`
- `recraft 3/precise-editorial-maritime-technical-atlas-illustr (1).svg`

These are likely vector vessel/coast/atlas assets. Inspect the actual SVGs, dimensions, viewBox, embedded references and duplicate variants before use. Prefer SVG for a precisely placed boat/diagram only when its style matches the selected boards. Avoid rendering embedded duplicate/repeated art as if it were a separate new illustration.

### Typography candidates

- `font and colour 1.docx`: **Cinzel Decorative** headings and **Unbounded** body; a very ornamental/display-heavy candidate. Test carefully; do not assume it is appropriate for long body copy or local-language coverage.
- `font and colour 2.docx`: **Fraunces** headings and **Google Sans Code** body. More promising for editorial headings, but test readability and script coverage. A monospaced/code-style face may be better reserved for technical metadata than long Field/Community paragraphs.

Recommendation for the other branch: preserve typography as a design decision to evaluate, not a hard-coded assumption. Choose a readable body font that covers the supported Indian languages and renders well at large text sizes. Check actual font loading and fallbacks.

### Skiper UI — scroll-to-images

`scroll to images.docx` includes a `ReactLenis` root and `framer-motion`-based sticky image cards. Use the pattern only if it helps tell the community/voyage story. It must remain optional, work on touch and keyboard, avoid scroll trapping, and degrade to ordinary scroll/reduced motion.

### Originkit

- `Scroll wave field.docx` — a comparatively elaborate 3D/WebGL-style scroll wave field.
- `tidal stipple.docx` — a dotted/stipple pattern effect.

Treat both as optional experiments, not foundational requirements. Start with static supplied Haikei wave assets and restrained CSS/Motion effects. Add the heavier field only if it clearly improves the design and performs well on ordinary mobile devices.

### Lenis and animation-library integration

Lenis is selected as the single root scrolling system. The Skiper reference already uses `ReactLenis` and `framer-motion`. Avoid creating multiple nested root Lenis instances.

The package snapshot within the archive lists Next.js 16.3.4, React 19.2.8, Tailwind CSS 4, `framer-motion`, GSAP, Anime.js, Lucide React, OGL, Leaflet and React Leaflet. This is a snapshot, not proof that the other branch's current checkout is identical. Before copying source, compare the live `package.json` and imports. Several Kokonut source files import `motion/react`; verify whether the current project actually has a compatible `motion` package/export before integrating them. Do not install overlapping animation libraries just to make one snippet compile.

---

## 5. The requested opening sequence: ship + waves + light

Add a short cinematic intro between initial site load and the homepage hero reveal. This is an agreed design behaviour and must be included in the frontend plan.

### Intended feel

1. Start with a calm warm-ivory or deep-indigo canvas that matches the selected board—not a blank, indefinite loading screen.
2. Supplied wave artwork sweeps in from one side.
3. A supplied fishing-boat illustration enters from the opposite side with a small, gentle bob.
4. A light beam is drawn as a frontend SVG/CSS overlay and flashes once from the ship.
5. The beam triggers a brief reveal/wipe into the actual homepage hero.
6. The hero and navigation become usable immediately.

### Asset candidates to inspect first

- Backdrop: `Panoramic Ukiyo-e Wave Seascape.png`, `Ukiyo-e Coastal Fishing Village Panorama-2.png` or `Ukiyo-e Ocean Waves and Distant Isles.png`.
- Ship: `Ukiyo-e Fishing Boat Wave Cycle.png`, `Traditional Ukiyo-e Fishing Boat at Sea.png`, `Ukiyo-e Fishing Boat on Indigo Waves.png`, or a matching supplied Recraft SVG.
- Wave layer: the supplied Haikei SVGs or one of the wave borders from `DESIGN GENERATED/`.

The actual ship/backdrop combination should be picked after inspecting image aspect ratios and whether the boat is separable from its background. Do not assume alpha transparency or sprite layout. Do not generate a new image to create the intro. If using the wave-cycle sheet, inspect its frame layout and crop frames accurately.

### Interaction and accessibility rules

- Target roughly 1.6–2 seconds for the sequence, but never delay the site while waiting for data/API requests.
- Include a visible **Skip intro** control, keyboard accessible and translated.
- Play at most once per session/initial entry unless product design later chooses otherwise; do not replay on every in-app route change.
- Respect `prefers-reduced-motion`: skip or replace the animation with a static, fast reveal.
- Preload only the few assets needed for this sequence; fall back immediately if an asset fails to load.
- The light flash must be brief and restrained—not a strobe. Use a gradient/cone mask rendered in code; the beam is not another generated image.
- Keep the hero accessible if JavaScript/animation fails.
- Treat the sequence as a brand intro, not as proof that backend data is loading or ready.

---

## 6. Colours and visual harmony

The user's stated palette is the starting point:

- Icy Blue `#AED5F5`
- Azure Blue `#367ADF`
- Fresh Sky `#4FACE5`
- French Blue `#394988`
- Charcoal Blue `#353A4C`

The reference artwork naturally introduces warm parchment/ivory, deep indigo and lapis-like blues. These can be considered supporting tokens to preserve the harmony of the supplied illustrations; do not force all surfaces into a uniformly dark theme. Test contrast before assigning foreground/background pairs.

Use warm-ivory surfaces for content-heavy and community-facing sections; use indigo/Charcoal Blue for the dashboard shell, navigation and selected technical panels; use brighter blue accents for clear primary actions, selected states and links. Do not use pale-blue text on pale-blue backgrounds. Status must be conveyed with text/icons, not colour alone.

---

## 7. Accessibility and the intended users

Design for low literacy, low digital confidence, small phone screens and inconsistent connectivity without labelling the users in the UI or assuming everyone is unable to read.

Required patterns:

- Plain language, short sentences and descriptive labels alongside icons.
- Large, easy-to-tap primary actions; avoid hover-only interactions.
- A visible **website-language** selector in the top navigation on desktop and mobile.
- A separate **spoken language/dialect** selector for voice services. Show only verified supported options.
- Tap-to-speak, stop recording, play answer and replay controls where supported.
- Text input as a fallback if microphone permission or voice services are unavailable.
- Optional read-aloud for important results if text-to-speech supports the selected language.
- A Field/Community view with fewer simultaneous controls and a Professional/Analysis view for advanced users.
- Meaningful empty, stale, conflicting, unavailable and failure states.
- Keyboard navigation, visible focus, appropriate screen-reader labels and reduced-motion support.
- Essential map information must also be available through readable summaries; do not make the map the only way to understand an important result.
- Do not rely on small labels embedded inside artwork; all important labels must be real, translated UI text.

The language selector should persist across navigation. The interface-language control and speech-language/dialect control must not be conflated. Actual choices depend on verified translation/speech capability in the current implementation.

---

## 8. Product truth and backend gates

The engineering docs in the ZIP define the product as an evidence-aware marine decision-intelligence platform. The frontend must preserve this distinction: Sagarvani is not merely a generic chatbot and must not imply verified/live evidence when there is none.

Before showing a capability as functional, the other branch must inspect and verify the current repository/backend for:

- Authentication/session handling and real account menu data
- Voice input/speech-to-text and spoken output/text-to-speech providers, supported languages and permission/error states
- File upload endpoint, accepted file types/size, storage and processing results
- Real map and source-layer data
- Evidence source, retrieval time, issue/run time, valid time and freshness status
- Actual pipeline stages for AI loading/progress
- Scenario replay data and timestamps
- Notifications/alerts and whether an action has side effects

Use these truthful states:

- **Verified / available** — supported by current runtime/source evidence
- **Needs checking / stale / conflicting / insufficient** — explain the gap
- **Unavailable** — service/source absent or error returned
- **Illustrative / demo** — visual example or fixture; do not present as real data
- **Planned** — not implemented yet

Never let UI mode, a model, an animation or a generated illustration bypass evidence validation or the deterministic release policy. Do not invoke real SMS/WhatsApp/voice broadcast endpoints, paid APIs or other external side effects while auditing unless the active prompt explicitly permits it and the action is safe/authorized.

---

## 9. Product/engineering references inside the ZIP

Under `Sagarvani-Files-To-Share/`, the archive contains the following files. Use them for their stated purposes; treat audit-reported implementation claims as claims that must be rechecked against the current branch:

- `MASTER_BLUEPRINT.md` — main technical/product blueprint and interpretation of architecture decisions
- `Sagarvani_Complete_Engineering_Master_Blueprint (1).md` — consolidated engineering blueprint
- `Sagarvani_Concept_Decision_Record_v2.md` and `Sagarvani_Concept_Decision_Record_v2 (1).md` — product and architecture decision record
- `Sagarvani_API_Dataset_Readiness_and_Data_Contract (1).md` — source readiness and API/data contract
- `Sagarvani_Outstanding_Verification_Report.md` — prior audit report; reverify against current checkout
- `Antigravity_Outstanding_Verification_Prompt.md` — verification/research prompt with explicit safety constraints
- `Sagarvani_Post_Audit_Decisions_and_Build_Plan (1).md` — post-audit implementation direction
- `Sagarvani_Antigravity_Backend_Kickoff_Prompt.md` — backend kickoff prompt
- `RESOURCE_REGISTER(1).md` — resource register covering 187 resources, including UI/UX options
- `Sagarvani(1).pdf` — project/SIH submission context
- `package.json` and `package-lock.json` — a dependency snapshot; compare against the current repository before acting

The archive also includes the maritime.sh research analysis in:

`maritime reverse engineeer for sagarvani/03_Analysis/`

- `01_executive_summary.md`
- `02_page_anatomy.md`
- `03_component_inventory.md` — 13 maritime.sh components, **not** Sagarvani's locked 30 components
- `04_visual_design_tokens.md`
- `05_interaction_matrix.md`
- `06_design_rationale.md`
- `07_responsive_accessibility_audit.md`
- `08_implementation_clues.md`
- `09_sagarvani_inspiration_mapping.md`
- `10_unknowns_and_evidence_gaps.md`

Raw evidence is in `02_REA_Evidence/`, including `css_tokens_and_variables.json`, `maritime_accessibility_tree.txt`, `maritime_dom_captured.html`, `network_requests_raw.txt`, `page_anatomy_raw.json` and `rea_scenario_metadata.json`. Reference screenshots are in `01_Reference_Screenshots/` and the other research screenshot folders.

The REA 13-component inventory is evidence about the inspiration website. Do not mistake it for or merge it into Sagarvani's locked 30-component plan.

---

## 10. Locked component-plan rule

The user has explicitly locked the Sagarvani top-level component plan at **30 components**. Do not add Component 31. Do not re-number the plan because a board shows page sections, UI snippets or animation motifs.

Some exact names for Components 1–6 are not captured in this ZIP's visible component inventory; recover the canonical list from the active branch conversation, user-supplied project file or current implementation context. Do not invent missing titles. The 13-component maritime.sh inventory is not the canonical Sagarvani list.

### Known locked component definitions from the earlier Sagarvani design decisions

Use these as the existing component-plan entries where they match the canonical list in the active branch. Preserve the numbers; do not create new ones. Names below are descriptive labels from the existing design notes, not permission to renumber the plan.

| No. | Existing component / design decision | Required interpretation |
|---:|---|---|
| 7 | Multi-domain use cases | Interactive, tabbed use-case showcase. Fisheries/PFZ is primary; other domains must be labelled by actual implementation status. |
| 8 | Sagarvani Intelligence Voyage | Boat follows a route with stops explaining the workflow; destination presents an evidence-supported result or explicit uncertainty. Hybrid scroll/click, tap-friendly. Recovery routes back to validation. |
| 9 | Before → Sagarvani → Outcome | Explain the value without implying a guaranteed safe decision. |
| 10 | Connected Ocean Ecosystem | Marine, weather, satellite and geospatial sources; explicitly distinguish active, planned, unavailable and illustrative sources. |
| 11 | Evidence Decision Journey | Show evidence passing, needing recovery or remaining insufficient. Distinguish intended behaviour from verified implementation; make no safety guarantee. |
| 12 | Living Intelligence Network | Show ocean/weather/geospatial signals and agent flow, harness, bounded recovery and policy control. Prefer tiny boats and maritime cues over robot icons. Runtime traces only when verified. Recovery cannot bypass validation/release policy. |
| 13 | Interactive Scenario Replay | Optional comparison of labelled current conditions, historical scenarios and proposed what-if experiments. Separate real traces, verified results, fixtures and proposed experiments. |
| 14 | Ocean Roadmap | Milestone/island visual; proposed until milestones are verified. |
| 15 | Return to the Ocean closing experience | Final narrative transition with functional CTAs only. |
| 16 | Editorial Ocean Footer | Technical navigation and links; show only verified links. |
| 17 | Adaptive desktop/mobile + accessibility | Responsive behaviour, keyboard navigation, readable status, reduced motion and performance are built in. |
| 18 | Editorial FAQ accordion | Answers grounded in verified project status; include capability status where useful. |
| 19 | Contextual Status Labels | Status text and evidence determine status; never use colour alone. Click/focus shows provenance, timestamps and limitations. A moving ship is reserved for verified live activity. |
| 20 | Loading, empty and failure states | Cover loading, no/stale data, conflicting evidence and exhausted recovery; explain honestly and do not show fake progress. |
| 21 | Continuous Ocean Current transitions | Connect sections through subtle motion without harming readability, performance or reduced-motion preferences. |
| 22 | Cinematic ocean hero with intelligence overlays | Varied vessel artwork and restrained movement, poster/static fallback and no implication of live vessel tracking. |
| 23 | Transparent navbar → floating glass pill | Functional links, responsive/keyboard support, and Explore the Platform CTA; language selector remains accessible. |
| 24 | Editorial cinematic typography | Expressive headings and whitespace; font family/weights remain candidates until readability and script coverage are evaluated. |
| 25 | Editorial grid with cinematic moments | Consistent responsive grid with selected full-width visuals. |
| 26 | Cinematic footage + custom-designed graphics | Combine visual media with real interface elements; avoid synthetic-looking generic collage aesthetics. Use supplied imagery only. |
| 27 | Guided Voyage + Ask Sagarvani | Ready-made Fisheries/PFZ demonstration; user queries only where the verified endpoint supports them. Label fixture/live correctly. |
| 28 | Origin story | Verified history and purpose; separate long-term vision from currently available features. |
| 29 | Complete discoverability package | Metadata, branded share image, favicon, appropriate indexing and correct verified links. |
| 30 | Component acceptance criteria + final release checklist | The final entry covers cross-component acceptance and site-wide release checks. Do not treat as permission to add Component 31. |

Component 30 is the final plan entry. The language/dialect control, welcome/intro animation, Kokonut patterns, wave treatments and asset selections must be mapped into these existing entries (or Components 1–6 recovered from the authoritative list), not added as standalone numbered components.

Map every design reference into the existing component plan with a matrix containing:

- Locked component number/name
- Page/section where it appears
- Exact asset file path(s)
- Selected UI/resource source
- Purpose and visible behaviour
- Animation and accessibility fallback
- Backend/API dependency and verification status
- Responsive/keyboard requirements
- Acceptance tests

If a design resource doesn't fit a current component, mark it Optional/Defer rather than creating another top-level component.

---

## 11. Existing project dependency cautions

The `package.json` snapshot in the ZIP lists Next.js 16.3.4, React 19.2.8, Tailwind CSS 4, `framer-motion` 13.1.1, GSAP 3.15.0, Anime.js 4.5.0, Lucide React 1.38.0, OGL, Leaflet and React Leaflet, among others. Do not assume the active branch matches this snapshot.

Before integrating a snippet:

1. Inspect the current checkout's `package.json` and lockfile.
2. Inspect imports in the specific provided component DOCX.
3. Resolve whether the package and import path are actually installed/compatible (e.g. `motion/react` versus `framer-motion`).
4. Choose a primary component-animation approach; don't introduce overlapping libraries for the same effect.
5. Use one root Lenis instance for website scroll if Lenis is retained; avoid nested smooth-scroll roots.
6. Test reduced motion, mobile performance, keyboard and error states.

No need to install every library in the resource register. The goal is a coherent design system, not maximum package count.

---

## 12. Build order and required outputs from the other branch

Respect the active branch's existing build prompt and safety rules. The user's previously agreed phase-by-phase frontend sequence is:

1. Home/hero page
2. Second page/section as defined by the active plan
3. Third page/section as defined by the active plan
4. Fourth page/section as defined by the active plan
5. Login page
6. Dashboard

Do not build the entire product in one giant step if the active prompt says to work phase by phase. Before implementation, reconcile the exact page/route boundaries against the current project prompt without losing any section from Board 1.

When the active prompt calls for design/integration documents, produce:

1. **Canonical UX/design specification** — pages, page order, user journeys, visual principles, language controls and animation behaviour.
2. **Locked 30-component mapping matrix** — exact component/resource/asset mapping; no invented numbering.
3. **Asset manifest** — all 46 original artwork filenames, intended use, current implementation path, crop/alpha/format notes and status (used/unused/review).
4. **Resource decision register** — Use / Adapt / Optional / Defer / Reject decisions for each selected resource, with reasoning and dependency/license/compatibility checks.
5. **Animation and transition spec** — load intro, hero reveal, scrolling, page/section transitions, boat loader, AI text/voice states, map interactions, reduced-motion alternatives and timing guidance.
6. **Accessibility and localization spec** — Field/Community versus Professional/Analysis view, website language selector, separate speech language/dialect selector, voice fallback, low-literacy-friendly content, mobile, keyboard and reduced-motion requirements.
7. **Backend capability verification matrix** — real endpoint/service, verification evidence, UI behaviour, unsupported/error fallback; keep backend facts based on current repo/runtime, not inferred from the design mockups.
8. **Testing/acceptance checklist** — each page/interaction, desktop/mobile, language switching, keyboard, reduced motion, loading/failure/stale/conflicting evidence, voice permissions and upload errors.

Don't create or modify production code before the active prompt's requested phase/approval. If the current prompt explicitly asks to implement a particular phase, do that phase only, after the source/dep checks above.

---

## 13. Copy/paste instruction for the other ChatGPT branch

> Read this handoff document together with `Sagarvani-Design Reconstruction.zip` and your existing Sagarvani backend/repository context and active implementation prompt. Treat this file as supplementary design context; do not replace or disregard your active prompt, build order, safety instructions or backend decisions.
>
> Inspect the actual archive paths. The three preferred boards are under `Intial design language for iteration/`; the 46 actual user-generated illustrations are under `DESIGN GENERATED/`; the selected component/code references, Haikei assets and Recraft SVGs are under `design elements/`; maritime.sh evidence and 10 analysis reports are under `maritime reverse engineeer for sagarvani/`; the resource register, product/engineering blueprints, API/data contract, package snapshot and prior prompts/reports are under `Sagarvani-Files-To-Share/`.
>
> Preserve the three preferred boards' section and interaction coverage while making the experience friendlier for users with low literacy/digital confidence. Use the exact supplied artwork paths; do not generate, retrieve or substitute unrelated imagery. Any animations must be coded around these supplied assets. Add the requested intro: wave artwork enters from one end, a supplied fishing boat enters from the opposite end, the boat's light flashes once via a frontend-drawn SVG/CSS beam, and the real homepage hero is revealed. Provide Skip intro, immediate fallback if assets fail, and reduced-motion behaviour.
>
> Keep the existing Sagarvani 30-component plan locked. Do not add Component 31, and do not mistake the 13-component maritime.sh REA inventory for Sagarvani's component list. Recover the exact existing component numbers/names from the active conversation/repository if needed; do not invent missing items. Map each existing component to the relevant original asset, resource reference, animation, page, backend dependency and acceptance test.
>
> Use Lenis for one root scroll system if it remains compatible; use the supplied Haikei waves selectively; review the Kokonut UI component DOCX files; treat Originkit Scroll Wave Field/Tidal Stipple and Skiper scroll-to-images as optional experiments; compare the two typography candidates before locking the body font; and inspect current package/import compatibility before installing anything. Keep UI/UX Pro Max and Taste as critique tools if available, not as authority to replace the chosen visual identity. Use the existing test skill/checklist for accessibility and UI acceptance where available.
>
> Put a visible website-language selector in the header on desktop and mobile, and keep the spoken-language/dialect selector separate. Only expose languages and voice options genuinely supported by the current services. Design for simple language, large tap targets, visual guidance, tap-to-speak/read-aloud where supported, text fallbacks, keyboard access and reduced motion. Keep the Field/Community view simple and the Professional/Analysis view detailed, while both use the same evidence and release policy.
>
> Treat illustrations, maps, mock data and animations as illustrative unless the current backend supplies verified data. Check auth, voice, uploads, source freshness, map layers, scenario replay and AI progress reporting in the actual repository before describing them as functional. Do not invoke external side-effect/paid alert services during an audit. Follow the current prompt's requested workflow and phases, and return the deliverables appropriate to the current phase rather than building everything at once.
>
> Before coding, give a short inventory of which archive folders/files you inspected and a component-to-asset/resource mapping. Then continue according to the existing prompt. Do not ask the user to upload the same ZIP again.

---

## 14. Final note

This bundle explains the design inputs and intended relationship between them; it does not certify that backend features work. The current repository and its safe verification results remain the authority on actual functionality. The design branch should preserve the visual identity and UX requirements while the backend/implementation branch confirms real capabilities and integrates them incrementally.
