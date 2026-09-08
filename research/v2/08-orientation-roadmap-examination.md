# Trivium v2 — Orientation, Roadmap & Examination

**Status:** Research / proposal.
**Depends on:** the Inheritance layer (`02-architecture.md` §3) and the Tutor (`02-…` §2).
**Fixes:** hinge moments 1, 2 and 5 from `05-learner-experience.md` §3.

This is the front door. A learner arrives, says what they are trying to become, and the product
answers with an inheritance and a route. It is also the surface where Trivium is most likely to
betray itself, so most of this document is about how not to.

---

## 1. The obvious design is a trap

The natural thing to build is an onboarding form: *What's your goal? What's your level? How many hours
a week? Which topics?* Then generate a curriculum.

Three reasons that fails, in order of severity.

**A beginner cannot answer "what is your goal."** If they could state a well-formed learning goal,
they would already have most of a roadmap — that *is* the hard part. Asking an unanswerable question
in the first ninety seconds is a worse cold start than an empty dashboard, because it also makes the
learner feel stupid before they have learned anything. The people who most need the roadmap are
exactly the people who cannot fill in the form.

**"What's your level?" is self-report, which the product forbids.** `PRD-v1.md` §7 and the shipped
profile enforce *evidence over self-report* — the Knowledge Profile is recomputed from
`review_state` and `review_history` and cannot be set by hand. An intake that asks a learner to rate
themselves and then routes on that answer contradicts the product's own founding rule at the very
first screen. Standing has to be **placed**, not declared.

**A generated curriculum is the thing the philosophy rejects.** v2 says a learner works in a lab their
predecessors left. Handing them a synthetic syllabus of invented lessons is the opposite: it replaces
inheritance with product output. Whatever we build must be **a route through real inherited
material**, not a course.

So the design constraint is:

> The orientation must produce a goal the learner could not have written alone, establish standing
> without asking for it, and hand back a route made of real sources — in under six minutes, without
> blocking, and while teaching the product's core mechanic in the act.

---

## 2. The Orientation is a tutor episode, not a form

The move that resolves all three problems at once: **the intake is the first tutor episode.** Same
declared move set as `02-architecture.md` §2 — `elicit`, `probe`, `commit`, `contrast` — applied to
the learner's own aim instead of to a knowledge unit.

This means the first ninety seconds of the product *are* the product. The learner does not fill in a
form to reach the thing; the thing is what they are doing.

### The six moves

| # | Move | What the learner sees | Why this, here |
|---|---|---|---|
| 1 | `elicit` | **"What do you want to be able to *do* that you can't do now?"** Free text. No dropdown, no topic picker. | The phrasing is load-bearing. "Want to be able to do" is answerable by a beginner; "what do you want to learn" is not. It also forces a *capability*, which is testable, instead of a *topic*, which isn't. |
| 2 | `probe` | **"Who has already done it?"** A name, a book, a repository, a paper — anything. | This is the inheritance question wearing ordinary clothes. Everyone can name someone they admire. The answer seeds the corpus with real material immediately, and it teaches the philosophy in the act of asking rather than in a paragraph of copy. |
| 3 | `commit` | **"When you can do it — what would you want to leave behind?"** Written, before anything is shown. | Their first `authored` object, created in the first two minutes. Vague answers are fine and expected; the point is that the terminal state exists from the beginning. |
| 4 | `contrast` | The system reflects the aim back as a **decomposition into capabilities**, drawn from the domain pack. The learner edits it directly. | **This is the moment the product proves itself.** A learner watches a vague ambition become a legible structure they can correct. It is also the single most persuasive thing the product can do, and it costs one model call. |
| 5 | *placement* | **"Some of this you may already have. Want to find out?"** — optional, 12 open-recall items across the decomposition. | Standing established by evidence, not self-report. Framed as **mapping**, never as testing (§5.6). Skippable, and skipping it just routes you to the beginner branch. |
| 6 | *the draft route* | A roadmap arrives as a **`generated` draft** — dashed, floating, not yet theirs. They accept-and-edit. | The provenance triple applied to the plan itself. Trivium cannot hand a learner a roadmap and stay honest; it drafts one, and the learner authors it. |

