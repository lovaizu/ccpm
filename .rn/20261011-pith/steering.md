---
pr: https://github.com/lovaizu/ccpm/pull/58
status: running
artifact-language: English
conversation-language: Japanese
readme: pith/README.md
design: dev/pith/design.md
verification: dev/pith/trials
---

# Goal

Whoever makes a work, a person or a plugin such as writ or rn, has it checked by a first user who
knows nothing of the talk and uses it as its receiver would, and gets back where it fell short of
the aim; for a kind of work with no essentials file, pith writes one. pith is its own plugin, built
on turn, and installed alone it works without writ (#52, #35). Its README, design and prompts are
made through `turn:up`, with writ's essentials files as the viewpoints.

# Acceptance criteria

## Attractive quality

- A1: A maker checks a document, a prompt, code or tests with pith alone installed, and decides what
  to fix from what pith returns, without reading the first user's records.
- A2: For a kind of work that has no essentials file, the maker gets one that has been tried on a
  real work of that kind.
- A3: writ and rn check their work through pith without depending on each other, so a change to the
  check is made in pith once.

## Must-be quality

- M1: Each part follows official best practice or says why it does not, and keeps nothing its
  purpose does not need.
- M2: Each part of pith traces to a decision of the user or to the purpose; nothing is written ahead
  of a need.
- M3: `claude plugin validate --strict` passes for pith and for the marketplace, tests cover every
  line, and CI passes.

# Assumptions

- Fact, from #52: pith is built on turn, in a pull request of its own.
- Fact, from the request: the README, the design and the prompts are each made by writing a CCS and
  calling `turn:up`; the viewpoints are writ's essentials files. rn is not used.
- Fact, decided by the user: trials and agents run on Opus; Haiku is not used.
- Fact, decided by the user: this session fixes turn while it makes pith.
- Fact, decided by the user: rn, writ and pith are released together, so this pull request does not
  release pith.
- Not yet decided: what pith leaves to turn and what it keeps (for example, whether checking a work
  that is already made goes through `turn:up`). Settled with the user, one point at a time, in #2.
- Not yet decided: whether this pull request removes pith from writ, or leaves writ as it is until
  writ is rebuilt (#53).

# Rules

- The documents are written in English from the start; the user reads them through machine
  translation, so each thing keeps one plain word.
- Implementation comes only from the signed-off README and design.
- turn is fixed here as pith is made: a shortfall seen in a turn's records is fixed only once its
  cause is confirmed in them, README and design first, then tests first.

# Tasks

### [ ] #1: Plan sign-off

### [ ] #2: pith's README

Purpose: what pith gives its users, and how they call it, is agreed with the user point by point,
then written through `turn:up` with `doc.md` and `readme.md`.

Serves: A1, A2, A3, M2

Completion criteria:

- Attractive quality: a maker who has never seen pith decides from the README alone whether to use
  it and how to call it.
- Must-be quality: each promise traces to a decision of the user or to #52.

### [ ] #3: pith's design

Purpose: for each promise of the README, which feature keeps it and how that is checked, written
through `turn:up` with `doc.md` and `design.md`.

Serves: A1, A2, A3, M1, M2

Completion criteria:

- Attractive quality: a builder builds pith from the README and design alone.
- Must-be quality: what turn already does is not built again in pith.

### [ ] #4: Design sign-off

### [ ] #5: pith built

Purpose: pith's smallest form is built from the signed-off README and design: its prompts through
`turn:up` with `prompt.md`, its scripts test first, and it is registered in the marketplace and the
root README.

Serves: A1, A2, A3, M1, M3

Completion criteria:

- Attractive quality: each prompt, run, does what the design says it does.
- Must-be quality: tests cover every line, and the plugin and marketplace validate.

### [ ] #6: pith tried as its users would

Purpose: pith is used on Opus to check real works of each kind and to make an essentials file, and
judged from every conversation and agent record; #35 is judged against it.

Serves: A1, A2, A3

Completion criteria:

- Attractive quality: in each trial, the maker's next move is decided from what pith returned alone.
- Must-be quality: #35 is closed or kept with what still happens.

# Not yet specified

- Release, together with rn and writ.
