# Sagarvani — Accessible UX, Page Flow, Animation & Component Specification

**Version:** 2.0 — Review draft  
**Purpose:** One complete design reference to read and approve before creating the implementation handoff documents.  
**Visual baseline:** The three Sagarvani boards approved by the user: public website, marine-intelligence workspace, and component/interaction system.  
**Artwork rule:** Use only the original user-provided/generated artwork in `DESIGN GENERATED(1).zip` and other supplied project asset packs. Do not generate replacement pictures. CSS/SVG interface effects such as a light beam, focus ring, marker pulse or mask transition may be drawn in code; these are not replacement illustrations.  
**Component constraint:** The established 30-component plan remains locked. This document clarifies behaviours inside that plan; it does not add Component 31 or renumber existing components.  
**Status:** Proposed design specification. Backend capabilities, supported languages, real data layers and production behaviour must be verified before any UI claims them as available.

## Contents

1. Product goal and audience
2. Visual direction and design tokens
3. New first-entry animation — “A light across the ocean”
4. Global navigation and language controls
5. Board 1 — Complete public-facing website
6. Page-to-page user journeys
7. Board 2 — Marine intelligence workspace
8. Ask Sagarvani — text and voice states
9. Authentication, account menu, avatar and file upload
10. Animation and motion catalogue
11. Accessibility and inclusive UX requirements
12. User-provided artwork manifest — 46 images
13. Backend-dependent behaviour and truthfulness gates
14. Technical guardrails for implementation
15. Acceptance checklist before implementation approval
16. Next-stage handoff documents

---

## 1. Product goal and audience

Sagarvani should feel like a friendly ocean companion, not a technical control room. A person should be able to open the site, choose a language, ask a marine question, understand the answer and see the supporting evidence without needing to understand GIS, AI agents or data engineering.

The primary audience includes fishers and coastal communities with different reading ability, language preference, digital confidence, devices and connectivity. Researchers, coastal authorities and maritime operators also need deeper evidence and map tools. Accessibility should not mean making the product look childish or removing expert capability. It means making the first action obvious and progressively revealing complexity only when needed.

### Experience principles

1. **Visual-first, not visual-only.** Use the supplied marine artwork to establish context, but pair icons with clear labels and provide a text/list alternative to map-only information.
2. **One clear next action.** “Ask Sagarvani” is the main entry point. Avoid a screen full of equally prominent controls.
3. **Voice is an option, not a requirement.** Users can speak, type, tap a suggested question, listen to an answer or read it.
4. **Plain language first.** Use familiar wording. Explain terms such as Potential Fishing Zone (PFZ) on first use; keep technical detail behind “More details.”
5. **Respectful by design.** Never label users as illiterate or assume they are unable to learn. Make the product easier for everyone.
6. **Immersive, but not obstructive.** Ocean motion should support orientation, explanation or delight. It must not block a critical action or make users wait unnecessarily.
7. **Evidence before confidence.** Never imply live, verified or safe conditions unless supported by actual source data and validation.
8. **Honest loading and failure states.** No fabricated progress, fake upload completion, invented source freshness or fallback marine answers that look real.
9. **Use the artwork as an authored visual system.** Reuse the user's exact artwork with considered crops and layouts, not unrelated stock imagery or newly generated substitutes.
10. **Accessibility is part of the design, not a later patch.** Support keyboard, touch, visible focus, readable contrast, larger text, reduced motion and assistive technologies.

## 2. Visual direction and design tokens

### 2.1 Art direction

The desired look is a carefully composed Japanese woodblock-print / ukiyo-e-inspired marine world: intricate curling waves, hand-inked coastlines, layered pigment, warm paper, deep indigo, lapis and icy highlights. The chosen visual language is distinctive because of its detail and colour harmony; it should not be flattened into a uniformly dark AI dashboard.

Use the most detailed artwork at intentional story moments: the opening sequence, homepage hero, Intelligence Voyage, community stories and selected evidence illustrations. Use calm, light surfaces for form fields, explanatory text, settings and long reading. The map workspace can use deep navy framing, while cards and instructions remain warm ivory to keep them legible.

### 2.2 Approved core palette

| Token | Hex | Intended role |
|---|---|---|
| Icy Blue | `#AED5F5` | Light accents, selected surfaces, gentle focus details |
| Azure Blue | `#367ADF` | Primary action, selected state and clear interactive emphasis where contrast passes |
| Fresh Sky | `#4FACE5` | Secondary accent, data-domain accents and motion highlights |
| French Blue | `#394988` | Deeper blue surface, illustration details and secondary emphasis |
| Charcoal Blue | `#353A4C` | Deep text and restrained dark surfaces, with contrast checked |
| Warm Ivory | `#EDE4D2` | Paper-like page background and calm editorial surfaces; validate against supplied artwork |

Deep indigo present in the supplied artwork can be used as an illustration colour. Keep the five named brand colours consistent in tokens. Do not force every colour into every section. Most reading areas should be light, with deep blue reserved for navigation, map framing, key focal moments and footer contrast.

