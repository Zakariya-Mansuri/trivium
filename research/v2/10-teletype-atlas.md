# Trivium v2 — The Resolved Direction: Teletype × Atlas

**Status:** Direction chosen. Supersedes the open question left by `09-ten-frontend-directions.md`.
**Live:** [Teletype Atlas](https://claude.ai/artifact/SAPguJkqkyEaTdYd8QQGnW) — both diagrams, and the
route toggle on the survey.

---

## 1. The decision

| | Direction | Role |
|---|---|---|
| **Primary grammar** | **05 · Teletype** | The grammar you *act* in. You address the product in text; the transcript is the record. |
| **The survey** | **06 · Atlas** | The surface you *orient* by. Where am I, what have I not shown, what is the cheapest way forward. |
| **Philosophy diagram** | **01 · Observatory** | Retained as an *argument*, not an interface. Landing page, orientation move 2, About. |

These are not two options blended into mush. **They do different jobs and meet at one seam:**

> **Atlas appears only where the question is spatial. Everywhere else is Teletype. There is no third
> style.**

---

## 2. The Observatory, drawn as a mechanism

The request was a diagram of the Observatory with a person at it. Drawn as a *mechanism* rather than
an illustration, because the metaphor turns out to carry the entire argument — including the
provenance triple, which nothing else has managed to show in one picture.

```
  THE CORPUS  ──inherited──▶  THE INSTRUMENT  ──offers──▶  a draft
  (inherited)                 extract · elicit             (generated,
       ▲                      · retrieve                    dashed, detached)
       │                           │                             │
       │                        [eyepiece]                  accept + edit
       │                           │                             │
       │                         ▼ YOU ──you write──▶   THE RECORD (authored)
       │                                                          │
       └──────── becomes inheritance for the next observer ───────┘
```

Three things the drawing establishes that prose had not:

1. **"The instrument does not add light."** A telescope resolves what is already there. That single
   property of the metaphor *is* the anti-dependence principle — and it is why the draft arrives
   dashed and detached rather than already written into your record.
2. **The three provenance states are spatially distinct.** Inherited is the far field. Generated is
   the unattached dashed box. Authored is the record with the ribbon-red edge. No badges needed.
3. **The return arc is the thesis.** The record flows back into the corpus. *Remove that one edge and
   the product is just a study tool.* It is the cheapest possible test of whether a design serves v2.

**Where it goes:** landing page, the orientation's move 2 ("who has already done it?"), and the About
surface. Observatory survives as an argument; it is not the app chrome.

---

## 3. Atlas, and what it actually optimises

The brief was that Atlas should be used because it *shows optimisation*. It does, and the thing it
optimises is precise.

**Elevation is demonstrated mastery.** Contoured ground is what a learner has shown they can do; blank
ground is unsurveyed. The map's question is not *how far is my goal* — it is **what is the cheapest
way there.**

### The computed result

Both routes were computed over the same generated terrain, not drawn by hand. Effort is the path
integral of `(1 − mastery)` along the route — it accumulates fastest where support is absent.

| Route | Distance | Effort | Unsurveyed ground |
|---|---|---|---|
| **Shortest** — straight at the aim | 643 | **475** | **71%** |
| **Cheapest** — via the ridge you already stand on | 730 | **209** | **22%** |
| | **+14%** | **−56%** | **−69%** |

> **The shortest route is not the cheapest route.** The cheapest one climbs the ridge the learner
> already occupies — Interleaving, then Elaboration — and only crosses open ground for the last short
> descent. It is 14% further and costs 56% less effort, because effort accumulates where mastery is
> absent, not where distance is long.

### Why this matters beyond a nice picture

**A learner cannot choose this route for themselves, because choosing it requires seeing terrain they
have not walked.** That is the clearest statement yet of what the roadmap in `08-…` is actually *for*
— and it converts the roadmap from a list of stages into a computed claim the product can be held to.

Atlas does not add a feature. It **draws the thing already specified in prose**: stages become
waypoints, prerequisites become the ridge, and `unsurveyed` replaces "0% mastered" — which the PRD
requires, because metrics must motivate rather than grade.

---

## 4. The seam

| District | Grammar | Why |
|---|---|---|
| Inherit | **Teletype** | Reading and annotating is textual; marginalia are typed into the same column. |
| Work | **Teletype** | The tutor's move set — elicit, probe, commit, reveal, contrast — *is* a transcript. |
| Retain | **Teletype** | Open recall is typing an answer. Nothing here is spatial. |
| Contribute | **Teletype** | A contribution is written; the publish gate is a checklist, not a place. |
| **The survey** | **Atlas** | The one Atlas surface. Reached from anywhere, lives nowhere else. |
| **The lineage** | **Atlas** | Territory already crossed. Same grammar, different question. |
| Landing / About | *Observatory* | The philosophy diagram only. One figure, not a visual system. |

### The rule that keeps them apart

From the Obsidian community, and it is the sharpest line of the whole research programme:

> *"Graph view is a map of the territory you've already crossed; Canvas is where you decide where to
> walk."*

**Atlas is the map. Teletype is where you walk.** They must not be merged — a map you can edit stops
being a record of what you did, and a workspace that auto-arranges stops being yours. Two surfaces,
two provenances: the survey is **generated from evidence and not editable**; the transcript is
**authored and nothing rearranges it**.

---

## 5. How the earlier work lands

| From | Carries over | Dropped |
|---|---|---|
| `07` component kit | Numbered transcript, accordion, forgetting curve, empty state, rebuild-the-diagram, command palette (now the *primary* input, not a shortcut) | Marquee ticker and pass cards — both fight a printout's stillness |
| `08` front door | The six orientation moves become literal: typed into one column. **Move 2's answer opens the survey for the first time**, so the map arrives as a reward rather than a navigation chore | — |
| `09` technique | Native CSS scroll-driven animations and View Transitions over a motion library; grain as a tiled data-URI; MX/semantic structure so contributions stay citable by other people's agents | — |
| `01` provenance grammar | Ruled ground / dashed float / ribbon edge. Legible in greyscale, no motion, no badge. One shadow in the system, on the draft, meaning *not yours yet* | — |

---

## 6. The two open items this does not settle

**1 · Monospace at length.** This is Teletype's one real weakness and the published page does not hide
from it — it is set entirely in mono, body text included, specifically so the call can be made from
reading rather than from theory.

If it tires the reader, the mitigation is **one narrow exception**: a proportional face for
*inherited source text only*, with everything Trivium generates or the learner types staying mono.
That keeps the grammar intact (the transcript is still a transcript) and removes the worst of the tax
from the surface where reading volume is highest. It is a deliberate, stated exception rather than a
drift — which is the standard the constraint document holds everything else to.

**Recommendation:** ship the exception. The Inherit district is where a learner spends the most
continuous reading time, and the field guide's own position is that readability failures are trust
failures.

**2 · FSRS.** Unrelated to frontend, flagged for the third time because this direction makes it
sharper: **the survey's terrain is only as honest as the mastery estimates underneath it.** Atlas
renders `review_state` as topography, so a weak scheduler becomes a visibly wrong map. FSRS has
replaced SM-2 as the 2026 standard; the shipped backend uses SM-2. This now deserves its own feature
document.

---

## 7. What happens next

1. This document replaces §4 of `01-frontend-constraint-document.md` — the constraint document is
   re-derived against Teletype tokens (contrast already validated: text 16.70 / 7.87 / 6.02, ribbon
   5.30, structural edge 3.50).
2. Phase 0 of `04-roadmap.md` executes against it.
3. Two feature documents follow, in this order:
   - **`features/01-provenance-triple.md`** — the moat, and everything visual depends on it.
   - **`features/02-the-survey.md`** — Atlas, including the route computation, since it is the piece
     with real algorithmic content and the one that makes the roadmap a claim rather than a list.
4. The FSRS question gets its own document, owned by whoever owns the review engine.

The remaining five decisions at the end of `04-roadmap.md` are still open — the tagline, "pious", the
first-release scope, and whether coding remains the wedge.
