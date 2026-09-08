# Trivium v2 — Reference Systems Studied

What to take from adjacent projects, what to refuse, and why. Two systems studied in depth:
[penecho](https://github.com/penecho/penecho) (spatial/visual thinking) and
[Nous Research's hermes-agent](https://github.com/nousresearch/hermes-agent) (self-improving agent).

---

## 1. hermes-agent — the exact inverse of Trivium's thesis

**What it is.** A self-improving autonomous agent with a closed learning loop, positioned as *"the
only agent with a built-in learning loop — it creates skills from experience, improves them during
use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening
model of who you are across sessions."* It runs as a single gateway across Telegram, Discord, Slack,
WhatsApp, Signal and CLI, over seven terminal backends (local, Docker, SSH, Singularity, Modal,
Daytona, Vercel Sandbox), with 40+ tools, MCP integration, spawned subagents, and full model
agnosticity (`hermes model`, no lock-in).

### 1.1 The insight that matters most

Read Trivium's mission next to that sentence:

| | hermes-agent | Trivium |
|---|---|---|
| Who accumulates skill? | **The agent** | **The learner** |
| What persists across sessions? | The agent's procedural memory and user model | The learner's demonstrated knowledge |
| Direction of the loop | Experience → agent capability | Experience → human capability |
| Success | The agent needs you to explain less over time | You need the agent less over time |

**These are the same machine pointed in opposite directions**, and that is the sharpest possible
articulation of what Trivium is for. It is also a warning: every mechanism hermes-agent uses to make
the *agent* better from your work is, from Trivium's point of view, a mechanism that could quietly
absorb the learner's growth. An agent that curates memory from your sessions, distils skills from
your hard-won solutions, and gets better at your domain each week is *precisely the dependence
Trivium exists to prevent* — dressed as a feature.

**Design rule that falls out of it, and it is worth stating in the PRD:**

> **The artifacts of experience accrue to the learner, not to the model.** Anything the system distils
> from a learner's work — a skill, a pattern, a heuristic — is created as the learner's `authored`
> object, held in their corpus, and exportable by them. Trivium may not maintain a private,
> non-exportable model of the user that improves the service while the learner stays flat.

This is a positioning wedge as much as an engineering rule. Every AI product in 2026 says it learns
about you. Trivium is the one that says *you* are the thing being improved, and can prove it, because
provenance (`02-architecture.md` §1) makes the claim mechanically checkable.

### 1.2 Four things worth taking

**(a) Skills as durable, portable, standard-conforming artifacts.**
Hermes creates skills autonomously after complex tasks, lets them self-improve during use, and stores
them against the [agentskills.io](https://agentskills.io) open standard.

Trivium already has `services/skills.py`, a `skill_reports` table, and a `Skills.tsx` page labelled
*Improve* — the concept is half-built and currently under-exploited. The v2 move:

- A Trivium **skill is the learner's procedural knowledge**, extracted from a bench, and it is an
  `authored` object with the same publish gate as any other contribution.
- Emit it in the **agentskills.io format**. Then the loop closes in a way nothing else in this
  category does: *your* demonstrated understanding becomes a skill file that other people — **and
  their agents** — inherit and run. A learner's contribution stops being a blog post and becomes
  executable inheritance.
- This is the cheapest, most concrete instance of `00-north-star.md`'s thesis available, and it costs
  one serialiser on top of a table that already exists.

**(b) Cross-session recall as real retrieval infrastructure.**
Hermes uses SQLite FTS5 full-text search over session history with LLM summarisation for
cross-session recall. `PRD-v1.md` §6.1 promises Learn over "a single message, a full chat, a project,
or a rolling view across months/years" — the *all-time* end of that range needs exactly this
substrate and currently has no named mechanism. FTS5 plus hierarchical summarisation is the
pragmatic, cheap, no-vector-store answer, and it works identically over the v2 corpus
(`02-architecture.md` §3), not just over chats. Take it as-is.

**(c) A model of the learner — quarantined from the Profile.**
Hermes builds a "deepening model of who you are" via Honcho dialectic user modeling. Trivium needs
something like this for the Tutor: pitch, pace, what to teach next, which misconception keeps
recurring. But there is a hard boundary, and it follows from v1's own principles:

> A dialectic user model is **inference**, not evidence. It may steer the Tutor. It may **never**
> write to `knowledge_profile_entries`, and it may never be shown to the learner as a claim about
> what they know.

The Knowledge Profile is recomputed from `review_state` + `review_history` and cannot be set by hand
— that rule is already enforced and tested, and it is the product's credibility. Adopt the mechanism
for teaching; keep it out of the record.

**(d) Delivery where the learner already is.**
The multi-platform gateway is over-scoped for Trivium, but `PRD-v1.md` §6.5 already calls for
"user-configurable delivery: review queue (pull), notifications (push), email digest, or
combination." Hermes shows the shape of a single gateway process serving many surfaces. Take **one**
channel beyond the web app for v2 — a review-due nudge — and no more. Spaced repetition dies from
un-delivered reviews more than from bad scheduling.

### 1.3 What to refuse

| Refuse | Why |
|---|---|
| Autonomous, unprompted skill creation | `PRD-v1.md` §4.1: learning is user-initiated, never auto-triggered. A skill the learner did not author is `generated`, and counts for nothing until accepted-and-edited. |
| Agent self-improvement from learner sessions | §1.1. This is the thing Trivium exists to invert. |
| Seven terminal backends, 40+ tools, subagent parallelism | Infrastructure for an autonomous operator. Trivium's agent exists to *teach*, and a larger tool surface makes it a better doer — which is orthogonal at best. |
| Personality/persona switching (`/personality`) | A tutor's manner should follow pedagogical state (`02-architecture.md` §2), not a costume the learner picks. |

### 1.4 What it validates

Model agnosticity with no lock-in (`hermes model`, any provider) is exactly Trivium's existing
`llm/` abstraction (`mock` | openai | groq | anthropic | sarvam), and it reinforces
`02-architecture.md` §7: a product built on inheritance cannot be a place where work is trapped.
Hermes running on "a $5 VPS or a GPU cluster" is the same argument about the substrate.

---

## 2. penecho — spatial thinking and the provisional draft

Covered in full in `00-north-star.md` §5. Condensed:

**Take:** (a) AI output as a separate movable draft that is not yours until accepted, and *"editing
your own ink never triggers an AI request"* — the anti-dependence principle made physical;
(b) stylus/handwriting as first-class input, cited honestly; (c) the tiled canvas architecture
(512×512 tiles only where ink exists, send only the relevant crop); (d) editable widgets instead of
static diagram renders; (e) *"craft lineage preserved between versions"* — penecho's phrase for
exactly Trivium's provenance idea.

**Refuse:** ten provider slots and CLI executor modes; the ungated public "Echoes" gallery (Trivium's
commons must be provenance-gated or it fills with slop); four visual themes (one system executed to
Linear/Apple/Stripe rigor beats four at 25%).

---

## 3. The two together

The pair maps cleanly onto the two halves of the v2 product, which is why studying both was worth it:

- **penecho** answers *"where does the learner work, and how does the machine offer help without
  taking the work over?"* → the Canvas and the provisional draft (`02-architecture.md` §4).
- **hermes-agent** answers *"what persists across sessions, and who does it belong to?"* → skills,
  recall, and the user model — with the ownership question answered in the learner's favour
  (`02-architecture.md` §1, §5, §6).

Neither is a competitor. penecho is a thinking surface with no pedagogy and no retention model.
hermes-agent is a learning loop pointed at the agent. Trivium is the only one of the three whose
success condition is a change in the human — and, with the provenance triple, the only one that can
prove it.