### 2.3 Typography and text hierarchy

Use a readable sans-serif for body text, menus, forms, data statuses and long explanations. A refined editorial serif may be used for short display headlines if testing shows it remains legible at mobile sizes. Use a monospace only for technical metadata where it adds meaning; do not use it for primary instructions.

- Headline: one clear idea, usually one to three short lines.
- Supporting text: one or two short sentences.
- Primary button: verb plus purpose, e.g. “Ask Sagarvani.”
- Data status: text and icon together, e.g. “Needs checking,” not colour alone.
- Advanced details: optional expansion with source, timestamp, freshness, comparison and caveat.

Avoid long uppercase labels, tiny text baked into illustrations, low-contrast fine print and headings rendered inside image files. Actual UI text must be real HTML text so it can translate, resize and be read by assistive technology.

## 3. New first-entry animation — “A light across the ocean”

This is a new addition to the approved design. It plays before the homepage hero on a fresh visit to the website and introduces Sagarvani as a welcoming, maritime experience.

### 3.1 Intended feeling

The screen begins quiet and open—not black, loud or futuristic. The ocean waves arrive from one side and the boat enters from the opposite side. The boat's lamp flashes once; a soft beam sweeps across the waves, and the lit area becomes the reveal transition into the homepage hero. The effect should feel like a ship arriving and guiding the viewer into the site, not an alarm or a cinematic barrier.

### 3.2 Use only the supplied source assets

Recommended source assets from the user's ZIP:

- `Minimalist Indigo Ukiyo-e Seascape.png` — calm opening background, if the crop suits the viewport.
- `Flowing Indigo Waves on Cream Paper.png`, `Indigo Ukiyo-e Ocean Wave Border.png` or `Ukiyo-e Indigo Wave Border.png` — wave layer / lower-edge wave detail.
- `Ukiyo-e Fishing Boat Wave Cycle.png` — source sheet for the small vessel. The sheet has a 4-column by 2-row arrangement of similar boat frames; inspect/crop a frame carefully before implementation. If frame differences are too small to animate usefully, animate one cropped boat with CSS position and bobbing instead.
- `Ukiyo-e Seascape with Sailboat.png` or `Ukiyo-e Coastal Fishing Village Panorama-2.png` — possible hero artwork after the reveal, depending on the chosen layout.

The lamp beam can be a CSS/SVG shape layered over the supplied boat art. Do not generate a new ship image to create the light. The beam must be subtle, low-opacity and non-flashing after its single transition cue.

### 3.3 Timeline and movement

Target duration: approximately **1.6–2.0 seconds**, with a hard maximum around **2.2 seconds**. The homepage should already be loading behind the animation.

| Time (approx.) | What the user sees | Behaviour |
|---|---|---|
| 0–150 ms | Warm-ivory / pale-sea opening field; a faint horizon appears | Avoid a blank black screen. Preloaded art is placed immediately; no blocking network call is required for the animation itself. |
| 120–650 ms | Waves sweep in from the lower-left / one side, settling into a readable ocean line | Use the supplied wave artwork as a masked or clipped layer. Keep the movement smooth, not a fast wipe. |
| 350–1,000 ms | A small boat enters from the opposite edge, travelling toward a stable point near the horizon | Animate the supplied boat crop with transform/opacity. Add a small, gentle vertical bob; do not make the ship bounce. |
| 950–1,250 ms | The boat's lamp emits one warm, controlled flash | A soft CSS/SVG beam briefly reveals a path over the waves. One pulse only; no repeated strobing or harsh full-white flash. |
| 1,200–1,850 ms | The beam opens into a soft light/paper reveal; the homepage hero becomes visible | Crossfade or mask from the opening composition to the actual hero artwork and header. The hero headline and buttons are ready immediately. |
| By 2,200 ms | The hero is fully usable | No further intro movement blocks scrolling, clicks, keyboard focus or voice access. |

Timing can be adjusted during implementation testing, but the order and meaning should remain: **waves arrive → boat enters → light flashes once → hero is revealed**.

### 3.4 Controls, repeat behaviour and fallback

- Provide a visible **“Skip intro”** control with keyboard access and an accessible name.
- Offer “Skip intro next time” in a simple preference if the intro is retained for returning visits.
- Play on a fresh external entry unless the user has opted out or the system requests reduced motion. Do not replay during internal page navigation; avoid replaying simply because the user opens a menu or changes language.
- If the user selects reduced motion, bypass the animated sequence and reveal the hero immediately or with a very short static fade.
- If the artwork or animation fails to load, show the hero directly; never leave a blank page.
- Never autoplay sound.
- Preload only the small assets required for the opening; lazy-load lower-page illustrations.
- Use transform and opacity where possible. Do not run heavy canvas/shader effects for this sequence.
- Ensure the hero is visible and usable if JavaScript fails or a low-end device cannot sustain the animation.
- Do not trap focus behind the splash. “Skip intro” must be reachable immediately; after the reveal, focus proceeds naturally to the page.

