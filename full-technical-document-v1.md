# Full Technical Document v1
## [Product Name TBD] — Consolidated Technical Reference

This is the single consolidated technical document, combining architecture, stack, database schema, and implementation sequencing into one reference. It supersedes needing to cross-reference Technical Architecture v1, Database Schema v1, and Developer Implementation Plan v1 separately, though those remain valid detailed backups.

---

## 1. Product Summary (Technical Framing)

A platform (web first, then desktop) that sits alongside vibe coding — via its own built-in AI agent or by observing sessions from external tools — and converts coding activity into durable personal knowledge through on-demand, any-granularity "Learn" actions, spaced/interleaved review, and a persistent evidence-based Knowledge Profile. Coding correctness is a baseline requirement; the differentiator is measurable user learning and independence over time.

---

## 2. Core Design Principles (Technical Implications)

| Principle | Technical Implication |
|---|---|
| Opt-in, never forced | No blocking gates in the API/UI flow; "Learn" is always a pull action |
| Any span, any time | Data model must support querying by message / chat / project / time-range uniformly |
| Retrieval over exposure | Passive content must never write to mastery/review state — only recall-based completions do |
| Desirable difficulty | Scheduling logic enforces delay/interleaving even when it reduces short-term "ease" |
| Evidence over self-report | Knowledge Profile is always derived from stored performance data, never manually set |
| Domain-pluggable | Extraction schema/prompts are config, not hardcoded logic, even though only coding ships in v1 |

---

## 3. System Architecture

### 3.1 Components

1. **Coding Interface Layer** — native built-in agent + wrapped/observed external tools
2. **Extraction & Indexing Engine** — async pipeline tagging concepts/decisions/bug-fixes/patterns
3. **Learning Artifact Generator** — format-selected quiz/diagram/QA/synthesis generation
4. **Spaced Review Engine** — adaptive scheduling, interleaving, diffuse-mode delay
5. **Knowledge Profile Store** — evidence-based skill.md-style output, privacy-controlled
6. **Metrics & Analytics Layer** — 3-layer metrics (engagement / retention / independence)

### 3.2 Data Flow

```
Coding session (native agent OR wrapped tool)
   → raw session log captured (messages, diffs, authored_by tagged at generation time)
        ↓
Extraction Engine (async, Redis-queued)
   → tags knowledge units: concept / decision / bug_fix / pattern
   → writes structured record (Postgres) + embedding (ChromaDB)
        ↓
"Learn" triggered (user-initiated, any scope) OR scheduled review fires
        ↓
Format Selection Engine → picks artifact type, logs decision
        ↓
Artifact Generator (LLM via provider-abstraction layer) → quiz / diagram / QA / synthesis
        ↓
User completes via active recall
        ↓
Performance recorded → updates Spaced Review Engine + Knowledge Profile + Metrics Layer
```

### 3.3 Provider Abstraction (LLM Layer)

Modeled on OpenCode's architecture pattern — a client-server backend with a unified model-provider interface, rather than hardcoding any single LLM vendor.

- **LiteLLM** as the unified completion interface — one call signature across OpenAI, Groq, Sarvam, Anthropic, local/Ollama models
- Config-driven provider selection per user/session/task type, with fallback chains
- MCP (Model Context Protocol) support for tool access in the native agent, keeping it extensible without core rewrites

---

## 4. Full Stack

| Layer | Choice | Rationale |
|---|---|---|
| Desktop shell | Tauri (Rust core) | Lightweight background companion; far lower idle memory/bundle size than Electron, appropriate since this runs alongside other (often Electron-based) coding tools |
| Frontend (web + desktop) | React, shared codebase | One UI across web app and Tauri webview |
| Backend/API | FastAPI | Async-friendly, matches existing team expertise |
| LLM provider abstraction | LiteLLM | Unified multi-provider interface, OpenCode-style flexibility, Python-native |
| Structured data / knowledge graph | PostgreSQL | Relational by nature — concepts, timestamps, projects, mastery/spacing state |
| Semantic retrieval | ChromaDB | Concept clustering, cross-session/cross-project similarity search |
| Cache / async job queue | Redis + arq | Session state, background extraction jobs, review scheduling — lightweight, async-native, pairs naturally with FastAPI |
| Real-time delivery | Socket.IO | Review-queue/notification push updates |

---

## 5. Database Schema

All structured data lives in PostgreSQL. ChromaDB holds only embeddings, cross-referenced via `embedding_ref`.

