# ▲ Trivium — vibe code without getting dumber

The learning layer for AI-assisted coding. Trivium converts your coding activity (agent chats,
imported sessions, decisions, bug-fixes) into durable personal knowledge through on-demand
**Learn** actions, **spaced & interleaved review**, and an evidence-based **Knowledge Profile**.

Built from `PRD-v1.md`, `full-technical-document-v1.md` and `developer-implementation-plan-v1.md`
(kept in the repo root as source-of-truth docs).

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI · SQLAlchemy 2 · Alembic · PyJWT · bcrypt · slowapi |
| Database | PostgreSQL (production) / SQLite (local dev & tests) |
| LLM | Provider abstraction: `mock` (offline, default) · OpenAI · Groq · Anthropic · Sarvam |
| Frontend | React 19 · TypeScript · Vite · Tailwind CSS 4 · react-router 7 · Mermaid |
| Deploy | Render (API + Postgres via `render.yaml`) · Vercel (SPA via `frontend/vercel.json`) |

## Quick start (local)

**Backend** — Python 3.12+
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements-dev.txt
alembic upgrade head                                 # create schema (SQLite by default)
python -m app.db.seed                                # optional: demo user with rich data
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs · Demo login: `demo@trivium.dev` / `Demo1234!`

**Frontend** — Node 20+
```bash
cd frontend
npm install
npm run dev                                          # http://localhost:5173
```

No LLM API key is needed: the default `mock` provider generates deterministic, content-aware
extractions/artifacts so the whole product works offline. Set `LLM_PROVIDER` + `LLM_API_KEY`
in `backend/.env` to use a real model.

## Tests

```bash
cd backend && python -m pytest tests -q              # 45 tests: functional + security
cd frontend && npm run build                         # type-check + production build
# browser e2e (needs backend on :8000 + `npx vite preview` on :4173):
node e2e/part1.mjs                                   # signup -> import -> extract -> learn
# simulate time passing, then part 2:
(backend venv) python e2e/make_due.py <email-from-e2e-state.json>
node e2e/part2.mjs                                   # review -> profile -> metrics -> logout
```

## Deployment

**Backend → Render**: push to GitHub, then Render → *New → Blueprint* → select the repo.
`render.yaml` provisions the API + free Postgres, runs migrations on boot, generates
`SECRET_KEY`. After the frontend is live, update the `CORS_ORIGINS` env var to the Vercel URL.

**Frontend → Vercel**: import the repo, set **Root Directory = `frontend`** (framework: Vite).
Add env var `VITE_API_URL=https://<your-service>.onrender.com`. `vercel.json` handles SPA
rewrites, security headers and asset caching.

## Architecture

```
backend/app/
  core/        config, JWT + bcrypt security, rate limiter
  db/          engine, portable types (SQLite<->Postgres), seed script
  models/      15 tables (14 from the schema doc + refresh_tokens)
  schemas/     Pydantic request/response validation
  llm/         provider abstraction (mock | openai | groq | anthropic | sarvam)
  services/    extraction, format selection, artifacts (Learn), SM-2 review,
               profile (skill.md), metrics (3 layers)
  api/routes/  auth, projects, sessions, agent, learn, reviews, profile, metrics
frontend/src/
  lib/         typed API client with single-flight token refresh
  context/     auth state
  components/  UI kit, app shell, ArtifactPlayer (recall flow), Mermaid renderer
  pages/       landing, auth, dashboard, projects, sessions(+import/detail),
               agent chat, learn, review, profile, metrics, settings
```

### Learning-science guarantees (enforced in code, verified by tests)

- **Testing effect** — artifacts are open-recall by default; the UI blocks "Reveal" until an attempt is written; no multiple choice.
- **Diffuse-mode delay** — a unit's first review is gated by `first_review_at` (default 12 h); early submissions get HTTP 409.
- **Spacing** — SM-2 adaptive intervals per unit; the same unit can never be reviewed twice within `MIN_REVIEW_GAP_HOURS`.
- **Interleaving** — review sessions round-robin across ≥2 projects when available.
- **No illusions of competence** — viewing/completing an artifact never touches mastery; only graded recall submissions write to `review_state`.
- **Evidence over self-report** — the Knowledge Profile is recomputed from `review_state` + `review_history`; it cannot be set by hand.
- **Auditability** — every format-selection decision is logged to `format_decisions` with rule version and triggering signal.
- **Fidelity honesty** — `source_fidelity` (`native`/`wrapped`) flows from session → knowledge unit → profile and is surfaced in the UI.

### Security

- JWT access tokens (30 min) + opaque refresh tokens stored **hashed** server-side with rotation
  and reuse-rejection; logout and password-change revoke them.
- bcrypt password hashing; password strength rules; identical error for unknown email vs wrong
  password (no account enumeration).
- Every resource query is ownership-scoped; foreign resources return **404**, never 403.
- Rate limiting on auth and LLM endpoints (slowapi), CORS allowlist (no wildcard),
  security headers middleware, API docs disabled in production.
- Payload size caps and strict enum validation on all inputs.

### Deviations from the tech doc (v1 pragmatics, documented)

- **ChromaDB → deferred**: recurrence linking uses normalized-title matching (the doc's own
  suggested starting point); pgvector on Render Postgres is the upgrade path.
- **Redis/arq → deferred**: extraction runs via FastAPI `BackgroundTasks` behind a plain
  function boundary (`run_extraction`) so an arq worker can be swapped in without refactoring.
- **LiteLLM → thin built-in adapter**: same env-driven provider switching, without the heavy
  dependency; the `LLMProvider` interface accepts a LiteLLM-backed implementation later.
- **Desktop (Tauri) & Socket.IO** — out of v1 web-slice scope per the phased plan.