### 3.5 Implementation boundary

Treat the intro as an entry-state transition, not a new component in the locked 30-component plan. It can be implemented within the existing hero/page-load experience. Use the existing animation stack after code audit; do not install a new animation library just for this effect.

## 4. Global navigation and language controls

### 4.1 Desktop header

Keep the clear editorial navigation from the approved Board 1:

- Sagarvani logo
- Platform / Home
- Use cases
- How it works
- Voyage
- Evidence
- About / Community
- **Website language selector** in the upper-right
- **Spoken-language / dialect selector**, distinct from the website language
- Log in or account/avatar menu
- Explore platform / Ask Sagarvani CTA as appropriate to the page

The website-language selector remains visible in the compact sticky header. Do not hide language selection only inside settings.

### 4.2 Two separate language controls

**Website language** changes interface text: navigation, buttons, headings, forms, help, error states, alt text, validation and accessibility labels.

**Spoken language / dialect** chooses the language used for speech recognition and spoken responses, only among options that the integrated speech services actually support.

Example labels:
- `Website: English ▾`
- `Voice: Kannada ▾`

Do not silently switch a requested language when unavailable. Explain briefly and offer a supported alternative. A language menu must list only reviewed interface translations; a voice menu must list only verified speech capabilities. Do not claim support for every language or dialect before implementation testing with fluent speakers.

### 4.3 Mobile language access

Keep a small, visible language button in the mobile header and offer the full list at the top of the menu sheet. The Ask screen must also expose spoken-language choice without requiring users to traverse several settings pages. Main touch targets should be about 44–48 CSS pixels or larger where possible.

### 4.4 Navigation behaviour

- Internal page navigation should feel direct and predictable; do not replay the opening splash.
- In-page anchor navigation should preserve browser history and keyboard focus.
- Sticky header transitions should be small and not cause layout jumps.
- Mobile bottom navigation can include Home, Map, Ask, Insights and Menu; labels should remain visible with icons.
- Any radial marking menu must have a conventional accessible menu/list alternative.

## 5. Board 1 — Complete public-facing website

Keep the complete website structure from the approved board. Use the supplied artwork from the asset map in Section 12. Illustration placement can change to support readability, but the sections themselves should not be removed merely to simplify the design.

### Section 1 — Homepage hero

**Purpose:** Explain Sagarvani quickly and lead to a useful action.

**Layout:**
- Header with website language and spoken-language controls.
- Hero illustration with a quiet text region, using a supplied wide coastal or seascape image.
- Headline: “A clearer view of our ocean.” or “Simple answers for a safer, stronger ocean.” Select one during design approval.
- Supporting copy: marine, weather and coastal evidence brought together to help people make better-informed decisions.
- Primary action: **Ask Sagarvani**.
- Secondary action: **Explore the ocean**.
- A small status/trust statement, only if grounded in verified implementation.

**Motion:** Run “A light across the ocean” before the hero on fresh entry. Afterward, keep only subtle wave ambience. Never delay the primary button.

### Section 2 — Who it serves / use cases

Four entry cards: Fishers, Marine Researchers, Coastal Authorities, Maritime Operators. Each card should include an illustration, a short benefit and one action. Selecting a card opens its use-case detail while retaining the visual system.

Examples of simple card copy:
- Fishers — “Understand conditions before you plan a trip.”
- Researchers — “Explore evidence from different sources.”
- Coastal authorities — “Review information for coastal planning.”
- Operators — “Check available conditions before operational decisions.”

Do not imply guaranteed safety or invent customer testimonials.

**Motion:** Small image pan or restrained state change on select, followed by a short content fade/slide. Provide a tap and keyboard path; do not depend on hover.

### Section 3 — Before → Sagarvani → Outcome

Three visual stages:
1. Fragmented information.
2. Evidence checked and compared.
3. A bounded answer—or an explanation that evidence remains insufficient.

The final stage should not always look like a positive green success. Withheld or uncertain answers are legitimate outcomes.

**Motion:** Sequential reveal on scroll, but each stage can be read without triggering a precise scroll position. Use the supplied `From Map Fragments to Lighthouse Bay.png` or `Ukiyo-e Ocean Layers Map.png` as illustration candidates.

### Section 4 — Connected Ocean Ecosystem

Show ocean observations, weather, satellite observations and geospatial context. Use `Ukiyo-e Coastal Village with Satellite Arcs.png`, `Ukiyo-e Coastal Vista with Satellite.png`, `Ukiyo-e Oceanographic Archipelago Map.png` or `Compass Currents_ A Cartographic Seascape.png` as candidates.

Keep an explicit label such as **“Illustrative marine cartography”** on generated map art. Actual sources and status labels must be driven by the application's real service metadata, not the illustration.

**Motion:** Fine connection lines reveal gently. Do not animate fake data flows to suggest that services are connected when they are not.

### Section 5 — From data to decisions

