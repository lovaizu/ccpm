Rn version: 0.8.0
Design: pith/docs/design.md

# Goal

Split pith out of writ into a plugin of its own (issue #35), so that anyone, rn included, can check
any work by having a first user use it, without installing a plugin for writing documents. writ keeps
checking every document it writes, now by depending on pith instead of carrying it. Each part writ
and pith share gets one home, and the two undecided points of the result file's form are decided
before rn reads it.

# Acceptance criteria

- Installing pith from this marketplace alone gives `/pith:up`, which checks a work by a first user's
  use and writes the result file, and does not install writ.
- Installing writ also installs pith through a plugin dependency resolved against `pith--v<version>`
  tags; `/writ:up` checks every document it writes through pith, as before.
- writ carries no copy of pith: the skill, the first user, its hook, the result-file form and check
  script, and the essentials for essentials files live only in pith.
- Every part the two plugins share (the generator, the essentials for documents and prompts) has
  exactly one home, and the other plugin reaches it from there, not through a copy.
- A caller outside writ, such as rn, can call pith without depending on writ, and what it hands pith
  and reads back is written in pith's design.
- The result file's form settles both open points: whether a new field may be added, and whether the
  `→ fixed:` / `→ let go:` / `→ to the user:` marks are part of the form.
- No regression for writ's users: `/writ:up`'s golden paths (writing a new document, fixing an
  existing one) still bring the benefits they did, judged by a validation run.
- pith's attractive qualities ("check by what happened in use", "write essentials worked back from the
  purpose") hold when called as `/pith:up`, judged by a validation run.
- Each plugin keeps `.claude/rules/plugin.md`: its tests in `dev/<plugin>/tests/` run every line in
  CI, its trials in `dev/<plugin>/trials/`, a README stating Python 3.9 or later, a CHANGELOG entry
  under `## [Unreleased]`, both `claude plugin validate --strict` runs pass, and it is listed in
  `.claude-plugin/marketplace.json` and the root `README.md`.

# Assumptions

- Fact (official docs): `plugin.json` `dependencies` resolve a bare name against the same marketplace,
  install automatically, and pick the highest `<plugin>--v<version>` tag in the range; with no matching
  tag, the marketplace's current copy is used.
- Fact (official docs): there is no path variable for a dependency's directory, and calling another
  plugin's skill or agent is not documented. Unverified whether `/writ:up` can call `pith:up` and start
  `pith:` agents, and how writ reaches pith's files; task #1 tries it before the design relies on it.
- `claude plugin validate --strict` is not documented to check dependencies, so the dependency is
  confirmed by installing, not by validate.
- Releasing pith 0.1.0 and writ's next version (version bump, tags, GitHub Release) is a separate,
  explicit instruction, not a task in this session.

# Rules

- commit and push every change; one completion marker per task
- design.md and the plugins' documents are written in Japanese while under review and put back into
  English before merge (the repository's language)
- nothing is built on the design before the Design sign-off
- trials are run without asking; the conductor only judges a trial, and does not patch and rerun on the
  spot

# Tasks

### #1: Try calling pith from another plugin

**Purpose**: Learn by running, on Claude Code 2.1.291, what a plugin can reach in a dependency, so the
design rests on what works.

**Prerequisites**: none

**Steps**:

- [ ] build a throwaway pair of plugins in the scratchpad (one depending on the other) and load both
  with `--plugin-dir`
- [ ] try: a skill in A calling B's forked skill; A's skill starting B's agent (`b:agent`); A reaching
  B's files (essentials) by some path; B's hook seeing B's agent's `agent_type`
- [ ] record what worked and what did not in `.rn/20261006-split-pith/checks/1.md`; delete the
  throwaway plugins
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] Verification expert review (subagent, per the task's medium)

**Completion criteria**:

- for each of the four ways, checks/1.md says whether it works, with the command run and what came
  back, so the design can choose without guessing
- nothing of the trial is left outside checks/1.md (no throwaway plugins, no edits to the user's
  settings)

### #2: Write pith's design and update writ's

**Purpose**: Decide where each part lives, how writ and rn call pith, and the result file's open
points, and record them in `pith/docs/design.md` and `writ/docs/design.md`.

**Prerequisites**: #1

**Steps**:

- [ ] settle with the user, one point at a time: the home of the generator and of each essentials file;
  how writ hands pith the essentials; the result file's directory (`.writ/open/` or pith's own); the
  two open points of the result file's form
- [ ] write `pith/docs/design.md` from the pith parts of writ's design, with the decisions above
- [ ] update `writ/docs/design.md`: pith's parts point to pith's design; what writ still owns stays
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, writing)
- [ ] Design expert review (subagent)

**Completion criteria**:

- a reader of the two designs alone can tell, for every part listed in issue #35, which plugin holds it
  and how the other reaches it, with the reason
