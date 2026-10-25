# Sagarvani — Evidence-Grounded Marine Intelligence

> **Status:** Hackathon prototype in active development  
> **Purpose:** Explore how marine and weather evidence can be gathered, validated, traced, and used for transparent decision support.

**Safety notice:** Sagarvani is not a certified maritime safety system. Never use prototype outputs as the sole basis for real-world navigation, fishing, departure, or emergency decisions.

## Overview

Sagarvani is an experimental marine-intelligence platform designed around evidence gathering, validation, provenance, bounded recovery, and deterministic release-policy checks.

The system aims to make uncertainty visible. When evidence is missing, conflicting, stale, or not evaluable, it should abstain rather than invent a confident recommendation.

The project combines a Next.js frontend with a FastAPI backend.

## Key objectives

- Gather available marine and weather evidence.
- Validate evidence quality, provenance, and usability.
- Use bounded recovery when a validation step fails.
- Prevent retries or generative models from bypassing release-policy checks.
- Return understandable outcomes when evidence is insufficient.
- Build toward transparent marine decision support for fishing communities, researchers, coastal authorities, and maritime operators.

## Technology stack

### Frontend
- Next.js App Router
- React and TypeScript
- Tailwind CSS
- Framer Motion
- Lucide icons
- Responsive landing page with supplied maritime artwork

### Backend
- FastAPI
- Pydantic v2
- Python dependency management with `uv`
- Marine and weather gateway adapters
- Evidence catalog and local artifact handling
- SQLite-backed prototype persistence
- Guarded workflow/state-machine logic
- DAG-style task harness, validation, and bounded recovery
- Deterministic release-policy checks

## System workflow

```text
User Request
     |
     v
Request Validation
     |
     v
Evidence Gathering
     |
     v
Evidence Validation and Provenance
     |
     v
Bounded Recovery (if needed)
     |
     v
Deterministic Release-Policy Gate
     |
     +---- Evidence sufficient/evaluable --> Bounded Result
     |
     +---- Evidence missing/conflicting ---> Abstain / Block
```

A generative model, if enabled in a future configuration, must not override deterministic policy decisions.

## Current implementation status

The following reflects the latest available project handoff. Verify the current GitHub branch and rerun tests before treating these as freshly confirmed.

| Feature | Status |
|---|---|
| Public landing page and responsive sections | Implemented in prototype |
| Intro animation with skip and reduced-motion handling | Implemented |
| Supplied maritime artwork | Integrated into selected sections |
| Illustrative scenarios | Implemented; not live marine conditions |
| Marine/weather adapters | Prototype adapters implemented |
| Authentication | Not available in the current prototype |
| Dedicated role-based operational dashboard | Not yet verified as implemented |
| Voice advisory | Not integrated |
| Verified live GIS and MPA boundaries | Not available as verified operational features |
| `GET /health` | Reported in the latest backend audit |
| `POST /api/orca/query` | Reported in the latest backend audit |
| Laya inference | Disabled by default; actual inference not verified |
| External alert dispatch | Disabled |

**Important:** Implemented adapters do not imply that all data sources are authoritative, current, or sufficient for a real-world decision. Static artwork, test fixtures, and illustrative scenarios must never be represented as live telemetry or live warnings.

`NOT_EVALUABLE`, `INSUFFICIENT_EVIDENCE`, `ABSTAINED`, and `BLOCKED` are valid system outcomes.

## Repository structure

The precise structure may vary by branch. Verify paths in the actual repository.

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── MASTER_BLUEPRINT.md
│   ├── BUILD_PLAYBOOK.md
│   ├── DATA_AND_QUALITY.md
│   ├── ENGINEERING_LOGBOOK.md
│   ├── HACKATHON_GUIDE.md
│   └── references/
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   └── components/
│   └── public/
│       └── artwork/
└── backend/
    ├── pyproject.toml
    └── ... FastAPI application and tests
```

## Prerequisites

Install the tools required by the current project configuration:

- Git
- Node.js compatible with the frontend's Next.js version
- npm
- Python version specified by the backend project
- `uv`

Check your installed versions:

```bash
git --version
node --version
npm --version
python3 --version
uv --version
```

## Running locally

### 1. Start the backend

The following commands assume the backend is in `backend/` and that its FastAPI entry point is `main.py` with an exported `app`. Confirm the actual entry point before running.

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

If the entry point is different, replace `main:app` with the actual Python module and ASGI application name.

Check the health endpoint:

```bash
curl -i http://127.0.0.1:8000/health
```

FastAPI documentation is commonly available at:

```text
http://127.0.0.1:8000/docs
```

This page is available only if the running application exposes the documentation route.

### 2. Start the frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Next.js, usually:

```text
http://localhost:3000
```

If the repository does not contain an npm lockfile, check the package-manager setup before choosing an installation command.

## API

The latest project handoff reports these routes:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/orca/query` | Submit a Sagarvani/ORCA query |

Check the current backend source and Pydantic models for the exact request and response schemas. The latest audit notes that `context_override.location` may be required to avoid an immediate abstention. Confirm the schema before constructing requests.