Explain the process in four steps:
1. Collect available evidence.
2. Check freshness and comparability.
3. Gather more evidence or re-plan if needed.
4. Release a supported answer or explain uncertainty.

Keep a one-line plain-language description under each step. Advanced readers may open the technical explanation.

**Motion:** A small marker tracks actual process state only when the backend provides it. Static diagrams are used for explanatory content.

### Section 6 — Intelligence Voyage

Use the supplied boat-and-coast artwork to explain the workflow as a journey. The stages are Gather → Validate → Recover if needed → Decide. The recovery path must return to validation and never bypass the release policy.

**Interaction:** Hybrid scroll-and-tap. Each waypoint can be tapped to open a short explanation. Mobile users must not be forced to scroll a long animation to advance.

**Motion:** Boat advances between waypoints only when the user scrolls or activates an explicit step. One gentle bob at a stop. Keep reduced-motion mode static with selectable step cards.

### Section 7 — Living Intelligence Network

Explain that specialist agents gather information and that a separate validation and release process checks the result. The harness, budgets, permissions and policies should be shown only at the detail level appropriate to the audience.

Label the diagram **“System concept”** or **“Illustrative workflow”** until connected to verified runtime traces. Do not represent agent graphics as proof of live execution.

### Section 8 — Scenario Replay

Let users compare clearly labelled conditions, historical examples or proposed “what-if” scenarios. Provide a timeline, Play/Pause/Reset, and a plain explanation of what changed. Separate observation, forecast and simulation.

**Motion:** User-controlled progression along the timeline. When reduced motion is enabled, show static comparison frames. No invented measurements or timestamps.

### Section 9 — Maps, exploration and marine insights

Retain a map preview and data panels. The public website may use illustration for visual explanation; the operational map must use a verified map source for geographic accuracy. Keep source names, timestamps, freshness and limitations visible when data is present.

Activity Terrain may appear only when meaningful, verified time-series data is available. Otherwise use an explicitly illustrative placeholder or omit the data chart.

### Section 10 — Roadmap, origin story and community impact

Keep all three content areas. Clearly label roadmap items as proposed until verified. The origin story should state grounded facts about purpose and motivation, not invent company history. Community impact content must use genuine approved stories or be labelled as illustration.

**Motion:** Editorial photo reveal may be used once when a story enters view. Avoid parallax that makes text hard to read or causes nausea.

### Section 11 — FAQ

Short, everyday questions with concise answers. Include evidence sources, uncertainty, supported languages, voice, how validation works and which features are available today.

**Motion:** A brief expand/collapse. Buttons must announce expanded/collapsed state and support keyboard use. An optional “Listen to answer” control may be provided where text-to-speech works.

### Section 12 — Closing call to action and footer

Close with a calm, supplied ocean illustration and one clear next step. Footer links should include platform navigation, use cases, evidence, accessibility, privacy, terms and contact only when the pages exist and the links are verified. Use supplied wave-border artwork as a restrained separator.

## 6. Page-to-page user journeys

| Journey | Sequence | Key design behaviour |
|---|---|---|
| First-time visitor | URL entry → intro animation → homepage hero → Ask or Explore | Intro can be skipped; hero becomes usable within about 2 seconds. |
| Fisher / community user | Home → choose website/voice language → Ask → hear or read answer → optionally view map | One main action, simple copy, optional voice, no forced login unless required by product policy. |
| User exploring a topic | Home → use-case card → simple story → relevant map or evidence explanation | Card clearly says what happens after selection. |
| Evidence review | Answer → “Why this answer?” → sources and status → limitations | Explain freshness, uncertainty and missing evidence plainly. |
| Researcher / operator | Workspace → stakeholder view → layers → scenario replay → decision trace/source lineage | Advanced controls can be expanded; detailed metadata remains available. |
| Account user | Login → workspace → account menu → settings / saved insights / uploads | Only show functional features. |
| Language change | Any page → website language control → translated UI | Keep the user on the same page and preserve input where feasible. |
| Voice-language change | Ask → spoken-language control → verified voice option → speak/listen | Clearly explain unavailable options and permission errors. |

## 7. Board 2 — Marine intelligence workspace

The workspace retains the broad layout from the approved Dashboard board: left navigation and stakeholder modes, central map, right-hand evidence/Ask panels, and a lower strip for decision trace, source lineage and release policy.

### 7.1 General view first

The default view should not expose every technical control immediately. It should show:
- a map or clear visual representation of the selected area;
- simple location/search input;
- a clear Layers control;
- a visible Ask Sagarvani entry point;
- a concise evidence summary with honest status labels;
- an alternative list or summary for users who find maps difficult.

### 7.2 Expert view

Researchers and operators can expand to see:
- detailed evidence layers and source metadata;
- decision trace;
- source lineage and timestamps;
- scenario replay;
- Activity Terrain, if real data exists;
- validation, recovery and release-policy detail.

Stakeholder switching should change which information is prioritised, not only change the selected tab colour. Preserve a user's location and map context when feasible.

### 7.3 Map controls

