# Product Requirements Document (PRD) v1
## [Product Name TBD] — "Vibe code without getting dumber"

Status: Draft for internal alignment, derived from Concept Doc v1
Scope: Web app (v1 usable slice) → Desktop app (full experience) → Tool integrations

---

## 1. Purpose & Mission

Vibe coding tools optimize purely for shipping speed. This product adds a learning layer on top of (or built into) the coding process so users retain understanding, build real skill, and become progressively *more* independent — not more dependent — over time.

**Mission statement:** Coding correctness is table stakes. The product's success is measured by whether the user got smarter and more self-sufficient by using it.

---

## 2. Goals & Non-Goals

### Goals
- Turn coding activity (chats, diffs, decisions, bugs/fixes) into durable personal knowledge
- Make learning review effortless to trigger, at any granularity, at any time
- Ground every learning mechanic in established learning science
- Give users a living, evidence-backed record of what they know (Knowledge Profile)
- Prove, with real metrics, that users become more independent over time — not just more engaged

### Non-Goals (v1)
- Competing on raw code-generation quality/speed with Cursor, Copilot, Claude Code
- Monetization strategy (explicitly deferred)
- Enterprise/team dashboards (future wedge, not v1)
- Full domain generalization beyond coding (architecture should allow it later, but v1 ships coding only)

---

## 3. Target Users

- **Primary:** People who vibe code — from beginners learning to code via AI assistance, to working developers who want to stay technically sharp
- **Future:** Broader knowledge-work domains (history, writing, math) via the same extraction/learning engine, once the coding vertical is proven

### Primary user need
"I want to move fast with AI help, but I don't want to wake up in six months unable to explain or rebuild what I shipped."

---

## 4. Product Principles

1. **Opt-in, not forced friction.** Learning is always available, never blocking. No mandatory gates before continuing to code.
2. **Any span, any time.** A learning artifact can be generated from a single message, a full chat, a project, or a rolling view across months/years.
3. **Retrieval over exposure.** Passive viewing (summaries, being shown an answer) never counts as learning. Only active recall counts.
4. **Friction is sometimes the point.** Delay, interleaving, and difficulty are deliberate design choices grounded in research (desirable difficulty), not UX flaws to smooth away.
5. **Evidence over self-report.** The Knowledge Profile reflects demonstrated performance, not claims.
6. **Coding correctness is a baseline, not a differentiator.** Never compromise code quality to force a learning moment — the two must coexist without one degrading the other.

---

## 5. System Architecture Overview

### 5.1 High-level components

1. **Coding Interface Layer**
   - Native built-in AI coding agent (full-fidelity data capture)
   - Wrapped/observed integrations with external tools (Claude Code, Cursor, Copilot, etc.) — thinner data fidelity, broader reach

2. **Extraction & Indexing Engine**
   - Parses chats, diffs, decisions, bug/fix pairs from coding activity
   - Tags each unit by: concept(s), topic, project, timestamp, difficulty, type (concept / decision / bug-fix / pattern)
   - Domain-pluggable design — coding extractor ships in v1; architecture should not hardcode "code" as the only content type

3. **Learning Artifact Generator**
   - Takes a selected span (message / chat / project / time range) + auto-detects content type(s) present
   - Auto-selects output format per the Format Selection Engine (Section 6)
   - Generates the artifact (quiz, diagram, QA, concept map, self-explanation prompt)

4. **Spaced Review Engine**
   - Schedules future reviews using adaptive spaced repetition
   - Applies interleaving across concepts/projects when building review sessions
   - Delivery via in-app review queue, notifications, and/or email (user-configurable combination)

5. **Knowledge Profile Store**
   - Aggregates concept mastery status, retention curves, independence metrics over time
   - Generates the user-facing skill.md-style profile
   - Supports privacy controls and selective export/sharing

6. **Metrics & Analytics Layer**
   - Layer 1 (engagement), Layer 2 (retention/recall), Layer 3 (behavioral/independence) — see Section 9
   - Powers both internal product decisions and user-facing dashboards

### 5.2 Data flow (per session)
```
Coding session (native agent or wrapped tool)
   → raw session log captured
   → Extraction Engine parses into tagged knowledge units
   → stored in per-user longitudinal knowledge graph (concept × time × project)
   → user triggers "Learn" (any granularity) OR scheduled review fires
   → Artifact Generator produces format-appropriate content
   → user completes artifact (recall-based interaction)
   → performance recorded → updates Spaced Review Engine schedule + Knowledge Profile + Metrics Layer
```

