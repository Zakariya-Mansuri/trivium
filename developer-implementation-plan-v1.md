# Developer Implementation Plan v1
## [Product Name TBD] — Phase-Wise Build Plan (Local Development Only)

This document sequences implementation into phases for local development. It assumes Concept Doc v1, PRD v1, Technical Architecture v1, Database Schema v1, and Website Feature Scope v1 as source-of-truth references — this plan tells you *what to build, in what order, and why*, not where to eventually host it.

All phases run entirely on local machines (Docker Compose for Postgres/Redis/ChromaDB, local FastAPI dev server, local React dev server). No deployment steps are included here by design.

---

## Phase 0 — Local Environment Setup

**Goal:** every developer can run the full stack locally with one command.

- Docker Compose file defining: Postgres, Redis, ChromaDB containers, matching Technical Architecture v1
- `.env.example` covering all required config: database URLs, LLM provider keys (via LiteLLM config), Redis URL
- FastAPI project scaffold with health-check endpoint (`/health`) as the first working thing to prove the stack boots
- React project scaffold (shared codebase intended for both web and Tauri desktop later, per Technical Architecture v1)
- Database migration tool set up (e.g., Alembic for FastAPI/SQLAlchemy) — schema changes must be scripted, never applied by hand, from day one

**Exit criteria:** a fresh clone + `docker compose up` + one migration command results in a running backend that responds on `/health`, with an empty database matching Database Schema v1.

---

## Phase 1 — Core Data Layer

**Goal:** the schema exists and is exercised by basic CRUD, before any AI logic is built on top of it.

- Implement all tables from Database Schema v1 as migrations: `users`, `projects`, `sessions`, `messages`, `knowledge_units`, `knowledge_unit_relations`, `format_decisions`, `learning_artifacts`, `learning_artifact_units`, `review_state`, `review_history`, `knowledge_profile_entries`, `metrics_events`, `independence_metrics`
- Basic auth (email/password or OAuth stub is fine locally) — needed early since almost every table is scoped by `user_id`
- CRUD endpoints for `users`, `projects`, `sessions` — enough to manually create test data via API calls or a seed script
- **Seed script**: generates realistic fake session/message data for local testing — this becomes essential for every later phase and for the investor demo data discussed earlier

**Exit criteria:** you can create a user, a project, a session with messages, and query them back — all data matches the schema exactly, indexes from Section 6 of Database Schema v1 are in place.

---

## Phase 2 — Native Coding Agent (Minimal)

**Goal:** a working, minimal version of the "own built-in agent" from PRD Section 5.1(1) — enough to generate real session data, not a full-featured coding assistant yet.

- FastAPI endpoint wrapping LiteLLM for chat completion, provider-configurable (start with one provider, e.g. Groq or OpenAI, to keep early testing cheap/fast)
- Every agent turn written to `messages` with `authored_by` correctly set (`ai` vs `user`) — **this field must be correct from the very first implementation**, since Layer 3 metrics depend entirely on it and cannot be reconstructed later
- Basic tool-use / code-diff capture — even simple (e.g., agent proposes a code block, developer marks it accepted/edited) is enough for Phase 2; full MCP tool integration can follow later
- Session start/end lifecycle wired to the `sessions` table

**Exit criteria:** a real, if basic, coding conversation with the agent produces correctly structured `sessions` + `messages` rows, with `authored_by` and `code_diff` populated accurately.

---

## Phase 3 — Extraction Engine

**Goal:** turn raw session data into `knowledge_units` — this is the product's core novel piece, per Technical Architecture v1 Section 2.2.

- Async worker using Redis + arq (per Technical Architecture v1) — build this async from the start, don't bolt it on later
- Extraction prompt pipeline via LiteLLM: classifies session chunks into `concept` / `decision` / `bug_fix` / `pattern`
- Writes to `knowledge_units`, with `embedding_ref` populated by writing the corresponding vector to ChromaDB
- `knowledge_unit_relations` population for recurring patterns (can start simple — exact/near-duplicate concept titles — before anything more sophisticated)
- Test against the Phase 1 seed data and Phase 2 real agent sessions, comparing extraction quality manually before moving on — **this phase deserves real manual review time**, since a weak extraction engine undermines every feature built after it

**Exit criteria:** running extraction against a test session reliably produces sensible, correctly-typed `knowledge_units`, inspectable and roughly accurate on manual review.

---

## Phase 4 — Format Selection + Learning Artifact Generation

**Goal:** implement the "Learn" action end-to-end for the smallest scope first (single chat), per PRD Section 6.1–6.3.

- Format Selection Engine: rule-based lookup table (content type → format) per Technical Architecture v1 Section 2.4, logging every decision to `format_decisions`
- Artifact generators:
  - Quiz/QA generator — recall-first by default (testing-effect requirement, PRD Section 7), self-explanation prompt as a distinct sub-type
  - Diagram generator — LLM outputs a diagram spec (Mermaid recommended per Technical Architecture v1 Section 2.5) rather than an image
- `learning_artifacts` + `learning_artifact_units` populated correctly, scoped to `scope_type: 'chat'` first
- API endpoint: trigger Learn on a given chat, return the generated artifact

**Exit criteria:** triggering "Learn" on a real seeded/agent-generated chat reliably produces a sensible quiz or diagram, correctly stored and retrievable.

---

## Phase 5 — Spaced Review Engine

**Goal:** implement scheduling, delivery, and the learning-science constraints from PRD Section 7.