Use plain labels: Ocean currents; Wind and waves; Weather; Satellite imagery; Coastline; Fishing activity. Show a layer only when the source is implemented or clearly label it as demo/illustrative. Each layer has an on/off state, short explanation and status.

A selected marker opens a bottom sheet on mobile or side panel on desktop. Show what it means, timestamp, source, freshness, limitation and a “Listen” option if voice output is available.

Never draw decorative vessel paths in a way that could be mistaken for real-time vessel tracking. Use the supplied `Three Detailed Boats from Above.png` only as an illustrative style reference or decorative marker artwork, not as a location dataset.

### 7.4 Contextual marking menu

Actions may include Info, Layers, Measure, Mark area and Add note. The radial menu is an optional shortcut; the same actions must be discoverable through an ordinary labelled menu. On touchscreens, use a visible button and do not rely on right-click or long-press alone.

### 7.5 Active evidence panel

Each item needs a source name and meaningful state such as Verified, Needs checking, Conflicting, Unavailable or Illustrative. “Fresh” requires an actual timestamp/freshness rule and backend state. A colour dot alone is not a status.

### 7.6 Wind → waves and Activity Terrain

Wind may be represented by the reusable wave component to make a technical field easier to understand. The waves are a visual encoding, not a replacement for units or values. Activity Terrain is a data visualisation only when a real, meaningful series exists; otherwise label it as illustrative or omit the graph.

### 7.7 Ask Sagarvani panel

Include text input, optional microphone input, suggested questions and, if supported, attachment. The returned answer starts with a short summary, then gives the user controls to listen, show on map, explain more simply and inspect the sources.

Do not replace backend errors with canned marine recommendations. If the request fails, show an honest message and a useful next step.

### 7.8 Decision trace, source lineage and release policy

These lower cards explain:
- Decision trace: what was checked and what happened.
- Source lineage: where each source came from, relevant timestamps and validation status.
- Release policy: why an answer can be released, limited or withheld.

Keep this content inspectable, but allow it to collapse for general users.

## 8. Ask Sagarvani — text and voice states

### Initial state

Use a large, obvious choice: tap microphone to speak, or tap text input to type. Include three or four suggested questions. Never require a user to understand prompt engineering.

### Listening state

- Request microphone permission only after the user initiates voice.
- Show “Listening” while audio capture is active.
- Display a live waveform only if it is derived from actual input levels; otherwise use a static microphone animation.
- Provide an explicit Stop/Cancel action.
- Show the transcript for review/editing where the speech service supports it.
- If permission is denied, explain how to enable it and leave text input available.

### Thinking state

Show informative progress text. Suggested steps are Understanding your question → Checking available information → Comparing evidence → Preparing an answer. Only mark a step complete when the backend confirms it. If stage events are not exposed, use a single truthful message such as “Checking the available information…” rather than pretending to know the internal stage.

### Answer state

Show one short answer first. Provide “Listen,” “Show on map,” “Explain more simply” and “Why this answer?” where the underlying features are available. Keep source names, time, limitations and uncertainty accessible.

### Insufficient evidence / failure state

Explain what is missing and suggest a practical next action such as changing the location, specifying a time, retrying later or reviewing available sources. Do not fabricate a confident answer to hide a failure.

## 9. Authentication, account menu, avatar and file upload

### Login

Use a calm, simple form with clear labels and readable errors. Display only authentication methods implemented by the application. If login is not required to ask a general question, avoid forcing it before the first useful interaction unless the product's security model requires it.

### Account menu

Show working actions only: profile, settings, saved insights, uploads, voice preferences, help and sign out. Avoid dead links and empty sections.

### Avatar picker

Use the user's `Vintage Japanese Maritime Emblem Collection.png` as a source reference for available marine emblems. If the image sheet is used, crop individual emblems carefully and make the selected avatar visible with more than colour alone. Do not substitute unrelated generated human faces.

### File upload

Expose upload only after backend support is verified. Requirements: accepted types and sizes, clear browse/drag-drop, permissions, validation, actual progress or indeterminate progress, cancel where supported, success confirmed by server, and understandable failure/retry states. Never show fake progress or claim the file was processed before server confirmation.

## 10. Animation and motion catalogue