Do not assume that additional endpoints exist unless they are implemented in the current backend.

## Configuration and environment variables

Keep environment-specific configuration outside the source code.

### Frontend

Configure the backend API URL using the exact variable name expected by the frontend API client.

Example only:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The variable above is illustrative; verify the name used in the current source code.

### Backend

Configure CORS to allow only intended origins, including the local frontend origin and the actual production Netlify domain.

- Never commit `.env` files, API keys, access tokens, or production credentials.
- Keep secrets in the hosting provider's environment-variable settings.
- Avoid wildcard CORS with credentials.
- Keep optional model inference disabled unless the selected provider, credentials, model, and failure behavior have been configured and tested.

## Deployment

The proposed deployment arrangement is:

- **Frontend:** Netlify
- **Backend API:** Render Web Service

This is a deployment plan, not a claim that the application is already deployed.

### Deploy the frontend to Netlify

1. Push the repository to GitHub.
2. Import the repository into Netlify.
3. Set the base directory to `frontend/`.
4. Verify that Netlify detects and configures the Next.js/OpenNext adapter for the current project.
5. Set the frontend API URL to the deployed backend address using the variable name the code actually reads.
6. Deploy and test the landing page and API connectivity.

Do not force static export unless the application is confirmed to support it.

### Deploy the backend to Render

1. Select **New Web Service**.
2. Connect the GitHub repository.
3. Set the root directory to the directory containing the backend's `pyproject.toml`.
4. Configure the build command according to the repository's actual Python and `uv` setup.
5. Configure the start command using the real FastAPI ASGI entry point.
6. Bind the service to `0.0.0.0` and Render's `$PORT`.
7. Configure environment variables and explicit CORS origins.
8. Deploy and verify `/health`.
9. Submit a valid request to `/api/orca/query`.

Example start command, **only if** the backend entry point is `main.py` and exports `app`:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```

Replace `main:app` if the actual application uses another entry point.

### Persistence considerations

The current project handoff describes SQLite and local artifact storage. Local files may be lost when deployed to a host with an ephemeral filesystem.

Before relying on persistent records:

- Configure supported persistent storage or migrate to managed database/object storage.
- Test database and artifact persistence across restarts and redeployments.
- Establish backup and recovery procedures.

### Deployment checklist

- [ ] Frontend loads over HTTPS.
- [ ] Backend health endpoint responds.
- [ ] Frontend points to the correct backend URL.
- [ ] CORS permits only intended origins.
- [ ] A valid query reaches the backend.
- [ ] Errors and insufficient-evidence outcomes are handled correctly.
- [ ] No secrets are committed or exposed in frontend bundles.
- [ ] Database and artifact persistence have been tested.

## Testing

Run the following checks from the relevant directories.

### Backend

```bash
cd backend
uv run pytest -v
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

Run `npm test` only if that script exists in the frontend's `package.json`.

Do not report tests as passing unless they were successfully run against the current code.

## Safety and data integrity

Sagarvani is an experimental prototype, not a certified navigation, weather-warning, or maritime safety product.

- Do not use it as the sole source for departure, route, fishing-ground, or emergency decisions.
- Confirm operational information with authoritative marine and weather authorities.
- Treat missing, stale, conflicting, or unevaluable evidence as uncertainty.
- Never present test fixtures, illustrative artwork, or example scenarios as live conditions.
- Do not allow an LLM or recovery loop to bypass the deterministic release-policy gate.
- Do not enable external alert dispatch without an explicitly reviewed and tested pathway.
- Do not commit credentials, local databases, generated artifacts, model weights, or private datasets.
- Check licensing and data-provider terms before redistributing assets or datasets.

## Roadmap

These are development directions, not guaranteed delivery dates.

- [ ] Verify and document exact API request/response schemas.
- [ ] Complete frontend-to-backend integration with real success and failure states.
- [ ] Build a dashboard backed only by actual API responses.
- [ ] Implement authentication and authorization before exposing user-specific data.
- [ ] Validate authoritative data sources, freshness, provenance, and geographic coverage.
- [ ] Define reviewable release and withholding policies.
- [ ] Choose durable database and artifact storage for deployment.
- [ ] Add deployment smoke tests, monitoring, and recovery procedures.
- [ ] Evaluate optional model inference using measured quality, latency, cost, and safety tests.

## Contributing

1. Create a focused branch.
2. Read `AGENTS.md` and the relevant documents in `docs/`.
3. Keep changes scoped and document architectural decisions in `docs/ENGINEERING_LOGBOOK.md` where appropriate.
4. Add or update tests for behavior changes.
5. Run the relevant backend and frontend checks.
6. Clearly distinguish implemented functionality from planned work, fixtures, and unverified integrations.

Avoid adding dependencies or integrations without checking the existing setup and documenting why they are needed.

## License

No license is declared in this README. Before redistributing this repository, add the license chosen by the project owner and confirm that bundled artwork, fonts, datasets, and third-party assets permit the intended use.
