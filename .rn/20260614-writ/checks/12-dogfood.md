# Task 12 — dogfood run of the shipped `SKILL.md`

**Body under test:** `writ/skills/up/SKILL.md` at `d2660dd` (139-line body, 2,650 words), with
`writ/skills/up/references/axes.md` at the same commit.
**Input draft:** `rn/README.md` in this repo — 98 lines, 789 words, a real shipped README with a
mermaid figure, three console transcripts and a naming-rationale section.
**Run:** executed by the assistant following the shipped body top to bottom, all eleven steps. Every
step is recorded below, in order, with what it emitted.
**Reader trials:** three rounds, each a fresh-context subagent given only the produced document and
the step-2 reader definition. Each report is committed verbatim under `checks/12-dogfood/`.

This record is evidence for completion criterion 3. It does **not** grade the run against acceptance
criteria ends 1–8 — steering reserves those for a fresh-context reader and forbids the author's own
reading, and an independent grader does that separately.

---

## Step 1 — Understand the input

**Emit**

```
Subject: the `rn` Claude Code plugin — what it does for a session, and the five commands that drive it.
Must convey: you name a goal once and approve one plan; after that rn works task by task, and a break
  costs you nothing because the session resumes from git rather than from your memory.
Proposed, not in force: (none)
```

The status sort was run against the artifact, not assumed. Every assertion in the draft is **in
force**: `rn/.claude-plugin/plugin.json` is at `0.7.0`; `rn/skills/` holds `on`, `dn`, `up`, `ty`,
`gm`; `rn/CHANGELOG.md`'s `## [0.7.0] - 2026-07-05` section ships the `/rn:ty` + `/rn:gm` verdict
pair, the `✅ done / 👉 now / ⬜ ahead` session map and the three-point sign-off. Nothing in the draft
is proposed and nothing is a hypothesis.

Consequence, stated plainly: this input does not exercise end 5 (a proposal surviving as a proposal).
The previous dogfood input, `.claude/rules/plugin.md`, had the same property. Step 1's sort ran and
found nothing to carry — that is a fact about the input, not evidence that the mechanism works.

## Step 2 — Define the reader and the purpose

- **WHO** — a Claude Code user who keeps losing work when the context fills up, and has just found
  `rn` in the ccpm marketplace listing.
- **WHAT** — decide whether to install `rn` and run their next work session through it.
- **HOW** — straight through, once.

