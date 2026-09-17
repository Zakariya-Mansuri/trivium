# Trivium — What to build next

A plain list of the work. Update status here, not in the research documents.

Status: ✅ done · 🟢 can start today · 🟡 waiting on a decision from you · 🔴 waiting on another task

---

## Already done

**The app's look and its accessibility problems.**
Branch: `claude/impl-phase0-design-foundation`. Not merged into `main` yet.

What a person would notice:

- The app was dark blue-grey with purple buttons. It's now light — cream background, black text, one
  red used for buttons and links.
- It used two fonts. It now uses one typewriter font throughout.
- Rounded corners everywhere are now square corners everywhere.
- The lines around cards and text boxes were almost invisible. They're now visible.
- Pressing Tab showed no outline around the button you'd landed on. It now shows a red outline.
- On a phone the sidebar covered most of the screen and couldn't be closed. Phones now get a row of
  buttons along the bottom instead.
- The menu had nine items in one flat list. They're now grouped into four sections. Same pages, just
  organised.
- Menu icons were text characters (◈ ⌨ ☰) which look different on every computer. They're now proper
  drawn icons.
- People who turn on "reduce motion" in their system settings were ignored. They're now respected.
- Diagrams used to appear late and shove the page down. Space is now reserved for them.

Nothing else changed — no pages added or removed, no wording changed, backend untouched.

---

## Can start today

### Backend

**1. Track who wrote what — extend what's already there** — small · id `B1`

**Correction to an earlier version of this document:** this is not a from-scratch job. Two pieces of
it already exist in the backend:

- `messages.authored_by` already records whether each message was written by the person or by the AI,
  and `ai_assist_ratio` in `metrics.py` is already computed from it.
- `sessions.source_fidelity` already records whether a session was captured natively or wrapped, and
  that value already flows through to knowledge units and the profile.

So the idea is built and proven at the message level. The remaining work is to:

- add the missing third state — content that came from a book, paper or repository someone else
  wrote — since today the only options are "person" and "AI";
- carry the label onto knowledge units and learning artifacts, which don't have it yet;
- make it permanent once set;
- add the rule that AI-written text only counts as the person's work if they accept **and** edit it.

Why it matters: the skill profile should only count what the person actually wrote. Most of the work
below depends on this.

**2. Show the blocked-action reason on screen** — very small · id `B2`

**Correction to an earlier version of this document:** I previously wrote that the backend returns a
bare error with no explanation. That was wrong. Both review gates already return a written reason —
*"This concept is in its consolidation window (diffuse-mode delay) and is not yet reviewable"* and
*"This concept was reviewed within the last N hours — spacing matters"* — and the frontend API client
already pulls that text out of the response.

The early-review gate also already lets the person override it deliberately (`early=true`), which is
the "never forced" principle actually implemented rather than just stated.

So the backend work here is done. What remains is a frontend check: confirm every screen actually
displays that message where the person can see it, rather than swallowing it into a generic error.

**3. Send review reminders** — small · id `B3`

There is no email, no notification, nothing. The scheduler decides when you should review something,
and then nobody is ever told. So reviews don't happen.

This is a few days of work and it's the single cheapest large improvement available.

**4. Replace the review scheduling algorithm** — medium · id `B4`

It currently uses SM-2, the algorithm from Anki's early days. FSRS is the current standard and
predicts forgetting more accurately.

Needs care: existing users have review schedules stored, so this needs a migration plan.

**5. Let people export everything** — medium · id `B5`

Plain files: their sources, notes, review history, profile. Plus an import that puts it all back.

If the product's argument is "build on what others left you", it can't be a place where a person's
own work dies if the company does.

**6. Ask the learner what they're trying to do** — small · id `B6`

Four questions when they sign up: what do you want to be able to do, who has already done it, what
would you want to leave behind, and then the system reflects their goal back as a list of specific
skills they'd need — which they can correct.

Best done after task 1, so the answers get labelled correctly from the start.

**7. Build the tutor properly** — large · id `B7`

