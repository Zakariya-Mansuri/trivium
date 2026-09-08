# Trivium v2 — Frontend Audit & Constraint Document

**Status:** Research / proposal.
**Method:** The shipped `frontend/` audited against the 13 documented AI-design tells and the WCAG 2.2
numbers in `frontend-research/research/attention-and-anti-slop-frontend-report.md` (§1.3, §9.5, §9.6),
then a constraint document written in the format that report's §10.4 prescribes as *"the single
highest-leverage anti-slop action available."*

All contrast ratios below were computed, not estimated.

---

## 1. Why a constraint document is the first deliverable

The report's central evidential finding (§10.4) is that Linear, Apple and Stripe look nothing like
each other yet share one thing: an exhaustively specific, internally consistent, non-default system
**with an explicit list of what is forbidden.** Linear bans gradients; Stripe's entire brand is a
gradient. Linear bans pill CTAs; Stripe mandates them. There is no correct surface style — there is
only the presence or absence of a system.

> *"Craft is not a look, it's a constraint system maintained with enough rigor that violating it would
> be immediately visible to the team that built it."*

Trivium currently has tokens but not a system: colours are declared in `index.css`, then duplicated by
hand in `Mermaid.tsx`, and there is no rule anywhere about what may use them. That is the gap this
document closes. **Section 4 onward is the deliverable; sections 2–3 are the justification.**

---

## 2. Audit of the shipped frontend

3,685 lines across 25 files. The code is clean and the information architecture is coherent. The
problems are systemic, not sloppy — which is why they are fixable in one pass.

### 2.1 Against the 13 documented tells — 7 hits

| # | Tell | Where it appears | Severity |
|---|---|---|---|
| 2 | **"AI purple"** | `--color-primary-600: #4f5ed6`, `--color-primary-500: #6172f3`. Squarely the indigo slop band — **and** within a few units of Linear's documented signature `#5e6ad2`. Two failures at once: where it isn't the default, it's someone else's identity. | High |
| 6 | **Dark mode + glow** | `shadow-lg shadow-primary-600/20` on every primary button (`ui.tsx:11`) and both landing CTAs (`Landing.tsx:58,120`). Linear's documented rule is *no drop shadows on dark, ever*. | High |
| 7 | **Glyphs standing in for icons** | `Layout.tsx:4-14` navigates with `◈ ⌨ ☰ ▣ ✦ ↻ ⬡ ↑ ∿`. Beyond the tell: these are font-dependent, so the nav renders differently on every OS and cannot be styled, sized or animated as a set. | High |
| 8 | **Default fonts, unmodified** | Inter + Sora, loaded at three and two weights respectively, with no tracking, no optical sizing, no deliberate weight ladder. Inter is the canonical tell. | High |
| 9 | **Centred-hero → card-grid skeleton** | `Landing.tsx`: centred eyebrow → centred `<h1>` → centred subhead → two centred buttons → a 4-card grid. This is the literal median SaaS page described in the report. | High |
| 5 | **Uniform radius** | `rounded-lg` on every control, `rounded-xl` on every card, `rounded-full` on every badge — two radii applied by habit rather than assigned by role. | Medium |
| 4 | **One motion preset everywhere** | A single `.fade-up` (0.35s ease) plus blanket `transition-colors`. No hierarchy of motion, no spring physics, and **no `prefers-reduced-motion` block anywhere in the codebase.** | Medium |

### 2.2 WCAG 2.2 — text contrast passes, structure fails

Text colour is genuinely good and should be preserved in spirit. Computed against the shipped tokens:

| Pair | Ratio | Verdict |
|---|---|---|
| `ink-100 #e3e8f2` on `ink-950` | **15.82** | Pass |
| `ink-200 #b6c0d4` on `ink-950` | **10.62** | Pass |
| `ink-300 #8a97b1` on `ink-900` | **6.26** | Pass |
| `primary-400` on `ink-950` | **7.20** | Pass |
| white on `primary-600` (button fill) | **5.38** | Pass |