- `review_state` scheduling logic — SM-2-style algorithm as the starting point (Database Schema v1 Section 8 notes this as the v1 choice)
- Diffuse-mode delay: enforce `first_review_at` minimum delay before a concept's first review is ever surfaced
- Interleaving: when building a review session, deliberately pull from ≥2 different `project_id`s where available, not pure due-date order
- `review_history` correctly logs every completed review attempt with `performance` and `day_offset`, since this is the raw data behind Layer 2 metrics later
- Local delivery: in-app review queue is sufficient for this phase — notifications/email can be stubbed or deferred, since they're a delivery-channel detail, not core logic

**Exit criteria:** a concept learned today is not offered for review immediately; when due, it appears in a review session interleaved with concepts from other projects; completing a review updates `review_state` correctly for next scheduling.

---

## Phase 6 — Knowledge Profile

**Goal:** implement the skill.md-style output, per PRD Section 6.6.

- `knowledge_profile_entries` computed from `review_state` + `review_history` (mastery status, retention trend)
- Markdown export endpoint, respecting `visibility` flags at generation time (per Technical Architecture v1 Section 2.7 — privacy must be enforced at generation, not just display)
- Basic web view of the profile (even minimal styling is fine locally — this is a data-correctness phase, not a design phase)

**Exit criteria:** a user with review history produces an accurate, readable Markdown Knowledge Profile; toggling a concept's visibility correctly includes/excludes it from export.

---

## Phase 7 — Metrics (Layer 1 → Layer 2)

**Goal:** implement engagement and retention metrics, per PRD Section 9.

- Layer 1: `metrics_events` logging on key actions (learn triggered, artifact completed, queue cleared) — straightforward event writes
- Layer 2: retention curve queries over `review_history` grouped by `day_offset` and `performance` — this is a read/aggregation layer on data you're already collecting from Phase 5, not new data collection
- Basic dashboard view (backend endpoints first; frontend chart display can follow once data is flowing correctly)

**Exit criteria:** after running enough seeded/manual review cycles locally, the retention curve query produces a sensible-looking curve (accuracy generally higher at low day-offsets, degrading or stabilizing at higher offsets depending on simulated review behavior).

**Note:** Layer 3 (AI-assist ratio, error-repeat rate) is intentionally deferred past this phase — per PRD Section 9's staging plan, it needs real usage volume to be meaningful, and its underlying data (`authored_by`, bug-fix tagging) is already being captured correctly since Phase 2/3, so it can be added later without a data-model change.

---

## Phase 8 — Web Frontend (Usable Slice)

**Goal:** build the React frontend implementing Website Feature Scope v1's product pages, running against the local backend.

- Session input (paste/import) page
- Learn view (trigger + display artifact)
- Review queue view
- Knowledge Profile view (read-only)
- Auth (signup/login) wired to Phase 1's auth
- All pages functional against `localhost` backend — no external hosting considerations at this phase

**Exit criteria:** a full local walkthrough — sign up, paste a session, trigger Learn, complete a review, view the Knowledge Profile — works end-to-end in the browser against the local stack.

---

## Phase 9 — Desktop Shell (Tauri) Integration

**Goal:** wrap the same React frontend in Tauri, add desktop-specific capabilities, still targeting local backend for now.

- Tauri shell pointed at the same React codebase from Phase 8
- Local file-watching / session-observer scaffolding for wrapped external tools (Claude Code, Cursor, etc.) — per Technical Architecture v1 Section 2.1, tagging ingested sessions `source_fidelity: 'wrapped'`
- Desktop-native notification hook-up for the review queue (local OS notifications, no external push service needed yet)

**Exit criteria:** the desktop app runs locally, shows the same product experience as the web app, and can successfully ingest a session from at least one external tool with correct fidelity tagging.

---

## Phase 10 — Cross-Feature Hardening

**Goal:** before considering this "done" locally, verify the features work *together*, not just individually.

- Full loop test: real coding session (native agent or wrapped tool) → extraction → Learn triggered at multiple scopes (message, chat, project) → review scheduled and completed → Knowledge Profile updates → metrics reflect the activity
- Verify `source_fidelity` flows correctly end-to-end and is visibly honest wherever surfaced (per Technical Architecture v1 Section 3.2)
- Verify privacy/visibility controls hold under export (re-check Phase 6's requirement)
- Manual review of Format Selection Engine decisions (`format_decisions` table) across a variety of real content — tune the rule table based on what's actually happening, not assumptions

**Exit criteria:** a full realistic local walkthrough, covering both the native agent and at least one wrapped tool, produces correct, coherent results across every feature discussed in this project — the point at which the product is meaningfully demo-ready (see investor demo plan) and ready for the eventual move to real infrastructure, which is intentionally out of scope for this document.

---

## Sequencing Notes

- Phases are mostly linear by dependency (you can't build the Format Selection Engine before Extraction produces knowledge units to classify), but Phase 7 (Metrics) can start in parallel with Phase 6 once Phase 5 is stable, since both read from the same review data.
- Phase 8 (Web Frontend) can begin earlier in parallel with Phases 4-7 if working solo/small-team allows context-switching — backend endpoints can be stubbed with fixed responses while frontend work proceeds, then wired to real logic as each phase completes.
- Given solo/small-team context, resist the temptation to jump to Phase 8/9 (visible UI) before Phases 1-3 are solid — the extraction quality and data model correctness are the actual hard, differentiating problems; UI polish is comparatively easy to redo later, extraction/data mistakes are expensive to unwind once real data exists on top of them.

---

*This document intentionally excludes deployment/hosting steps. Once local phases are complete and validated, refer to Deployment Guide v1/v2 and the Investor Demo & Major Cloud Plan for taking this to servers.*