Right now it's a chat window. A tutor should ask what you already think before it explains, make you
write your answer before it shows you the answer, and then tell you exactly where your answer and
the source's answer differed.

**8. Let people bring in books, papers and repositories** — extra large · id `B8`

Today the app can only read your own AI chat logs. That means a new user signs up and finds an empty
app, and has to go use another tool for a few hours before Trivium can do anything.

This is the biggest piece of work here and it fixes the worst problem the product has.

### Frontend

**9. Merge the finished design work into `main`** — very small · id `F1`

**10. Update the 14 pages to use the new colour names** — medium · id `F2`

The pages currently use the old names (`ink-950`, `primary-600`). They still display correctly
because those names now point at the new colours, but the names are misleading. One page per pull
request; safe to do gradually.

**11. Stop loading fonts from Google** — very small · id `F3`

Host the font file ourselves. Removes an outside dependency that delays first paint.

**12. Show the blocked-action reason on screen** — very small · id `F4`

Pairs with task 2.

**13. Add the keyboard command bar (⌘K)** — medium · id `F5`

Type a command instead of clicking. Already built and working in the component demo — needs porting
into the real app.

**14. Port the rest of the components from the demo** — medium · id `F6`

The numbered transcript, the expand/collapse sections, the properly designed empty screen, the
interactive forgetting curve, and the drag-to-rebuild diagram that replaces the static one.

---

## Waiting on another task

| Task | Waiting for | id |
|---|---|---|
| Show the three content labels visually in the app | task 1 | `F7` |
| Search across everything the learner has ever read | task 8 | `B9` |
| The knowledge map, and working out the cheapest route to a goal | tasks 4 and 8 | `B10` / `F11` |
| Letting people publish something they've made | tasks 1 and 8 | `B11` |
| Supporting subjects other than coding | task 8 | `B12` |
| The drawing canvas | task 1 | `B13` |
| Turning a learner's know-how into a file other people's AI tools can use | task 11 above | `B14` |
| The sign-up flow screens | task 6 | `F9` |
| The reading screen for books and papers | task 8 | `F10` |
| The tutor screen | task 7 | `F12` |
| The view showing everything a learner has already covered | task 8 | `F13` |

---

## Waiting on you

| Decision | What it holds up | My suggestion |
|---|---|---|
| The tagline | The landing page | *"Everything you know, someone left for you. Learn it well enough to leave something."* |
| Whether to use the word "pious" publicly | Landing page wording | Keep the idea, drop the word in public. It's a positioning call, not a design one. |
| How much to ship in the first release | The order of everything | Tasks 1–3 alone are a real release, about three weeks. Adding task 8 makes the bigger idea true. |
| Whether coding stays the main subject | Tasks 8 and 12 | I've assumed yes, with two non-coding subjects added later as proof it generalises. |
| Whether long reading should use a normal font instead of the typewriter font | The reading screen | Yes, for book and paper text only. Everything the user types stays typewriter. |

---

## Suggested order

```
  1.  Merge the design work                              very small
  2.  Track who wrote what        ──▶ show it on screen  small
  3.  Check blocked-action messages reach the screen     very small
  4.  Send review reminders                              small
  5.  Ask the learner their goal  ──▶ sign-up screens    small
  6.  Replace the scheduler                              medium
  7.  Let people bring in books   ──▶ reading screen     extra large
                                  ──▶ the map, publishing

  Alongside all of it: update colour names, host fonts,
  command bar, port the demo components.
```

**Two things worth getting right:**

Do the scheduler (6) before the map (7). The map shows what you know as hills and valleys — things
you know well are high ground. If the scheduler is inaccurate, the map is *visibly* wrong, which is
much worse than a slightly wrong number in a table.

After the basics, choose "let people bring in books" over "build the tutor". The tutor is better for
someone who already has material to work with. Bringing in material is how they get any.

---

## Before writing code

Two short specification documents need writing and your approval first:

1. Tracking who wrote what (task 1)
2. The scheduler replacement (task 4) — this one changes behaviour for anyone already using the app,
   so it needs a migration plan