Four structural failures, all numbered criteria:

1. **SC 1.4.11 (Non-text Contrast, 3:1) — the elevation system is below perceptual threshold.**
   `ink-700 #1f2940` on `ink-900 #0f1420` = **1.27:1**. `ink-600` on `ink-800` = **1.43:1**. Trivium
   borrowed Linear's "hairlines instead of shadows" principle but set the hairlines so dark that they
   convey nothing — so the app has *neither* shadows nor working borders, i.e. no depth mechanism at
   all. This is simultaneously the biggest visual-quality defect and a numbered violation.
2. **SC 2.4.11 (Focus Appearance) — `Button` in `ui.tsx` has no `focus-visible` treatment at all.**
   Keyboard users get the UA default over a dark ground, or nothing. The criterion requires a ≥2px
   perimeter at ≥3:1.
3. **Responsive layout is absent.** `Layout.tsx:21` — `w-56 shrink-0 … h-screen` with no breakpoint.
   On a 375px phone the sidebar consumes 60% of the viewport and there is no alternative nav. The
   product is desktop-only by accident, not by decision.
4. **CLS risk (SC-adjacent, §9.5 budget).** `Mermaid.tsx:62` renders into a zero-height `<div>` and
   injects SVG asynchronously. Every diagram is a guaranteed layout shift. Streaming tutor text has
   the same shape of problem.

### 2.3 Other systemic findings

- **`main` is `max-w-6xl` with no `mx-auto`** (`Layout.tsx:66`) — content hugs the left edge on wide
  displays, which reads as unfinished on exactly the large monitors the target user has.
- **No tabular numerals anywhere.** `Metrics.tsx` and `Profile.tsx` render changing figures in
  proportional Inter; they jitter on update. Stripe mandates `tnum` on every numeric cell precisely
  because this detail is invisible until it's missing.
- **Token duplication.** `Mermaid.tsx:11-17` hard-codes `#1f2940`, `#e3e8f2`, `#6172f3`, `#8a97b1`,
  `'Inter, sans-serif'` in JavaScript. These will drift from `index.css` on the first palette change.
- **Single hardcoded theme.** `html { background-color: … }` with no `color-scheme` and no light
  mode. Defensible as a *decision*; currently it is a default.
- **Fonts are render-blocking third-party.** A Google Fonts stylesheet in `<head>` with `display=swap`
  — an LCP dependency on a third-party origin plus a guaranteed flash of fallback text.

### 2.4 The report's own pre-ship checklist, answered honestly

| Question (§12) | Today |
|---|---|
| Is there a constraint document, and does the page follow it? | No document exists. |
| Would the hero be mistaken for an unmodified template? | Yes. |
| Are fonts and accent unmodified defaults? | Yes — Inter and indigo. |
| Does every animation use the same duration and easing? | Yes — one 0.35s fade. |
| Focus indicators ≥2px/3:1? Targets ≥24×24? `prefers-reduced-motion`? | Fail / pass / absent. |
| Is there one deliberate peak moment? | No. |
| Is every proof point real and verifiable? | **Yes** — the science table cites real researchers and real enforced behaviour. This is the strongest thing on the page and the v2 design should build on it. |

---

## 3. The direction: *the Observatory*

Two directions are foreclosed before the work starts. Indigo-on-slate is tell #2. The 2026 "tasteful
default" — cream ground, Instrument Serif or Fraunces display, sage-green primary — is tell #0, the
*new* median, and it is where a well-read designer's instincts now auto-complete to. Trivium must be
neither.

**Proposed direction: the working scientific instrument and its records.** Plate engravings, star
charts, ledger rules, marginalia, instrument bezels — not "paper," not "dashboard."

The justification is not aesthetic, it is semantic. The v2 philosophy is *"contribute through the lab
your predecessors left behind."* An observatory is the purest instance of that idea in the physical
world: you use an instrument someone else built, to make a record someone after you will read. The
visual language therefore isn't a mood — it is the thesis, rendered. That distinction matters,
because §7.5 of the report is precise about why unmodified defaults are dead signs: a signifier only
acquires meaning through consistent, specific, repeated use. A system chosen *because it means the
thing the product means* can accumulate that meaning; a system chosen because it looks nice cannot.

