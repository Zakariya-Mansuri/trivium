# Trivium v2 — Ten Frontend Directions

**Status:** Research. Supersedes `06-frontend-directions.md` as the live option set.
**Live:** [Ten Grammars](https://claude.ai/code/artifact/5a04d47c-4f9f-431d-b953-5c4658bbc318) — switch
between all ten; each renders the same corpus data in its own visual language.

---

## 1. Why the first four weren't worth a user's attention

The feedback was right and it is worth being precise about why, because the failure was structural,
not cosmetic.

| What went wrong | Why it matters |
|---|---|
| **They were design-system spec pages, not product.** Swatches, token tables, type specimens. Even carrying product copy, they read as documentation about an interface rather than an interface. | You cannot judge whether a user would be held by something that never behaves like the thing. |
| **The awe moment was described, never built.** All four talked about the Lineage; all four drew a static field of dots. | The peak was the whole differentiator, and it was a promissory note in every option. |
| **Three of four were quiet variations on one idea.** Observatory, Foundry and Codex are all "restrained system, single accent, careful hairlines." The variance was in detail, not in what a user would feel. | Offering three flavours of restraint plus one you're told not to use is not a real choice. |
| **They varied palette, not thesis.** Every one answered "what should it look like." None answered "what *is* this interface." | Colour is reversible in an afternoon. The interaction thesis is not. |

**The correction:** these ten vary by **interaction thesis** — what the interface fundamentally *is*.
A record, a tool, a book, a poster, a printout, a map, a table, an edition, a collection, an
instrument. And each one renders the same data live, so the comparison is about the grammar rather
than about the copy.

---

## 2. What the research pass turned up

Fresh sources (all logged in the README), because the previous pass leaned entirely on the internal
field guide.

### 2.1 What the award circuit is actually rewarding in 2026

From a judged review of the year's Awwwards/FWA/CSSDA winners:

- **"WebGL used for atmosphere instead of spectacle."** The 3D that wins frames the work; the 3D that
  loses *is* the work. Directly relevant: Trivium's plate should make the corpus feel vast, not
  perform.
- **"Transitions that never call attention to themselves"** and interfaces that feel like *one
  continuous surface* rather than a sequence of pages. By-Kin won a Developer Award for frame-by-frame
  discipline, not for effects.
- **"A confident grid that breaks at exactly the right moments."** Not asymmetry everywhere — one
  authored break.
- Kinetic typography tuned so **motion never blocks reading.**
- The disqualifier, stated flatly: **performance failure on mid-range devices**, and *no site
  overcomes weak art direction through motion alone.*

### 2.2 What is now saturated

- **Generic AI imagery**, with a specific over-used yellow now recognisable at a glance.
- **Animation everywhere** because it became easy.
- **Glassmorphism**, back in restrained form but noisy when every card uses it.
- **Saturated colour used uniformly** — the trend works through contrast, not ubiquity.
- **Heavy 3D**: bounce rates rising ~40% where added without optimisation.
- **Low-contrast "elegant" palettes** — an accessibility and trust failure.

### 2.3 Named 2026 movements worth knowing

| Movement | What it is | Failure mode |
|---|---|---|
| **Tactile brutalism** | Raw engineered surfaces; 0px or fully pill; 1px borders; **no shadows — depth from overlapping grid lines and z-index** | Without precision it reads as unfinished rather than deliberately raw |
| **Chromatic extremes + CSS texture** | Near-black interrupted by one saturated acid colour; noise and film grain as lightweight overlays instead of WebGL | Over-saturation becomes chaos; fatiguing rather than arresting |
| **Typography as primary architecture** | Viewport-scaled type replacing hero imagery; **variable-font axes mapped to scroll position**; neo-serif paired with monospace | Readability collapses at small viewports |
| **The bento paradox** | Modular grids via native CSS Grid, state-aware | Amateur versions duplicate DOM per breakpoint, doubling page weight |
| **Machine Experience (MX)** | Semantic structure and ARIA so **LLM agents can parse and cite the page** | Unsemantic markup makes content invisible to AI search |
| **Carbon-aware design** | Dark-first defaults, vectors over photography, strict budgets | Over-optimising sacrifices fidelity; dark-only alienates bright-environment users |

**MX design is a genuine product finding, not just a frontend one.** A learner's published
contribution should be structured so that other people's *agents* can parse and cite it. That is
`03-reference-systems.md`'s "executable inheritance" argument arriving from a completely different
direction, and it strengthens it.

### 2.4 Technique that is newly available

- **Native CSS scroll-driven animations** — `animation-timeline: scroll()` and `view()`. Chrome/Edge
  115+, Firefox 132+, Safari 18+; ~90% support in 2026. Runs off the main thread, no JavaScript, no
  GSAP. Note: setting a scroll timeline makes `animation-duration` meaningless — scroll position
  *is* the timeline.
- **View Transitions API** — full cross-browser support in 2026.
  Together these replace most of what GSAP ScrollTrigger was needed for, at a fraction of the weight.
- **Film grain**: `feTurbulence` is computed per-pixel and is a real paint cost on mobile at
  full-viewport size. The correct implementation is a **small tiled pre-rendered noise** with
  `will-change: transform` to isolate the layer. The showroom does exactly this.

### 2.5 Two findings that changed the design

**On canvases, from the Obsidian community — the sharpest single line in the whole pass:**

> *"Graph view is a map of the territory you've already crossed; Canvas is the workspace where you
> decide where to walk."*

That is precisely Trivium's split. **The Lineage is the map of territory crossed** (inheritance,
generated, not editable). **The Workbench is where you decide where to walk** (authored, arranged by
you). They are different surfaces with different provenance, and conflating them would be a
significant design error. Direction 07 exists because of this line.