---

## 6. Feature Specifications

### 6.1 "Learn" Action (core primitive)
- Available as a persistent UI affordance at every granularity level:
  - Single message
  - Full chat/session
  - Project (all sessions under one project)
  - Time range (week / month / year / custom / all-time)
- User-initiated, never auto-triggered mid-session
- On trigger: system determines content type(s) present in the selected span, then generates one or more artifacts

**Acceptance criteria**
- User can select any of the above granularities from any point in the product (chat view, project view, timeline/history view)
- Artifact generation completes within an acceptable latency (target: define SLA, e.g. <10s for single chat, async/notify for large spans like "all-time")
- If a span has insufficient extractable content, system communicates this clearly rather than generating a low-quality artifact

### 6.2 Format Selection Engine
Auto-selects the artifact format based on detected content type. Initial rule-based mapping (see Concept Doc Section 6) — should evolve toward a tunable/model-driven approach as data accumulates.

| Detected content | Format |
|---|---|
| New unfamiliar concept, first exposure | Flashcard / definition |
| Decision with tradeoffs | QA / reasoning prompt |
| Multi-component architecture | Diagram |
| Bug + fix | Retrieval-practice question |
| Recurring pattern across sessions | Synthesis / chunking question |

**Requirement:** format selection logic must be logged and inspectable (for tuning), even if not user-facing in v1.

### 6.3 Quiz / QA Generator
- Recall-based by default (open response), not recognition-based (multiple choice), per testing-effect research
- Multiple-choice acceptable as fallback only when recall isn't feasible for the content type
- Includes self-explanation / elaborative-interrogation prompts ("why did this approach work here and not in case X") as a distinct sub-type, not folded into generic quizzes

### 6.4 Diagram Generator
- Generated from actual user code/architecture, not generic templates
- Should visually reflect evolution over time where relevant (e.g., "this is how your auth flow changed across 3 sessions")

### 6.5 Spaced Review Engine
- Adaptive intervals per concept, adjusted by individual user performance (not fixed Anki-style defaults)
- Deliberate delay before first review (diffuse-mode principle) — not offered immediately post-session
- Review sessions interleave concepts across different projects/topics rather than blocking by single topic
- User-configurable delivery: review queue (pull), notifications (push), email digest, or combination

**Acceptance criteria**
- System never schedules two reviews of the same exact concept closer than [minimum interval, TBD]
- Interleaving logic must draw from at least 2 different projects/topics per review session where available

### 6.6 Knowledge Profile ("skill.md")
- Auto-generated, evidence-based record: mastered / in-progress / stale concepts, retention trends, independence trend
- Private by default; user controls per-item or full-profile visibility
- Exportable (format TBD — markdown export aligns with the "skill.md" framing and is portable)
- Updates continuously as new evidence (quiz results, review outcomes) comes in

### 6.7 User-Facing Metrics Dashboard
- Surfaces Layer 2 (retention curves, recall success rate) and Layer 3 (AI-assist ratio trend, error-repeat rate) metrics directly to the user
- Framing must be motivating, not judgmental — e.g. "areas to review" rather than "weaknesses," trend-based rather than single-score shaming
- Should visually resemble a growth/contribution-style graph (familiar pattern from tools like GitHub) rather than a report card

---

## 7. Learning Science Requirements

Every learning mechanic in this product must trace to established research. This is a hard constraint on the Format Selection Engine and Spaced Review Engine design, not just a marketing talking point.

| Principle | Source | Requirement on system |
|---|---|---|
| Testing effect | Roediger & Karpicke | Default all quiz/QA to recall format |
| Spacing | Ebbinghaus, Bjork, Cepeda et al. | Adaptive interval scheduling, not fixed |
| Interleaving | Oakley, Dunlosky et al. | Review sessions mix topics/projects |
| Chunking | Oakley | Track and surface concept consolidation over repeated exposure |
| Diffuse mode | Oakley | Enforce minimum delay before first review |
| Desirable difficulty | Bjork | Do not "smooth away" friction that research shows aids retention |
| Avoiding illusions of competence | Oakley | Passive content (summaries, being shown answers) must never update mastery status |
| Self-explanation / elaboration | Dunlosky et al. | Distinct "why" prompt format required, not optional |

---

## 8. Format Auto-Selection — Technical Notes

