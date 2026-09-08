# Trivium v2 — North Star

**Status:** Research / proposal. Not yet accepted into the PRD.
**Written against:** `PRD-v1.md`, `full-technical-document-v1.md`, the shipped `frontend/` and `backend/`,
the `frontend-research` repo (`research/attention-and-anti-slop-frontend-report.md`, `exemplary-sites/`),
and [penecho](https://github.com/penecho/penecho).

---

## 1. The shift, stated precisely

**v1 thesis (shipped):** *"Vibe code without getting dumber."*

**v2 thesis (proposed):** *A learner's ultimate goal is to contribute through the lab, environment and
resources their predecessors left behind.*

These are not the same claim wearing different words. They have different subjects, different verbs, and
different terminal states — and the v1 architecture cannot express the v2 one.

| | v1 | v2 |
|---|---|---|
| Grammar | Negation ("without getting dumber") | Assertion ("in order to contribute") |
| Subject | A user being protected from a harm | An heir who is expected to add |
| Time | Present-defensive | Past → present → future |
| Substrate | Your own agent chats | The inherited corpus + your work on it |
| Terminal state | A Knowledge Profile (a measurement of self) | A contribution (a thing that leaves you) |
| Failure mode it fears | Dependence | Sterility — knowing much, leaving nothing |
| Measurable when? | Only by proxy | Directly: did someone inherit what you made? |

### The three things v1 structurally cannot do

1. **v1 has no past.** Trivium ingests only the user's own agent sessions. A learner whose entire
   corpus is their own output has inherited nothing — there is no lab, no predecessor, no resource
   left behind. *Missing: the Inheritance layer.*

2. **v1 has no future.** The loop terminates at the Knowledge Profile. That is a mirror, not a door.
   Under v2 the loop must terminate in something that leaves the system and becomes the next
   learner's inheritance. *Missing: the Contribution layer.*

3. **v1 has no teacher.** It has a chat window and a scheduler. "One-on-one learning software" means a
   tutor with pedagogical intent and an inspectable move set, not an assistant with a message list.
   *Missing: the Tutor.*

Everything else in this proposal follows from those three gaps.

### The name was already right

*Trivium* is the medieval foundational three — grammar, logic, rhetoric — the inheritance you had to
take on before you were permitted to contribute to anything above it. The v1 tagline fights the name;
the v2 philosophy **is** the name. Keep the product name. Retire the tagline.

Three candidate formulations of the v2 line, from most concrete to most declarative:

- *"Everything you know, someone left for you. Learn it well enough to leave something."*
- *"Inherit the lab. Earn the bench. Leave the work."*
- *"A learner's end is not to know. It is to contribute."*

The first is recommended for the marketing surface: it contains the whole philosophy, names the
obligation, and is impossible to confuse with a productivity tool's tagline.

> **Note on "pious":** the source formulation says *pious* predecessors. That word carries a real
> claim — that the inheritance is owed reverence, not just use — and it is worth keeping in internal
> docs. On a public surface it will be read as denominational by some audiences and will narrow the
> product. Recommendation: keep the *obligation* ("someone left this for you") in the copy; keep the
> word in the philosophy doc. This is a positioning call, not a design one — flagging it, not deciding it.

---

## 2. The four estates

The v2 philosophy has a natural four-part structure. It is also, conveniently, a legible information
architecture in Kevin Lynch's sense (`frontend-research` §6.2) — four **districts**, each with a
distinguishable sub-identity inside one system:

| Estate | Question it answers | Contains |
|---|---|---|
| **Inherit** | What was left for me? | Corpus, sources, citation lineage, the reading surface |
| **Work** | What am I doing with it? | Tutor, canvas, sessions, projects |
| **Retain** | What can I actually do? | Learn, review, profile, metrics |
| **Contribute** | What am I leaving? | Drafts, published work, the commons |

This replaces today's nine flat sidebar items (Dashboard, Agent, Sessions, Projects, Learn, Review,
Profile, Improve, Metrics) — nine competing choices is a Hick's Law problem and, worse, it makes the
product look like a feature list instead of an argument.

The current product occupies **Work** and **Retain** only. That is the whole diagnosis in one line.

---