It also supplies, natively, three things Trivium currently lacks: a reason for tabular figures and
rule lines (records), a reason for generous negative space at the large end (vastness), and a
native answer to "what is the one awe moment" (§7).

---

## 4. THE CONSTRAINT DOCUMENT

> This is the artifact §10.4 prescribes. It is deliberately short, absolute, and full of prohibitions.
> Everything in `frontend/` should be derivable from it.

### 4.1 Colour

One accent. One. Reserved for exactly four uses: **primary action, focus ring, active district, and
the `authored` provenance mark.** Nothing else may be brass.

```css
/* Ground — warm near-black (iron-gall ink), NOT blue-slate */
--ground:        #0B0A08;
--surface-1:     #131110;
--surface-2:     #1B1815;
--surface-3:     #242019;

/* Text */
--text-hi:       #F2EDE3;   /* 16.96:1 on ground */
--text-mid:      #B9AF9F;   /*  9.14:1 on ground */
--text-lo:       #8A8172;   /*  5.15:1 on ground · 4.60:1 on surface-2 */

/* THE accent — brass */
--brass:         #C8963E;   /*  7.43:1 on ground · 6.64:1 on surface-2 */

/* Lines — two tiers, and the distinction is load-bearing */
--edge:          #786F5E;   /* STRUCTURAL. ≥3.27:1 on every surface. Any boundary that
                               identifies an interactive component or its state. */
--rule:          #403B32;   /* DECORATIVE only. 1.78:1. Table rules, section dividers,
                               ledger lines. Never the only cue for a control. */

/* Verdicts — earth, never traffic lights */
--verdict-strong:  #7C9B6E;  /* lichen   · 6.38:1 */
--verdict-partial: #B08A4A;  /* dim brass· 6.20:1 */
--verdict-weak:    #A85D4E;  /* iron oxide 4.09:1 */
```

**Why two tiers of line.** SC 1.4.11 requires 3:1 for boundaries that *identify a component* — it does
not require it for decorative rules. Collapsing both into one token is precisely how the shipped app
ended up with 1.27:1 borders on input fields. Splitting them makes the rule mechanically checkable:
*if it is the boundary of something clickable, it is `--edge`.*

**Why earth-tone verdicts.** Green/amber/red is a slop default and, per the PRD's own requirement,
judgmental ("motivating, not judgmental"). These three are desaturated far enough that none competes
with brass for saliency — which is the §2.4 Von Restorff requirement: the CTA must remain the
computable maximum on the page.

**Explicit don'ts:**
- ❌ No second chromatic accent. Ever.
- ❌ No gradient anywhere, including `bg-clip-text`.
- ❌ Brass is never a body-text colour and never a background for large areas. It is an action colour.
- ❌ Verdict colours never appear outside a graded-recall context.

### 4.2 Elevation

- ❌ **No drop shadows in the dark theme. Ever.** Depth is the four-step surface ladder plus `--edge`.
- ✅ **Exactly one shadow exists in the entire system**, and it means one thing:
  ```css
  --shadow-draft: 0 8px 28px -6px rgba(0,0,0,0.55);
  ```
  It is applied **only** to an unaccepted `generated` draft — the AI's proposal floating above your
  work, not yet yours. One shadow, one meaning. A learner will learn to read "this thing is hovering
  because it isn't mine yet" without being told.

### 4.3 Typography

Two families, both customised, one weight deliberately absent.

| Role | Family | Rules |
|---|---|---|
| **Expressive** — display, headings, the peak moment | **Newsreader** (variable `opsz` 6–72) | Never below 20px. Never above weight 600. Tracking −0.02em at ≥40px, −0.01em at 28–39px, 0 below. The `opsz` axis must actually be driven by size — that variation is the customisation. |
| **Structural** — UI, body, all prose | **IBM Plex Sans** | Body **16.5px / 1.55 / +0.005em**. |
| **Data** — figures, code, ledger | **IBM Plex Mono** | `font-feature-settings: "tnum" 1, "zero" 1` **mandatory on every numeric cell.** |

