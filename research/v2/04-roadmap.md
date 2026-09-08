# Trivium v2 — Sequenced Roadmap

Ordered by *value per unit of risk*, not by excitement. Each phase states what "done" means and which
claim it makes true. Phases 0 and 1 are independent and should run in parallel.

---

## Phase 0 — The constraint document, shipped

**Nothing new. Everything visibly different.** This is the cheapest large jump available and it
unblocks every later phase, because from here on every new screen is derivable from a system instead
of improvised.

| Work | Ref |
|---|---|
| Write the constraint document into `frontend/src/index.css` as the single source of truth | `01-…` §4 |
| Replace the palette: warm ink ground, one brass accent, two-tier line system | `01-…` §4.1 |
| Fix **SC 1.4.11** — structural edges to `--edge` (currently 1.27:1) | `01-…` §2.2 |
| Fix **SC 2.4.11** — 2px brass `:focus-visible` ring on every interactive element, `Button` included | `01-…` §2.2 |
| Fix responsive — sidebar → bottom rail below 768px; `mx-auto` on `main` | `01-…` §2.3 |
| Add `prefers-reduced-motion`; replace the single fade preset with the four motion bands | `01-…` §4.6 |
| Self-host and subset Newsreader + IBM Plex Sans/Mono; kill render-blocking Google Fonts | `01-…` §4.3 |
| `tnum` on every numeric cell in Metrics and Profile | `01-…` §4.3 |
| Three radii by role; **remove every pill** | `01-…` §4.5 |
| Delete the `◈ ⌨ ☰ ▣ ✦` glyph nav; adopt Lucide or Phosphor | `01-…` §2.1 |
| `Mermaid.tsx` reads tokens from CSS custom properties; reserve height to kill CLS | `01-…` §9 |
| Nine nav items → four districts | `01-…` §6 |
| Put the §12 pre-ship checklist in `.github/pull_request_template.md` | `01-…` §9 |

**Done means:** zero WCAG 2.2 AA failures on the audited criteria; a screenshot of any screen is not
mistakable for an unmodified template; every colour, size, radius and duration on screen traces to a
token with a written reason.

**Claim it makes true:** *this was built by someone who made decisions.*

---

## Phase 1 — The provenance triple

Small, and it is the moat. Runs in parallel with Phase 0.

- `Provenance` enum + immutable column on every content-bearing table (`02-…` §1)
- Service guards: only `authored` writes to `review_state` / `knowledge_profile_entries`
- `generated → authored` requires accept **plus** a non-trivial edit
- `GET /provenance/ledger`
- The material grammar in the UI — ruled ground / dashed float / solid brass edge (`01-…` §5)
- Tests, in the style of the existing review-gate tests

**Done means:** every object on screen declares whose work it is, without a badge; the Profile
provably counts only what the learner authored.

**Claim it makes true:** *"evidence over self-report" applies to everything, not just quiz results.*

---

## Phase 2 — The Inheritance layer

The phase that changes what the product *is*.

- `sources`, `source_edges`, `benches`, `annotations` (`02-…` §3)
- Ingest: PDF, EPUB, papers, repos, lecture transcripts
- `knowledge_units` gain edges to `Source`, not only to `Session`
- FTS5 + hierarchical summarisation for cross-session and cross-corpus recall (`03-…` §1.2b) — this
  is also what finally makes `PRD-v1.md` §6.1's "all-time" Learn span real
- The **Inherit** district: reading surface with three materials on one page

**Done means:** a learner who has never opened an agent chat still has a full Trivium loop, from a
book.

**Claim it makes true:** *you are working in a lab someone left you.*

> **Why this before the Tutor and the Canvas:** it works with zero other users, it is the only source
> of data for the Lineage, and it is what makes domain packs mean anything. It is also the riskiest
> phase, so it should not be last.

---

## Phase 3 — The Tutor

- `tutor_episodes`, `tutor_moves` with the declared move set (`02-…` §2)
- The `commit`-before-`reveal` gate — 409, mirroring the review gate
- `contrast` as the highest-value move
- Dialectic learner model steering the Tutor, **quarantined from the Profile** (`03-…` §1.2c)
- Replace `AgentChat.tsx` with the tutor surface

**Done means:** the tutor never answers first, the transcript is a provenance record, and every move
is inspectable the way `format_decisions` already is.

**Claim it makes true:** *one-on-one, and auditable.* (Cite real effect sizes. Never claim 2 sigma.)

---

## Phase 4 — The Canvas

- Tiled canvas, crop-and-geometry requests (`02-…` §4)
- Stylus/ink as first-class input
- Drafts as separate movable `generated` objects; editing your own ink never calls the model
- Manipulable widgets replacing static Mermaid renders

**Done means:** a learner can work spatially, and the machine's help is physically distinguishable
from their own hand.

**Claim it makes true:** *the help never becomes the work by accident.*

---

## Phase 5 — Contribution, the commons, and the Lineage

- `contributions`, `contribution_sources`, the publish gate (`02-…` §5)
- Published contributions re-enter the system as `Source` **with lineage attached**
- Skills emitted in the agentskills.io format — executable inheritance (`03-…` §1.2a)
- **The Lineage**: the one awe moment, budgeted properly (`01-…` §7)
- The end beat on every review session

**Done means:** the loop closes. One learner's Contribute is another's Inherit, in the data model.

**Claim it makes true:** *a learner's end is not to know; it is to contribute* — and it is measurable:
did a stranger inherit what you made?

---

## Phase 6 — Generality and durability

- Domain packs: code (extract the implicit one) + mathematics + text (`02-…` §6)
- Full plain-file export and round-trip import (`02-…` §7)
- One delivery channel beyond the web app for review nudges (`03-…` §1.2d)

**Done means:** the engine demonstrably serves a non-code domain, and the corpus outlives the vendor.

**Claim it makes true:** *first thinker, polymath, essentially anything* — as a property, not a slogan.

---

## The metric ladder, re-pointed

`PRD-v1.md` §9 defines three layers and files the important one under "v2+, mission-critical, hardest
to build." v2 promotes it:

| Layer | v1 framing | v2 |
|---|---|---|
| 1 — Engagement | Artifacts generated, reviews completed | Kept, but explicitly **not** a success metric |
| 2 — Retention | Recall success, retention curves | Kept. Now over the corpus, not just chats. |
| 3 — Independence | AI-assist ratio, error-repeat rate (proxies) | **Replaced by the direct measure: did someone inherit what you made?** |

Layer 3 was hard to build because v1 had no contribution surface to measure. Phase 5 creates one,
and the metric stops being a proxy.

---

## Decisions needed from you

Genuinely blocking; everything else in this research is actionable as written.

1. **The tagline.** Three candidates in `00-…` §1. Recommend *"Everything you know, someone left for
   you. Learn it well enough to leave something."*
2. **"Pious."** Keep in the internal philosophy, or carry it to the public surface? Positioning call,
   not a design one (`00-…` §1).
3. **The Observatory direction.** `01-…` §3 asserts it and derives the whole system from it. If it is
   wrong, §4 needs re-deriving — the *method* survives, the tokens don't.
4. **Scope of the first release.** Phases 0+1 alone are a real, shippable improvement and about three
   weeks. Phases 0–2 are the smallest set that makes the v2 philosophy true. Which is the target?
5. **Does coding remain the wedge?** `00-…` §4 assumes yes, with two non-code packs as proof of
   generality. If v2 leads with polymath breadth instead, Phase 6 moves much earlier and Phase 2's
   ingest priorities change.