## 3. The invariant that makes the philosophy enforceable: the provenance triple

A philosophy that lives only in copy is a marketing claim. Trivium's existing credibility comes from
the fact that its learning-science claims are *enforced in code and verified by tests* (the review
gates, `first_review_at`, `MIN_REVIEW_GAP_HOURS`, the "passive viewing never updates mastery" rule).
The v2 philosophy needs the same treatment.

**Proposal — every object in the system carries one of exactly three provenance values, assigned at
creation, immutable thereafter:**

| Value | Meaning | Example |
|---|---|---|
| `inherited` | Came from a predecessor. Not yours. | A paper, a book chapter, an upstream repo, another learner's published contribution |
| `generated` | Produced by a model on your behalf. Not yours *yet*. | A tutor draft, an extracted unit, a suggested diagram |
| `authored` | You made it, under your own hand. | Your recall attempt, your annotation, your accepted-and-edited draft, your contribution |

Rules that fall out of it, all mechanically checkable:

- The Knowledge Profile counts **only** `authored` evidence. (This is v1's "evidence over self-report"
  rule, generalized from sessions to every object.)
- A `generated` object becomes `authored` only by an explicit accept **plus** a non-trivial edit —
  accepting verbatim leaves it `generated` forever.
- A contribution cannot be published unless it clears an `authored` ratio threshold and every
  `inherited` claim inside it carries a resolvable source edge.
- Provenance is rendered as **material, not as a badge** (see `01-frontend-constraint-document.md` §5).

This generalizes the `source_fidelity` (`native`/`wrapped`) column that already flows session →
knowledge unit → profile. It is a small data-model change and it is the entire moat: it is the one
thing in the product that a competitor cannot copy without also adopting the philosophy, because
without the philosophy it is pure friction.

---

## 4. Domain generality without mush

The v2 audience is "first thinker, polymath, essentially anything." The failure mode here is obvious:
a generic quiz generator that serves every domain badly. The PRD already anticipates this
("architecture should allow it later, but v1 ships coding only").

**Proposal — domain packs.** A pack is a small declared rubric, not a model. Each declares three things:

| | Unit of knowledge | Evidence of mastery | Shape of a contribution |
|---|---|---|---|
| **Code** (exists) | concept, decision, bug-fix, pattern | rebuild it / explain the tradeoff without the transcript | a PR, a library, a written post-mortem |
| **Mathematics** | definition, theorem, technique | re-derive it; state where the hypothesis is load-bearing | a solution, an exposition, a counterexample |
| **Philosophy / text** | argument, distinction, commitment | reconstruct the argument *and* its strongest objection | an essay, an annotated edition, a translation |
| **Empirical science** | mechanism, method, result | predict the result of a variant experiment | a replication, a review, a dataset |

Ship coding (done) plus **one humanities pack and one mathematics pack** — not because those two
markets matter yet, but because two non-code packs are the only honest proof that the engine
generalizes. One pack proves nothing; three proves the abstraction.

---

## 5. What to take from penecho — and what not to