| Animation | Where | Desired feeling / action | Guardrails |
|---|---|---|---|
| **Opening: A light across the ocean** | Fresh URL entry before homepage | Waves sweep in, ship arrives, lamp flashes once, light reveals hero | 1.6–2.0 sec target; Skip intro; reduced-motion bypass; hero fallback; no audio; no repeated flash |
| Ocean-current ambience | Hero / selected section | Slow, subtle living ocean surface | Decorative only; no text obstruction; static fallback |
| Wave section transition | Between major sections | A current gently connects one chapter to the next | 300–600 ms; use supplied wave art or SVG masks; never block scrolling |
| Lenis scroll | Site-wide | Smooth but responsive movement | One root instance; preserve anchor/focus behaviour; disable or simplify when reduced motion requested |
| Story/photo reveal | Community story / editorial grid | Focus is drawn to the next story | One small fade/translate; no forced autoplay; keyboard alternatives |
| Journey boat motion | Intelligence Voyage | The boat moves between meaningful stages | Advance only with user scroll/action or real state; static alternative |
| Map pin emphasis | Selected marker/area | Gentle orientation cue | One short ripple; never suggest live tracking by animation alone |
| Map layer change | Workspace | Clear state change | Short crossfade; actual layer availability reflected |
| Marking menu | Workspace | Quick contextual action | Brief reveal; ordinary accessible menu alternative required |
| AI text loading | Ask | Reassuring progress | Backend-truthful stage display; text equivalent always present |
| Boat loader | Long-running actual request | Small vessel gently bobs over a wave | Only while real work is pending; no false completion; reduced-motion fallback |
| Voice listening | Microphone state | Responsive and clear | Waveform tied to actual input where possible; labels for Listening/Processing/Stopped |
| Answer reveal | Answer card | The result appears without drama | Short fade/slide; cautions and uncertainty are immediately readable |
| File upload progress | Upload | Clear confirmation of actual progress | Driven by transfer/server events; no timer pretending to be percent complete |
| Scenario replay | Compare conditions | User-controlled exploration through time | Play/Pause/Reset; labels distinguish history, forecast and scenario |
| FAQ accordion | FAQ | Familiar expansion | Keyboard and screen reader state support |
| Sticky header | Scroll state | Compact and unobtrusive | No major layout jump; language control remains visible |

### Motion timing guidance

These are starting targets for testing, not hard-coded requirements:
- Micro-feedback: 120–200 ms.
- Standard panel/menu transitions: 180–300 ms.
- Section/story reveals: 300–600 ms.
- Opening animation: 1.6–2.0 seconds, hard ceiling near 2.2 seconds.

Avoid stacking Lenis, GSAP, Motion and other animation systems on the same element. Review existing imports and use the simplest existing tool for each job. Never animate every marker, every card and every wave at once.

## 11. Accessibility and inclusive UX requirements

- Use plain, short sentences; define technical terms at first use.
- Pair icons with labels during onboarding and wherever ambiguity is possible.
- Keep one main action prominent per view.
- Make voice optional; typing and tapping must remain viable alternatives.
- Allow answers and essential instructions to be read aloud where supported.
- Provide list/text alternatives to map-based information.
- Maintain visible keyboard focus and logical tab order.
- Make all menus accessible by keyboard, touch and screen readers.
- Use text + icon + status, not colour alone.
- Respect system `prefers-reduced-motion`; also provide an easy Skip intro option.
- Do not autoplay sound or require exact swipe gestures.
- Support enlarged text and narrow mobile layouts without hiding controls.
- Keep error messages specific and actionable.
- Ensure translated labels fit layouts and are reviewed by fluent speakers.
- Do not assume a specific literacy level from the user's role; make the interface universally understandable.
- Announce asynchronous updates to assistive technology without repeating noisy status messages.

## 12. User-provided artwork manifest — 46 images

All filenames below are from the user's `DESIGN GENERATED(1).zip` under the `DESIGN GENERATED/` folder. These are proposed placements based on filename and visual review of the supplied contact sheet. The frontend team should preserve filenames in the source asset directory and confirm final crops against the full-resolution files. The generated map artwork is illustrative, not a geographically accurate or live-data layer.

