# Trivium v2 — The Learner's 180°

**Status:** Research. An examination of the product from the seat of the person using it, not from the
architecture diagram.

**Method:** Walk the shipped product minute by minute as a new learner, name where it breaks and why,
identify the moments that actually decide whether someone stays, then walk the same journey in v2.
Ends with a readiness bar — what has to be true before this is a product rather than a demo.

The finding worth stating up front:

> **The v2 philosophy is not a nicer story bolted onto v1. It is the fix for v1's specific, concrete
> retention failures.** Every gap identified philosophically in `00-north-star.md` shows up here as a
> place a real learner leaves. That is the strongest argument for v2 available, and it is a UX
> argument, not a branding one.

---

## 1. Who is actually sitting down

Not personas. Three situations, each with a different reason for being here and a different reason
for leaving.

**The Anxious Shipper.** Three years in, ships fast with Claude Code, and has started noticing they
can't explain their own auth flow in a meeting. Comes to Trivium out of low-grade dread. **Leaves
because:** the product confirms the dread and then asks for homework. Shame gets the signup; it does
not get the second session.

**The Beginner Who Suspects.** Six months of learning to code entirely through AI. Suspects — correctly
— that they are assembling rather than understanding. **Leaves because:** everything Trivium extracts
from their sessions is stuff the model told them, so reviewing it teaches them the model's answers,
not the subject. They need the inherited corpus more than anyone, and v1 has none.

**The Serious Autodidact.** Working through a real subject on their own — a textbook, a paper trail, a
domain they intend to contribute to. Not primarily a coder. **Leaves because:** v1 doesn't accept
their material at all. This is the person the v2 philosophy is written for, and today they cannot use
the product.

Two of the three are poorly served by v1 by construction. That is a positioning finding as much as a
UX one.

---

## 2. The shipped experience, minute by minute

### Minute 0 — the landing page

The headline reads *"Vibe code without getting dumber."*

**What the learner feels:** accused. The sentence's presupposition is that they are currently getting
dumber. This is a shame hook, and shame is an excellent acquisition mechanism and a terrible
retention mechanism — it produces a signup driven by anxiety, and anxiety-driven signups churn as
soon as the anxiety is either relieved or too expensive to keep feeling.

**Also true:** the science table below the fold is the best thing on the page. Real researchers, real
enforced behaviour, no invented testimonials. A learner who scrolls that far gets a genuine reason to
trust the product. Very few will, because the hero has already set the frame.

### Minute 1 — signup, then the void

Account created. Dashboard loads. **It is empty.**

This is the single largest experience problem in the product, and it is structural, not cosmetic:

> **Trivium cannot show a new learner anything until they have already done work somewhere else.**

The learner has arrived wanting to learn. The product's first instruction is, effectively, *go away,
use a different tool for a few hours, then come back and import.* There is a seeded demo account,
which means the team has felt this — but a real new user hits a void.

Every product with this shape either solves the cold start or dies at it.

### Minutes 2–5 — the import tax

To fill the void: install a browser extension (Chrome/Edge/Brave only), or paste a session by hand.

**What the learner feels:** asked to pay a setup cost before seeing any value. An extension install is
one of the highest-friction actions on the web — a permissions dialog, a trust decision, a browser
restart for some — and it is being requested *before the learner has any evidence the product works.*

Order is wrong. Value must precede friction.

### Minute 6 — extraction, and the "I already know this" problem

The session imports. Knowledge units appear: concepts, decisions, bug-fixes, patterns.

**What the learner feels:** flat. Every extracted unit is something they read twenty minutes ago in
their own chat window. The list is accurate and it is worthless *at that moment*, because recognition
is at its peak. The product's value is entirely in the future, and nothing on screen conveys that.

This is the **perceived-value trough**, and it arrives before any value has been delivered.

### Minute 8 — the first Learn, which is too easy

Learn produces a recall artifact. It asks the learner to recall something from eight minutes ago.

They get it right. Of course they do.

**What the learner feels:** mild insult. The one mechanic in the product with real evidential
grounding — the testing effect — is being demonstrated at the exact moment it cannot work, because
the material is still in working memory. The first experience of the core loop teaches the learner
that the core loop is trivial.

### Then: twelve hours of nothing

`first_review_at` gates the first review by twelve hours. Submitting early returns **409**.

The rule is correct. Diffuse-mode consolidation is real, the PRD cites it properly, and the gate is
enforced in code and covered by tests — which is exactly the rigour that makes Trivium credible.

**And it is, as currently staged, an onboarding catastrophe:**

