# Feature: [name]

**Status:** Draft · Awaiting approval · Approved · Implemented · Rejected
**Phase:** [from `04-roadmap.md`]
**Author / date:**
**Implementation branch:** [filled in at approval]

---

## 1. The one-sentence claim

What becomes true for a learner when this ships. Not what gets built — what changes.

## 2. Which part of the philosophy this serves

Name the estate (Inherit / Work / Retain / Contribute) and the specific line in `00-north-star.md`
this makes real. **If it doesn't serve one, it doesn't ship.**

## 3. The human situation

Per the field guide §6.1: name the specific person in the specific moment this serves — not a persona,
a situation. *"A learner who has just been given an answer they don't understand and doesn't yet know
what to ask."* If this can't be written, the feature is a component looking for a reason.

## 4. Evidence

Research, prior art, or observed behaviour supporting this — **at its real strength.** Effect sizes,
sample sizes, and caveats travel with the claim. If the evidence is thin, say so here rather than
letting it get discovered later.

| Claim | Source | Strength / caveat |
|---|---|---|
| | | |

## 5. Scope

**In:**
-

**Out (explicitly):**
-

The "out" list is the more useful one. It is what stops the feature growing during implementation.

## 6. Design

Against `01-frontend-constraint-document.md`. Any token, radius, duration or colour used here must
already exist in §4 — **if it doesn't, this document must justify adding it to the system**, not
quietly use a one-off.

- Surfaces / screens affected:
- New components (and which existing one each is based on):
- Provenance treatment (`inherited` / `generated` / `authored` — §5 material grammar):
- Motion band(s) used and why:
- Does this compete with the one awe moment? If yes, resolve it here.

## 7. Data model & API

Tables added or changed, columns, migrations, endpoints. Note anything irreversible.

## 8. Invariants and gates

What must always be true, and what returns an error rather than silently degrading. Follow the
existing pattern: the review gates return 409 and are covered by tests. Every gate needs a reason the
learner can see in the UI — a gate whose reason is invisible is indistinguishable from a bug.

## 9. Failure modes

What goes wrong, what the learner sees, what the system does. Include the empty state and the
first-run state, which are usually where this kind of product actually lives.

## 10. How we'll know it worked

The metric or observation. Distinguish Layer 1 (engagement — **not** a success metric), Layer 2
(retention), Layer 3 (independence / contribution). Per `04-roadmap.md`, Layer 3 is the one that
tests the thesis.

## 11. Accessibility & performance

The specific numbers from `01-…` §4.7 that this feature touches. Contrast, focus, target size,
reduced motion, CLS. Treated as design bugs, not engineering afterthoughts.

## 12. Cost

Rough effort, riskiest unknown, and what it blocks or unblocks in `04-roadmap.md`.

## 13. What we're not sure about

Open questions for the approval conversation. Be specific — "which of these two, and why" beats
"thoughts?".

---

## Approval

| | |
|---|---|
| **Decision** | |
| **Date** | |
| **Amendments** | |
