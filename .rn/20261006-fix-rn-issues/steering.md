---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/50
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification-next.md
---

# Goal

Rebuild rn, writ and pith together so that each gives in real use what its README promises, and
release the three at once. rn 0.9.0 does harm: in use the user is not heard, must watch over the
work, cannot decide from a 72-line proposal, and waits hours in the design stage. It came from adding
a step or a hook for each fault, and from never using rn as its README's story runs. writ shares the
same faults in its checks (#37, #36), and the check by use (pith) lives in both writ and rn and grows
apart (#35). Each plugin is written again small from its README, its viewpoints and
`.claude/rules/plugin.md`, instructing by purpose and intent rather than procedure; every open issue
(#35-#37, #39, #41, #43-#46) is closed by that, never by patching the place it names.

# Acceptance criteria

Each plugin's own promises, word for word from its README or design, with what this session adds.

## Attractive quality

rn (`rn/docs/design.md`):

- A1: The user gets what they really want, though they start from rough words.
- A2: The user is called only for decisions that are theirs, and does not watch over the work.
- A3: At a sign-off, the user decides from the proposal, without re-reading all the work.
- A4: Work that takes days goes on, the next day or in a fresh conversation, from where it stopped,
  without the user explaining anything again.

writ (`writ/README.md`):

- A6: The reader understands the document in one reading, and knows what to do once they finish.
- A7: The user can hand the document straight to their reader, without reading it over and fixing it.
- A8: The user can judge the result from the final report alone, without reading the whole document
  again.
- A9: What the reader needs and no one has decided comes back to the user as a question instead of
  being covered over.

pith (PR #40, `writ/README.md`):

- A10: Installing pith alone, without writ, checks any work (a document, a prompt, code, tests) by
  what happened when a first user used it, first writing the essentials for a kind of work that has
  none.
- A11: writ and rn both check their work through pith, so a change to how work is checked is made
  once and reaches both.

## Must-be quality

- M1: The user's default branch changes only when they merge.
- M2: Every decision is committed and pushed as it is made, with a line that says what was decided
  and what comes next.
- M3: Every settled item is whole in the commit that settles it, so the record shows why things came
  out as they did.
- M4: `steering.md`, the names of the files in `open/`, and the verification document keep the form
  every command reads them by, and every ID they refer to exists.
- M5: A sign-off is passed only by the user's approval, and is put to the user with nothing
  unsettled behind it.
- M6: What the first user reports is what the user would get, since it knows nothing of how the work
  was made.
- M7: rn, writ and pith install from the marketplace and pass their strict validation.
- M8: The conductor waits for every agent it starts before it goes on, the same way in every
  conversation, however Claude Code runs the agent (#44).
- M9: rn, writ and pith keep `.claude/rules/plugin.md`: tests that run every line in CI, trials, a
  README stating Python 3.9 or later, a CHANGELOG entry, and a listing in
  `.claude-plugin/marketplace.json` and the root `README.md`.
- M10: Other sessions work beside an rn session: its conductor can message them, and none of them is
  taken for its conductor or stopped by its checks (#43).
- M11: `/writ:pith` is removed, whoever called it finds the same check in pith, and no copy of pith's
  parts remains in writ or rn.

# Assumptions

- Fact, `gh issue view`: each of #39, #41, #43, #44, #45, #46 states, under "What it should be",
  what rn should do in its place.
- Fact, issue #46: what the user reads is settled once for `.claude/rules/plugin.md` and every plugin
  following it (rn, writ and pith), not for rn alone.
- Fact, decided by the user: rn, writ and pith are rebuilt in this session and released together;
  pith becomes a plugin of its own. PR #40 (split pith, #35) and PR #42 (#36) were stopped; their
  work is material for this rebuild.
- Fact, decided by the user: the installed `rn@ccpm` is disabled while it is rebuilt, since its hooks
  stop this work; this steering.md is kept as a plain document, and the new rn is tried with
  `claude --plugin-dir` on the practice repository.
- Fact, the issues' own text: each issue falls short of a criterion above: #41 and #45 of A2 (the
  user is moved to a branch they did not ask for, and asked what rn could settle itself); #39 of A2
  (the user waits hours through rounds of writing in the design stage); #46 of A3 (a 72-line proposal
  the user cannot decide from); #43 of M10; #44 of M8; #35 of A10 and A11; #37 (one `/writ:up` runs
  pith about three times) of A2 through rn; #36 (a first user stopped reading its own
  output) of M6.
- Fact, decided by the user: a question to the user is not checked by a first user before it is
  asked. The conductor makes it right before writing it, by looking up what can be settled; rn 0.9.0's
  check of every question by a first user (`rn/references/conduct.md`, "Asking the user") is a fault
  this session removes.
- Fact, `git diff --stat 5adb39a 3a80a90 -- rn`: rn 0.9.0, rebuilt to be simpler, grew from 0.8:
  +2858 / -1490 lines; 882 lines of hooks in 14 checks were added, and `conduct.md` alone is 285
  lines.
- Fact, read in `rn/docs/design.md` and `rn/references/conduct.md`: a first user is started for the
  plan, the design, each task, the deliverable, each question, each proposal, and again for each fix
  of an attractive More; nothing bounds how many runs a session makes, and every report feeds the
  proposal, whose template asks for the goal, every criterion, and every final Good and More.
- Fact, read in `rn/docs/design.md:86` and the hooks: rn's own policy is to improve by sharpening the
  viewpoints, not by adding steps, yet each fault met while building it became a step or a hook
  (the question check, checks 3, 7, 13, 14).
- Fact, read in `rn/docs/verification.md` and `rn/docs/design.md:176-187`: rn is verified scene by
  scene, each from the state just before one moment; no check measures a whole session, its time,
  or what the user reads, so #39's 2 h 43 min was seen in #33 and released.
- Fact, official docs (sub-agents) and seen in this session: a background agent's result reaches the
  main conversation as a notification that starts a later turn by itself, with nothing from the user.
- Fact, official docs (hooks): every hook input has `session_id`; a hook fired inside a subagent adds
  `agent_id` and `agent_type`; `SubagentStart` and `SubagentStop` exist; `UserPromptSubmit` fires on
  every user message with `session_id`.
- Fact, tried with `claude -p` 2.1.291 and a logging PreToolUse hook: a hook fired for a subagent's
  tool call carries the main conversation's `session_id`, with its own `agent_id` and `agent_type`.
- Fact, decided by the user: the work is judged against the last versions that run to the end, rn
  0.8.0 (`rn--v0.8.0`) and writ 0.1.0 (`writ--v0.1.0`, with pith inside it); rn 0.9.0 cannot finish
  a session, and plain Claude Code is no bar for these plugins.
- Fact, decided by the user: the plan is made and carried out without stopping at the sign-offs in
  between; the user is told when it is done, and decides by merging.
- Fact, decided by the user: what makes a plugin good is held as pith's viewpoints, checked by use;
  how work is made and checked lives once, in rn's and pith's designs, which other plugins use rather
  than copy; `.claude/rules/plugin.md` keeps only this repository's own conventions.
- Fact, official docs (plugins/dependencies) and tried on 2.1.291 in PR #40: a dependency installs
  with the plugin that declares it; a plugin's skill calls a dependency's skill with the Skill tool,
  and that skill starts its own plugin's agent and reads files under its own root; the caller cannot
  name a file inside the dependency.

# Rules

- Judge every change from what rn should be for its user, and fix the cause wherever it shows; never
  patch only the line an issue names.
- Where rn 0.9.0's own procedure has a first user check what the conductor writes to the user (a
  question, the plan, a proposal), this session leaves it out: that is the fault it fixes, and the
  user decided so for questions.
- Files are moved with `git mv`, so their history follows.
- Releasing rn, writ and pith (version bump, tags, GitHub Release) waits for an explicit release
  instruction, as `.claude/rules/plugin.md` says.

# Tasks

### [x] #1: Plan sign-off
### [x] #2: Design sign-off
### [ ] #3: The bar, measured

Purpose: Know what rn 0.8.0 and writ 0.1.0 give and cost the user, so the rebuild is judged by it.

Serves: A1-A4, A6-A11

Completion criteria:

- Attractive quality: the README's story is run end to end on `lovaizu/rn-try` with rn 0.8.0, and
  writ 0.1.0 writes one document and checks one prompt; for each, the time the user waited, what they
  read to decide, each call to them, and what they got are recorded.

### [ ] #4: The plugin rules split by where each is used

Purpose: What makes a plugin good becomes pith's viewpoints, how work is made and checked lives once
in rn's and pith's designs, and `.claude/rules/plugin.md` keeps only this repository's conventions.

Serves: A10, A11, M9

Completion criteria:

- Attractive quality: a maker reading pith's viewpoints for a plugin knows what to aim for, including
  what the user spends on the golden path, and nothing in them is a step or a history.
- Must-be quality: no rule is held in two places.

### [ ] #5: pith, a plugin of its own

Purpose: Any work can be checked by use with pith alone, and writ and rn check through it.

Serves: A10, A11, M6, M11

Completion criteria:

- Attractive quality: installed alone, pith checks a prompt and a piece of code by use and returns
  a short result bounded by what the caller decides.
- Must-be quality: tests run every line; strict validation passes.

### [ ] #6: writ, rebuilt on pith

Purpose: writ returns a document the reader can be handed, at less cost than writ 0.1.0.

Serves: A6-A9, A2 (#36, #37)

Completion criteria:

- Attractive quality: writing the same document as in #3 gives a document as good or better, in less
  time and fewer agent runs, with a report the user decides from.
- Must-be quality: tests run every line; strict validation passes.

### [ ] #7: rn, rebuilt small from its README

Purpose: rn gives the README's story in use (#39, #41, #43-#46).

Serves: A1-A4, M1-M10

Completion criteria:

- Attractive quality: the README's story run end to end as in #3 is as good or better on every
  attractive criterion, with less waiting, less to read at each sign-off, and calls only for what is
  the user's.
- Must-be quality: tests run every line; strict validation passes; other sessions are not stopped.

### [ ] #8: The three released together, ready to merge

Purpose: The user can merge the three and release them at once.

Serves: M7, M9

Completion criteria:

- Must-be quality: CI passes; `marketplace.json`, the root README and each CHANGELOG list the three;
  the user is told the result against #3, each criterion's standing, and what is theirs to decide.

### [ ] #9: Deliverable sign-off

# Not yet specified

- The design: `open/01-notes-design.md` is its first draft, and `open/06-notes-design.md` holds what
  was agreed (three axes; rebuild `conduct.md` and the hooks small; keep the README, the record's
  form, the agent definitions and the viewpoints). pith's open points come from PR #40's plan: how
  writ and rn reach pith, which of rn's parts move to it, and the result file's form.
- `verification` names a file that does not exist until the design writes it.
- How it is shown to work: the README's story run end to end on the practice repository, beside rn
  0.9.0's run of the same request, on time to the Design sign-off, the proposal's length, and what
  the user was asked.