Time and horizon are **not** asked. They appear last, as a control on a roadmap the learner can
already see — adjusting a visible thing beats answering an abstract question, and it removes two form
fields from the front.

### Hard rules

- **Never blocking.** `PRD-v1.md` §4.1 — learning is opt-in, never forced friction. There is a
  permanent "start from a source instead" escape that lands in the Inherit district.
- **Six minutes, hard cap.** If it can't be done in six, cut moves, not depth.
- **Resumable, and useful if abandoned.** A learner who quits after move 3 still leaves with a written
  aim and a named predecessor — which is more than the shipped product gives anyone.
- **Only three moves require typing.**

---

## 3. Two branches, decided by evidence

Placement, not the learner, decides which branch they are on.

### Beginning → **a route**

Little or nothing demonstrated against the decomposition.

- A staged roadmap, from the first source to the terminal contribution.
- **Placement is offered but not run cold.** Testing a beginner in minute four produces the first
  honest miss at the worst possible moment (`05-…` §3, hinge 3). Instead the first stage *is* the
  placement — the miss arrives after they have done something, framed as information.
- The first source is **offered, never requested**: something short, excellent and complete that pays
  off inside one session. Never a 400-page book on day one.

### Already underway → **gaps and the nearest contribution**

Real capability demonstrated in placement.

A forty-week route is insulting to this learner and they will leave. What they get instead:

1. **The gaps** — prerequisites in the decomposition they skipped and have never demonstrated. This is
   the single most valuable thing you can tell an experienced self-taught person, and almost nothing
   else offers it.
2. **The nearest contribution** — one thing they could publish this month with what they already hold.
3. **A thin route** covering only the gaps, not the whole domain.

> Same machinery, two shapes. The branch is a *rendering* of the same roadmap object at different
> standing, not a separate product.

---

## 4. The Roadmap

### What it is, structurally

Not a course. **A route through inherited material, terminating in a contribution.**

| Property | Consequence |
|---|---|
| Made of **real inherited sources**, never invented lessons | Consistent with the philosophy: you get a path through the lab, not a synthetic syllabus |
| Terminates in a **contribution**, not a certificate | The loop closes where `00-north-star.md` says it must |
| Is a **hypothesis**, not a syllabus | Evidence moves you. Placement and checkpoints rewrite it, visibly |
| Arrives `generated`, becomes `authored` on accept-and-edit | The learner authors their own path, with help. This is non-negotiable — it is the whole product in miniature |
| **Every stage leaves something** | Not just a checkpoint: a small contribution. This is the fix for "the contribution bar feels unreachable" (`05-…` §5) |

### Anatomy of a stage

```
STAGE
  ├─ capability          what you will be able to do (testable, not a topic)
  ├─ inherited sources   2–5 real things, with why each is here
  ├─ tutor episodes      the concepts that need dialogue, not just reading
  ├─ checkpoint          an exam that reports; it does not block  (§5.2)
  └─ small contribution  an annotated passage, a worked solution, a note —
                         published with its lineage. Every stage leaves a trace.
```

### Revision is visible

A roadmap that silently rewrites itself is untrustworthy. Every revision is logged with what caused
it — *"stage 4 moved earlier: you missed three retrievals on its prerequisite"* — and the learner can
reject the revision. The route is theirs; the system advises.

---

## 5. Examination

Trivium's identity constrains this hard: open recall by default, no multiple choice, no illusions of
competence, motivating rather than judgmental framing. Five kinds, each with a different job.

### 5.1 Placement — *where do I enter?*

Adaptive, ~12 open-recall items across the decomposition, ~8 minutes. Not scored as a mark; the output
is a **position on the route**. Ends on the highest thing you *could* do, never on the lowest thing
you couldn't.

### 5.2 Checkpoint — *did that stage take?*

At the end of each stage. **Reports, never blocks** — `PRD-v1.md` §4.1 forbids mandatory gates.
A failed checkpoint does not lock the next stage; it revises the route and says why.

### 5.3 Retention — *is it still there?*

The existing spaced-review engine, reframed. Not an event: continuous examination that already runs.
Nothing new to build, and it is the one that actually measures learning.