| Supplied filename | Proposed use |
|---|---|
| `Coastal Waves_ Calm to Storm.png` | Scenario replay; compare calm, changing and stormy sea illustrations |
| `Compass Currents_ A Cartographic Seascape.png` | Connected Ocean Ecosystem; evidence-to-decision illustration |
| `Flowing Indigo Waves on Cream Paper.png` | Opening wave layer; light section background |
| `From Map Fragments to Lighthouse Bay.png` | Before → Sagarvani → Outcome; evidence journey |
| `Hokusai-Inspired Stormy Fishing Waters.png` | Weather / difficult-condition story; use sparingly |
| `Indigo Ukiyo-e Ocean Wave Border.png` | Footer edge or section divider |
| `Indigo Ukiyo-e Wave on Ivory Paper.png` | Light hero/section illustration or decorative crop |
| `Indigo Waves on Parchment.png` | Low-detail background texture |
| `Japanese Nautical Woodblock Icon Sheet.png` | Source reference for visual icon language; crop deliberately or redraw as actual accessible UI icons |
| `Maritime Chronicles in Four Panels.png` | Community stories / stakeholder section |
| `Minimalist Indigo Ukiyo-e Seascape.png` | Opening splash background if crop and contrast fit |
| `Panoramic Ukiyo-e Wave Seascape.png` | Homepage hero or chapter banner |
| `Stormy Indigo Waves Under Swirling Skies.png` | Weather/scenario state, clearly contextualized |
| `Sunlit Ukiyo-e Coastal Archipelago.png` | Light public-facing hero, community or closing section |
| `Three Detailed Boats from Above.png` | Illustrative vessel reference for map-marker styling; never real tracking data |
| `Topographic Ocean Wave Engraving.png` | Activity Terrain art reference / data visual background, only with clear illustrative label when no data exists |
| `Traditional Ukiyo-e Fishing Boat at Sea.png` | Fishers use case or vessel vignette |
| `Tranquil Ukiyo-e Sea Ripples.png` | Calm loading/empty-state background or subtle wave effect |
| `Turbulent Indigo Ukiyo-e Waves.png` | Scenario comparison or turbulent-condition illustration |
| `Ukiyo-e Archipelago Sea Chart.png` | Decorative coastal map artwork, labelled illustrative |
| `Ukiyo-e Boat Amidst Curling Waves.png` | Intelligence Voyage or small story image |
| `Ukiyo-e Boat Amidst Stormy Waves.png` | Recovery/uncertainty story illustration; never imply actual unsafe conditions |
| `Ukiyo-e Coastal Fishing Village Panorama-2.png` | Homepage hero or fishing-community story |
| `Ukiyo-e Coastal Seascape Vignettes.png` | Use-case/story cards |
| `Ukiyo-e Coastal Village with Satellite Arcs.png` | Connected Ocean Ecosystem; satellite concept illustration |
| `Ukiyo-e Coastal Vista with Satellite.png` | Satellite/observation explanation |
| `Ukiyo-e Currents Around Island Shores.png` | Current-field and map illustration |
| `Ukiyo-e Currents in Indigo and Gold.png` | Current pattern/ornamental accent |
| `Ukiyo-e Fishing Boat Wave Cycle.png` | Boat-loader animation reference sheet; inspect/crop one or more cells and animate in code |
| `Ukiyo-e Fishing Boat on Indigo Waves.png` | Darker hero or fishers story |
| `Ukiyo-e Fishing Village at Dawn-1.png` | Fishers use case and harbour story |
| `Ukiyo-e Indigo Wave Border.png` | Alternate wave-border treatment; compare before selecting one border asset |
| `Ukiyo-e Lighthouse Among Stormy Waves.png` | Lighthouse journey / uncertainty narrative |
| `Ukiyo-e Maritime Research Voyage.png` | Researcher use case |
| `Ukiyo-e Ocean Currents and Coastal Isles.png` | Current fields / map section |
| `Ukiyo-e Ocean Layers Map.png` | Evidence layers explanation |
| `Ukiyo-e Ocean Waves and Distant Isles.png` | Light hero, section banner or closing scene |
| `Ukiyo-e Oceanographic Archipelago Map.png` | Connected ecosystem / coastal-map illustration |
| `Ukiyo-e Research Ship in Stormy Seas.png` | Marine research use case; use only in a fitting context |
| `Ukiyo-e Seascape Beneath Billowing Clouds.png` | Opening atmosphere or dark/light transition backdrop |
| `Ukiyo-e Seascape with Sailboat.png` | Lighter hero or section illustration |
| `Ukiyo-e Sunrise Fishing Harbour.png` | Fishers story and community impact |
| `Ukiyo-e Tidal Islands and Whirlpools.png` | Current-field/map illustration |
| `Ukiyo-e Underwater Reef and Fish School.png` | Marine ecosystem / fishery context illustration |
| `Ukiyo-e Voyage to the Lighthouse.png` | Intelligence Voyage and closing journey |
| `Vintage Japanese Maritime Emblem Collection.png` | Avatar picker / emblem reference; crop individual emblems if suitable |

### Asset handling rules

- Keep originals untouched in a versioned project asset folder; create derivatives only by crop, resize, compression or format conversion for performance.
- Generate an asset manifest with original filename, chosen page/component, crop/position, alt text, intended use and “illustrative only” flag.
- Do not place labels or critical text inside raster art; use HTML text for translation and accessibility.
- Use actual application map tiles for real geographic work. Supplied map paintings are decorative or explanatory only.
- The boat-cycle sheet has eight panels arranged as four columns by two rows. The boat poses are similar, so a clean single-frame boat with CSS transform/bobbing may look better than a frame-by-frame sprite; verify at actual display size.
- For the opening lamp, use a subtle CSS/SVG beam over the supplied vessel image. This is a frontend effect, not newly generated art.
- Lazy-load below-the-fold assets and reserve image dimensions to avoid layout shifts.

## 13. Backend-dependent behaviour and truthfulness gates

The frontend design must be ready to represent these states, but a component can be enabled in production only after verification.