**Gate:** the input answers WHO several ways (a prospective user, a user already running sessions who
wants the command mnemonic, and the plugin's author). No user was in the loop, so the run took the
headless path: infer the primary, and prepend `Assumed reader:` to the output. The primary is the
prospective user — the audience a marketplace README is read by. The other two are kept out at step 3
and named in the note.

## Step 3 — Build the outline from the purpose

`${CLAUDE_SKILL_DIR}/references/axes.md` was read before the axis was picked. The read succeeded, so
the failure path at `SKILL.md:43` did not fire.

Axis: **Article / explanation** — the reader reads to understand and then decide. Guide/procedure was
considered and rejected: its slot 1 is "goal and prerequisites" for someone *doing it now*, and this
reader has not decided to do anything yet.

**Both-ways test**

*Slot → reader.* Three blocks of the draft do not serve this reader and stay out:

| Kept out | Whose reader it serves | Where it belongs |
|---|---|---|
| `## Why on / dn / up?` — the on/down/up mnemonic | someone already running sessions who wants the three commands to stick | a command reference, or a line in the plugin description |
| The `/rn:on` and `/rn:dn` console transcripts (two of three) | someone learning the output format | the same reference; one transcript is enough to show the texture |
| `:53` "That opening block — ✅ done / 👉 now / ⬜ ahead — heads every message…" as its own paragraph | a user mid-session | folded into the substance as one clause, not a paragraph |

*Reader → slot.* The reader must have the two install commands to act on a positive decision, and the
article axis has no slot that carries them — its slot 2 says in the file's own words "alternatives and
background welcome, **instructions are not**". This is a need with no slot, so it is raised as a
**proposed slot**:

- **Proposed slot:** "Install it and start", placed after the substance and before the closing.
- **Reader evidence:** the reader's WHAT is "decide whether to install it"; a decision they cannot act
  on is not a decision. The draft itself puts install second, which is the same judgement made by its
  author.
- Not absorbed as prose under a nearby heading — that is exactly what `SKILL.md:37` forbids.

No composite was declared: two install lines are not a second document, and nothing else in the
content pulls a second axis. So `:41` did not fire, and step 5's per-part walk had nothing to walk.

**Emit**

Axis chosen: **Article / explanation**. Its skeleton's slots, quoted from `axes.md` as they stand
there:

```
1. The question and its answer (the why-question this document answers, and the answer to it, in 1–2 sentences)
2. The substance (per unit: claim → why → implications and connections; alternatives and background welcome, instructions are not)
3. In closing (the limits, what it does not settle, pointers onward — not a recap of the answer)
```

Outline headings specialized to this content:

| Slot | Heading | Departure, and the admission that argued for it |
|---|---|---|
| 1 | (the lead paragraph, unheaded) | none — the question and its answer, in one sentence |
| 2 | "You sign off once, on the plan" | none |
| 2 | "Then it runs, and the messy part stays off your screen" | slot 2 carries three headings, one per unit of substance, which is the per-unit specialization the slot itself asks for |
| 2 | "Every break is dn → clear → up" | same |
| — | "Install it and start" | **proposed slot** — the reader need above, with no skeleton slot behind it |
| 3 | "What stays yours" | none — limits and what rn does not settle, no recap |

## Step 4 — Fill the outline

Bullets, in the run's own words, one fact each. Abbreviated here; the rendered result is below.

- Lead: name the goal once → plan on a PR → task by task → a break resumes from git.
- Sign off once: `/rn:on <goal>` restates, decomposes, opens the draft PR; the plan is on the PR
  because it is longer than a console shows; `/rn:ty` approves, `/rn:gm` revises, plain `/rn:gm`
  walks the PR review comments; the same two answer every later sign-off.
- Then it runs: experts and reviewers are separate agents; cleared work lands on the same PR; you are
  pulled in only when the call is yours; every stopping message opens with the three-line map.
- Every break: `/rn:dn` commits, pushes, leaves a note; you run `/clear`; `/rn:up` finds the session,
  reconciles against the git log, starts the unreached task.
- Install: the two `/plugin` lines; then `/rn:on` with the goal in plain words.
- What stays yours: the three sign-off calls; `/clear`.

## Step 5 — Check the story in the reader's order

Walked in the step-2 reader's order: decide → how the plan works → what happens after → what a break
costs → install → limits. No composite, so no per-part walk.

- **Gap:** none. The reader reaches "install or not" with every input to that decision behind them.
- **Repeat:** the lead's "picks the session back up from git" and the third unit's "reconciles it
  against the git log" touch the same fact. Kept, as answer-then-substance, with the wording made
  non-parallel so it does not read as tell 2.
- **Detour:** none.
- **Filled outline beside the input:** three bullets carried the draft's own phrasing —
  "verifiable tasks", "the trial-and-error never crowds the conversation", "heavy work, kept out of
  sight". Re-filled from meaning at this step, before rendering: "tasks that can each be checked",
  "the messy part stays off your screen", "their trial and error never lands in your window".

## Step 6 — Decide voice and form

**Emit**

```
Voice: warm and plain; an easy motive before each term
Closing: what was learned, and the limits
```

Form per section, chosen for each part of the story walked at step 5:

| Section | Form | Why |
|---|---|---|
| Lead | Prose | a line of reasoning, one sentence |
| You sign off once | Prose | reasoning; the command names carry the concreteness |
| Then it runs | **Diagram (mermaid)** | the session loop branches (you weigh in) and cycles (task → review → task); prose would have to say "then back to" three times |
| Every break | Prose + one console block | a short linear sequence — three commands in order — so no diagram; the transcript is the literal artifact |
| Install it and start | Console block | two literal commands |
| What stays yours | Prose | reasoning |

No list appears anywhere in the document. The draft's three commands were a natural candidate for a
bullet list, but they are not parallel — `dn` commits, `/clear` is the reader's own move, `up`
resumes — so they are written as prose, per the form rule and tell 5.

## Step 7 — Write it out

Rendered from the filled outline in the chosen voice and forms. The produced document is at the end
of this record.

Honest exception, recorded rather than glossed: the mermaid figure, the `/rn:up` transcript and the
two `/plugin` commands were reproduced **verbatim** from the input. They are literal artifacts of the
subject — a figure and two console captures — not prose, and `SKILL.md:113` admits "material quoted
on purpose". But reproducing them exactly means the input was open at render time, which `:78` says
it is not. The body has no clause reconciling the two. See the carried-forward list in `checks/12.md`.

## Step 8 — Brush up to the ceiling

- Conclusion first: the lead sentence is the answer, not a preamble.
- Headings alone: "You sign off once, on the plan / Then it runs, and the messy part stays off your
  screen / Every break is dn → clear → up / Install it and start / What stays yours."
- Density: every section names commands, not capabilities.
- Nothing was added at this step, so the admission at `:88` had nothing to admit.

## Step 9 — Clear the floor (the net)

The finished document was read once against the seven-tell table.

| # | Tell | Present? |
|---|---|---|
| 1 | Padding / throat-clearing | No — the document opens on the answer |
| 2 | Restatement | One candidate, the git-resume fact at the lead and again in the third unit; kept as answer-then-substance with non-parallel wording |
| 3 | Retreat into generalities | No |
| 4 | Flavorless connectives | No |
| 5 | Reflexive bulleting | No — no list in the document |
| 6 | Wavering voice | No |
| 7 | Hedging | No |

Nothing was fixed at this step, because nothing needed it — which is what `:10` predicts of a
document built fresh rather than edited.

## Step 10 — Self-check the mechanics

Thirteen items. The `axes.md` re-read at item 3 was actually performed: the file was read again after
step 3 and the three article slots printed back, then compared to the step-3 emit character by
character.

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Reader is one person in one reading stance | PASS | One WHO, one HOW; the WHAT is one decision |
| 2 | One axis, no mixing | PASS | Article throughout; no composite declared |
| 3 | Slots quoted at step 3 are `axes.md`'s own | PASS | Re-read of `axes.md:5-8`; the three slots in the step-3 emit are identical to the file word for word. Departures of the outline: three headings under slot 2 (the per-unit specialization the slot asks for) and one proposed slot — both argued at step 3 |
| 4 | Nothing carried from the input's wording | PASS | Measured: four maximal shared 8-token spans, 25.33% of the produced text inside one. All four are literal artifacts — the mermaid figure (69 tokens), the `/rn:up` transcript (27), the two `/plugin` commands (11), the example goal string (9). No shared span of prose |
| 5 | Every heading and point admitted; every need carried by a slot | PASS | Three blocks kept out with whose reader and where they belong; one proposed slot with reader evidence; both in the note |
| 6 | Form fits content | PASS | One mermaid, on the only branching/cycling part; no list anywhere |
| 7 | No prose repeats what the diagram carries | PASS | The paragraph after the figure carries only what the figure does not — that the experts are separate agents, and the three-line map |
| 8 | Voice and closing fit the step-2 reader | PASS | Warm and plain; closing is limits, not a recap |
| 9 | None of the seven tells remain | PASS | Step 9 table above |
| 10 | `Assumed reader:` line present iff the reader was inferred | **FAIL → fixed → PASS** | The reader was inferred at step 2's Gate and the line was missing from the first render. Fixed by prepending it, per `:106`'s "any FAIL, fix and re-check"; re-checked PASS |
| 11 | Produced size recorded, growth argued | PASS | 504 words against the input's 789 — 0.64x. A shrink, so nothing to argue for; the six kept-out blocks account for it |
| 12 | Every claim carries its status | PASS | All facts, asserted plainly, each verified at step 1 against `plugin.json`, `rn/skills/` and `CHANGELOG.md` |
| 13 | Ceiling, floor, forms and claim statuses judged on the produced document | PASS | Every check above ran against the produced document; the prompt was not the subject of any of them |

One FAIL, fixed and re-checked as the body requires. No third verdict was invented — the UNVERIFIED
verdict `:108` defines did not apply, because no read failed.

## Step 11 — Reader trial, then deliver

Three rounds, each a fresh-context subagent. Each was handed exactly two things and nothing else, as
`:126` requires:

1. the produced document as it then stood, pasted in full;
2. the step-2 reader definition (WHO / WHAT / HOW).

No outline, no draft, no `axes.md`, no history, no repository access — each brief closes with "Do not
use any tools. Do not read any files. Answer from this text alone."

The reports are committed verbatim:

- `checks/12-dogfood/trial-1.md`
- `checks/12-dogfood/trial-2.md`
- `checks/12-dogfood/trial-3.md`

(rounds recorded below)

### Round 1 — 6 stumbles, 3 blocks of unneeded content

Document read: the step-9 render, 504 words. Report: `checks/12-dogfood/trial-1.md`.

| Stumble | Class | Disposition |
|---|---|---|
| The heading "the messy part stays off your screen" concedes, two sentences later, that you do get pulled in | Prose defect | Fixed — heading became "Then it runs, and pulls you in only when the call is yours" |
| "The experts and reviewers are separate agents" — the reader does not know what an expert or reviewer *is* | Prose defect | Fixed — named as subagents |
| "a plan worth reading is longer than a console comfortably shows" reads as a maxim the reader is asked to accept | Prose defect | Fixed — restated as the input's own reason, "too long to read there comfortably" |
| `/rn:gm`'s two behaviours (with and without an argument) had to be re-read to bind | Prose defect | Fixed — reordered |
| "there is never a moment where you have to work out how to reply" overclaims, right after a mode split | Prose defect | Fixed — cut |
| The closing "What stays yours" restates the three sign-off calls already given | Prose defect (tell 2) | Fixed — closing rewritten as a limit, not a recap |

| Content not needed | Whom it serves | Disposition |
|---|---|---|
| The mermaid diagram — "it duplicates what the prose right above and below it already states" | someone skimming for the control-flow shape | Kept for round 2, with the duplicating prose cut instead |
| The `/rn:up` console transcript — "reassurance/flavor rather than decision-relevant" | someone who wants to see the UI before installing | Cut |
| The closing section's recap | someone who already decided to install | Cut |

Also reported at question 1, and not fixable from this input: what happens if the git log and the plan
disagree at `/rn:up`, and what is lost if `/clear` runs early. The input never says. Named as subject
defects, not patched.

### Round 2 — 6 stumbles, 4 blocks of unneeded content

Document read: the round-1 fixes, 476 words. Report: `checks/12-dogfood/trial-2.md`.

| Stumble | Class | Disposition |
|---|---|---|
| The `/rn:gm` sentence's pronouns ("it", "that", "on its own") had to be re-read twice | Prose defect | Fixed — rewritten |
| "the approach when it needs its own look" has no antecedent in the document | Prose defect | Fixed — cut |
| dn/clear/up stated three times: opener, its own section, and the closing | Prose defect (tell 2) | Fixed in the closing — **and it survived**; see round 3 |
| The mermaid block "is a dump of flowchart syntax" in a straight-through read if it does not render | Prose/form defect | Fixed — diagram cut, see below |
| "its message opens with a three-line map … so you answer from that" asserted with no example | Prose defect | Fixed — cut, since the same reader also reported the map as content not needed |
| `ty` and `gm` are never explained as words | Subject defect | Named, not patched — the input's naming section covers `on`/`dn`/`up` only |

| Content not needed | Whom it serves | Disposition |
|---|---|---|
| The diagram's internal detail ("Expert does it", "reviewers try to break it") | someone who wants the architecture | Cut with the diagram |
| The three-line map (✅ 👉 ⬜) | an existing user mid-session | Cut |
| "the approach when it needs its own look" | an existing user who has hit a mid-task gate | Cut |
| The third repetition of dn/clear/up | "serves nobody in a straight-through read" | Fixed in the closing; survived |

**The diagram was cut on two independent readers' evidence.** Round 1 said the prose above and below
already carried it; round 2 said the raw fence is noise mid-read. That is `SKILL.md:68`'s own rule —
"when prose reads faster … skip it" — arriving from the reader rather than from the author, which is
what step 6 means by "the step-2 reader is the source of truth". It cost one sentence of prose to
replace, and the carryover measure dropped with it: 3 shared spans and 18.70% before, 2 spans and
4.90% after, because the 69-token figure was the largest single carried block in the document.

Also reported at question 1, and not fixable from this input: whether rn requires a GitHub repo with
PR access. The input never states it. Named as a subject defect.

### Round 3 — the cap, 7 stumbles, 3 blocks of unneeded content

Document read: the round-2 fixes, 409 words. Report: `checks/12-dogfood/trial-3.md`. **No edit was
made after this trial**, so the run ends on a reading, as `SKILL.md:139` requires.

| Stumble | Class | Disposition |
|---|---|---|
| The opener writes `dn` / `up` bare, every later mention writes `/rn:dn` / `/rn:up` | Prose defect | **Survives** — named at delivery |
| "reviewers whose job is to break it" — still no elaboration on what a reviewer is | Prose defect | **Survives** — named. Round 1 raised its ancestor; naming the experts as subagents did not settle the reviewers |
| "Only what they clear lands on the PR" — "they" binds a sentence later | Prose defect | **Survives** — named |
| "You get asked for something when the call is genuinely yours" — "something" is never concrete | Prose defect (tell 3) | **Survives** — named. Step 9 marked tell 3 absent; a fresh reader found it, which is the case 4.6 exists for |
| "too long to read there comfortably" asserted with no basis | Prose defect | **Survives** — the third reader in a row to object to this clause, in its second wording. Named |
| dn→clear→up stated three times — opener, heading, closer | Prose defect (tell 2) | **Survives** — the round-2 fix did not clear it |
| The title "rn — Right Now" is never explained | Prose defect | **Survives** — named. Its explanation was kept out at step 3 as serving the returning user |

| Content not needed | Whom it serves | Disposition |
|---|---|---|
| The PR-vs-console rationale | someone auditing rn's design choices | Named, not cut — cap reached |
| The closing's restatement | a reader validating internal consistency | Named, not cut — cap reached |
| `/rn:gm`'s two input modes | an existing user mid-session | Named, not cut — cap reached |

Also reported at question 1: whether rn works for non-code goals, and what it costs to run several
subagents per task. The input answers neither. Named as subject defects.

---

## Delivery

`SKILL.md:139` gates delivery on **no prose defect remaining**, and that gate is not met — seven
survive. The three-round cap fires and the document ships with every survivor named, which is what the
same line prescribes: "a prose defect that survives three rewrites is not going to be fixed by a
fourth, so deliver and name it too."

No verdict outside the body's own vocabulary was used anywhere in this run. Step 10's one FAIL was
fixed and re-checked, per `:106`. The previous dogfood invented `PARTIAL` at exactly that point; this
one did not.

### The delivered document (409 words, against the input's 789)

```markdown
Assumed reader: a Claude Code user who keeps losing work when the context fills up and has just found `rn` in the ccpm marketplace / must decide whether to install it and run their next work session through it / reads straight through, once.

# rn — Right Now

Name the goal once. rn turns it into a plan you approve on a pull request, then works through it task by task — and when your context fills up, `dn` → `/clear` → `up` picks the session back up from git instead of from your memory.

## You sign off once, on the plan

`/rn:on fix the bug in the payment screen` restates the goal in its own words, breaks it into tasks that can each be checked, and opens a draft PR carrying the whole plan. The plan lands on the PR rather than in the console because it is too long to read there comfortably.

`/rn:ty` approves it as written. `/rn:gm` sends it back — type your changes after the command and those are what it works from, or send `/rn:gm` bare and it goes to the review comments you left on the PR and works through them one at a time. The same two commands answer every later sign-off.

## Then it runs, and pulls you in only when the call is yours

Each task goes to a subagent that does the hands-on work, and to reviewers whose job is to break it. Only what they clear lands on the PR, task after task, so none of that back-and-forth reaches your conversation. You get asked for something when the call is genuinely yours, and once at the end, to confirm the goal is actually met.

## Every break is dn → clear → up

`/rn:dn` commits what is finished, pushes it, and leaves a note for next time. Then run `/clear` yourself. In the next conversation, `/rn:up` finds the suspended session, reconciles it against the git log, and starts the task you had not reached.

## Install it and start

    > /plugin marketplace add lovaizu/ccpm
    > /plugin install rn@ccpm

That puts `/rn:on`, `/rn:dn`, `/rn:up`, `/rn:ty` and `/rn:gm` in the session. Start with `/rn:on` and your goal in plain words.

## The one move it cannot make for you

Clearing the context — a plugin has no way to do that on your behalf, which is why the break is three steps and not one.
```

### The what-changed note

**Structure.** Article / explanation axis, chosen because the step-2 reader reads to understand and
then decide, not to do something now. Five headings: the answer up front, then the plan sign-off, then
what runs unattended, then the break sequence, then install, then the one limit. Slot 2 carries three
headings, one per unit of substance.

**Story.** Walked in the reader's order — decide, how the plan works, what happens after, what a break
costs, install, limits. No gap, no detour; one near-repeat (the git-resume fact at the lead and again
at the break section) kept as answer-then-substance and flagged by round 3 anyway.

**Voice.** Warm and plain, an easy motive before each term, closing on the limit — the step-2 reader
reads through, so the voice table's first row. No list appears anywhere: the three commands are not
parallel (one commits, one is yours to run, one resumes), so they are prose.

**Content kept out**, at the step-3 admission:

| Kept out | Whose reader it serves | Where it belongs |
|---|---|---|
| `## Why on / dn / up?` — the mnemonic | someone already running sessions | a command reference |
| The `/rn:on` and `/rn:dn` console transcripts | someone learning the output format | the same reference |
| The `:53` session-map paragraph | a user mid-session | folded, then cut at round 2 on the reader's own report |
| The `/rn:up` transcript | someone who wants to see the UI before installing | cut at round 1 on the reader's report |
| The mermaid figure and its detail | someone who wants the control-flow shape at a glance | cut at round 2 on two readers' reports |
| The three-line session map | an existing user mid-session | cut at round 2 |

**Slot proposed, and unruled.** "Install it and start" is a **proposed slot** — the article axis's
slot 2 says in the file's own words "instructions are not" welcome, and the reader cannot act on a
positive decision without the two `/plugin` lines. Evidence: the reader's WHAT is "decide whether to
install it". Placed after the substance, before the closing. The owner of `rn/README.md` has not ruled
on it; it ships named.

**Subject defects — named for whoever owns `rn/README.md`, not patched.** None of these is answerable
from the input, and no reconciling clause was written for any of them:

1. Whether rn requires a GitHub repo with PR access (round 2).
2. What `/rn:up` does when the git log and the plan disagree (round 1).
3. What is lost if `/clear` runs early or not at all (round 1).
4. What `ty` and `gm` stand for — the input's naming section covers `on`/`dn`/`up` only (round 2).
5. What it costs to run several subagents per task (round 3).
6. Whether rn works for goals that are not code in a repo (round 3).

**Prose defects surviving the cap**, all seven from round 3, listed in the table above.

**Tells step 9 caught:** none. Step 9's read found nothing to fix, which is what a document built
fresh rather than edited is supposed to produce — and round 3 then found a tell 3 ("something" where a
concrete decision belongs) and a tell 2 (dn/clear/up three times) that step 9's own read had passed.
That gap between the author's floor pass and a fresh reader's is the honest result of this run, and it
is `design.md` 4.6's whole argument arriving as evidence rather than as a claim.

**Size:** 409 words against the input's 789 — 0.52x. A shrink, so there is no growth to argue for; the
six kept-out blocks account for it.

**Unverified at delivery:** nothing. The delivered text is the text round 3 read, unchanged.

**Carryover measure across the three rounds**, maximal shared 8-token spans against `rn/README.md`:

| Round | Spans | Share of the produced text inside one | What the spans were |
|---|---|---|---|
| 1 | 4 | 25.33% | the mermaid figure (69 tokens), the `/rn:up` transcript (27), the `/plugin` commands (11), the example goal (9) |
| 2 | 3 | 18.70% | the figure, the commands, the example goal |
| 3 | 2 | 4.90% | the `/plugin` commands, the example goal |

Every span in every round is a literal artifact — commands, a console capture, a figure — which
`SKILL.md:113` admits as "material quoted on purpose". No span of prose was ever shared. The figure
being the largest carried block, and leaving on a reader's report rather than on the measure, is worth
recording: the carryover item would have passed it at 25.33% because the span was admissible.
