Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

`rn` is rebuilt from zero (#31, PR #33), so the user gets the goal they really want while spending
their time only on the three sign-offs and on what only they can decide.

# Acceptance criteria

- Every benefit in `rn/README.md` passes its scene in the verification document, run on the practice
  repository `lovaizu/rn-try` with the real `writ`.
- Points 1–10 agreed on 2026-10-02/03 (task #1's steps) are in the README and design document as
  approved on PR #33, and the prompts, viewpoint files, and hooks do what those documents say.
- Pause and resume (`/rn:dn`, `/rn:up`), feedback (`/rn:gm`), and bringing a 0.8.0 session to the new
  form each work on the practice repository.
- `claude plugin validate --strict` passes for `rn` and for the marketplace.
- `rn/CHANGELOG.md` states what changes for the user, and nothing the user would not notice.
- The practice repository holds no PRs or branches left from earlier trials (#18, #20, #21, #22).

# Assumptions

- `writ` PR #15 (branch `worktree-writ`) merges before the integration check; until then trials use
  `writ` from that branch. Unverified when it merges.
- A PreToolUse hook can tell which subagent made a tool call. Unverified — checked before hooks 9–11
  are built; if false, the design changes for those three.

# Rules

- commit and push every change; one completion marker per task
- After every change to the prompts, an evaluator that did not write them reads all of them against
  `writ`'s essential viewpoints for prompts (`writ/references/essentials/prompt.md` on branch
  `worktree-writ`), and the change is not done until its Mores are settled. `writ` is still being
  built, so `rn`'s design document does not name it for this.
- A More is fixed from what the work should be for its purpose, and design changes reach both the
  design document and the prompts.
- The README and design document are changed and approved on the PR first; the prompts and hooks are
  built from them only after.
- Points are put to the user one at a time, in plain Japanese, with grounds and one recommendation.
- Artifacts in English; conversation in Japanese.
- This work is released as `rn` 0.9.0, a large step up from 0.8.0 (the user's release instruction,
  2026-10-03). After the user merges PR #33, tag `rn--v0.9.0` on `main` and publish its GitHub Release.

# Tasks

### #1: README, design document, and verification document carry agreed points 1–10

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
  essentials.md, 31dba86). Rewrite rn's viewpoint files to it with the Kano and naming changes, e.g.
  "Is each fact checked?" and "Has the work shown nothing…". (Documents here; files in #3.)
- [ ] 9. `writ` stays a dependency (same marketplace, updated together).
- [ ] 10. The session's pull request body carries, besides the link to `steering.md`, what GitHub
  needs to connect the work: `Closes #N` for an issue the work completes, `Refs #N` for one it only
  serves, and the pull requests it supersedes.
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)
- [ ] Design expert review (subagent)

**Completion criteria**:

- A reader of `rn/README.md`, `rn/docs/design.md`, and the verification document alone can say, for
  each of points 1–10 above, where it is stated and what it means for the user or the maintainer — no
  point is missing or changed in meaning.
- Every acceptance criterion in the design has an ID and at least one verification check that names
  it; no check names an ID that does not exist.
- Each named source (grilling, wayfinder, Kano model, generator/evaluator split, decision records)
  matches what its origin says, at the cited version.
- The documents hold no procedure notes, history, or restated content, and the README reads as
  benefits and use rather than a list of mechanisms.

### #2: Design sign-off

**Purpose**: The user approves the README, design document, and verification document before the
prompts and hooks are built on them.

**Prerequisites**: #1

**Steps**:

- [ ] Present the README, design document, and verification document on PR #33 and take the verdict
  via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The README, design document, and verification document are approved.

### #3: Prompts and viewpoint files built from the approved design

**Purpose**: `rn`'s skills, references, and viewpoint files do what the approved README and design
document say, including the Kano split, IDs, hearing, task creation, and viewpoints stated as the
receiver's state.

**Prerequisites**: #2

**Steps**:

- [ ] Rebuild `rn/skills/*` and `rn/references/*` (including `rn/references/essentials/*`) from the
  approved documents
- [ ] Evaluator that did not write them reads all prompts against `writ`'s prompt viewpoints and the
  design; settle every More
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, dry-run)

