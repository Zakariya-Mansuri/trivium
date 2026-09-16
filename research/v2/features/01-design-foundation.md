# Feature: Design foundation — Teletype tokens and the four WCAG fixes

**Status:** Implemented (awaiting review)
**Phase:** 0 — `04-roadmap.md`
**Direction:** Teletype × Atlas (`10-teletype-atlas.md`)
**Implementation branch:** `claude/impl-phase0-design-foundation`

---

## 1. The one-sentence claim

Every screen in Trivium becomes legible to keyboard and low-vision users, works on a phone, and looks
like something a person decided — without changing a single behaviour.

## 2. Which part of the philosophy this serves

None directly, and that is the point. This is the substrate the field guide calls non-negotiable:
*"Trust is communicated non-verbally, before any claim is read."* A product whose entire argument is
**evidence over self-report** cannot ship four numbered accessibility failures and a desktop-only
layout, because those are evidence too.

## 3. The human situation

A learner opens Trivium on their phone during a commute and finds a 224px sidebar eating 60% of the
screen with no way to dismiss it. A keyboard user tabs to the primary button and sees no focus
indicator at all. Neither of them reaches the product.

## 4. Evidence

| Claim | Source | Strength |
|---|---|---|
| Component boundaries need ≥3:1 | WCAG 2.2 SC 1.4.11 | Normative |
| Focus indicators need ≥2px perimeter at ≥3:1 | WCAG 2.2 SC 2.4.11 | Normative |
| Interactive targets ≥24×24 CSS px | WCAG 2.2 SC 2.5.8 | Normative |
| Shipped card/input borders measured **1.27:1** and **1.43:1** | Computed, `01-…` §2.2 | Measured |
| `Button` has no `focus-visible` treatment | `ui.tsx`, read directly | Measured |
| Unmodified defaults are the strongest "slop" signal | Field guide §1.3, §7.5 | Argued, well-sourced |

## 5. Scope

**In:**
- Teletype token set in `index.css`, with legacy aliases so no page breaks
- SC 1.4.11 — structural borders to `--color-edge` (3.12–3.50:1)
- SC 2.4.11 — 2px ribbon `:focus-visible` ring, 2px offset, on every interactive element
- SC 2.5.8 — minimum 44×44 targets on controls
- Responsive shell — sidebar becomes a bottom rail below `md`; `mx-auto` on `main`
- Four motion bands + unconditional `prefers-reduced-motion`
- Nine nav items → four districts
- Glyph nav (`◈ ⌨ ☰ ▣ ✦ ↻ ⬡ ∿`) replaced with inline SVG icons
- Zero border radius system-wide (the Teletype signature)
- `tnum` on figures; `Mermaid.tsx` reads tokens from CSS and reserves height (CLS)
- One font family instead of two, cutting the render-blocking payload
- `.github/pull_request_template.md` carrying the field guide's §12 checklist

**Out (explicitly):**
- Self-hosted font binaries — a real improvement, deferred because it adds binary assets to the diff.
  Logged as follow-up; payload already cut by dropping from two families to one.
- Any change to routes, API calls, data, or copy
- The Inherit district and the survey — they need Phases 2 and 5
- Migrating page-level components off the legacy token aliases

## 6. Design

Against `10-teletype-atlas.md`. Two surface levels, not four — a printout has paper and one shaded
band.

| Token | Value | Role | Verified |
|---|---|---|---|
| `--color-paper` | `#F4F2EC` | the sheet | ground |
| `--color-surface` | `#E9E5DE` | cards, inputs, table headers | 1.16 vs paper |
| `--color-ink` | `#14120F` | primary text | 16.70 / 14.35 |
| `--color-ink-mid` | `#4E4A42` | body text | 7.87 / 6.76 |
| `--color-ink-lo` | `#605B52` | muted text | 6.02 / 5.37 |
| `--color-ribbon` | `#B23A2E` | THE accent | 5.30 / 4.73 |
| `--color-edge` | `#85807A` | **structural** boundaries | 3.50 / 3.12 |
| `--color-rule` | `#D5D1C7` | decorative rules only | 1.36 |
| `--color-recalled` | `#3F6B45` | verdict | 5.52 / 4.92 |
| `--color-partial` | `#7A5A10` | verdict | 5.69 / 5.07 |

All ratios computed, not estimated. **Primary and danger are distinguished by weight, not hue** —
primary is a ribbon fill, danger is a ribbon outline. That is the two-colour-ribbon grammar, and it
avoids two different actions sharing one colour.

Motion: `0ms` provenance/state · `120ms` micro · `260ms` transition · `560ms` reveal.
Provenance never animates.

## 7. Data model & API

None. No migration, no endpoint, no behaviour change.

## 8. Invariants and gates

- `--color-rule` may never be the only boundary of an interactive control; that is `--color-edge`.
- No element may set `border-radius` to anything but `0`.
- Nothing that carries provenance may animate.
- `prefers-reduced-motion` collapses every transition; the reduced path must be complete, not broken.

## 9. Failure modes

Legacy aliases invert the old dark ramp onto the new light one (`ink-950` → paper, `ink-100` → ink).
If any page used the ramp non-semantically — a dark value where it meant "dark" rather than
"background" — it will now read inverted. The migration path is to move pages onto semantic names;
until then the aliases are documented as deprecated in `index.css`.

## 10. How we'll know it worked

Layer 1 only, deliberately — this feature makes no learning claim. The tests are binary: zero
failures on the audited criteria, and the app usable at 375px.

## 11. Accessibility & performance

The whole feature. 1.4.11, 2.4.11, 2.5.8, reduced motion, and the Mermaid CLS fix.

## 12. Cost

About a day. Blocks nothing; unblocks every later phase, because from here every new screen is
derivable from a system instead of improvised.

## 13. What we're not sure about

**Monospace at length** (`10-…` §6). Everything is now IBM Plex Mono, which is the direction as
chosen. If the Inherit district's reading surface proves tiring in Phase 2, the stated exception is a
proportional face for *inherited source text only*. Not decided here.

---

## Approval

| | |
|---|---|
| **Decision** | |
| **Date** | |
| **Amendments** | |
