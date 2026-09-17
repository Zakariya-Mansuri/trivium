# Trivium v2 — Backlog

Everything the research produced, as tasks, with honest dependencies. **Living document** — update
status here rather than in the research docs, which are a record of thinking and should not be edited
to track work.

Legend: ✅ done · 🟢 ready (nothing blocks it) · 🟡 blocked on a decision · 🔴 blocked on another task

> **Note on "ready":** almost everything below is technically unblocked. The real question is not
> *what can we do* but *what order*. §5 answers that.

---

## 1. Done

| | Task | Where |
|---|---|---|
| ✅ | **Phase 0 — Teletype design foundation + four WCAG fixes** | `claude/impl-phase0-design-foundation` · `features/01-design-foundation.md` |

**Not yet merged to `main`.** That is task zero.

---

## 2. Backend

| # | Task | Size | Status | Source | Notes |
|---|---|---|---|---|---|
| **B1** | **Provenance triple** — `Provenance` enum, immutable column on `messages`, `knowledge_units`, `learning_artifacts`; guards in `profile.py` + `review.py`; `services/provenance.py`; `GET /provenance/ledger`; tests | **S** | 🟢 | `02` §1 | **The moat.** Smallest change with the largest downstream unlock. Only `authored` may write to `review_state` / `knowledge_profile_entries`. `generated → authored` requires accept **plus** a non-trivial edit. |
| **B2** | **Gate reasons in API responses** — every 409 carries a machine-readable `reason` + a human sentence | **XS** | 🟢 | `05` §6 readiness bar | Stated invariant: *a gate whose reason is invisible is indistinguishable from a bug.* Today the review gate returns 409 with nothing the UI can show. Pairs with **F4**. |
| **B3** | **Delivery channel** — one review-due nudge | **S** | 🟢 | `05` §7 | *"A spaced-repetition engine with no way to tell anyone a review is due has a broken engine regardless of how good the scheduler is."* Days, not weeks. Cheapest large win available. |
| **B4** | **FSRS migration** — replace SM-2 in `services/review.py` | **M** | 🟢 | `09` §2.5, `10` §6 | Flagged three times. Needs its own feature doc **and a migration story for existing `review_state` rows**. Must land **before B10 (the Survey)**: the Survey renders mastery as topography, so a weak scheduler becomes a visibly wrong map. |
| **B5** | **Export / durability** — plain-file export + round-trip import of corpus, profile, history, contributions | **M** | 🟢 | `02` §7 | A product built on inheritance cannot be where work dies with the vendor. Also a costly-signal trust feature. |
| **B6** | **Orientation Lite** — `orientations` table + decomposition; moves 1–4 only | **S** | 🟢 | `08` §9 | Recommended into Phase 1. One model call, two tables. Creates the learner's first two `authored` objects in three minutes. Best read: land **after B1** so provenance is right at creation rather than backfilled. |
| **B7** | **Tutor state machine** — `tutor_episodes`, `tutor_moves`, the declared move set, `commit`-before-`reveal` gate (409) | **L** | 🟢 | `02` §2 | Genuinely independent of Inheritance, but most valuable over inherited material. Every move logged the way `format_decisions` already is. |
| **B8** | **Inheritance layer** — `sources`, `source_edges`, `benches`, `annotations`; PDF/EPUB/paper/repo ingest | **XL** | 🟢 | `02` §3, `05` §7 | **The fix for the product's worst experience defect.** Cold start, perceived-value trough, empty first session and the 12-hour gap are one problem wearing four hats, and this is the only thing that solves any of them. Works with **zero** other users. |
| **B9** | **FTS5 + hierarchical summarisation** — cross-session and cross-corpus recall | **M** | 🔴 B8 | `03` §1.2b | Also the missing substrate for the PRD's "all-time" Learn span, which has no named mechanism today. |
| **B10** | **The Survey** — route computation over the mastery terrain | **L** | 🔴 B4, B8 | `10` §3 | Effort as the path integral of `(1 − mastery)`. The piece with real algorithmic content, and what turns the roadmap from a list into a computed claim. |
| **B11** | **Contribution layer** — `contributions`, `contribution_sources`, the publish gate | **L** | 🔴 B1, B8 | `02` §5 | The only gate that blocks by design. Published contributions re-enter as `Source` **with lineage attached** — this is the loop closing. |
| **B12** | **Domain packs** — extract the implicit code pack; add mathematics + text | **M** | 🔴 B8, 🟡 D4 | `00` §4 | One pack proves nothing; three proves the abstraction. |
| **B13** | **Canvas** — tiled surface, ink, drafts as movable `generated` objects | **XL** | 🔴 B1 | `02` §4 | *"Editing your own ink never triggers a model request."* |
| **B14** | **Skills as agentskills.io artifacts** | **S** | 🔴 B11 | `03` §1.2a | `services/skills.py` and `skill_reports` already exist — this is one serialiser on top. Makes a contribution *executable* inheritance. |

---

## 3. Frontend