- v1: rule-based classifier on extracted knowledge units (content type → format mapping table)
- Future: model-driven selection informed by accumulated performance data per user (e.g., if a user consistently underperforms on diagram-based review for architecture concepts, shift weighting toward QA format for that user)
- All classification decisions logged with the underlying signal that triggered them, to support later tuning and auditability

---

## 9. Success Metrics (Detailed)

### Layer 1 — Engagement Proxies (v1 telemetry)
- Learn-button usage rate (% sessions where triggered)
- Quiz/QA completion rate
- Review queue clear rate
- Time-to-first-review after session end

### Layer 2 — Retention/Recall (v1.5–v2, core credibility layer)
- Spaced-repetition performance curves per concept (accuracy at day 1 / 7 / 30)
- Retrieval-practice success rate (recall accuracy before answer shown)
- Cross-project transfer rate (correct recognition/application of a concept in a new project context)

### Layer 3 — Behavioral/Independence (v2+, mission-critical, hardest to build)
- AI-assist ratio per concept over time (% of code touching concept X that was AI-generated vs. user-written) — should trend downward for well-practiced concepts
- Error-repeat rate (does the same category of mistake recur after review, vs. before)
- Explanation quality trend (if self-explanation UI is used, track sophistication/accuracy over time)

**Staging plan**
1. v1: instrument Layer 1 fully
2. v1.5–v2: build Layer 2 seriously — required before user-facing retention stats can ship credibly
3. v2+: attempt Layer 3, starting with AI-assist ratio and error-repeat rate since both are derivable from existing code diffs without new UI

---

## 10. Differentiation / Moat (Product Implications)

Design and prioritization should reinforce these four pillars, not just describe them:

1. **Longitudinal data** → every architectural decision should default toward retaining and cross-referencing history rather than treating sessions as disposable
2. **Learning-science engine** → Section 7's requirements are non-negotiable; do not ship generic flashcard scheduling
3. **Positioning** → product copy, onboarding, and UI tone should consistently reinforce "doesn't make you dumber," including explaining *why* friction exists when introduced
4. **Cross-tool aggregation** → integrations (Section 11) should aim to unify the user's learning history regardless of which coding tool was used on a given day

---

## 11. Platform Plan

### 11.1 Web App (v1 — usable product + marketing)
Dual purpose: must deliver real standalone value (not just a funnel to desktop) while also serving as the marketing/positioning surface.

Proposed v1 usable slice:
- Connect or paste in a chat/coding session
- Trigger "Learn" on that session → receive an auto-formatted artifact
- Basic review queue (single-session scope acceptable for v1; full cross-project/time-range history can follow)
- Basic Knowledge Profile view (even minimal, evidence-based, not aspirational)

Marketing surface requirements:
- Clear articulation of the "doesn't make you dumber" positioning
- Visible, credible tie-in to learning science (Section 7 table is strong candidate content)
- Path to desktop app download

### 11.2 Desktop App (full experience)
- Native built-in agent for full-fidelity session capture
- Full cross-project, cross-time Knowledge Profile and review system
- Full metrics dashboard (Layers 1–3 as they become available)

### 11.3 Tool Integrations (Claude Code, Cursor, Copilot, etc.)
- Observed/wrapped session data, fidelity dependent on what each tool exposes
- Explicitly communicate to users when integration-based learning artifacts are lower-fidelity than native-agent ones, rather than overpromising uniform quality

---

## 12. Open Questions (carried from Concept Doc + new)

- Exact SLA/performance targets for artifact generation at large time-range scope ("all-time" learn action)
- Minimum viable Extraction Engine accuracy before shipping — how do we validate quality pre-launch?
- Knowledge Profile schema/versioning — markdown-based export format details
- Where does the delay threshold sit for diffuse-mode-informed first review (hours? next calendar day?)
- Enterprise/education wedge — explicitly deferred, but architecture should not preclude it later
- Product name and final positioning language

---

## 13. Appendix: Core Loop Diagram (textual)

```
User codes
  → native agent OR wrapped external tool
        ↓
Extraction Engine tags: concept, topic, project, time, type
        ↓
User triggers "Learn" (any granularity) — opt-in, never forced
        ↓
Format Selection Engine picks artifact type
        ↓
Artifact Generator produces quiz / diagram / QA / concept map / self-explanation prompt
        ↓
User engages via active recall (not passive viewing)
        ↓
Performance recorded
        ↓
Spaced Review Engine schedules future interleaved review
        ↓
Knowledge Profile + Metrics Dashboard update
```

---

*This PRD builds directly on Concept Doc v1 and should be treated as a living document, refined as web app development and user testing begin.*