> The product's first genuine moment of value is placed twelve hours after signup — past the point at
> which almost every new user has decided whether this thing is for them.

This is the sharpest conflict in the product. It is not a reason to weaken the gate. It is a reason
that **something else must occupy the first session**, and v1 has nothing to put there. (v2 does —
§4.)

### Day 1 — nothing comes to get them

The review queue is pull-only. There is no notification, no digest, no channel of any kind in the
shipped product. The PRD anticipates this (§6.5 lists push, email, digest as configurable) but none
is built.

**A spaced-repetition engine with no delivery mechanism is a dead engine.** The scheduling can be
perfect; if nobody is told, nothing is reviewed. This is the cheapest large win available anywhere in
the product.

### Day 3 — the first review that could have worked

If the learner has come back on their own — a small fraction — this is the first honest moment. The
material has decayed enough that retrieval is real work, and succeeding at it feels like something.

**This is where the product's actual value lives, and the entire journey to here is unguarded.**

### Week 2 — the honesty tax

The learner grades their own recall: *Got it · Partially · Didn't recall.* The AI suggests a verdict;
they confirm or override.

**What the learner feels:** a small cost for telling the truth. Marking "didn't recall" produces more
work, a lower profile, and a worse-looking record. Marking "got it" produces relief. The incentives
point away from the honesty the entire product depends on.

Nothing in the interface rewards the honest answer. It should be the opposite: an honest miss is the
single most valuable event in the system — it is the only moment that produces real information —
and it currently reads as a small failure.

### Month 3 — "so what?"

The Knowledge Profile says the learner has 47 concepts at some mastery. The metrics dashboard shows
trends.

**What the learner feels:** *and?*

There is no destination. The loop returns them to the start with a slightly better number. This is
the "no future" gap from `00-north-star.md` §1 — and it is not felt as a philosophical absence, it is
felt as **the point at which a diligent user runs out of reasons to continue.** The most committed
learners hit this hardest, because they are the ones who get far enough to notice.

---

## 3. The five hinge moments

Everything above compresses into five points where the product is actually decided.

| # | Moment | What must be true | Today |
|---|---|---|---|
| 1 | **The first 90 seconds** | Something happens that the learner could not have done themselves, before any setup is asked for | Empty dashboard; extension install requested first |
| 2 | **The first session's ending** | The learner leaves with something, despite the 12-hour review gate | Nothing to do; gate returns 409 |
| 3 | **The first honest miss** | "I didn't know that" feels like relief and information, not failure | Costs the learner; no reward for truth |
| 4 | **The return** | Something brings them back at the right time | Nothing does |
| 5 | **The destination** | Sustained work leads somewhere that isn't a bigger number about yourself | Nowhere |

**Three of the five are unaddressed in the shipped product, and two are actively working against it.**

---

## 4. The same journey in v2

What changes, moment by moment. Note how much of this is a *consequence* of the philosophy rather
than a feature added on top.

### Minute 0 — a hook that isn't shame

*"Everything you know, someone left for you. Learn it well enough to leave something."*

Same audience, opposite emotional register: obligation and inheritance rather than deficiency. It
frames the learner as someone with a debt worth paying rather than a problem to fix — and, unlike
shame, that framing survives repeated exposure.

### Minute 1 — the product is not empty

**This is the largest single experience unlock in v2, and it is a free side effect of the Inheritance
layer.**

The learner picks something to inherit — a paper, a chapter, a repository, another learner's
published contribution — and there is immediately material to work with. No extension. No prior work
elsewhere. No void.

> The cold-start problem does not get *solved* in v2. It **stops existing**, because a product built
> on inheritance is full before the learner arrives.

### Minutes 2–8 — the first session is reading and marking up, not quizzing

The learner reads on the Inherit surface. They annotate. Their marginalia are `authored`; the text is
`inherited`; the tutor's notes are `generated` — three materials on one page, distinguishable at a
glance without a single badge.

Now the tutor does the one thing a chat cannot: it `elicit`s before it explains, makes them `commit`
before it `reveal`s, and then `contrast`s — *"here is exactly where your account and the source's
diverge."*

**What the learner feels:** they did something. They produced marks on a page that are visibly theirs.
This is a real first session, and it is not a quiz about something they read eight minutes ago.

### The 12-hour gap is now full

The diffuse-mode gate stays exactly as it is — correct, enforced, tested. It stops being an
onboarding problem because **the first session is no longer about review.** Reading, annotating and
dialogue are not gated and should not be; only graded retrieval is. The science is unchanged; the
staging is fixed.