**Completion criteria**:

- Tracing every command end to end, nothing is read that nothing writes and nothing is written that
  nothing reads.
- Each feature in the design document is carried by a named part of the prompts, and no prompt
  behavior lacks a basis in the design document.
- The prompt evaluation against `writ`'s viewpoints holds no unsettled More.

### #4: Hooks check rn's rules mechanically

**Purpose**: The rules in point 4 are enforced by hooks at the three points the design names, so a
breach is stopped rather than left to the evaluator.

**Prerequisites**: #3

**Steps**:

- [ ] Confirm whether a PreToolUse hook can tell which subagent made a call; if not, take the
  design change for checks 9–11 to the user
- [ ] Build checks 1–8, then 9–11, as the design says
- [ ] Run each check against a breaking case and a passing case
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, coding)
- [ ] Verification expert review (subagent, test)

**Completion criteria**:

- Each of checks 1–11 stops its breaking case and lets its passing case through, at the points the
  design names.
- A normal session run raises no false stop.

### #5: CHANGELOG states what 0.9.0 changes for the user

**Purpose**: A user reading `rn/CHANGELOG.md`'s 0.9.0 section learns how far `rn` has moved from 0.8.0
and what changes for them.

**Prerequisites**: #4

**Steps**:

- [ ] Write the `## [0.9.0]` entries from the approved README and design, dated the day the release
  is finalized
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)

**Completion criteria**:

- Every user-noticeable change from this work has one line stating what changed and why it helps,
  and no line covers something the user would not notice.
- `plugin.json` is 0.9.0, the CHANGELOG's top section is `## [0.9.0] - <release date>`, and no empty
  `## [Unreleased]` is left.

### #6: Trials run on the practice repository

**Purpose**: Each benefit's scene in the verification document passes when `rn` is run on
`lovaizu/rn-try`, including pause and resume, `/rn:gm`, and bringing a 0.8.0 session to the new form.

**Prerequisites**: #5

**Steps**:

- [ ] Run each scene with a stand-in user, using `writ` from `worktree-writ`
- [ ] An evaluator that did not make it judges each run against the verification document
- [ ] Fix any More within the round and run again before the verdict
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA expert review (subagent)
- [ ] Verification expert review (subagent, dry-run)

**Completion criteria**:

- Every scene in the verification document passes, judged by an evaluator that did not make the run.
- No evaluation or trial record is posted as a PR comment.

### #7: Integration check with the real writ

**Purpose**: `rn` works with `writ` as merged to `main`, not only with its working branch.

**Prerequisites**: #6, and `writ` PR #15 merged

**Steps**:

- [ ] Install `rn` and `writ` from the marketplace on this branch and run the scenes that call `writ`
- [ ] Run `claude plugin validate --strict` for `rn` and the marketplace
- [ ] self-check (OK/NG per completion criterion, record in checks/7.md)
- [ ] QA expert review (subagent)
- [ ] Verification expert review (subagent, dry-run)

**Completion criteria**:

- The scenes that call `writ` pass with the merged `writ`.
- Both strict validations pass.

### #8: Practice repository cleaned up

**Purpose**: `lovaizu/rn-try` holds nothing left from earlier trials.

**Prerequisites**: #7

**Steps**:

- [ ] Close PRs #18, #20, #21, #22 and delete their branches
- [ ] self-check (OK/NG per completion criterion, record in checks/8.md)
- [ ] QA expert review (subagent)

**Completion criteria**:

- PRs #18, #20, #21, #22 are closed and their branches no longer exist; no other PR or branch was
  touched.

### #9: Evaluation sign-off

**Purpose**: The user approves the run of the Acceptance criteria.

**Prerequisites**: #8

**Steps**:

- [ ] Present the Acceptance criteria run result on PR #33 and take the verdict via `/rn:ty`
  (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The Acceptance criteria run is approved.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