**Weight ladder: 300 / 400 / 600 / 700. Weight 500 is deliberately absent from the system.**

Justifications, since every one of these numbers must be defensible:

- *Why not Inter/Geist:* tell #8, and §7.5 — ubiquity has drained them of any signified.
- *Why Newsreader over Fraunces/Instrument Serif:* those two **are** the 2026 tasteful-default tell.
  Newsreader carries a real optical-size axis, so a 64px heading is a genuinely different letterform
  from a 20px one rather than the same outline scaled. Almost no generated site drives `opsz`, which
  makes it a cheap, real, §5.2-style cost signal.
- *Why 16.5px:* Plex Sans has a smaller x-height than Inter, so 16px Plex reads visibly smaller than
  16px Inter. 16.5 restores parity. It is a specific number with a specific reason — which is the
  entire point (cf. Apple's 17px).
- *Why Plex Sans + Plex Mono:* prose and data belong to one family, so a metrics table and a paragraph
  read as the same system. Trivium is a record-keeping product; that coherence is the identity.

**Explicit don'ts:**
- ❌ Never set the serif at weight 700, and never for running body copy.
- ❌ Never set UI text at weight 500 — it does not exist in this system.
- ❌ Never render a figure that can change in a proportional face.
- ❌ Do not load fonts render-blocking from a third-party origin. Self-host, subset, `font-display: swap`
  with a metric-matched fallback so there is no layout shift.

### 4.4 Spacing

```
2 · 4 · 8 · 12 · 16 · 24 · 32 · 48 · 72 · 108 · 162
```

4px base at the small end; **×1.5 from 48 upward.**

This is deliberately not Linear's flat 4px or Apple's 8px, and the reason is specific to this product:
Trivium must be *dense* where it is a tool (§3.7 — flow state means the chrome recedes and the work is
close together) and *vast* where it makes its argument (§2.5 — awe requires scale contrast against
acres of negative space). A single uniform scale can do one or the other. The 48→72→108→162 tail is
what makes the peak moment in §7 possible at all.

**Explicit don'ts:** ❌ No arbitrary values. If a gap isn't on the ruler, the layout is wrong, not the ruler.

### 4.5 Radius — exactly three, assigned by role

| Token | Value | Role |
|---|---|---|
| `--r-record` | **2px** | Data surfaces: table cells, code blocks, ledger rows, **badges** |
| `--r-control` | **6px** | Buttons, inputs, chips, toggles |
| `--r-container` | **10px** | Cards, panels, sheets, modals |

**❌ No pill radius anywhere in the product.** This is the system's most immediately visible signature
and it inverts the shipped `rounded-full` badge on purpose. Rationale: pills read as chat and social
software. Trivium is a record. A 2px badge sitting in a 10px card is a small, specific, deliberate
thing that no template produces — which is exactly what §5.2 means by a concentrated-effort signal.

### 4.6 Motion — four bands, by importance

| Band | Duration | Curve | Used for |
|---|---|---|---|
| `instant` | **0ms** | — | Provenance marks and state. **A `generated` block must never fade in charmingly — it must appear as a foreign object.** |
| `micro` | 120ms | `cubic-bezier(0.2, 0, 0, 1)` | Hover, toggle, focus |
| `transition` | 260ms | ease-out entering / ease-in leaving | Route and panel changes |
| `reveal` | 520–700ms | authored per instance | **At most two in the entire product**: the Lineage (§7) and the publish beat |

Anything the user can grab mid-flight — canvas objects, drafts, the review card — uses **spring
physics, not duration** (`stiffness 210, damping 28, mass 1`), because an interrupted spring continues
from real velocity while an interrupted easing curve restarts from zero and reads as mechanical (§9.1).

```css
@media (prefers-reduced-motion: reduce) {
  /* All bands collapse to 0ms except opacity crossfades, capped at 120ms.
     The Lineage becomes a static composed view, not a broken one. */
}
```

**Explicit don'ts:** ❌ No blanket `transition-colors` on everything. ❌ No fade-up-on-scroll preset.
❌ No motion without a state change to communicate.

### 4.7 Accessibility — numbered floors, treated as design bugs

| Criterion | Requirement | Current |
|---|---|---|
| 1.4.3 Text contrast | ≥4.5:1 | Passing — preserve |
| 1.4.11 Non-text contrast | ≥3:1 for any component boundary → use `--edge` | **1.27:1 — fix** |
| 2.4.11 Focus Appearance | 2px `--brass` ring + 2px offset, `:focus-visible`, on **every** interactive element | **Absent on `Button` — fix** |
| 2.5.8 Target Size | ≥24×24 AA everywhere; **≥44×44 on the ink/canvas toolbar** (stylus context justifies AAA) | Passing / N-A |
| Reduced motion | Honoured unconditionally | **Absent — fix** |
| CLS | <0.1 — reserve height for Mermaid, streamed text, and images | **At risk — fix** |
| LCP / INP | <2.5s / <200ms; self-hosted subset fonts | At risk (3rd-party fonts) |

---

## 5. The provenance grammar — rendered as material, not as badges

This is the one component spec that matters more than the rest combined, because it is where the
philosophy (`00-north-star.md` §3) becomes visible.

A badge saying "AI-generated" is a label the eye learns to skip in a week — the same banner-blindness
mechanism NN/g has confirmed across eye-tracking studies since 1997. Provenance must instead be a
**material property of the surface**, so it is read pre-attentively by the same Gestalt machinery
that separates figure from ground:

| Provenance | Material | Read as |
|---|---|---|
| `inherited` | Ruled ground — a faint `--rule` horizontal rhythm behind the text, like a ledger page. Never tinted. | *"This came from somewhere. It is a record."* |
| `generated` | **Dashed** `--edge` outline, no fill, plus `--shadow-draft`. Floating, provisional, visibly unfinished. | *"This is hovering. It is not yours yet."* |
| `authored` | Solid `--surface-2` fill, solid `--brass` hairline on the leading edge only. | *"You made this. It is on the record."* |

Rules:
- The three treatments must be distinguishable **in greyscale** and **without motion**. Test both.
- A `generated` block never animates on entry (`instant` band). It must feel like it arrived, not
  like it was performed.
- The transition `generated → authored` is the single most important state change in the product: the
  dashed edge closes and the shadow drops in one 260ms spring. That moment is the product's core
  argument, so it gets real craft budget.
- No badge, chip, or label anywhere duplicates this information. The material *is* the label.

---

## 6. Information architecture — four districts

Nine flat nav items become four districts (`00-north-star.md` §2), mapped to Lynch's legibility
elements (§6.2):

- **Paths** — one obvious main route per district. No competing CTAs in the same viewport.
- **Districts** — Inherit / Work / Retain / Contribute. Each is a *variation* on the system, never a
  different product:
  - *Inherit* — the most typographic; Newsreader-forward, widest measure, ruled grounds.
  - *Work* — the densest; Plex Mono-forward, tightest spacing, most surface levels.
  - *Retain* — the most spacious; large end of the spacing ruler, one thing per screen.
  - *Contribute* — the only district permitted large brass fills.
- **Edges** — a district change is marked by a background-value shift, not a heading.
  *The colour change is the divider* (Apple's rule, §10.2).
- **Nodes** — decision points (publish, accept a draft, grade a recall) get the clearest treatment on
  the page; this is where navigational anxiety peaks.
- **Landmark** — one persistent mark plus the current district name, in the same place always, so a
  learner can re-orient instantly after a long scroll or a back-navigation.

Responsive: sidebar → bottom rail below 768px; a dedicated stylus layout for canvas. Currently there
is nothing, and this is a straightforward fix.

---

## 7. The one awe moment: **the Lineage**

Every substantial product should have exactly one engineered peak (§3.5, §2.5), it should get
disproportionate craft budget, and nothing else should compete for the role.

**Trivium's is the Lineage — and it is not decoration, it is the thesis made visible.**

- **Trigger.** One control in the Inherit district; and automatically, once, immediately after a
  learner's first accepted contribution.
- **Behaviour.** The unit you are studying sits alone, centred, at normal scale. As you scrub, the
  camera pulls back continuously and without cuts: first the session it came from; then the source it
  was inherited from; then that source's own citations; then the corpus as a field of thousands of
  faint marks stretching past the viewport; and finally — brass, small, at the near edge — your own
  contribution, feeding forward into the dark.
- **Why it can only exist here.** §2.5's "revealed vastness" recontextualises what you just saw as
  part of something much larger. A template generator cannot produce this, not because it is hard to
  animate, but because it requires a data model with provenance edges and a philosophy that says what
  the edges *mean*. That is the §5 costly-signal argument in its purest form: this moment is
  expensive precisely because it is specific to one product's actual idea.
- **Budget guard.** Instanced points on canvas/WebGL, 60fps on a mid-range phone or it does not ship
  (§9.2). `prefers-reduced-motion` gets a single composed static frame — the same picture, no camera.

**And the end beat.** Peak–End says the final moment carries equal weight. A review session must never
end on "0 cards left." It ends on: *the one thing you now know that you did not yesterday, and the
name of the person or source it came from.* That single line closes the philosophical loop on every
session, cheaply, in text.

---

## 8. Landing page — the procession

Replace the centred-hero/4-card skeleton with a threshold → procession → arrival sequence (§6.3):

1. **Threshold.** Asymmetric, left-weighted. The load-bearing statement in Newsreader at ~72px,
   `opsz 72`, −0.02em: *"Everything you know, someone left for you."* No card grid, no second CTA, no
   gradient. Right-hand column holds a live, real fragment of an actual Lineage — product as proof,
   the Attio/Raycast pattern from the exemplary-sites list, not an abstract illustration.
2. **Procession.** The four estates as a scroll sequence, each with real product evidence. Section
   edges are background-value changes.
3. **Arrival.** The full Lineage zoom-out. This is the peak and it is placed last, not first — slop
   front-loads everything into the hero and has nowhere to go.
4. **Proof.** The existing science table is the best thing on the current page: real researchers, real
   enforced behaviour, no invented testimonials. Keep it, set it in Plex Mono with `tnum`, and place
   it adjacent to the primary CTA (proximity, §7.1). **The PRD forbids self-report in the profile;
   extend that rule to the marketing surface** — no fabricated logos, no invented user counts, ever.

---

## 9. Implementation notes

- **One source of truth.** Tokens live in `index.css` under `@theme` and are read from CSS custom
  properties everywhere — including `Mermaid.tsx`, which must stop hard-coding hex values
  (`getComputedStyle(document.documentElement).getPropertyValue('--brass')`).
- **Motion primitives before components.** Ship the four bands and the spring as named utilities so
  the wrong duration becomes hard to write.
- **Provenance is a data-model change first** (`00-north-star.md` §3). The material grammar in §5 is
  worthless without a trustworthy `provenance` column, and trivially cheap once it exists.
- **Delete the glyph nav** and adopt one real icon set (Lucide or Phosphor), stroke-matched to Plex's
  weight.
- **A pre-ship gate.** Put §12 of the source report in `.github/pull_request_template.md` as a
  checklist. The system decays the first time someone ships a `rounded-full` badge and nobody notices.

---

## 10. What this does not cover

- Light theme. The dark system is specified; a light counterpart needs its own ladder and its own
  one-shadow rule, and should be designed deliberately rather than derived by inversion.
- Illustration and diagram style for the Inherit district (plate-engraving direction is asserted here,
  not specified).
- Sound. §9.4 says default to none unless real craft time is available. Recommend none for v2.
- Localisation of colour and information density (§8.2–8.3), which matters if the audience is not
  single-culture, and which is a research task of its own.
