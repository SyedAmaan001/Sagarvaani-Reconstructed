# Sagarvani Reconstructed

Sagarvani is a conversational marine decision-intelligence prototype intended to turn fragmented marine, weather and geospatial information into context-specific, evidence-backed summaries—and to expose when evidence is missing, stale, incomparable or conflicting.

> **Prototype boundary:** This is not certified marine navigation or safety advice. Do not use it to make real-world departure, evacuation or vessel-operation decisions.

## Workspace

- `AGENTS.md` — persistent rules for Antigravity.
- `legacy/` — manually copy the original **Sagarvani Complete** project here. Preserve it; do not treat it as the new working tree.
- `backend/` — reconstructed canonical backend.
- `data/` — dataset manifest and intentionally labelled fixtures/replay material.
- `tests/` — offline unit/integration tests and safe mocked fixtures.
- `docs/` — the five project documents listed below.
- `docs/references/` — optional background reports and prior research; these do not override the seven core files. Keep outdated versions clearly labelled as archived.

## Read order

1. `docs/MASTER_BLUEPRINT.md` — product and architecture intent.
2. `docs/BUILD_PLAYBOOK.md` — phase-by-phase implementation order and acceptance gates.
3. `docs/DATA_AND_QUALITY.md` — credentials, datasets, evidence contract, tests and safety requirements.
4. `docs/ENGINEERING_LOGBOOK.md` — actual implementation decisions, workflow, execution, status and blockers.
5. `docs/HACKATHON_GUIDE.md` — concise explanation, demo story and judge preparation.

## Build status

**Status: reconstruction not yet verified.** Antigravity must populate the engineering log from the actual workspace and must not assume earlier audit statements still hold. Do not copy secrets or virtual environments from the legacy project.

## Setup and commands

The exact install/run commands must be added by Antigravity after it confirms the selected backend layout and dependency manager. Prefer `uv` for Python dependency management. Never guess an import path or declare a command tested before running it.

## Supporting materials

Only copy selected references into `docs/references/` when useful: the latest verification/audit report, post-audit correction note, concept decision record v2, the original SIH submission PDF and the uploaded resource register. Mark them `REFERENCE ONLY — NOT THE CURRENT SOURCE OF TRUTH` where appropriate. The old document pack and superseded concept record v1 are not needed for normal work. The active seven files listed here take precedence.

## Sources and attribution

All live observations/forecasts must identify the source, parameter, unit, relevant time and retrieval time. Historical files and synthetic test fixtures must be labelled clearly and never presented as live conditions.