- a caller outside writ can tell from pith's design what to hand pith and what it gets back
- both open points of the result file's form are decided with their reason
- no point is decided in the designs that the user did not decide or that #1 did not show to work
- what each design says once is not said again in the other

### #3: Design sign-off

**Purpose**: Have the user approve the two designs before anything is built on them.

**Prerequisites**: #2

**Steps**:

- [ ] present the designs on the PR and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise →
  address the feedback, re-present)

**Completion criteria**:

- the user approved `pith/docs/design.md` and `writ/docs/design.md` with `/rn:ty`

### #4: Build the pith plugin

**Purpose**: Make `pith/` a plugin that works on its own as the approved design says, with its tests
and trials.

**Prerequisites**: #3

**Steps**:

- [ ] move the skill (as `pith/skills/up/`), result form, check script, first user, its hook and the
  parts the design gives pith, with `git mv` so history follows
- [ ] rename `writ:`-scoped names to `pith:` (agent types, hook match, result directory as designed)
- [ ] move pith's tests to `dev/pith/tests/` and its trial scenes to `dev/pith/trials/`
- [ ] write `pith/README.md`, `pith/CHANGELOG.md` and `pith/.claude-plugin/plugin.json` (0.1.0)
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, coding)
- [ ] Verification expert review (subagent, coding)

**Completion criteria**:

- with only pith loaded (`--plugin-dir pith`), `/pith:up` checks a work and writes a result file that
  passes its check script
- the hook stops a `pith:first-user` reading git history and lets other agents through, shown by tests
- `dev/pith/tests/` runs every line of `pith/`, and `claude plugin validate pith --strict` passes
- no file under `pith/` names writ or reaches into writ's directory

### #5: Make writ use pith through the dependency

**Purpose**: Have writ declare pith as a dependency and check documents through it, keeping no copy.

**Prerequisites**: #4

**Steps**:

- [ ] add `dependencies` on pith to `writ/.claude-plugin/plugin.json`
- [ ] change `/writ:up` to call pith and reach the shared parts as designed; remove what moved
- [ ] keep writ's own hook only for what writ still owns; update `dev/writ/tests/` and trials
- [ ] update `writ/README.md` and `writ/CHANGELOG.md`
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, coding)
- [ ] Verification expert review (subagent, coding)

**Completion criteria**:

- with writ and pith loaded, `/writ:up` writes a document and its check reaches pith (a result file is
  written by pith)
- no file of pith's remains under `writ/`, and `grep` finds no `writ:pith`, `/writ:pith` or
  `writ:first-user` left in `writ/` or `dev/writ/`
- `dev/writ/tests/` runs every line of `writ/`, and `claude plugin validate writ --strict` passes

### #6: Register pith in the marketplace

**Purpose**: Make pith reachable by Claude Code and by a person reading the marketplace.

**Prerequisites**: #5

**Steps**:

- [ ] add pith to `.claude-plugin/marketplace.json` and the root `README.md`; update writ's line if its
  description changed
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA expert review (subagent)

**Completion criteria**:

- `claude plugin validate . --strict` passes and the marketplace lists rn, writ and pith
- installing writ from this marketplace (a local add of this worktree) also installs pith

### #7: Validate both plugins as their users would

**Purpose**: Judge, by running the trials, whether pith's attractive qualities hold as `/pith:up` and
writ's did not get worse.

**Prerequisites**: #6

**Steps**:

- [ ] run pith's trial scenes (prompt with a hole / without; essentials for release notes)
- [ ] run writ's trial scenes (migration plan, typing guide)
- [ ] report, for each attractive quality, how close it came against the last run before the split,
  with the verdict (new: usable now / changed: improved without getting worse)
- [ ] record in checks/7.md

**Completion criteria**:

- each attractive quality of pith comes back as close as before the split, or closer, with the trial's
  output as ground
- none of writ's attractive qualities is worse than before the split

### #8: Final check before merge

**Purpose**: Read the whole change against the goal for contradictions, parts not needed, and work that
does nothing toward it, and put the documents back into English.

**Prerequisites**: #7

**Steps**:

- [ ] read the whole diff against the goal and the approved designs; bring to the user what the
  approved design does not settle
- [ ] translate the reviewed Japanese documents back into English
- [ ] run what the final check fixed, as its user would
- [ ] record in checks/8.md

**Completion criteria**:

- no two parts of the change contradict each other, and nothing in it is outside the goal
- every fix made here keeps to the approved designs and was run
- every document in the change is in English

### #9: Evaluation sign-off

**Purpose**: Have the user approve the Acceptance criteria run.

**Prerequisites**: #8

**Steps**:

- [ ] present the Acceptance criteria run result and take the verdict via `/rn:ty` (approve) or
  `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- the user approved the Acceptance criteria run with `/rn:ty`

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
