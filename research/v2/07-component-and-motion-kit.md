# Trivium v2 — Component & Motion Kit

**Status:** Research. A live, interactive component and motion library.
**Live:** [Trivium Instrument Kit](https://claude.ai/code/artifact/5bf623dd-c75f-42db-9eca-7a2fd38ebe29)

The four directions in `06-frontend-directions.md` answered *what should it look like*. This answers
*what does it need to do* — and it is the layer that turns a chosen direction into something
implementable.

Built in direction A (Observatory) because that is the current recommendation, but **every component
here is plain HTML, CSS and vanilla JS with no framework**, so it ports into the React app as-is and
re-skins onto any of the four directions by swapping tokens.

---

## 1. The merge rule

The brief was to merge the best of many sites from `frontend-research/exemplary-sites/`. That is a
real risk: the field guide is explicit that "different for the sake of different is just slop with the
seed changed," and a page assembled from twenty admired sites is pastiche by default.

The rule that avoids it:

> **Borrow the mechanic, never the look.**
>
> Every component below behaves like its source and looks like Trivium. A merge of *looks* is
> pastiche. A merge of *mechanics* held together by one constraint system is a design system with
> good sources.

Concretely: we take Everlane's *idea* that a breakdown should animate rather than be listed — not
Everlane's colours, type or layout. We take Superhuman's *bet* that perceived speed is the brand —
not its palette. Nothing on the page would be recognisable as any of its sources from a screenshot,
and every behaviour would be.

The second rule, which follows from it:

> **A borrowed mechanic must serve something Trivium specifically needs.** If the only reason to add
> it is that a good site has one, it is decoration and it does not ship.

Each row of the inventory below has to pass that test, and the "why Trivium needs it" column is where
it is answered.

---

## 2. The inventory

Twenty components and behaviours, all live and interactive in the kit.

### Motion

| # | Component | Source | The mechanic — and why Trivium needs it |
|---|---|---|---|
| 01 | **Ticker** | cloudstudio.es | A marquee of live system facts. Trivium's carries provenance events, so it is a status readout rather than decoration. Pauses on hover. |
| 02 | **Scroll rail as navigation** | BASIC/DEPT | The progress bar *is* the nav — one element doing two jobs instead of two competing for attention (Hick's Law). |
| 04 | **Line reveal** | Locomotive · Obys | Staggered entry, **once**. Re-triggering on scroll-back is the animation-spam tell; the observer unsubscribes after the first intersection. |
| 08 | **Spring-physics draggable** | penecho · §9.1 | Interrupt the drag mid-flight and it continues from real velocity; a fixed-duration easing restarts from zero and reads mechanical. It is also the anti-dependence principle made physical — the draft is not yours until accepted. |
| 17 | **Scrollytelling** | The Pudding · NYT | Narrative intent with scroll as the pacing mechanism, a pinned graphic responding to stepped text. The only honest way to build the Lineage. |
| 19 | **Cursor-reactive field** | Cassie Evans | Ambient response, canvas-based, halts when the pointer leaves. Cheap warmth in an otherwise restrained system. |
| — | **Scroll-driven `opsz`** | Glossier | A variable font responding to scroll position. Newsreader's optical-size axis is driven by scroll on the masthead — a real customisation almost no generated site performs. |
| — | **Press `scale(0.97)`** | Apple §10.2 | One documented micro-interaction applied to every button in the product, not a library of different hover effects. |
| — | **Count-up on reveal** | cloudstudio · Datadog | Figures animate once, on first intersection, and never again. |

### Surfaces

| # | Component | Source | The mechanic — and why Trivium needs it |
|---|---|---|---|
| 03 | **Command palette (⌘K)** | Superhuman · Raycast | Perceived speed as the brand promise. For a keyboard-first audience this is the highest-value single app component. Full arrow-key and Escape handling. |
| 05 | **Interactive forgetting curve** | Bang & Olufsen · Lemon Squeezy | B&O make audio fidelity touchable; Lemon Squeezy embeds a working calculator instead of describing one. **Trivium's intangible is retention** — so the page should let a visitor *feel* spacing work rather than claim it does. Reviews land on real expanding intervals (day 1, 3, 7, 14, 24). |
| 06 | **Animated breakdown** | Everlane · Allbirds | Everlane animates cost; Trivium animates provenance. Both turn a number nobody reads into something people remember. Three benches show healthy, over-generated, and day-one states. |
| 07 | **Material grammar** | Linear §10.1 | Depth from a surface ladder and hairlines, never shadows — with exactly one shadow in the system, reserved to mean *"not yours yet."* |
| 09 | **Accordion** | cloudstudio.es | Progressive disclosure used to help people self-select, not to hide anything. Proper `aria-expanded` / `aria-controls`. |
| 10 | **Source pass cards** | cloudstudio.es | Identity cards that expand on click. Trivium's sources get faces — which is the entire point of inheritance. Each carries a deterministic signature plot (Oura/Datadog: data as brand asset). |
| 11 | **Bento, ruled** | Ramp | A bento grid is not a slop tell; an *unspecified* one is. Ramp formalised theirs with rules — fixed row height, whole-unit spans, one focal tile. |
| 12 | **Snap rail** | Fantasy · Cron | Horizontal browsing that adapts properly on mobile rather than being a desktop pattern squeezed down. |
| 13 | **Empty state + skeleton** | Retool · Mobbin | Retool's discipline is that empty states get as much design effort as populated views. **For Trivium this is not polish — it is the cold-start fix** (`05-learner-experience.md` §2). An empty state offers the next action; it does not apologise. |
| 14 | **Tabs** | — | Standard, but with roving `aria-selected` and arrow-key handling that most implementations skip. |
| 15 | **Tooltip** | — | Opens on hover **and** keyboard focus. The hover-only version is a bug, not a component. |
| 16 | **Toast** | — | `aria-live`, auto-dismiss, and never the only place a piece of information appears. |
| 18 | **Rebuild the diagram** | Ciechanowski · Hex | A diagram you look at is exposure — which Trivium's own principles classify as an illusion of competence. A diagram you *rebuild* is retrieval practice. **This is what replaces the static Mermaid render.** |
| 20 | **Before / after** | Modern Treasury · Databricks | Modern Treasury's whole pitch is one before/after diagram of an abstract process. Trivium's abstract process is the loop itself — and this is the clearest way to show what v2 changes. |

---

## 3. Rules that hold regardless of direction

These came out of building the kit and belong in whichever constraint document wins:

1. **Motion varies by importance, and never re-triggers.** Four bands, one of which is `0ms`.
   Anything carrying provenance is in the zero band — a generated block must appear as a foreign
   object, not perform an entrance.
2. **Every interactive element has a visible `:focus-visible` state.** No exceptions, including
   custom controls built from `div`s.
3. **`prefers-reduced-motion` is honoured unconditionally**, and the reduced path must be *complete*,
   not broken — the Lineage becomes one composed still frame, the ticker stops, the cursor field
   renders statically. Shipping a broken reduced-motion path is the amateur tell the award judges
   specifically look for.
4. **Canvas over DOM for anything ambient or generative**, with a frame-rate budget: 60fps on a
   mid-range phone or it does not ship (Resn's discipline — particles *and* graceful degradation).
5. **Every figure that can change is `tnum`.** (Stripe.)
6. **One micro-interaction for press, applied everywhere.** (Apple.)
7. **Nothing animates that a learner needs to read to make a decision.**

---

## 4. What is deliberately not here

Named so nobody adds them later assuming they were forgotten:

| Not included | Why |
|---|---|
| WebGL / Three.js scenes | Real cost, real differentiation — but it belongs to the Lineage alone (`01-…` §7), and canvas 2D covers it at a fraction of the risk. Revisit only if the peak needs it. |
| Page-transition choreography | Requires a router-level commitment. Worth doing, but it is a Phase 0+ decision, not a component. |
| Sound | The field guide says default to none unless real craft time is available. Recommend none for v2. |
| Hand-drawn illustration (Arc, Sentry, Wise) | A strong differentiator and a real commissioning cost. Worth proposing separately as its own feature document. |
| Horizontal-scroll *page* (Fantasy) | The rail is borrowed; the whole-page pattern is not. It fights reading, which is Trivium's central act. |
| A mascot (cloudstudio.es) | Charming, and wrong for a product whose credibility rests on not overclaiming. |

---

## 5. New source logged

**[cloudstudio.es](https://cloudstudio.es/)** — dark, monospace-forward developer-agency site.

- **Good for:** the ticker/marquee as a live status readout; numbered section indices; identity-card
  components that expand on click; FAQ accordions; live metric counters; and generally for showing
  how much interface energy a small surface can carry without clutter.
- **Refuse:** the mascot and the "digital workers with salaries" conceit — playful framing that would
  read as overclaiming on a product whose entire brand is not overclaiming. Also its density of
  simultaneous motion; Trivium needs one peak, not many.
