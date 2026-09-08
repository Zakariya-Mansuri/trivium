# Trivium v2 — Research

Research and proposals for the v2 direction. **Nothing here is approved or implemented.** These are
inputs to the feature documents described in *Working process* below.

---

## Documents

| # | Document | What it answers |
|---|---|---|
| 00 | [`00-north-star.md`](./00-north-star.md) | What the philosophy shift actually changes. The four estates, the provenance triple, domain packs, honest risks. |
| 01 | [`01-frontend-constraint-document.md`](./01-frontend-constraint-document.md) | Audit of the shipped frontend against the 13 AI-design tells and WCAG 2.2, then the constraint document: colour, type, spacing, radius, elevation, motion, the provenance material grammar, the one awe moment. |
| 02 | [`02-architecture.md`](./02-architecture.md) | The five missing components — provenance, Tutor, Inheritance, Canvas, Contribution — with data models against the shipped backend. |
| 03 | [`03-reference-systems.md`](./03-reference-systems.md) | penecho and hermes-agent: what to take, what to refuse, and why hermes is the exact inverse of Trivium's thesis. |
| 04 | [`04-roadmap.md`](./04-roadmap.md) | Sequenced phases, what "done" means for each, the re-pointed metric ladder, and the decisions that need answering. |

**Read in order if new to this.** 00 is the argument; 01 is the largest single deliverable; 04 is what
to do on Monday.

---

## Sources this draws on

- `frontend-research/research/attention-and-anti-slop-frontend-report.md` — the field guide. Its §10.4
  ("write a one-page constraint document") is the direct origin of document 01. Its §12 checklist
  should become a PR template.
- `frontend-research/exemplary-sites/` — the reference library (case-studies deliberately excluded).
- [penecho](https://github.com/penecho/penecho) — spatial thinking, provisional AI drafts, ink.
- [nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent) — self-improving agent;
  studied as the inverse case.
- `PRD-v1.md`, `full-technical-document-v1.md`, and the shipped `backend/` + `frontend/`.

---

## Working process

The loop we're running, so each pass is repeatable and nothing gets implemented before it's agreed.

```
  ┌─────────────────────────────────────────────────────────────┐
  │                                                             │
  │   1. STUDY        existing research + the shipped product   │
  │        ↓                                                    │
  │   2. SOURCE       find new references worth studying        │
  │        ↓          (add them to §Sources, with what they     │
  │        ↓           are good for and what to refuse)         │
  │   3. PROPOSE      write a FEATURE DOCUMENT                  │
  │        ↓          (one per feature — template below)        │
  │   4. APPROVE      you accept / reject / amend               │
  │        ↓                                                    │
  │   5. IMPLEMENT    build only what was approved,             │
  │        ↓          on its own branch                         │
  │   6. FOLD BACK    what we learned returns to the research   │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
```

Rules that keep this honest:

- **Research documents never become implementations directly.** A feature document sits in between,
  and it is the thing that gets approved. Research can be speculative; a feature document cannot.
- **One feature document per feature**, in `research/v2/features/`, numbered, using the template.
- **Nothing is implemented without an approved feature document**, and the implementation branch
  names it.
- **Every new source gets logged** in §Sources with one line on what it is good for and one on what
  to refuse from it — that second line is the part that usually gets skipped and is usually the more
  valuable one.
- **Claims carry their real strength.** Effect sizes, sample sizes and caveats travel with the claim
  into the feature document. A product whose brand is *evidence over self-report* cannot round its
  own numbers up.

### Feature document template

Copy [`TEMPLATE-feature-document.md`](./TEMPLATE-feature-document.md) into `features/NN-name.md`.

### Status

| Stage | Where we are |
|---|---|
| 1. Study | ✅ This pass |
| 2. Source | ✅ penecho, hermes-agent, the frontend-research repo. Ongoing. |
| 3. Propose | ⬜ Next — feature documents, driven by the phases in `04-roadmap.md` |
| 4. Approve | ⬜ Blocked on the five decisions at the end of `04-roadmap.md` |
| 5. Implement | ⬜ |