### 5.4 The defence — *can you hold it under pressure?*

The terminal exam for a roadmap, and it is not a quiz. A **viva**: you explain your understanding
under questioning, and you must state and answer the strongest objection to your own position. This
is the tutor's `contrast` move turned on the learner's whole body of work.

It is the honest terminal assessment because it is how mastery is actually tested everywhere it
matters — a thesis defence, a design review, a code review. Passing it unlocks nothing; it *is* the
thing.

### 5.5 Transfer — *is it yours, or is it the domain's?* (§6.2)

### 5.6 Framing rules, non-negotiable

- Placement is **mapping**, never testing. The copy says where you are, never how much you lack.
- No score is ever a single number presented as a verdict on a person.
- **A miss is a find.** It is the only event producing new information and it generates the next
  artifact — the interface must say so at the moment it happens.
- No exam blocks anything, with exactly one exception: **the contribution publish gate**
  (`02-…` §5), which blocks by design because publishing makes a claim on other people's attention.
- No leaderboards, no streaks, no percentile against other learners. Ever.

---

## 6. Polymath and first thinking

The user's framing — *first thinker, polymath, essentially anything* — needs a mechanical definition
or it becomes a slogan. Two capabilities, both testable.

### 6.1 A polymath is not a collector

Knowing many subjects is being a dilettante. **A polymath is someone in whom a structure learned in
one domain gets deployed in another where it isn't native.** The capability is *transfer*, and it is
the only thing worth measuring.

**The spine-and-transfer roadmap.** A polymath roadmap is *not* N parallel roadmaps — that produces
breadth with no transfer, which is the exact failure mode.

```
        SPINE                          TRANSFERS
   one domain, taken to the      then a second domain entered
   depth where its structures    THROUGH the spine's structures,
   become statable abstractly    and a third through both
   ──────────────────────────►   ──────────┬──────────┬────────►
                                           │          │
                          "this is the same shape as the
                           thing I already know"
```

The gate between them is specific and checkable: **you may open a transfer only when you can state
your spine domain's core structures without reference to its subject matter.** Before that, there is
nothing to transfer. This is the one place a roadmap should be opinionated, because the failure it
prevents is the defining failure of self-directed polymathy.

### 6.2 The transfer exam

Requires ≥2 benches with demonstrated capability.

- A problem is posed in bench B whose solution needs a structure you demonstrated in bench A — **and
  A is not named.**
- Scored in three bands: the structure carried; the analogy was recognised but misapplied; no
  transfer.
- Trivium can actually generate these, because provenance edges tell it what you have demonstrated
  where. Almost nothing else has that information.

**The metric: transfer rate** — how often a structure you hold in one domain is deployed in another
unprompted. That is the polymath number. Not subjects studied.

### 6.3 First thinking, made mechanical: **the Descent**

"First-principles thinking" is usually unfalsifiable. Here is a version that isn't.

Take a claim the learner holds — ideally from their own `authored` notes. The tutor descends:
*why is that true?* — and again, and again — until every branch terminates in a typed leaf:

| Leaf | Meaning |
|---|---|
| **verified** | "I can check this myself, and here is how." |
| **trusted** | "I take this on authority — and here is the source." Must resolve to a real `inherited` source. |
| **assumed** | "I take this on authority and I cannot name the source." |
| **stuck** | "I don't actually know why this is true." |

The output is a **dependency tree of your own belief, with the unsourced assumptions highlighted.**

The diagnostic is not "how few trusted leaves do you have" — everyone has many, and a person with
none is lying. It is:

> **A first-principles thinker is not someone with no trusted leaves. It is someone who knows exactly
> where their trusted leaves are.** The measures are the **assumed ratio** (trusted-but-unsourced —
> the dangerous ones) and the **depth at which you hit `stuck`.**

This is provenance applied to belief rather than to text, which makes it the most Trivium-native
feature in this document — it could not exist in a product without a provenance model, and it is
genuinely useful to a working thinker regardless of domain.

A completed Descent is itself a publishable contribution: an argument with its dependencies made
explicit is a real artifact, and a rare one.

---

## 7. Data model

