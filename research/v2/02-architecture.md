# Trivium v2 — Essential Components

**Status:** Research / proposal. Written against the shipped `backend/app/` (15 tables, 10 route
modules, 7 services) and `PRD-v1.md`.

The frontend work in `01-frontend-constraint-document.md` makes Trivium *look* like a product with a
thesis. This document is what makes it *be* one. Five components, in dependency order.

---

## 0. What exists, and where the gaps sit

The shipped backend is well-factored and the additions below fit its existing grain rather than
fighting it.

```
projects · sessions · messages                 → Work    (exists)
knowledge_units · knowledge_unit_relations     → Work    (exists)
format_decisions                               → Work    (exists, and is the model for §2)
learning_artifacts · learning_artifact_units   → Retain  (exists)
review_state · review_history                  → Retain  (exists)
knowledge_profile_entries · skill_reports      → Retain  (exists)
metrics_events · independence_metrics          → Retain  (exists)

                                               → Inherit     (MISSING — §3)
                                               → Contribute  (MISSING — §5)
                                               → provenance  (MISSING — §1)
```

Two of the four estates have no representation at all. That is the whole gap, and it is why the
product currently reads as a study aid rather than as the thesis in `00-north-star.md`.

---

## 1. The provenance triple — do this first

**Why first:** it is the smallest change, it is the moat, and every other component depends on it.

### Data model

```python
# One enum, one column, added to every content-bearing table.
class Provenance(str, Enum):
    inherited = "inherited"   # came from a predecessor
    generated = "generated"   # a model made it on your behalf — not yours yet
    authored  = "authored"    # you made it, under your own hand

# messages, knowledge_units, learning_artifacts, annotations, canvas_objects,
# contributions  →  provenance: Mapped[Provenance]  (immutable after insert)
```

This generalises the existing `source_fidelity` (`native`/`wrapped`) idea from sessions to every
object. `source_fidelity` answers *"how faithfully was this captured?"*; `provenance` answers *"whose
work is this?"* — orthogonal, and both should survive.

### Rules, enforced in services and covered by tests

| Rule | Where |
|---|---|
| `provenance` is set at insert and never updated in place | model-level constraint |
| Only `authored` evidence writes to `review_state` / `knowledge_profile_entries` | `services/profile.py`, `services/review.py` |
| `generated → authored` requires an explicit accept **and** a diff above a minimum edit distance. Accepting verbatim leaves it `generated` permanently. | new `services/provenance.py` |
| A contribution cannot publish unless its `authored` ratio clears a threshold and every `inherited` claim resolves to a source edge | `services/contribution.py` (§5) |

That last rule is the same shape as the review gates that already return HTTP 409 for an early
submission. Trivium's credibility comes from gates that are real; this is one more.

### API

`GET /provenance/ledger?scope=…` → the authored/generated/inherited breakdown for any span. This is
what the frontend's material grammar (`01-…` §5) renders, and what the Contribution gate checks.

**Effort:** small. One enum, one migration, three service guards, one endpoint. **Value:** it is the
only thing in the product a competitor cannot copy without adopting the philosophy.

---

## 2. The Tutor — one-on-one, and inspectable

Today `api/routes/agent.py` + `pages/AgentChat.tsx` is a chat: messages in, messages out. "One-on-one
learning software" is not a chat with a nicer prompt. It is a **pedagogical state machine with a
declared move set** — and, crucially for this product, an *auditable* one.

Trivium already has the right precedent: `format_decisions` logs every format choice with its rule
version and triggering signal, so the engine can be tuned and defended. The tutor gets the same
treatment.

### The move set

| Move | Contract |
|---|---|
| `elicit` | Ask what the learner already thinks. **The tutor may not state the answer on this move.** |
| `probe` | "Why? What would change your mind?" Follows an `elicit` or a `commit`. |
| `counterexample` | Present a case where the learner's stated rule fails. |
| `commit` | The learner must write their answer **before** anything is revealed — the same gate `ArtifactPlayer` already enforces for Reveal, applied to dialogue. |
| `reveal` | State the received answer — permitted only after a `commit` in the same episode. |
| `contrast` | Name precisely where the learner's answer differed from the received one. This is the highest-value move and the one a generic chat never makes. |
| `extend` | Raise difficulty within the same concept. |