| # | Task | Size | Status | Source | Notes |
|---|---|---|---|---|---|
| **F1** | **Merge Phase 0 to `main`** | XS | 🟢 | — | Task zero. |
| **F2** | **Migrate pages off legacy token aliases** | **M** | 🟢 | `features/01` §9 | 14 pages still use `ink-950`/`primary-600`. They render correctly — the alias map handles it — but the names now lie. Parallelisable, one page per PR. Delete the alias block when done. |
| **F3** | **Self-host font subset** | **XS** | 🟢 | `features/01` §5 | Explicitly scoped out of Phase 0. Removes a third-party LCP dependency. |
| **F4** | **Show gate reasons in the UI** | **XS** | 🟢 | `05` §6 | Pairs with **B2**. |
| **F5** | **Command palette (⌘K)** | **M** | 🟢 | `07` §3 | In Teletype this is the **primary input**, not a shortcut. Built and working in the Instrument Kit — port it. |
| **F6** | **Component kit carry-over** — line-numbered transcript, accordion, crafted empty state, forgetting curve, rebuild-the-diagram | **M** | 🟢 | `07` | All built and working in the Instrument Kit. Rebuild-the-diagram replaces the static Mermaid render. |
| **F7** | **Provenance material grammar on real objects** | **S** | 🔴 B1 | `01` §5 | CSS classes already shipped in Phase 0 (`.prov-inherited`, `.prov-generated`, `.prov-authored`). Just needs real data. |
| **F8** | **Landing page rebuild** | **M** | 🟡 D1, D2 | `01` §8 | Still the centred-hero/4-card skeleton and the shame hook. Includes the **Observatory diagram** as the philosophy figure. |
| **F9** | **Orientation UI** — the six moves, typed into one column | **M** | 🔴 B6 | `08` §2 | Move 2's answer opens the Survey for the first time, so the map arrives as a reward rather than a navigation chore. |
| **F10** | **Inherit district + reading surface** | **L** | 🔴 B8, 🟡 D5 | `10` §5 | Where the mono-at-length question actually bites. |
| **F11** | **The Survey (Atlas)** | **L** | 🔴 B10 | `10` §3 | The one Atlas surface. Contours, route, *unsurveyed*. |
| **F12** | **Tutor surface** — replaces `AgentChat.tsx` | **L** | 🔴 B7 | `02` §2 | |
| **F13** | **The Lineage** — territory already crossed | **L** | 🔴 B8 | `01` §7 | Atlas grammar, different question from the Survey. **Do not merge the two.** |

---

## 4. Decisions blocking work — yours

| # | Decision | Blocks | Recommendation |
|---|---|---|---|
| **D1** | **The tagline** | F8 | *"Everything you know, someone left for you. Learn it well enough to leave something."* |
| **D2** | **"Pious"** — internal philosophy only, or public surface? | F8, copy | Keep the *obligation* in public copy; keep the word in internal docs. Positioning call, not design. |
| **D3** | **First-release scope** | sequencing | Phases 0+1 alone are real and shippable (~3 weeks). Phases 0–2 are the smallest set that makes the v2 philosophy true. |
| **D4** | **Does coding remain the wedge?** | B12, B8 ingest priorities | Assumed yes, with two non-code packs as proof of generality. |
| **D5** | **Mono at length** — proportional face for inherited source text only? | F10 | **Ship the exception.** Inherit is where reading volume is highest, and readability failures are trust failures. |

---

## 5. Recommended order

Almost everything is unblocked, so sequence is the real decision. This order maximises unlock per unit
of risk.

```
  0 ── F1   merge Phase 0                                    XS
       │
  1 ── B1   provenance triple  ──────────┐                    S   ← the moat
       │                                  └─▶ F7  material grammar
  2 ── B2 + F4   gate reasons                                 XS  ← stated invariant, trivial
       │
  3 ── B3   delivery channel                                  S   ← fixes a broken engine
       │
  4 ── B6   orientation lite ────────────▶ F9  orientation UI S   ← fixes the first 90 seconds
       │
  5 ── B4   FSRS  ───────────────────────┐                    M   ← must precede B10
       │                                  │
  6 ── B8   INHERITANCE LAYER ────────────┼─▶ B9  FTS5        XL  ← the phase that changes
       │                                  │   F10 Inherit UI      what the product is
       │                                  └─▶ B10 ─▶ F11 Survey
       │                                      B11 ─▶ contribution
  ···  in parallel throughout: F2 token migration · F3 fonts · F5 palette · F6 kit
```

**The one fork worth arguing about:** after step 4, the choice is **Inheritance (B8)** or **Tutor
(B7)**. `05` §7 argues for Inheritance and I think it is right — the Tutor is a better experience for
someone who already has material, and Inheritance is the reason anyone has material at all.

**The one sequencing trap:** do not build the Survey (B10/F11) before FSRS (B4). The Survey renders
`review_state` as terrain, so an inaccurate scheduler produces a map that is *visibly* wrong — a much
more expensive failure than a number being slightly off in a table.

---

## 6. Next two feature documents

Per the working process, these need writing and approving before implementation:

1. **`features/02-provenance-triple.md`** — B1. The moat; everything visual depends on it.
2. **`features/03-fsrs.md`** — B4. Needs a migration story for existing `review_state` rows, and it
   is the one task here that changes behaviour for anyone already using the product.
