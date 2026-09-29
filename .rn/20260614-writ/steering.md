Rn version: 0.8.0
Design: writ/docs/design.md

# Goal

writ is a Claude Code plugin that makes a document read as if a person wrote it, so its reader takes
it in with the least effort, applied on demand by a human or by Claude itself. This plan settles what
writ ought to be — its essentials, its README, and its design — and ends at the user's
approval of those three. Writing the skill itself comes after that approval, in a plan of its own.

The plan starts from zero. The earlier build was removed so it cannot steer the new one; what it
taught survives only as the user's feedback listed under Assumptions.

# Acceptance criteria

- The essentials state what every document writ produces must reach, as a few essential questions
  rather than a list of bans, so a form of noise nobody listed is still caught.
- Every piece of the feedback in `instruction.md`, `writing-feedback-rn.md` and
  `writing-feedback-telldes.md` is either answered by an essential or deliberately left out with the
  user's agreement.
- A reader of the README who uses Claude Code grasps, top to bottom, what writ does for them and how
  to use it, through an example they can picture as their own work.
- A reader of the design grasps, top to bottom, how writ reaches the essentials: who takes part, what
  passes between them, and why each decision was made, in one sentence at the decision.
- The README and the design each meet the essentials themselves.
- The user has approved the essentials, the README, and the design on PR #15.

# Assumptions

- Fact: the sources of record are `instruction.md` (the original instruction),
  `writing-feedback-rn.md` (the writing know-how agreed in the rn rebuild, PR #33) and
  `writing-feedback-telldes.md` (Telldes's points for reviewing a README and a design and the user's writing
  feedback there). All stay in their original Japanese because they are the user's words.
- Fact: the two feedback files disagree in places — e.g. the rn one says never to refer the reader
  to another section and to keep no section of costs or rejected options, while the Telldes one has
  the README link to the design for reasons and the design name its costs and rejected options.
- Fact: earlier field feedback from real runs is kept where it was given — PR #15's review comments,
  and `writ-feedback-3.md` / `writ-feedback-4.md` on branch `worktree-aiya` under
  `.rn/20260813-aiya/`. It is input to the essentials, not a base to build on.
- Fact: rn's rebuild (branch `rn-rebuild`) is the model for the approach: the essentials first,
  then README and design written and judged against them.
- Fact: the user approved how the essentials are used, to be carried into #2's design as its core:
  the writing role reads the essentials as aims and decides layer by layer, top layer first; a
  separate checking role, given only the document, the reader definition and the essentials, reads as
  the reader, answers the top question first, then reports stumbles and NGs top layer first, skipping
  lower layers when a higher one fails; only fixes that serve the purpose are made, a defect of the
  subject goes back to its owner, and there is one evaluation before the user decides.
- Fact: the user agreed to keep two things in `instruction.md` out of the essentials: the outline
  per kind of document (derived from the reader instead), and the orders to the writing AI (write in
  md, draw figures in mermaid, ask back when the reader is unclear), which go to #2's design.
- Fact: input to #2's design from the rn rebuild session: a writer cannot return to not knowing the
  discussion, so rereading cannot find where a document is unclear; the checking role, in a fresh
  context, restates what it understood, and where the restatement drifts is where the document is
  unclear.
- Assumption: the essentials live at `writ/references/essentials/`, one file per kind of document, so the skill later
  writes and judges by the same file.

# Rules

- commit and push every change; one completion marker per task
- Work toward each task's Purpose and judge the result against the essentials; no fixed review
  ceremony per task.
- The only procedural rules are this repository's plugin rules (`.claude/rules/plugin.md`,
  `marketplace.md`, `language.md`): artifacts in English, and when the plugin ships, version only in
  `plugin.json` and the marketplace and root README updated together.
- Write the essentials, README, and design in Japanese for the user's review, and translate them to
  English before the merge.
- Do not read the removed build (commits before this plan) as a starting point.

# Tasks

### #1: Write writ's essentials

**Purpose**: State, in `writ/references/essentials/`, one file per kind of document, the few essential questions every document
must reach, so writing and judging look at the same thing.

**Prerequisites**: none

**Steps**:

- [x] Draw the essentials from `instruction.md`, both feedback files, and the earlier field feedback
- [x] Bring each point where the sources disagree to the user, one at a time
- [x] Refine until each question is essential and none repeats another
- [x] Reorder the questions in `doc.md` by the layers they are decided in: reader, core, headings,
      figures, sentences, then words, certainty, style and marks

**Completion criteria**:

- Each item of the feedback is caught by an essential, or left out with the user's agreement.
- No essential is a ban on a single form of noise; each names the end it protects.

### #2: Write writ's README and design

**Purpose**: Show what writ ought to be — to its user in `writ/README.md`, and to whoever builds it
in `writ/docs/design.md` — held to the essentials.

**Prerequisites**: #1

**Steps**:

- [x] Write the README
- [ ] Write the design

**Completion criteria**:

- Read top to bottom, the README tells a Claude Code user what writ does for them and how to use it.
- Read top to bottom, the design shows who takes part, what passes between them, and why each choice
  was made.
- Both meet every essential.

### #3: Refine the essentials, README, and design together, and take the user's approval

**Purpose**: Bring the three to agreement with one another and to the user's approval on PR #15.

**Prerequisites**: #2

**Steps**:

- [ ] Judge the three against the essentials and fix what falls short, in any of the three
- [ ] Take the user's review on PR #15
- [ ] Once approved, translate the three to English

**Completion criteria**:

- The three use one word for each thing and do not contradict one another.
- The user has approved all three.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-09-29
- **Last completed**: #2 step "Write the README" (user approved on PR #15)
- **Next**: #2 "Write the design" — rebuild from improved essentials. The user approved this order:
  (1) improve the essentials, (2) delete `writ/docs/design.md` and push, (3) regenerate it the same way
  (writer subagent → one evaluation → conductor sorts More → review request with final Good/More)
- **Notes**: Essentials fixes approved (2026-09-29), not yet applied:
  design.md — every element (role, state, handoff) traces its reason to what reaches the user, else
  it is not placed; decisions are written as intent and invariants, never the settings or steps that
  realize them, even before the implementation exists; qualities to confirm are only whether what
  reaches the user is fulfilled, with pass criteria in what happens to the reader and user
  (mechanisms are clues, not qualities); "external agreement" = what stays in the user's environment
  or what later versions read (the directory tree is limited to that; role-to-role handoffs are not).
  doc.md — do not re-explain the mechanisms of the tools used; write only the decision built on them.
  prompt.md — the requester judges each fix against the reader and purpose (only reading without the
  discussion is the non-author's job); the checker answers every question with Good and/or More;
  Good carries grounds like More and the requester doubts each Good, sorting a broken one as More.
  Design decisions for the rebuild: no draft — write straight to the target file; md/mermaid are
  defaults, following the user's or the target place's format. Process: the evaluator answers every
  question; the conductor applies every question before the review request. After editing
  prompt.md, tell rn session rebuild-rn-c1 the line numbers.
