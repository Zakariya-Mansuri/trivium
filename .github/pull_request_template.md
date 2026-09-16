<!--
  Trivium PR template.
  The frontend checklist is the pre-ship review from the anti-slop field guide
  (§12), adopted because a design system decays the first time someone ships a
  violation and nobody notices. Delete the sections that don't apply.
-->

## What this changes

<!-- One or two sentences. What is true after this merges that wasn't before? -->

## Why

<!-- Link the approved feature document. Nothing ships without one:
     research/v2/features/NN-name.md -->

Feature document:

---

## Learning-science invariants

Tick only what this PR touches. These are enforced in code and covered by tests —
if a change here weakens one, say so explicitly rather than quietly.

- [ ] Retrieval over exposure — passive viewing still never updates mastery
- [ ] Reveal is still blocked until an attempt is written
- [ ] The diffuse-mode gate still holds, and **its reason is visible in the UI**
- [ ] Interleaving still draws from ≥2 benches where available
- [ ] The profile still counts only `authored` evidence and cannot be set by hand
- [ ] No claim on any surface is stronger than its evidence (effect sizes at replicated values)

## Frontend checklist

Skip if this PR touches no UI.

- [ ] Every colour, size, radius and duration traces to a token in `index.css`
- [ ] Structural boundaries use `--color-edge` (≥3:1); `--color-rule` is decorative only
- [ ] Every interactive element has a visible `:focus-visible` ring (2px, ≥3:1)
- [ ] Interactive targets ≥44×44
- [ ] Text contrast ≥4.5:1 — computed, not eyeballed
- [ ] No border radius; no pill anywhere
- [ ] No shadow except `.prov-generated`, which means *not yours yet*
- [ ] Motion varies by importance and never re-triggers; provenance never animates
- [ ] `prefers-reduced-motion` honoured, and the reduced path is **complete, not broken**
- [ ] Figures use tabular numerals
- [ ] Works at 375px
- [ ] No layout shift from async content (reserve height)
- [ ] Would a screenshot of this be mistaken for an unmodified template? If yes, what changed?
- [ ] Could you defend every component's presence by naming the human situation it serves?
- [ ] Read the copy aloud. Does it sound like it was written for one specific person?

## Verification

<!-- What did you actually run? Paste the output, including failures. -->

```
```