| Capability | What must be verified before enabling the production UI |
|---|---|
| Login/account | Supported auth methods, session persistence, profile/settings actions and sign-out behaviour |
| Website language | Completed translations for navigation, copy, forms, errors and accessibility labels; QA with fluent speakers |
| Voice input/output | Speech-to-text and text-to-speech provider, supported language/dialect list, permissions, cancellation, timeout and failure behaviour |
| AI progress | Real pipeline status events or an honest generic waiting state; no fabricated progress steps |
| Upload | Endpoint, accepted file types/size, auth, storage/processing, status events, cancellation and failure response |
| Ocean/map layers | Actual map provider/layers, timestamps, attribution, availability and update cadence |
| Fisheries/PFZ | Current source and expiry/freshness rules; never re-use expired entries as current |
| Activity Terrain | Real dataset, units, time window and empty/stale-data rules |
| Scenario replay | Confirmed source data or a clearly labelled simulation/fixture, time axis and play/pause semantics |
| Alerts/notifications | Real event source, permissions, delivery status and accessible text explanation |
| Evidence lineage | Source identifier, timestamp, validation result, conflict/missing-data semantics and limitations |
| Release/withhold | Explicit rule/state surfaced to UI; uncertain answer must remain an allowed outcome |

Never use frontend-only timers or hard-coded fixtures to make the production interface appear connected. Demo scenarios are acceptable for presentation if clearly labelled “Illustrative demo / not live.”

## 14. Technical guardrails for implementation

- Audit the existing frontend before adding packages. Reuse established dependencies where appropriate.
- Lenis is the selected site-wide scroll system; use one root instance and preserve native anchor, keyboard and reduced-motion behaviour.
- Avoid overlapping animation libraries on the same element. Select the simplest existing solution after reviewing actual imports.
- Use CSS transform/opacity for the opening sequence and micro-interactions where possible.
- Preload only the opening art; lazy-load later story illustrations.
- Avoid large video or shader backgrounds unless measured performance justifies them.
- Keep map interactions independent from decorative scroll transitions.
- Reserve layout space for images and async content to prevent shifts.
- Preserve server-rendered or immediately available text so that the intro never hides a blank/unusable page if a script fails.
- All forms, buttons, dropdowns, file controls and menus need real behaviour and visible success/failure states.

## 15. Acceptance checklist before implementation approval

### Visual and navigation
- [ ] The three approved board structures are retained; all major website and workspace sections remain represented.
- [ ] Only the user's supplied/generated artwork is used; there are no substitute generated images.
- [ ] Warm ivory, indigo, lapis, azure and icy blue are balanced; the site is not uniformly dark.
- [ ] The website language control is visible in the upper header and remains available in compact/mobile navigation.
- [ ] Spoken language/dialect is a separate control and lists only verified options.

### Opening animation
- [ ] Waves enter from one side and the ship enters from the opposite side.
- [ ] The ship lamp flashes one time with a soft, non-strobing beam.
- [ ] The light becomes the transition into the actual homepage hero.
- [ ] Target duration is approximately 1.6–2.0 seconds, no longer than about 2.2 seconds in normal conditions.
- [ ] Skip intro is visible, keyboard-accessible and functional.
- [ ] Reduced-motion mode bypasses the motion and reveals the hero.
- [ ] No autoplay audio; direct fallback to the hero if assets or JavaScript fail.
- [ ] The intro does not replay during internal navigation.

### Inclusive UX and motion
- [ ] Primary actions use plain language and are obvious.
- [ ] Voice, typing, tapping and read-aloud options work where supported.
- [ ] Maps have a list/text alternative.
- [ ] Motion never carries a critical status by itself.
- [ ] Keyboard focus, screen-reader states and larger text are tested.
- [ ] Mobile layout does not depend on hover or precise gestures.

### Data and backend integrity
- [ ] No fake loading progress, source status, upload completion, live tracking or fabricated data.
- [ ] Every illustrative map/artwork is labelled when it could be mistaken for live data.
- [ ] Backend dependencies in Section 13 are verified before enabling respective controls.
- [ ] Stale, conflicting, insufficient and unavailable states are tested.

## 16. Next-stage handoff documents (not included in this review draft)

After the user reviews and approves this specification, prepare the separate working documents for implementation:

1. **Frontend Implementation Brief** — page breakdown, layout rules, routes/sections, asset mapping, responsive behaviour and component reuse.
2. **Animation & Interaction Build Sheet** — intro sequence, timings, states, skip/reduced-motion/fallback behaviour and page transitions.
3. **Backend Capability Verification Matrix** — authentication, voice/language, upload, map/data, evidence status, progress events and release/withhold integration.
4. **Frontend–Backend UI Contract** — state/event fields the UI needs, failure semantics, loading semantics and truthful status requirements; based on actual repo/API inspection, not invented endpoints.
5. **Asset Manifest** — exact supplied filenames, target usage, crop notes, alt text, optimisation and illustrative/live distinction.
6. **UX QA and Release Checklist** — accessibility, language, responsive, animation, stale/conflicting evidence, errors and end-to-end acceptance tests.

Do not begin implementation or create fake backend contracts from this proposal alone. Review and approval come first; then inspect the actual repository and backend to turn the design decisions into concrete, verifiable handoff documents.

---

**Review summary:** The experience begins with a brief wave-and-ship welcome, then reveals the complete public website; the workspace stays powerful but progressively reveals complexity; voice and language are prominent but optional; animations feel calm and purposeful; and all visuals come from the user's supplied artwork pack.