```python
class Orientation(Base):
    __tablename__ = "orientations"
    # user_id, aim (authored), predecessor_ref, terminal_contribution (authored),
    # decomposition (json, generated → authored on edit), completed_moves, abandoned_at

class Roadmap(Base):
    __tablename__ = "roadmaps"
    # user_id, orientation_id, shape: route | gaps | spine | transfer
    # provenance (generated until accepted+edited), horizon_weeks, hours_per_week

class RoadmapStage(Base):
    __tablename__ = "roadmap_stages"
    # roadmap_id, ordinal, capability, status,
    # checkpoint_exam_id, contribution_id (the small one this stage leaves)

class RoadmapStageSource(Base):        # the inheritance for this stage
    __tablename__ = "roadmap_stage_sources"
    # stage_id → source_id, rationale (why this source is here)

class RoadmapRevision(Base):           # visible, rejectable
    __tablename__ = "roadmap_revisions"
    # roadmap_id, at, cause, diff (json), accepted_by_user

class Exam(Base):
    __tablename__ = "exams"
    # user_id, kind: placement | checkpoint | defence | transfer | descent
    # scope, opened_at, closed_at, outcome (json)   # never a bare score

class DescentNode(Base):
    __tablename__ = "descent_nodes"
    # exam_id, parent_id, claim, leaf_type: verified | trusted | assumed | stuck,
    # source_id (required when leaf_type == trusted), depth
```

`Orientation.aim` and `terminal_contribution` are `authored` at creation — the learner's first two
authored objects, produced in the first three minutes.

---

## 8. Risks

| Risk | Why it's real | Mitigation |
|---|---|---|
| **Intake abandonment** | Every question is a drop-off point, and this one has six moves | Six-minute cap; three typing moves; useful output if abandoned at any point; a permanent skip that lands somewhere real |
| **The roadmap becomes a curriculum** | It is the natural gravity of the feature, and it is the thing the philosophy rejects | Stages are made of inherited sources only. No invented lesson content, ever. If a stage has no real source, the stage is wrong |
| **Exams become grades** | Five exam types is a lot of assessment for a product that isn't school | Only one gate blocks anything (publish). No single-number verdicts. The framing rules in §5.6 are testable, not aspirational |
| **Placement demotivates a beginner** | The first honest miss at minute four is the worst possible timing | Never place a beginner cold. The first stage is the placement |
| **Goal-setting theatre** | A stated aim nobody revisits is worse than none | The aim is shown at the top of every roadmap view and revisited at each defence. If it hasn't changed in six months, ask whether it's still true |
| **Over-fitting to a stated goal** | Aims change, especially good ones | The roadmap is explicitly a hypothesis. Changing the aim is a first-class action, not a settings edit |
| **The Descent as navel-gazing** | "Why is that true" five times can be sophistry | Terminates on typed leaves, not on exhaustion. `verified` requires stating *how* you'd check. `trusted` requires a resolvable source. Both are checkable |
| **Polymath framing invites dabbling** | The feature could licence exactly the behaviour it should prevent | The spine gate (§6.1) is enforced: no transfer until spine structures are statable abstractly |

---

## 9. Where this lands

It depends on Inheritance (Phase 2) and the Tutor (Phase 3) — but **a reduced version ships far
earlier and is worth it on its own**:

| Version | Needs | Ships | Value |
|---|---|---|---|
| **Orientation Lite** — moves 1–4 only. Aim, predecessor, terminal contribution, decomposition. No placement, no roadmap. | One model call and two tables | **Phase 1**, alongside provenance | Fixes the empty first screen and creates the learner's first authored objects in three minutes. Cheap, and it is most of the emotional payload |
| **Full orientation + roadmap** | Inheritance layer | Phase 2 | Real sources means a real route |
| **Placement, checkpoint, defence** | Tutor | Phase 3 | Standing by evidence |
| **Transfer + Descent** | ≥2 benches, contribution layer | Phase 5–6 | The polymath and first-thinking claims become testable |

**Recommendation: pull Orientation Lite into Phase 1.** It is a few days of work, it fixes hinge
moment 1 (the first ninety seconds), and it means the learner's very first interaction with Trivium
is the tutor doing the one thing a chat cannot — turning what they said into a structure they can
correct.