**On collections, from museum digitisation practice:**

> Catalogue numbers form the critical link between a specimen, its associated data, and its
> derivatives (casts, images, molds).

A museum accession number *is* a provenance edge. Natural-history cataloguing has solved Trivium's
exact problem, with three centuries of practice and a settled vocabulary — accession, determination,
provenance, derivative. Direction 09 borrows that vocabulary wholesale.

**One product finding, incidental but material:** **FSRS has replaced SM-2** as the standard
spaced-repetition scheduler in 2026. The shipped backend uses SM-2. Worth a separate look — not a
frontend matter, flagged here because it surfaced during this pass.

---

## 3. The ten

Each defined by its **interaction thesis** — what the interface fundamentally is. All ten palettes
were contrast-checked numerically before anything was drawn: text ≥4.5:1, structural edges ≥3:1,
accent legible on both ground and surface, ground legible on accent fill. **Zero failures.**

| # | Direction | Interaction thesis | Ground | Accent | Recedes | Announces |
|---|---|---|---|---|---|---|
| 01 | **Observatory** | You take readings. The interface is calibrated apparatus. | `#0B0A08` | `#C8963E` brass | ●●●●● | ●●○○○ |
| 02 | **Foundry** | Density and speed. Nothing decorative survives the grid. | `#E4E2DD` | `#B93518` signal | ●●●●● | ●●○○○ |
| 03 | **Codex** | Reading is the act. The margin is a first-class column. | `#FAFAF8` | `#8C2F39` oxblood | ●●●●○ | ●●●○○ |
| 04 | **Atelier** | The interface argues. Whole fields swap; the colour change is the divider. | fields | `#BF251A` | ●○○○○ | ●●●●● |
| 05 | **Teletype** | You address the product in text. The transcript is the record. | `#F4F2EC` | `#B23A2E` ribbon | ●●●●○ | ●●●●○ |
| 06 | **Atlas** | Knowledge is territory. Mastery is elevation; contours are confidence. | `#EFE9DC` | `#AD3E34` route | ●●●○○ | ●●●●○ |
| 07 | **Workbench** | There are no pages. Objects on one surface; navigation is pan and zoom. | `#16191C` | `#E0784F` | ●●●○○ | ●●●○○ |
| 08 | **Broadsheet** | Your learning arrives as an issue — dated, numbered, with a lead story. | `#F2EFE8` | `#B0342B` spot | ●●●○○ | ●●●●○ |
| 09 | **Cabinet** | Every unit is a catalogued specimen with accession, determination, provenance. | `#E9E2D2` | `#A63A2C` | ●●●●○ | ●●●○○ |
| 10 | **Signal** | Knowledge state as continuous live signal, not lists. | `#06080A` | `#E8734A` | ●●●●○ | ●●●●○ |

### The plates

The strongest evidence that these are ten *grammars* and not ten palettes: each renders the **same
corpus** — 1,400 marks, 86 edges, one contribution — in its own language.

| Direction | The plate |
|---|---|
| Observatory | A field of light, pulled back, with the contribution as a brass point |
| Foundry | Plotted on an engineering grid with real axes |
| Codex | Engraving hatch — each mark a burin stroke |
| Atelier | Hard geometric fields, the contribution as a knocked-out square |
| **Teletype** | **The corpus typed as ASCII density** — `.:-=+*#%@` by mark count |
| **Atlas** | **True contour lines**, elevation = demonstrated mastery, with your dashed route and *unsurveyed* territory |
| Workbench | Cards pinned on a surface with connector lines, one card yours |
| Broadsheet | Halftone density under column rules, with a lead-story bar |
| **Cabinet** | **Specimens pinned to a sheet with accession tags**, one accessioned in red |
| Signal | Three oscilloscope retention traces, review markers visible |

Teletype, Atlas and Cabinet are the three that could not have come out of a palette swap — they
required a different way of thinking about what the data *is*.

### Signature elements

Exactly one per direction, and never more — Codex gets the margin column, Teletype the numbered
transcript, Atlas the coordinate strip, Broadsheet the masthead, Cabinet the determination label,
Signal the readout bar. Four directions get none, deliberately.