### The first honest miss becomes the most valuable event

Two changes, both cheap:

1. **The tutor's `contrast` move reframes the miss.** "You were wrong" is a verdict. "Your account
   held up until the third case, and here is the clause the source adds" is information. Same fact,
   completely different experience, and the second one is more useful.
2. **The interface must visibly reward the honest answer.** An honest miss is the only event in the
   system that produces new information — it should be treated as a find, not a fault. Concretely:
   the miss is what generates the next artifact, and the UI should say so.

### The return has a reason and a channel

One delivery channel (`04-roadmap.md` Phase 6), and — more durably — the learner has *unfinished work
in a corpus*, which is a far stronger return trigger than a due-card count. People come back to a
book they are halfway through. Almost nobody comes back to a queue.

### The destination exists

Sustained work now terminates in a contribution: an explainer, an annotated edition, a working
implementation, a proof — published with its lineage, becoming the next learner's inheritance.

**And the peak-end beat.** Every session ends on the one thing the learner now knows that they did not
before, and the name of the source it came from. Not "0 cards left." That single line closes the
philosophical loop on every single session, and it costs one query.

---

## 5. The experience risks v2 introduces

Being straight about the new failure modes rather than only the fixed ones.

| Risk | The learner's experience of it | Mitigation |
|---|---|---|
| **Gate fatigue** | v2 adds provenance gates, accept-plus-edit, and publish thresholds on top of v1's already-deliberate friction. A learner who hits three gates in one session experiences a product that says no a lot. | Every gate shows its reason at the moment it fires — the way the 409 should, and currently doesn't. **A gate whose reason is invisible is indistinguishable from a bug.** Cap the number of gates a single session can hit. |
| **Inheritance as homework** | "Pick a source to inherit" can feel like being assigned reading. | The first source should be offered, not requested — a short, excellent, complete thing that pays off inside one session. Never a 400-page book on day one. |
| **The contribution bar feels unreachable** | If publishing requires a high authored ratio and full source resolution, a beginner may never see the destination at all — the exact people who most need it. | Contributions must have small shapes. An annotated paragraph with a resolved citation is a contribution. Ship the smallest one first, and show it existing early. |
| **Provenance as surveillance** | "Everything I write is being classified" can read as judgment rather than record. | The materials are neutral and non-punitive by design; nothing is ever coloured red for being `generated`. The frame is a ledger, not a grade. |
| **Empty commons** | Early learners publish into a void. | Inheritance works with zero other users — books and repos are the corpus. The commons is additive, and should not be surfaced as an empty room. |

---

## 6. The readiness bar

What must be true before calling this ready. Ordered by how badly its absence hurts.

**Blocking — the product is not ready without these**

- [ ] A new learner reaches something of value **without installing anything and without prior work elsewhere.**
- [ ] The first session ends with a visible artifact of the learner's own making, *despite* the 12-hour review gate.
- [ ] Something brings the learner back at the right time — at least one delivery channel.
- [ ] Every gate that returns an error states its reason in the interface, at the moment it fires.
- [ ] An honest miss is visibly the most valuable thing a learner can report.
- [ ] The product works on a phone. (Today's sidebar has no breakpoint.)
- [ ] Keyboard users can see focus. (Today's `Button` has no focus style.)

**Required for the v2 claim to be honest**

- [ ] A learner can inherit something that is not their own agent output.
- [ ] A learner can produce something that leaves — however small.
- [ ] Provenance is visible without a badge, and legible in greyscale.
- [ ] The Profile counts only `authored` evidence, and the learner can see that it does.
- [ ] No claim on any surface is stronger than its evidence. Effect sizes cited at replicated values.

**Quality bar**

- [ ] Zero WCAG 2.2 AA failures on the audited criteria.
- [ ] One engineered peak moment, and one considered end beat per session.
- [ ] A screenshot of any screen is not mistakable for an unmodified template.

---

## 7. What this changes about the roadmap

The learner's view does not contradict `04-roadmap.md`, but it sharpens two things:

1. **The Inheritance layer (Phase 2) is not the third priority — it is the fix for the product's worst
   experience defect.** The cold start, the perceived-value trough, the empty first session and the
   12-hour gap are all one problem wearing four hats, and Inheritance is the only thing that solves
   any of them. It should move as early as it can be built safely.

2. **Delivery (currently Phase 6) is disproportionately cheap for what it fixes.** A spaced-repetition
   product with no way to tell anyone a review is due has a broken engine regardless of how good the
   scheduler is. Pull it forward; it is days of work, not weeks.

Everything else in the sequence holds.
