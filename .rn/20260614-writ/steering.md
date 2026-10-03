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
- Fact: the user agreed on 2026-10-03 that the essentials and the check by them are one thing, held
  in a skill named `pith` (`/writ:pith` now, `/pith:up` once split into its own plugin): it writes
  essentials files and checks a work by them. `/writ:up` keeps writing documents and checks through
  `pith`. The point of `pith` is a few essential questions, the opposite of an exhaustive checklist,
  so how each question is checked is left to the checking role's judgment.
- Fact: the user agreed on 2026-10-03, with the rn session, that the role that checks is the
  first user (always the two words): it uses the work as its user would and reports what happened,
  without judging it; the requester sets that beside the aim and gives each a Good or a More.
- Fact: the user agreed on 2026-10-03 how `pith` works. It runs in a forked context, and is built
  from the conductor, the generator and the first user (`.claude/rules/plugin.md`). To check a work,
  the caller hands the work, its receiver and purpose, the aim (what the receiver should get and what
  was decided) and the essentials files; the conductor first checks that the aim covers every
  essential, the first user (given the work, receiver, purpose and essentials, never the aim) uses it
  and reports what happened, and the conductor sets that beside the aim, gives Good and More, checks
  their form by script, and returns them; there is no generator, and the caller decides what to fix.
  To write an essentials file, the generator writes it worked back from the purpose, the first user
  tries it on a real work of that kind and reports, and the conductor judges by `essentials.md`,
  has it fixed, and returns it. A work is checked again only when the aim or decisions change; a
  question that comes up is returned as a result, never asked of the user by `pith`. `/writ:up`
  takes the same three role names.
- Fact: the user agreed on 2026-10-03 that the essentials must find what a work does not need,
  and that the check is driven by the essentials: fix the essentials first, check the work with a
  first user, then fix the work. A question that asks whether something is good is answered from the
  first user's report only for what was used, so parts read past never surface. `essentials.md` gets
  two questions in the first user's form: whether the answers showed which parts of the work were
  used toward the purpose and which were passed by; and which question's answer was not used to judge
  whether the work achieved its purpose (replacing "would removing it let a missing work pass").
  Every question in `essentials.md`, `doc.md`, `readme.md` and `design.md` is rewritten into the
  form of what the first user did in use, and `doc.md` asks which parts the reader used to decide or
  act and which they read past.
- Fact: tried on 2026-10-03 with Claude Code 2.1.285 and a throwaway plugin: a skill with
  `context: fork` can start a plugin agent through the Agent tool (`subagent_type: "<plugin>:<agent>"`),
  and a skill's `agent` field can name a plugin agent the same way, which then runs the skill.
  `omitClaudeMd: true` on a plugin agent kept a project CLAUDE.md out of it (two runs; without the
  field the agent saw it, two runs), although the sub-agents doc says the field is ignored for
  plugin agents. A PreToolUse hook input carries `agent_type` (`<plugin>:<agent>`) inside a subagent,
  and plugin hooks fire for a subagent's tool calls (hooks doc).
- Assumption: the essentials live at `writ/references/essentials/`, one file per kind of document, so the skill later
  writes and judges by the same file.

# Rules

- commit and push every change; one completion marker per task
- Work toward each task's Purpose and judge the result against the essentials; no fixed review
  ceremony per task.
- The only procedural rules are this repository's plugin rules (`.claude/rules/plugin.md`) and
  artifacts in English: when the plugin ships, version only in `plugin.json` and the marketplace and
  root README updated together.
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
- [x] Evaluate them once, first on the benefits; sort, fix, and take the user's review on PR #15

**Completion criteria**:

- Every decision in the design is realized in the prompts, and nothing in them lacks a reason in the
  design.
- The prompts meet `prompt.md` and `doc.md`.
- The user has approved them.

### #5: Make checking by essentials its own skill

**Purpose**: Hold how a work is checked by its essentials in one skill, separate from `/writ:up`,
so every improvement to the check reaches every user of it, and rn can later reuse it once it is
proven and split into its own plugin.

**Prerequisites**: #4

**Steps**:

- [x] Settle with the user, one point at a time, what the skill does and where its boundary with
      `/writ:up` lies, following the best practices for checking by a rubric
- [x] Rewrite the questions of `essentials.md`, then `doc.md`, `readme.md` and `design.md`, so each
      is answered by what the first user did in use, including which parts were used to decide or
      act and which were read past
- [x] Check the README and the design by those essentials, with a first user that does not carry
      over the conversation and is not given the aim
- [ ] Fix what the results call for, and take the user's review on PR #15 (fixed; the user said
      to build through #6 without waiting, so the review is taken with #6's results)
- [ ] Rebuild the prompts from the README, the design and the essentials, with the generator and
      first user as plugin agents
- [x] Build pith's result check and the first user's hook in Python 3.9, with unittest tests in
      `writ/tests/`
- [ ] Rewrite `prompt.md` with pith

**Completion criteria**:

- `/writ:up` gets its check through the new skill, and gives the user the same benefits as before.
- The design says how the checking role's eye is measured, so the trial in #6 can tell whether it
  finds what the essentials ask about.

### #6: Try writ against the design's qualities

**Purpose**: Confirm that a user running writ actually gets what the README promises.

**Prerequisites**: #5

**Steps**:

- [ ] Run writ in every scenario the design's quality section names, and judge each quality by what
      happens to the user and the reader
- [ ] Fix what falls short within the same round and run again, until each quality passes or the
      user decides

**Completion criteria**:

- Each quality in the design passes in its named scenarios, with the runs' results as grounds.

### #7: Ship writ

**Purpose**: Make writ installable from the marketplace and hand the merge to the user.

**Prerequisites**: #6

**Steps**:

- [x] Translate the prompts to English
- [x] Add `plugin.json` with a version, a `CHANGELOG.md`, the marketplace entry and the root README line
- [ ] Pass `claude plugin validate --strict` for the plugin and the marketplace
- [ ] Ask the user to merge PR #15
- [ ] Once merged, tag `main` as `writ--v<version>` with `claude plugin tag --push` and publish
      the GitHub Release (the rule is in `.claude/rules/plugin.md`)

**Completion criteria**:

- `/plugin install writ@ccpm` installs writ and `/writ:up` runs.
- The user has merged PR #15.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**:
- **Last completed**:
- **Next**:
- **Notes**:
