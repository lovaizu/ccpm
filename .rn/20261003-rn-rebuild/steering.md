Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

`rn` is rebuilt from zero (#31, PR #33), so the user gets the goal they really want while spending
their time only on the three sign-offs and on what only they can decide.

# Acceptance criteria

- Every benefit in `rn/README.md` passes its scene in the verification document, run on the practice
  repository `lovaizu/rn-try` with the real `writ`.
- Points 1–14 agreed on 2026-10-02/03 (task #1's steps) are in the README and design document as
  approved on PR #33, and the prompts, viewpoint files, and hooks do what those documents say.
- Pause and resume (`/rn:dn`, `/rn:up`), feedback (`/rn:gm`), and bringing a 0.8.0 session to the new
  form each work on the practice repository.
- `claude plugin validate --strict` passes for `rn` and for the marketplace.
- `rn/CHANGELOG.md` states what changes for the user, and nothing the user would not notice.
- The practice repository holds no PRs or branches left from earlier trials (#18, #20, #21, #22).

# Assumptions

- `writ` PR #15 (branch `worktree-writ`) merges before the integration check; until then trials use
  `writ` from that branch. Unverified when it merges.
- A hook can tell which subagent made a tool call: inside a subagent, the hook input carries
  `agent_id` and `agent_type`, and a plugin agent reports `<plugin>:<agent>` (e.g. `rn:first-user`)
  (docs: hooks). The matcher filters by tool name only, so the script checks `agent_type`. A plugin
  agent's own `hooks` frontmatter is ignored (docs: plugins/components), so hooks for one agent live in
  the plugin's `hooks/hooks.json`. Documented, not yet run.
- A skill with `context: fork` runs without the caller's conversation; it gets the SKILL.md body,
  and CLAUDE.md and git status as its agent loads them (docs: skills, sub-agents). A plugin agent
  supports `omitClaudeMd` (docs: plugins/components); the sub-agents page says a plugin agent ignores
  it, yet on Claude Code 2.1.285 it worked (the writ session, 2026-10-03: 2/2 with, 2/2 without), so
  it works now without a documented guarantee. Whether a skill's `agent` field can name the
  plugin's own agent is not documented — confirmed by running before the design relies on it.

# Rules

- commit and push every change; one completion marker per task
- This session runs on `rn` 0.8.0, but where it departs from 0.8.0 it goes the 0.9.0 way, as
  `rn/docs/design.md` describes it (the user's instruction, 2026-10-03). The departures:
  - A task's result is not reviewed by 0.8.0's self-check and QA, Design, Craft, and Verification
    experts, and no `checks/` file is written. Instead: the conductor checks the result against the
    task's purpose; a fresh first user (a subagent handed only the work, its purpose, and the
    viewpoints, nothing of how it was made) uses it once and answers each viewpoint with what it
    understood or what happened, giving no Good or More; the conductor sets those answers beside the
    aim and gives Good or More; each More whose fix brings the work closer is fixed by the generator;
    a fix to a More on attractive quality is checked by a fresh first user for that viewpoint alone,
    while a More on must-be quality is fixed and needs no re-check (point 11; the user, 2026-10-03);
    the final Good and More go into the task's check-off commit message.
  - A first user writes its whole report to `.rn/20261003-rn-rebuild/open/{NN}-report-{target}.md`
    (overwritten when the same target is used again) and returns only a short result and that path
    (point 14). The commit that settles it carries the report whole with the conductor's decisions,
    and removes the file from `open/`.
  - The viewpoints are the file in `rn/references/essentials/` for what the result is (the design for
    #1, `writ`'s `essentials.md` for #2), and for prompts also `writ`'s viewpoints for prompts
    (`writ/references/essentials/prompt.md` on `worktree-writ`); after every change to the prompts, all of them are used this way.
- A More is fixed from what the work should be for its purpose, and design changes reach both the
  design document and the prompts.
- The README and design document are changed and approved on the PR first; the prompts and hooks are
  built from them only after.
- The user's instruction (2026-10-03): go through #8 without the user's check, building it all
  once; ask only what is the user's to decide. #4 stays unchecked until the user gives its verdict;
  the work after it goes on without waiting.
- Points are put to the user one at a time, in plain Japanese, with grounds and one recommendation.
- Artifacts in English; conversation in Japanese.
- This work is released as `rn` 0.9.0, a large step up from 0.8.0 (the user's release instruction,
  2026-10-03). After the user merges PR #33, tag `rn--v0.9.0` on `main` and publish its GitHub Release.

# Tasks

### [x] #1: README, design document, and verification document carry agreed points 1–14

**Purpose**: The README and design document state every point agreed on 2026-10-02/03, with
verification split into its own document, so the prompts and hooks can be built from them.

**Prerequisites**: none

**Steps**:

- [ ] 1. Kano model, explicit. The plan's criteria section is named Acceptance criteria (for the
  goal), and a task's Completion criteria (for its purpose); each has subsections Attractive quality
  and Must-be quality. The same split carries through to verification, tasks, and the deliverable's
  evaluation. Tasks first raise attractive quality until the goal is nearly achieved, then finish
  must-be quality.
- [ ] 2. Verification is split from the design into its own document (e.g. `docs/verification.md`):
  for each acceptance criterion, the scene where it is checked and what passes, in the same
  attractive → must-be order. The Design sign-off approves design and verification together.
- [ ] 3. Traceability: each acceptance criterion has an ID (A1, A2… attractive; M1, M2… must-be).
  Design features, verification checks, tasks, and the deliverable's evaluation refer to criteria by
  ID.
- [ ] 4. Hooks check rn's rules mechanically, at three points: right after a file is written
  (PostToolUse), at the end of each stage before its evaluation, and again before every commit. What
  they check:
  1. steering.md form: front matter, headings, task headings `### [ ] #N: name`, unique IDs.
  2. `open/` file names `{NN}-{kind}-{about}.md`, kind evaluation | feedback | notes.
  3. Traceability: every referenced ID exists; every criterion has a verification check, and a task
     once tasks are planned.
  4. Every conductor commit ends with a decision line `● … ── … → …`.
  5. A settled `open/` item's text is whole in the commit message.
  6. A stop commit: `open/` holds only design points waiting for writ, the latest default branch is
     merged, and the line ends `waiting for #N …`.
  7. A sign-off is marked `[x]`, and `status: finished` set, only in an approval commit.
  8. Every commit is pushed.
  9. Only the conductor uses git: generator, evaluator, and writ agents are stopped from commit/push.
  10. An evaluator writes only its own evaluation file.
  11. An evaluator does not read the maker's account (commit messages, notes, earlier evaluations).

  Content (whether it serves the purpose, the language, feedback kept whole) stays with the evaluator
  and conductor.

  Keeping the roles apart (9–11) serves one aim: the first user checks the work knowing nothing of
  how it was made, so what it reports is what the user would get. That is held first by how each agent
  is defined — what it is handed and which tools it has (a fresh subagent, `omitClaudeMd`, only the
  work and its purpose, no Agent tool for the generator so it cannot call the first user). The design
  settles which of 9–11 the definitions hold; only what they cannot hold stays a hook.
- [ ] 5. Hearing: adopt the know-how of `grilling` (mattpocock/skills, MIT, d81f3a1, 2026-09-29) — a
  tree of decisions, ask what its prerequisites allow with a recommended answer, facts are looked up
  not asked, done when nothing is silently assumed — and add rn's own part: find what the user really
  wants from the purpose behind their words and the ideal it calls for, and record each point as
  agreed. Know-how only, not a dependency: neither fits rn as it is.
- [ ] 6. Task creation: adopt the know-how of `wayfinder` (same source and version) — destination
  first, decisions resolved one at a time, what is not yet clear kept visible as not yet specified.
- [ ] 7. Name the sources where they explain a decision: grilling, wayfinder (with version), Kano
  model, generator/evaluator split, decision records (ways not chosen). Verify each attribution before
  writing it. Watch upstream changes of mattpocock/skills and decide whether to take them in.
- [ ] 8. Viewpoints ask about the state of what the receiver gets, not what the maker did (writ's
  essentials.md, 31dba86). Rewrite rn's viewpoint files to it with the naming changes, e.g.
  "Is each fact checked?" and "Has the work shown nothing…". (Documents here; files in #2.)
  Viewpoint files are not split by Kano quality: a question stays only if removing it would let a
  work that misses its purpose pass (writ's essentials.md, e50d263), whatever its quality. The Kano
  split is used where it changes what is done: the Acceptance criteria and the tasks and checks tied
  to them; the plan's viewpoint file asks whether the plan brings attractive quality first. (Agreed
  2026-10-03.)
- [ ] 9. `writ` stays a dependency (same marketplace, updated together).
- [ ] 10. The session's pull request body carries, besides the link to `steering.md`, what GitHub
  needs to connect the work: `Closes #N` for an issue the work completes, `Refs #N` for one it only
  serves, and the pull requests it supersedes.
- [ ] 11. Validation (agreed in the writ session; now `.claude/rules/plugin.md` § Check on
  `worktree-writ`, 6ca67db): attractive quality is confirmed by using the work as the user would, on the golden path,
  comparing what happened with what was aimed for. Edge cases and other flows are not covered in
  advance: a must-be gap is fixed when it shows up in use, since it is visible and quick to fix,
  while covering everything adds checks that can all pass with no one having confirmed the attractive
  quality. What a machine can judge is checked by machine every time. This shapes point 2: the
  verification document holds each attractive criterion's golden-path scene and the machine checks.
- [ ] 12. When work is checked against viewpoints, the checker gives no Good/More: for each viewpoint
  it answers "from the work I understood this" or "doing as written, this happened". The one who
  knows the aim (the conductor in rn) compares those answers with the aim and gives Good/More.
  Viewpoints are few essential questions worked back from the purpose; how to check is left to the
  checker. (writ will gather viewpoints and how to check them in a skill `pith`, later a plugin rn
  may use; its viewpoints for viewpoints are not yet agreed.)
- [ ] 13. With point 12, the role that checks the work is the first user, not the evaluator: it uses
  the work as the user would, before the user does, and answers with the facts of that use — what it
  understood and what happened — without judging. Comparing those facts with the aim (validation) is
  the conductor's. Terms follow it throughout (e.g. the `open/` kind evaluation becomes report).
- [ ] 14. Results (agreed in the writ session; `.claude/rules/plugin.md` § Build › Results on
  `worktree-writ`, ffa1579): a first user, `writ`, or any agent rn calls writes its whole result to a
  file and returns only a short result and the file's place — the conductor's view, one line per
  viewpoint (Good or More, and where), and in full only what the user must decide. One file per
  target, overwritten on each run, in the place rn names under the session's directory in `.rn/`.
  The whole result in the conversation is too long to be read, crowds the conductor's context, and is
  lost when the conversation is summarized.
- [ ] Used by a first user and settled by the conductor (Rules), once #2 has made the viewpoints usable

**Completion criteria**:

- A reader of `rn/README.md`, `rn/docs/design.md`, and the verification document alone can say, for
  each of points 1–14 above, where it is stated and what it means for the user or the maintainer — no
  point is missing or changed in meaning.
- Every acceptance criterion in the design has an ID and at least one verification check that names
  it; no check names an ID that does not exist.
- Each named source (grilling, wayfinder, Kano model, generator/evaluator split, decision records)
  matches what its origin says, at the cited version.
- The documents hold no procedure notes, history, or restated content, and the README reads as
  benefits and use rather than a list of mechanisms.

### [x] #2: Viewpoint files rewritten to writ's essentials for essentials

**Purpose**: Each viewpoint file in `rn/references/essentials/` can be used by a first user and settled
by the conductor, so the results of #1 onward can be checked the 0.9.0 way.

**Prerequisites**: #1 written (its terms: first user, Kano split, criterion IDs)

**Steps**:

- [ ] Rewrite each file in `rn/references/essentials/` to `writ/references/essentials/essentials.md`
  on `worktree-writ` (e50d263) and to what `rn/docs/design.md` § Viewpoints says of them
- [ ] Used by a first user and settled by the conductor (Rules), with `essentials.md` as the viewpoints

**Completion criteria**:

- A first user given one viewpoint file and a work of its kind can answer each question only by using
  the work, and the conductor can give Good or More by setting each answer beside the aim.
- No question can be removed without letting a work that misses its purpose pass, each asks about one
  point, and each has grounds saying what the receiver gains.

### [x] #3: Documents cut to what their readers use

**Purpose**: The README, design document, and verification document hold only what their readers use
to decide or act, with the diagrams readable at page width, so the user can judge the design at the
Design sign-off.

**Prerequisites**: #1, #2

**Steps**:

- [x] Add to each viewpoint file in `rn/references/essentials/` the question of which parts of the
  work were used for its purpose and which were passed over unused, and rewrite every question into
  the form answered by what happened in use, as agreed in the writ session (2026-10-03): the
  essentials for essentials gain "which parts of the work were used and which passed over", and
  "if removed, would a missing work pass" becomes "which question's answer was not used to judge
  whether the work achieved its purpose"
- [x] A first user uses the three documents with the design viewpoints; the conductor decides for each
  part passed over whether the purpose needs it, and details the prompts or hooks hold move to #5
  and #7
- [x] The verification document's purpose is to rerun the same checks later and find a regression
  (agreed 2026-10-03). It holds only: where a run starts (the practice repository's commit, `writ`'s
  version), how it is run, each scene as a test case of input (what the stand-in says, knows, and
  decides) and Passes when, and the machine checks as commands with the criteria they check. A first
  user is handed a scene's input only; Passes when stays with the conductor, which sets the report
  beside it. Why attractive quality is checked by use and must-be quality has no scenes is stated
  once, in the design document. This holds for the verification document `rn` has `writ` write for
  a user's product as for `rn`'s own: the design document's form for it, hook check 3, and
  `rn/references/essentials/deliverable.md` change with it
- [x] The generator cuts and rewrites, diagrams first and text only for what they do not show,
  each diagram readable at page width
- [x] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- A first user reading each document as its reader passes over no part the conductor keeps for the
  purpose, and every part it passes over is gone or moved.
- No diagram needs horizontal scrolling or shrunk text on the pull request.

### [x] #4: Design sign-off

**Purpose**: The user approves the README, design document, and verification document before the
prompts and hooks are built on them.

**Prerequisites**: #3

**Steps**:

- [x] Present the README, design document, and verification document on PR #33 and take the verdict
  via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The README, design document, and verification document are approved.

### [x] #5: Prompts built from the approved design

**Purpose**: `rn`'s skills, references, and viewpoint files do what the approved README and design
document say, including the Kano split, IDs, hearing, task creation, and viewpoints stated as the
receiver's state.

**Prerequisites**: #4

**Steps**:

- [x] Rebuild `rn/skills/*` and `rn/references/*` (the viewpoint files are #2's) from the
  approved documents
- [x] From #2's use: a decision record names each fixed More's cause, not only its symptom, and the
  Goods the fix touched; a proposal and a report name the commit they are about
- [x] From #3's cut: the formats a prompt or hook holds (open/ names and the settled-report form, the
  stop kinds, the steering.md form and fields, each hook's mechanism, the agent definition) are
  built from `rn/docs/design.md` at 68e9766, the commit before the cut, as far as the approved
  design still holds them
- [x] From #3's report: a safe default where the design is silent — `/rn:on` on uncommitted changes
  stops and says so without touching them; a merge conflict when the branch is brought up keeps
  both sides' intent or goes back to the design; with no Python the session stops at its start
- [x] From #1's fix: `rn/references/essentials/report.md` opens with what the first user writes to
  `open/` and the short result it returns (point 14), not "what a first user returns"
- [x] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- Tracing every command end to end, nothing is read that nothing writes and nothing is written that
  nothing reads.
- Each command, run with `--plugin-dir` on the practice repository, goes the way the README and
  design document say, and no prompt behavior lacks a basis in the design document.
- The prompts' use against `writ`'s prompt viewpoints and the design holds no unsettled More.

### [x] #10: Practice repository cleaned up

**Purpose**: `lovaizu/rn-try` holds nothing left from earlier trials.

**Prerequisites**: #5; done before the trials, so no earlier trial's branch or plan is read in them

**Steps**:

- [x] Close PRs #18, #20, #21, #22 and delete their branches
- [x] Remove `.rn/` from `main` in one commit, so the start the verification document names holds
- [x] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- PRs #18, #20, #21, #22 are closed and their branches no longer exist; no other PR or branch was
  touched; `main` holds the tree of `eabf76b` without `.rn/`.

### [x] #6: Trials run on the practice repository

**Purpose**: Each benefit's scene in the verification document passes when `rn` is run on
`lovaizu/rn-try`, including pause and resume, `/rn:gm`, and bringing a 0.8.0 session to the new form.

**Prerequisites**: #5

**Steps**:

- [x] From #1: decide how a `claude -p` run is stopped partway through a task (A4's first and third
  scenes), and whether a teammate's commits on the session branch need a rule (A4's second scene)
- [ ] Run each golden-path scene with a stand-in user, using `writ` from `worktree-writ`; fix a
  must-be gap that shows up in use
- [ ] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- Every golden-path scene in the verification document passes, as a first user's account of the run
  set beside the scene by the conductor.
- No evaluation or trial record is posted as a PR comment.

### [x] #7: Hooks check rn's rules mechanically

**Purpose**: The rules in point 4 are enforced by hooks at the three points the design names, so a
breach is stopped rather than left to the evaluator.

**Prerequisites**: #6

**Steps**:

- [x] For any of 9–11 the design leaves to a hook, run a hook that reads `agent_type` and confirm it
  tells the first user and the other agents apart; if not, take the design change to the user
- [x] From #1: run whether `UserPromptExpansion` fires for a command passed through `claude -p`, and
  what `command_name` is for a plugin skill, before check 7 relies on it
- [x] Build checks 1–8, and whatever of 9–11 the design leaves to hooks, with their tests, following
  `.claude/rules/plugin.md` § Build (shared with writ; on `worktree-writ` until PR #15 merges, then
  on `main`)
- [x] Run each check against a breaking case and a passing case
- [x] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- Each check built stops its breaking case and lets its passing case through, at the points the
  design names.
- A normal session run raises no false stop.

### [x] #8: CHANGELOG states what 0.9.0 changes for the user

**Purpose**: A user reading `rn/CHANGELOG.md`'s 0.9.0 section learns how far `rn` has moved from 0.8.0
and what changes for them.

**Prerequisites**: #7

**Steps**:

- [x] Write the `## [0.9.0]` entries from the approved README and design, dated the day the release
  is finalized
- [x] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- Every user-noticeable change from this work has one line stating what changed and why it helps,
  and no line covers something the user would not notice.
- `plugin.json` is 0.9.0, the CHANGELOG's top section is `## [0.9.0] - <release date>`, and no empty
  `## [Unreleased]` is left.

### [x] #9: Integration check with the real writ

**Purpose**: `rn` works with `writ` as merged to `main`, not only with its working branch.

**Prerequisites**: #8, and `writ` PR #15 merged

**Steps**:

- [x] Build `rn/trials/` and `rn/trials/fixtures/` from `rn/docs/verification.md` (each scene its
  own minimal trial, started from a fixture rather than the sessions before it), reusing what fits
  of `.rn/20261003-rn-rebuild/trials-before-split/`, then remove that directory; Python 3.9, stdlib,
  left out of the line count (`.claude/rules/plugin.md` § Check, writ PR #15, e0d5719)
- [x] Rewrite `dev/rn/tests` (moved from `rn/tests` with the trials to `dev/rn/trials`, writ 1abd703) to `.claude/rules/plugin.md` § Build on `main` once PR #15 merges: each test
  named by what must happen, as one sentence, its body marked `# Given`, `# When`, `# Then`
- [x] Install `rn` and `writ` from the marketplace on this branch and run the scenes that call `writ`,
  with the hooks on
- [x] Run every machine check in the verification document, `claude plugin validate --strict`
  for `rn` and the marketplace included
- [x] Used by a first user and settled by the conductor (Rules)

**Completion criteria**:

- The scenes that call `writ` pass with the merged `writ`.
- Every machine check in the verification document passes, both strict validations included.

### #11: Evaluation sign-off

**Purpose**: The user approves the run of the Acceptance criteria.

**Prerequisites**: #10

**Steps**:

- [ ] From #9: in A2's rerun rn told the user "the checker tried it 3 times" before its question
  (how the work was made reaching the user); whether the user's want to tell users apart is asked
  after call 3 is not yet seen (the scene ends at call 3). Bring both to the user with the result
- [ ] Present the Acceptance criteria run result on PR #33 and take the verdict via `/rn:ty`
  (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The Acceptance criteria run is approved.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: (YYYY-MM-DD)
- **Last completed**: (task #N, or —)
- **Next**: (task #N)
- **Notes**: (blockers, decisions pending, anything the next session needs)
