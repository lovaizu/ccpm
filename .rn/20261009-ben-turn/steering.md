---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/57
status: running
artifact-language: English; the documents under review are Japanese until they are put into English before merge
conversation-language: Japanese
readme: turn/README.md
design: dev/turn/design.md
verification: dev/turn/trials
---

# Goal

A plugin that has AI make something hands turn one task, and turn carries it through making, using
and fixing. turn is built from its smallest form and checked by trials in `dev/turn/`, read from the
conversation records. Every decision made so far, the CCS record among them, goes into turn's README
and design, and turn is built from them. The rules for plugins stay inside ccpm in
`.claude/rules/plugin.md` and grow only by a failure met while building turn. pith, writ and rn are
rebuilt on turn afterwards (#52, #53, #54); ben is drawn out of the rules once they have settled.

# Acceptance criteria

## Attractive quality

- A1: A plugin hands one task to turn and decides its next move from the returned record alone,
  without reading the work.
- A2: The plugin's user receives work that someone who did not know the talk has already used, with
  what they stumbled on fixed, and is asked only what only the user can decide.
- A3: A builder builds and checks turn from ccpm's rules alone, and each rule carries the failure met
  while building turn and its reason.

## Must-be quality

- M1: Each part follows official best practice or says why it does not, and keeps nothing its
  purpose does not need.
- M2: Each rule and each part of turn traces to a decision of the user or to the purpose; nothing is
  written ahead of a need.
- M3: `claude plugin validate --strict` passes for turn and for the marketplace, and CI passes.

# Assumptions

- Fact, decided by the user: ben is set aside; building the measure and what it measures at once
  left no stable measure.
- Fact, decided by the user: the user's decisions go straight into turn's README and design, not into
  this file.
- Fact, decided by the user: a trial that needs GitHub runs in the private practice repository
  `lovaizu/rn-try`.
- Fact, decided by the user: trials run on Opus, with turn's maker on Sonnet; Haiku is not used.
- Fact, decided by the user: rn is disabled while it is rebuilt.

# Rules

- The documents stay in Japanese while under review and are put into English before merge.
- Implementation comes only from the approved documents; a shortfall is traced through the record to
  its cause and the cause is fixed.

# Tasks

### [x] #1: Plan sign-off
### [ ] #2: turn's README and design hold every decision

Purpose: the decisions of 2026-10-06 to 10-10, read in time order in their latest form, are in turn's
README and design, so turn is built from them alone.

Serves: A1, A2, M2

Completion criteria:

- Attractive quality: each decision about turn is found in its README or design.
- Must-be quality: nothing about ben is left in them, and no word the user ruled out is used.

### [ ] #3: Plugin rules in ccpm

Purpose: `.claude/rules/plugin.md` is back from git and says how a plugin here is built, tested,
tried and released, with no reference to ben.

Serves: A3, M1

Completion criteria:

- Attractive quality: building turn needs nothing the rules do not say.
- Must-be quality: each rule has its reason.

### [ ] #4: turn built and tried

Purpose: turn's smallest form, built from its README and design, carries a task with a pitfall
through a small calling plugin in a trial, and what happened is read from the conversation records.

Serves: A1, A2, M1, M3

Completion criteria:

- Attractive quality: in the trial, the receiver uses the work once without stumbling, and the
  calling plugin decides its next move from the returned record alone.
- Must-be quality: tests cover every line, and the plugin and marketplace validate.

### [ ] #5: Design sign-off

# Not yet specified

- English before merge, registration in the marketplace and the root README, and release.