[penecho](https://github.com/penecho/penecho) is an infinite-canvas visual-thinking tool: a
20,000×20,000 logical canvas with 512×512 tiles allocated only where ink exists, stylus/lasso input,
AI answers that arrive as separate movable drafts, sandboxed editable HTML/diagram widgets,
multi-provider execution, and shared public canvases ("Echoes") with *"craft lineage preserved
between versions."*

**Take these:**

1. **AI output arrives as a separate, movable draft that is not yours until accepted** — and
   *"editing your own ink never triggers an AI request."* This is the single most important thing in
   penecho for Trivium's purposes: it is the anti-dependence principle rendered as a physical
   property of the workspace rather than a policy in a settings page. Adopt it as a system-wide
   invariant (§3 above), not just a canvas behaviour.

2. **Handwriting / stylus as first-class input.** Not decoration. Van der Weel & Van der Meer
   ([*Frontiers in Psychology*, 2024](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2023.1219945/full);
   36 university students, 256-channel EEG) found handwriting produced widespread theta/alpha
   connectivity between parietal and central hubs that typing did not — connectivity patterns
   associated with memory encoding. **Honest caveat:** n=36, and EEG connectivity is a proxy, not a
   measured retention outcome. That is weaker evidence than the testing effect the PRD already builds
   on, and it should be cited at its true strength in any user-facing copy. But it is the right
   *direction* for a retention product, and it is a capability no competitor in this category has.

3. **Tiled canvas architecture** — tiles only where ink exists; send only the relevant crop plus
   geometry to the server. This is the correct way to build the spatial workspace and worth copying
   directly rather than rediscovering.

4. **Editable widgets as artifact output.** Trivium currently renders a static Mermaid SVG. A diagram
   the learner can *pull apart and rebuild* is a retrieval exercise; a diagram they look at is an
   illusion of competence — which v1's own principles already forbid.

5. **"Craft lineage preserved between versions"** — penecho's phrase, and it is exactly the v2
   philosophy applied to a canvas. Adopt the concept into the contribution model.

**Do not take these (scope discipline):**

- Ten configurable provider slots and CLI-executor modes. Trivium already has a provider abstraction;
  a provider *chooser* is a power-user feature that serves no pedagogical goal.
- The public "Echoes" gallery as designed. Trivium's commons must be provenance-gated (§3) — an
  ungated public gallery is the fastest possible way to fill the inheritance with slop.
- Four visual themes. Trivium needs exactly one system executed to Linear/Apple/Stripe rigor
  (see `01-frontend-constraint-document.md`), not four executed at 25% each.

---

## 6. On "100x"

One piece of straight feedback before the plan, because it changes where effort should go.

**A frontend rebuild alone is not 100x.** The current frontend is competent and generic — the audit in
`01-frontend-constraint-document.md` §2 shows it hits 7 of the 13 documented AI-design tells and has
four numbered WCAG 2.2 failures. Fixing all of that and rebuilding against a real constraint document
is a large, visible, worthwhile jump in perceived quality. It is roughly a 3–5× jump, and it is the
cheapest one available. It is not 100×.

**The 100× is that the product becomes the only one of its kind.** Right now Trivium is "spaced
repetition, but for your Cursor logs" — a good idea in a crowded category, defensible mainly on the
rigor of its learning-science enforcement. With the Inheritance and Contribution layers and the
provenance triple, it becomes something with no direct competitor: *a system that takes you from
what was left to you, through demonstrated understanding, to something you leave behind* — with the
whole chain auditable.

The frontend's job in that world is to make the chain **legible and felt**. That is a much more
interesting design brief than "make it look premium," and it is why the design work in
`01-frontend-constraint-document.md` is organized around rendering provenance and lineage rather
than around picking nicer colors.

Sequence accordingly: the constraint document and the a11y fixes first (cheap, immediate, unblocks
everything), then the provenance triple (small, and it is the moat), then the two new layers.

---

## 7. Honest risks

| Risk | Why it's real | Mitigation |
|---|---|---|
| **Scope explosion** | v2 adds three layers to a product that already has fifteen tables and nine routes | Phase 1 is a data-model change plus a design system, not a feature. Ship value before the canvas. |
| **The friction becomes the product** | v2 adds *more* deliberate difficulty (provenance gates, accept-plus-edit, publish thresholds) on top of v1's already-deliberate friction | Every gate must have a stated research basis and a visible reason in the UI, exactly as the review gates do today. A gate the user can't see the reason for is just a bug. |
| **Empty-commons cold start** | The Contribution layer is worthless with no contributors, and the Inheritance layer is worthless with no corpus | Inheritance ships first and works with *zero* other users — a solo learner still inherits books, papers and repos. The commons is additive, not load-bearing. |
| **Over-claiming on tutoring** | "One-on-one" invites a Bloom 2-sigma claim | **Do not make it.** Replications put tutoring nearer 0.36–0.79 SD, not 2.0, and the recent AI-tutor RCT evidence is real but modest. A product whose brand is "evidence over self-report" cannot cite a contested number. Claim mastery-based and adaptive; cite the actual effect sizes. |
| **Handwriting evidence is thin** | n=36 EEG study, proxy outcome | Cite it at its true strength. Ship ink because it is a better *interaction* for spatial/mathematical work regardless, and treat the retention benefit as plausible, not established. |