### 5.1 Identity & Content
```sql
users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  notification_prefs JSONB NOT NULL DEFAULT '{}',
  learning_intensity TEXT NOT NULL DEFAULT 'balanced',
  deleted_at TIMESTAMPTZ
)

projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
)

sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  project_id UUID REFERENCES projects(id),
  source_tool TEXT NOT NULL,        -- 'native' | 'claude_code' | 'cursor' | 'copilot' | ...
  source_fidelity TEXT NOT NULL,    -- 'native' | 'wrapped'
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  raw_log_ref TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES sessions(id),
  role TEXT NOT NULL,               -- 'user' | 'assistant' | 'tool'
  content TEXT NOT NULL,
  authored_by TEXT,                 -- 'ai' | 'user' — MUST be set at generation time (AI-assist ratio depends on it)
  code_diff TEXT,
  timestamp TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
```

### 5.2 Knowledge Graph
```sql
knowledge_units (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  project_id UUID REFERENCES projects(id),
  session_id UUID REFERENCES sessions(id),
  source_fidelity TEXT NOT NULL,
  unit_type TEXT NOT NULL,          -- 'concept' | 'decision' | 'bug_fix' | 'pattern'
  title TEXT NOT NULL,
  summary TEXT,
  difficulty TEXT,                  -- 'novice' | 'intermediate' | 'advanced'
  embedding_ref TEXT,               -- ChromaDB vector id
  extracted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
)

knowledge_unit_relations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  related_unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  relation_type TEXT NOT NULL,      -- 'recurs_as' | 'depends_on' | 'contrasts_with'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

format_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  detected_type TEXT NOT NULL,
  chosen_format TEXT NOT NULL,      -- 'flashcard' | 'qa' | 'diagram' | 'retrieval_practice' | 'synthesis'
  rule_version TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
```

### 5.3 Learning & Review
```sql
learning_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  scope_type TEXT NOT NULL,         -- 'message' | 'chat' | 'project' | 'time_range'
  scope_ref JSONB NOT NULL,
  format TEXT NOT NULL,
  content JSONB NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  triggered_by TEXT NOT NULL        -- 'user_action' | 'scheduled_review'
)

learning_artifact_units (
  artifact_id UUID NOT NULL REFERENCES learning_artifacts(id),
  unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  PRIMARY KEY (artifact_id, unit_id)
)

review_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  next_review_at TIMESTAMPTZ NOT NULL,
  interval_days NUMERIC NOT NULL DEFAULT 1,
  ease_factor NUMERIC NOT NULL DEFAULT 2.5,   -- SM-2 style
  consecutive_correct INTEGER NOT NULL DEFAULT 0,
  first_review_at TIMESTAMPTZ,                -- enforces diffuse-mode delay
  mastery_status TEXT NOT NULL DEFAULT 'new',  -- 'new' | 'learning' | 'consolidated' | 'stale'
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, unit_id)
)

review_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  artifact_id UUID REFERENCES learning_artifacts(id),
  performance TEXT NOT NULL,        -- 'correct' | 'partial' | 'incorrect'
  response_text TEXT,
  day_offset INTEGER NOT NULL,
  reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
```

### 5.4 Profile & Metrics
```sql
knowledge_profile_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  unit_id UUID NOT NULL REFERENCES knowledge_units(id),
  mastery_status TEXT NOT NULL,
  retention_trend TEXT,             -- 'improving' | 'stable' | 'declining'
  visibility TEXT NOT NULL DEFAULT 'private',  -- 'private' | 'shared'
  last_computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

metrics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  event_type TEXT NOT NULL,         -- 'learn_triggered' | 'artifact_completed' | 'queue_cleared'
  metadata JSONB,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

independence_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  unit_id UUID REFERENCES knowledge_units(id),
  metric_type TEXT NOT NULL,        -- 'ai_assist_ratio' | 'error_repeat_rate'
  value NUMERIC NOT NULL,
  window_start TIMESTAMPTZ NOT NULL,
  window_end TIMESTAMPTZ NOT NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
```

### 5.5 Key Indexes
```sql
CREATE INDEX idx_sessions_user_project ON sessions(user_id, project_id);
CREATE INDEX idx_knowledge_units_user_time ON knowledge_units(user_id, extracted_at);
CREATE INDEX idx_knowledge_units_project ON knowledge_units(project_id);
CREATE INDEX idx_review_state_due ON review_state(user_id, next_review_at);  -- hottest index, backs scheduled review job
CREATE INDEX idx_review_history_unit_offset ON review_history(unit_id, day_offset);
CREATE INDEX idx_messages_session ON messages(session_id, timestamp);
```

---

## 6. Learning Science → Technical Requirements

| Principle | Source | System Requirement |
|---|---|---|
| Testing effect | Roediger & Karpicke | Quiz/QA generation defaults to recall format, not recognition |
| Spacing | Ebbinghaus, Bjork, Cepeda et al. | `review_state` uses adaptive intervals, not fixed schedules |
| Interleaving | Oakley, Dunlosky et al. | Review-session query pulls from ≥2 distinct `project_id`s |
| Chunking | Oakley | `mastery_status` tracks consolidation over repeated exposure |
| Diffuse mode | Oakley | `first_review_at` enforces a minimum delay before first review |
| Desirable difficulty | Bjork | Scheduling/interleaving logic is never "simplified away" for UX ease |
| Avoiding illusions of competence | Oakley | Passive content never writes to `review_state`/`mastery_status` |
| Self-explanation/elaboration | Dunlosky et al. | Dedicated "why" prompt format, not folded into generic QA |

---

## 7. Feature-to-Component Map

| Feature | Primary Components |
|---|---|
| "Learn" at any granularity | API scope resolver → Postgres query (+ ChromaDB for related context on large scopes) → Artifact Generator |
| Format auto-selection | Format Selection Engine → `format_decisions` log |
| Quiz/QA generation | LiteLLM + recall-first prompt templates |
| Diagram generation | LiteLLM → Mermaid spec output (versionable, diffable) |
| Spaced review | `review_state` + `review_history` + arq-scheduled jobs |
| Knowledge Profile export | `knowledge_profile_entries` → Markdown generator, visibility-filtered at generation time |
| Metrics dashboard | Layer 1: `metrics_events`; Layer 2: `review_history` aggregation; Layer 3: `independence_metrics` (derived from `messages.authored_by` and bug-fix recurrence) |
| Cross-tool aggregation (moat) | Unified `sessions`/`knowledge_units` schema regardless of `source_tool` |

---

## 8. Implementation Phases (Local Development)

Sequenced by dependency; all local (Docker Compose for Postgres/Redis/ChromaDB, local dev servers) — no hosting/deployment steps included here.

1. **Local environment setup** — Docker Compose stack, migrations tooling, health-check endpoint
2. **Core data layer** — all schema tables, basic auth, CRUD, seed script for realistic test data
3. **Native coding agent (minimal)** — LiteLLM-backed chat, `authored_by` correctly tagged from the start
4. **Extraction engine** — async pipeline producing `knowledge_units`; manual quality review before proceeding
5. **Format selection + artifact generation** — "Learn" working end-to-end at single-chat scope
6. **Spaced review engine** — scheduling, diffuse-mode delay, interleaving, `review_history` logging
7. **Knowledge Profile** — Markdown export, visibility enforcement at generation time
8. **Metrics (Layer 1 → Layer 2)** — event logging, retention curve queries; Layer 3 deferred until real usage volume exists
9. **Web frontend** — session input, Learn view, review queue, profile view, auth — against local backend
10. **Desktop shell (Tauri)** — same React codebase wrapped, local file-watching for wrapped tools, fidelity tagging
11. **Cross-feature hardening** — full end-to-end walkthrough across native + wrapped sources, before considering this demo/production-ready

**Priority note:** Phases 2-4 (data layer, agent, extraction) are the hardest and most differentiating; resist moving to visible UI work (Phases 9-10) before these are solid. Extraction mistakes are expensive to unwind once real data exists on top of them; UI is comparatively cheap to redo.

---

## 9. Differentiation, Reflected in Architecture

- **Longitudinal data moat** → unified schema across all sources and time ranges is a natural consequence of the data model, not a bolt-on feature
- **Learning-science credibility** → Section 6's mapping is a hard constraint on the Spaced Review Engine and Format Selection Engine, not optional polish
- **Data fidelity honesty** → `source_fidelity` flows from `sessions` through `knowledge_units` to every surfaced artifact/profile entry consistently

---

## 10. Open Technical Questions (Consolidated)

- Spaced-repetition algorithm variant: SM-2 (v1 default) vs. custom adaptive model later
- Diagram spec format: Mermaid (recommended) vs. custom DSL
- Async job runner: `arq` (recommended, lightweight/async-native) vs. Celery (heavier, more mature)
- MCP tool layer scope for the native agent in early phases
- `review_state` single-track vs. multi-track per unit (recall vs. application) — leaning single-track for v1
- Materialization strategy for `knowledge_profile_entries` — on-demand at export time recommended for v1 given expected data volume

---

*This consolidated document supersedes cross-referencing Technical Architecture v1, Database Schema v1, and Developer Implementation Plan v1 separately for day-to-day reference, though those documents remain available with additional narrative detail. Deployment/hosting is intentionally out of scope here — see Deployment Guide v1/v2 and the Investor Demo & Major Cloud Plan for that.*