> Implementation note worth keeping: the reveal rule must carry the `display` value, never the base
> class. Putting `display:flex` on `.sig-masthead` and `display:none` on `.sig` lets the base class
> win by source order, and every signature leaks into every direction. This was a real bug, caught
> by rendering rather than by reading.

---

## 4. How to choose

Three questions, in order. They are about the product, not about taste.

**1. Does the interface need to recede or to announce?**
A learner in flow needs it to disappear (§3.7 of the field guide). A first-time visitor needs it to
arrest. **No direction is best at both** — that is the actual decision.
→ Recede: 01, 02, 03, 09. Announce: 04, 06, 08, 10. Both, partially: 05, 07.

**2. Which district carries the most time?**
- *Inherit* (reading) → 03, 06, 09
- *Work* (canvas, tutor, dense sessions) → 02, 05, 07
- *Retain* (review, profile) → 01, 08, 10

**3. Which learner is primary?** (`05-learner-experience.md` §1)
- Serious autodidact → 03, 09, 06
- Anxious shipper → 01, 02, 05
- Beginner who suspects → 09, 08, 01

---

## 5. Recommendation

**A pairing, not a single direction — and this is the honest answer rather than a hedge.**

> **09 · Cabinet for the product. 04 · Atelier for the landing surface.**

**Why Cabinet for the product.** It is the only one of the ten whose grammar *is* the philosophy
rather than a mood that suits it. Trivium's thesis is inheritance and provenance; museum cataloguing
is a three-century-old, fully worked-out practice for exactly that, complete with a vocabulary the
product can adopt without inventing anything — accession, determination, provenance, derivative. A
knowledge unit rendered as a catalogued specimen with a real identifier is the provenance triple made
visible without a single badge. It also happens to be warm, which matters: the anxious learner and
the beginner both need warmth at the moment they first miss, and Observatory and Foundry have none to
give. Its trade is real — it is closest of the ten to twee — and the mitigation is the one already
written into its don'ts: the grammar is typographic, never photographic. No torn edges, no paper
textures, no fake ageing.

**Why Atelier for the landing.** The product must recede; the landing must arrest. Atelier is the
only one with real headroom for the peak, and using it *only* where announcing is the job resolves
its fatal flaw instead of fighting it.

**Second choice, if a single system is required for both:** **05 · Teletype.** It is the only
direction that is genuinely strong at receding *and* announcing, it is the most distinctive of the
ten at a glance, and its interaction thesis — you address the product in text — matches the Tutor and
the command palette better than any other. Its cost is honest and known: monospace body text at
length is harder to read, which is a real tax on a product whose central act is reading.

**Observatory (01) remains a defensible safe choice** and is the one to pick if the goal is to ship
Phase 0 fastest with the least risk. It is also the least memorable.

**What to take regardless of the choice:**
- Atlas's **contour idea** — mastery as elevation, and *unsurveyed* rather than "0%" for what you
  have not touched. That framing is motivating rather than judgmental, which the PRD requires.
- Signal's **decay traces** for the retention view specifically — no other grammar shows the
  mechanism working.
- The **map/canvas split** from §2.5: the Lineage is territory crossed, the Workbench is where you
  decide where to walk. Do not merge them.
- Native **CSS scroll-driven animations** and the **View Transitions API** over a motion library.
- **MX/semantic structure** so published contributions are citable by agents.

---

## 6. New sources logged

| Source | Good for | Refuse |
|---|---|---|
| 2026 award-circuit review (By-Kin, Iventions, Mat Voyce, Uncommon, Minh Pham) | "WebGL for atmosphere, not spectacle"; transitions as one continuous surface; the grid that breaks once; performance on mid-range devices as a hard gate | The assumption that a motion library is required — most of it is now native CSS |
| 2026 trend surveys (Figma, Fireart, Bubble) | Named movements: tactile brutalism, chromatic extremes, type-as-architecture, MX design, carbon-aware design | Trend-following wholesale; the saturated list in §2.2 is a list of things to avoid, not adopt |
| MDN / Chrome — scroll-driven animations, View Transitions | Production-ready native technique with real support numbers | — |
| Codrops / performance write-ups on `feTurbulence` | Grain as texture, and the honest mobile paint cost | Live full-viewport SVG filters |
| Obsidian Canvas community | **The map/canvas distinction** — the single most useful line of the pass | Force-directed graph views as a primary navigation surface; they look impressive and navigate badly |
| Museum digitisation practice (Smithsonian, AMNH, herbarium literature) | Accession/determination/provenance vocabulary; catalogue numbers as provenance links | Skeuomorphic ageing — the borrow is the cataloguing discipline, not the patina |
| Spaced-repetition app landscape 2026 | **FSRS has replaced SM-2** as the standard scheduler — a product finding, flagged for separate review | "All-in-one study platform" feature-creep framing; Trivium is not competing on breadth of study tools |