### Data model

```python
class TutorEpisode(Base):        # one concept, one sitting
    __tablename__ = "tutor_episodes"
    # user_id, knowledge_unit_id, domain_pack, opened_at, closed_at, outcome

class TutorMove(Base):           # mirrors format_decisions' auditability
    __tablename__ = "tutor_moves"
    # episode_id, ordinal, move (enum), rule_version, triggering_signal,
    # learner_text (authored) | tutor_text (generated), latency_ms
```

### Invariants worth testing

- No `reveal` without a preceding `commit` in the same episode → 409, same as the review gate.
- `learner_text` is always `authored`; `tutor_text` is always `generated`. The transcript is therefore
  a provenance record for free.
- Episode outcome writes to `review_state` **only** via the learner's `commit` content — never via
  their agreement with a `reveal`. (v1's "no illusions of competence" rule, applied to dialogue.)

### On claims

Do not market this as solving Bloom's 2-sigma problem. Replications put human tutoring nearer
0.36 SD (0.59 SD for certified teachers) and period intelligent-tutoring systems around d = 0.76 —
not 2.0. Recent AI-tutor RCTs are genuinely positive but modest and new. A product whose entire brand
is *evidence over self-report* cannot lead with a contested number. Claim mastery-based, adaptive, and
auditable — then show the audit.

---

## 3. The Inheritance layer — *the lab your predecessors left*

The largest gap and the one that changes what the product *is*. Today a learner's corpus is their own
agent chats; under the v2 philosophy that means they have inherited nothing.

### Data model

```python
class Source(Base):
    __tablename__ = "sources"
    # kind: book | paper | repo | lecture | dataset | contribution
    # title, authors, year, identifier (DOI/ISBN/URL/commit),
    # ingested_at, provenance = inherited (always)

class SourceEdge(Base):
    __tablename__ = "source_edges"
    # from_source_id → to_source_id, relation: cites | derives_from | implements | responds_to
    # This table is the Lineage. Everything in 01-…§7 renders from it.

class Bench(Base):                # a project, reconceived
    __tablename__ = "benches"
    # A bench = inherited sources + your work on them. Replaces/extends `projects`.

class Annotation(Base):
    __tablename__ = "annotations"
    # source_id, anchor (locator), body, provenance (authored | generated)
```

### Behaviour

- **Ingest:** PDF, EPUB, papers, repositories, lecture transcripts, and — critically — *other
  learners' published contributions*. That last one is what closes the loop: one learner's
  Contribute becomes another's Inherit.
- **Every knowledge unit gains an edge to its source.** `knowledge_units` currently traces to a
  session; it must also be able to trace to a `Source`. Sources trace to *their* sources where
  extractable: bibliographies, imports, `@cite` keys, package manifests.
- **The reading surface** is where the material grammar earns its keep: the text is `inherited`
  (ruled ground), your marginalia are `authored`, the tutor's notes are `generated` — three
  materials on one page, no badges, legible at a glance.

### Why this unblocks everything else

- It gives the Lineage (§7 of the frontend doc) real data to render.
- It is the only component that works with **zero other users** — a solo learner inherits books and
  repos on day one — so it is the right thing to ship before the commons.
- It is what makes domain packs (§6) meaningful: a philosophy pack without primary texts is a quiz
  generator.

---

## 4. The Canvas — spatial work and ink

Borrowed from penecho, with the specific carve-outs in `00-north-star.md` §5.

### Architecture (copy penecho's, it is correct)

- Large logical canvas; **512×512 tiles allocated only where ink exists** — no giant bitmaps.
- The client sends only the relevant crop plus geometry to the server; the server routes to the
  existing `llm/` provider abstraction and streams back a draft.
- Stylus and mouse input, lasso-select to move/resize/recolour/delete confirmed ink.

### The two invariants that matter

1. **A model response arrives as a separate, movable object that is not yours until accepted.** It
   carries `provenance = generated`, renders with the dashed edge and the system's single shadow, and
   becomes `authored` only on accept-plus-edit (§1). This is the anti-dependence principle made
   physical rather than declared.
2. **Editing your own ink never triggers a model request.** Your side of the canvas is yours. This is
   penecho's rule and it is worth adopting verbatim.

### Widgets

Upgrade artifact output from static Mermaid SVG to **manipulable** diagrams and sandboxed HTML. The
pedagogical argument is Trivium's own: a diagram you can pull apart and rebuild is retrieval
practice; a diagram you look at is exposure — which the PRD already classifies as an illusion of
competence. The current `Mermaid.tsx` render path is the weakest link between Trivium's principles
and its implementation.

### Ink

First-class handwriting input, cited honestly (`00-north-star.md` §5, item 2): the EEG connectivity
evidence is directional, n=36, and a proxy — not the settled testing-effect literature the review
engine rests on. Ship it because it is the right interaction for mathematical and spatial work, and
treat the retention benefit as plausible rather than proven.

---

## 5. The Contribution layer — the terminal state

Without this the philosophy is decoration. The loop must end in something that **leaves**.

### Data model

```python
class Contribution(Base):
    __tablename__ = "contributions"
    # bench_id, kind: explainer | annotated_edition | implementation
    #                | proof | dataset | replication
    # body, authored_ratio, published_at, license, lineage_snapshot_id

class ContributionSource(Base):
    __tablename__ = "contribution_sources"
    # contribution_id → source_id, role: builds_on | responds_to | corrects
```

### The publish gate

A contribution publishes only when:

1. `authored_ratio` clears the domain pack's threshold (§6),
2. every `inherited` claim inside it resolves to a `SourceEdge`, and
3. the learner has demonstrated recall on the units it depends on — evidence, not assertion.

On publish, the contribution is written back as a `Source` **with its lineage attached**, so the next
learner inherits both the artifact and the path that produced it. That is the loop closing, in the
data model rather than in the copy.

### The metric this finally makes honest

The PRD's Layer 3 ("behavioural/independence — mission-critical, hardest to build") currently
proposes AI-assist ratio and error-repeat rate. Those are proxies. The real one is now directly
measurable: **did a stranger inherit something you made?** Promote it from "v2+, hardest" to the
product's headline metric — it is the only number that tests the thesis rather than the engagement.

---

## 6. Domain packs — generality without mush

A pack is a declared rubric, not a model. Three fields, per `00-north-star.md` §4: unit type,
evidence of mastery, contribution shape — plus the `authored_ratio` threshold and the format-selection
table for that domain.

```
packs/
  code.yaml          # exists today, implicitly — extract it
  mathematics.yaml
  text.yaml          # philosophy, history, close reading
```

`services/format_selection.py` and `services/extraction.py` become pack-parameterised rather than
coding-specific. Ship code plus two non-code packs — one pack proves nothing about generality; three
proves the abstraction is real. This is what makes "first thinker, polymath, essentially anything"
a design property instead of a slogan.

---

## 7. Durability — the inheritance must outlive the vendor

A product built on *"what your predecessors left behind"* cannot be a place where work goes to die
when a company does. This is not a nice-to-have; under the v2 philosophy it is a correctness
requirement, and per §5 of the source report it is also a costly, legible trust signal.

- **Full export:** corpus, annotations, artifacts, review history, profile, contributions — plain
  Markdown plus a JSON manifest, on demand and complete.
- **Round-trip import** that reconstitutes the graph, including provenance and source edges.
- The `skill.md` framing already in the PRD is the right instinct. Extend it to everything.

---

## 8. Dependency order

```
provenance triple (§1)
        │
        ├──> Inheritance layer (§3) ──> Lineage (frontend §7) ──> Contribution (§5)
        │                                                              │
        ├──> Tutor (§2)                                                │
        │                                                              │
        └──> Canvas (§4) ─────────────────────────────────────────────┘
                                                              Domain packs (§6)
                                                              Durability (§7)
```

`01-frontend-constraint-document.md` §1–4 (tokens, a11y fixes, type, motion) has **no dependency on
any of this** and should run in parallel from day one.
