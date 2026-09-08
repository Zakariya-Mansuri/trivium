# Trivium v2 — Four Frontend Directions

**Status:** Research. Four competing design directions, each built as a working page so they can be
judged rather than described. **Pick one.**

Each direction is a complete system — not a mood board. Each carries the same content (same hero,
same four districts, same recall moment, same provenance materials, same science table, same peak)
so the comparison is about the system and nothing else.

| | Direction | Pole | Ground | Accent | Radius | Live |
|---|---|---|---|---|---|---|
| **A** | **Observatory** | Instrument & record | Warm ink-black | Brass `#C8963E` | 2 / 6 / 10px by role | [open](https://claude.ai/code/artifact/a6658db2-5dec-44ac-ad9d-275ed0a8718e) |
| **B** | **Foundry** | Loos — restraint | Industrial light grey | Signal `#C9391A` | **0px, everywhere** | [open](https://claude.ai/code/artifact/6cd766b3-76cb-46d2-990f-23131cd81783) |
| **C** | **Codex** | Editorial — the book | Cool bone | Oxblood `#8C2F39` | 0px | [open](https://claude.ai/code/artifact/974e2ea8-6120-4ef3-b5ea-6bc5e2b7b5b7) |
| **D** | **Atelier** | Constructivist — imbalance | Four swapping fields | Red + cobalt (fields) | 0px, 2px borders | [open](https://claude.ai/code/artifact/3221e11c-6b64-4c85-90d1-3cf45e239544) |

Every palette was contrast-checked numerically before it was drawn. No direction ships a value that
fails its own stated floor.

---

## The four, in one paragraph each

**A · Observatory** — the working scientific instrument and its records. Plate engravings, ledger
rules, marginalia, tabular figures. The justification is semantic, not stylistic: an observatory is
the purest physical instance of the v2 thesis — *you use an instrument someone else built, to make a
record someone after you will read.* Newsreader driven on a real optical-size axis, IBM Plex for UI
and data, one brass accent, three radii assigned by role, exactly one shadow in the system which
means *"this draft isn't yours yet."*
Reference set: Linear · Apple · Bloomberg Graphics · Oura.

**B · Foundry** — tool-grade restraint, and the only light-industrial option. Zero border radius on
every element in the product, a visible working grid, one signal orange, Archivo driven on a width
axis, no shadows at all. The fastest motion of the four (90ms micro) because a tool should feel like
it has already responded.
Reference set: Linear · Teenage Engineering · Rebellion · Warp · Raycast.

**C · Codex** — the page is a book page, and reading is the act. A real outer margin holding
marginalia, running heads and folios, a 68ch measure, drop caps, Spectral held at weight 200 and
never above 300 for display. The body face *is* the display face — the typographic argument being
that in a product whose central act is reading, the reading face must be good enough to carry the
headlines too. Deliberately not cream + Fraunces + sage, which is the 2026 tasteful-default tell.
Reference set: Aesop · Hermès · The Pudding · Ciechanowski · Sarah Drasner.

**D · Atelier** — deliberate imbalance as the argument. One twelve-column grid, four full-bleed
colour fields that swap the entire palette at each section boundary, Bricolage Grotesque at ~11vw
driven on optical-size *and* width axes, giant ordinals, 2px borders. The field change is the
divider — no section rules anywhere.
Reference set: Hoss Agency · Rebellion · Obys · Liquid Death · Instrument.

---

## Component coverage

Every item the field guide's §11 playbook calls for, present in all four:

| §11 component | A · Observatory | B · Foundry | C · Codex | D · Atelier |
|---|---|---|---|---|
| 11.2 Hero — asymmetric, one statement, one action | ✅ left-weighted, live ledger right | ✅ grid-overlay, live ledger | ✅ threshold, withholds | ✅ full-bleed type, drop-offset |
| 11.3 Nav & IA — Lynch paths/edges/districts/nodes/landmark | ✅ four districts | ✅ four districts, indexed | ✅ chapters + folio landmark | ✅ four districts |
| 11.4 Content — no uniform icon-card grid | ✅ estates with hierarchy | ✅ hairline grid | ✅ prose + marginalia | ✅ asymmetric blocks |
| 11.5 Proof — real, checkable only | ✅ science table | ✅ science table | ✅ science table | ✅ science table |
| 11.6 Colour & type system, documented | ✅ | ✅ | ✅ | ✅ |
| 11.7 Motion — four bands, reduced-motion | ✅ 0/120/260/520–700 | ✅ 0/90/200/560 | ✅ 0/140/320/640 | ✅ 0/110/280/620 |
| 11.8 Substrate — contrast, focus, targets, CLS | ✅ | ✅ | ✅ | ✅ |
| 11.9 The one awe moment | ✅ Lineage | ✅ Lineage | ✅ Lineage | ✅ Lineage |
| 11.10 Copy voice — one specific reader | ✅ | ✅ | ✅ | ✅ |
| — Provenance material grammar | ruled / dashed+shadow / brass edge | ruled / hatched / signal bar | ruled / dashed+shadow / oxblood | ruled / hatched / heavy rule |
| — Peak–End beat on every session | ✅ | ✅ | ✅ | ✅ |
| — Explicit "don'ts" list | ✅ | ✅ | ✅ | ✅ |

The provenance row is the one worth studying closely — it is where the four directions differ most,
and it is the product's most important mechanic. **Foundry and Atelier encode it without colour at
all**, so it survives greyscale by construction; Observatory and Codex use a single shadow to mean
"unaccepted," which is more elegant but leans on one channel.

---

## What each is actually good at, and what it costs

| | Strength | Cost |
|---|---|---|
| **A · Observatory** | The only direction whose visual language is derived from the philosophy *semantically* rather than by category association. Dark-first suits the Work district, where learners spend the most time. Best provenance mechanic of the four — one shadow, one meaning. | Dark-first is a commitment; the light theme needs designing rather than inverting. Less distinctive at a glance than D. |
| **B · Foundry** | Maximum density and speed. The most disciplined system — a violation is instantly obvious. The only light option that reads as a serious instrument rather than a document. | Almost no capacity for warmth or awe; its single peak carries the entire emotional load. Least differentiated from Linear at a glance. The Anxious Shipper may find it cold at the exact moment they need encouragement. |
| **C · Codex** | The best possible home for the Inherit district and the reading surface — which the learner-experience research says is where the first session must now live. Ages well; feels like something you keep for years. | Slowest and least dense. The Work district (canvas, tutor, live sessions) needs a much tighter sub-treatment or it will feel sluggish — real design work, not a detail. Sits nearest the tasteful-default trap and must be defended from drifting into it at every review. |
| **D · Atelier** | Strongest identity at a glance and the most headroom for the peak. The only one that will get talked about. | Highest risk and highest maintenance — four palettes to keep accessible, and every new screen is a judgement call rather than a lookup. **It fights the product's own purpose:** a learner in flow needs the interface to recede, and Atelier does not recede. |

---

## How to decide

Three questions settle it. They are about the product, not about taste.

**1. Which learner is primary?** (`05-learner-experience.md` §1)
- *The Serious Autodidact* — working through a real subject, not primarily a coder → **C**
- *The Anxious Shipper* — a working developer staying sharp → **A** or **B**
- *The Beginner Who Suspects* → **A** (warmest of the disciplined options)

**2. Where does the learner spend their time?**
- Reading and thinking → **C**
- Operating — canvas, tutor, dense sessions → **B**
- Genuinely both → **A**

**3. Is the product's job to recede or to announce?**
- Recede (flow state, §3.7) → **A**, **B**, or **C**
- Announce → **D**

---

## Recommendation

**A · Observatory as the product system, with C · Codex's reading pattern adopted into the Inherit
district.**

Reasoning, in order of weight:

1. **It is the only direction whose look is derived from the argument rather than from a category.**
   The other three are excellent instances of established genres — a tool, a book, a poster. The
   Observatory is the thesis rendered, which is exactly what the field guide's §7.5 says a real brand
   identity mechanically *is*: a signified built by consistent, specific use. That advantage compounds;
   the others don't.

2. **It is the only one that can hold both districts without a sub-system.** Codex cannot make the
   canvas feel fast. Foundry cannot make the reading surface feel worth lingering in. Observatory's
   spacing ruler was built for exactly this — 4px at the small end for density, ×1.5 above 48 for
   scale contrast.

3. **Its provenance mechanic is the best of the four.** One shadow in the entire system, meaning
   *"this is hovering because it isn't yours yet"* — a learner reads that without being told, and it
   is the product's core idea rendered as a physical property.

4. **Dark-first is correct for the actual usage pattern.** Long sessions, evening work, an audience
   that already lives in dark editors.

Two things to take from the losing directions regardless of the decision:

- **Codex's marginalia column** belongs in the Inherit district whichever system wins. The reading
  surface needs a real outer margin for annotations, and no other direction provides one.
- **Atelier's field discipline** — *the field change is the divider, and a field colour never appears
  inside another field's section* — is the cleanest solution to Lynch district edges of the four, and
  is worth adopting as the rule for how districts separate.

**If the decision is that the Serious Autodidact is the primary learner** — which is where the v2
philosophy actually points, and it is a legitimate reading — then the answer flips to **C**, and
Observatory's brass and one-shadow rule get carried into it. That is the one substitution that
doesn't cost anything.

**Atelier should not be the app.** It is a strong candidate for the marketing surface alone,
regardless of which system wins the product. That split is normal and honest; it is not a compromise.

---

## What happens after the choice

1. The chosen direction's constraint document replaces §4 of `01-frontend-constraint-document.md`
   (which currently specifies Observatory).
2. Phase 0 of `04-roadmap.md` executes against it — tokens, the four WCAG fixes, self-hosted type,
   four districts, motion bands, the PR checklist.
3. The other three stay in this folder as the record of what was considered and why it was rejected.
   That record is worth keeping: the most common way a design system decays is that nobody remembers
   what the alternatives were.
