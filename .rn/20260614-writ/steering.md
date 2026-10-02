Rn version: 0.8.0
Design: writ/docs/design.md

# Goal

writ is a Claude Code plugin that makes a document read as if a person wrote it, so its reader takes
it in with the least effort, applied on demand by a human or by Claude itself. This plan settles what
writ ought to be — its essentials, its README, and its design — then builds the skill from the approved
design, tries it against the design's qualities, and ends when writ ships on PR #15.

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
- A Claude Code user who installs writ from the marketplace and runs `/writ:up` gets what the README
  promises: each quality in the design's quality section passes when writ is actually run.

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
  the reader, restates what it understood, then answers every question with Good and/or More; only fixes that serve the purpose are made, a defect of the
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
- [x] Write the design

**Completion criteria**:

- Read top to bottom, the README tells a Claude Code user what writ does for them and how to use it.
- Read top to bottom, the design shows who takes part, what passes between them, and why each choice
  was made.
- Both meet every essential.

### #3: Refine the essentials, README, and design together, and take the user's approval

**Purpose**: Bring the three to agreement with one another and to the user's approval on PR #15.

**Prerequisites**: #2

**Steps**:

- [x] Judge the three against the essentials and fix what falls short, in any of the three
- [x] Take the user's review on PR #15
- [x] Once approved, translate the three to English

**Completion criteria**:

- The three use one word for each thing and do not contradict one another.
- The user has approved all three.

### #4: Write writ's skill

**Purpose**: Write the prompts that make writ act as the approved design says, so the requester,
writing role and checking role each reach their purpose even in cases the prompts did not foresee.

**Prerequisites**: #3

**Steps**:

- [x] Have a writing role write the prompts from the design and the essentials
- [x] Have a checking role outside the discussion evaluate them once against `prompt.md` and `doc.md`
- [x] Sort every Good and More, have the fixes made, and judge them against reader and purpose
- [x] Fix the essentials to the framework the user agreed (benefits and use in the README, a
      feature per benefit in the design, qualities from the benefits; steps only for what role and
      purpose cannot carry; every part of a prompt traces to the design)
- [x] Fix the README and the design with the essentials, and take the user's review on PR #15
- [x] Delete the prompts and rebuild them from the README, the design and the essentials alone
- [ ] Evaluate them once, first on the benefits; sort, fix, and take the user's review on PR #15

**Completion criteria**:

- Every decision in the design is realized in the prompts, and nothing in them lacks a reason in the
  design.
- The prompts meet `prompt.md` and `doc.md`.
- The user has approved them.

### #5: Try writ against the design's qualities

**Purpose**: Confirm that a user running writ actually gets what the README promises.

**Prerequisites**: #4

**Steps**:

- [ ] Run writ in every scenario the design's quality section names, and judge each quality by what
      happens to the user and the reader
- [ ] Fix what falls short within the same round and run again, until each quality passes or the
      user decides

**Completion criteria**:

- Each quality in the design passes in its named scenarios, with the runs' results as grounds.

### #6: Ship writ

**Purpose**: Make writ installable from the marketplace and hand the merge to the user.

**Prerequisites**: #5

**Steps**:

- [x] Translate the prompts to English
- [x] Add `plugin.json` with a version, a `CHANGELOG.md`, the marketplace entry and the root README line
- [ ] Pass `claude plugin validate --strict` for the plugin and the marketplace
- [ ] Ask the user to merge PR #15
- [ ] Once merged, tag `main` as `writ--v<version>` with `claude plugin tag --push` and publish
      the GitHub Release (the rule is in `.claude/rules/plugin.md` on branch `rn-rebuild`, ad1bb3d)

**Completion criteria**:

- `/plugin install writ@ccpm` installs writ and `/writ:up` runs.
- The user has merged PR #15.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
