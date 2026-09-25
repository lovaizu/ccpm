Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

Rebuild `rn` from scratch on the three principles and the kept mechanism in
[issue #31](https://github.com/lovaizu/ccpm/issues/31), and ship it as release 0.9.0. Instead of
agreeing a full plan up front, build it in rounds: write a small `rn`, run it on real material,
have the result evaluated, fix, repeat — so what gets evaluated is always a working `rn`, never a
description of one. Existing sessions are not migrated by hand; they migrate when their next `rn`
command runs under 0.9.0.

# Acceptance criteria

- The whole of `rn`'s prompt text can be read in one sitting, and for every step in it a reader can
  say what that step is for. (Checked by a third party reading it end to end in one pass.)
- Every result `rn` evaluates — a plan, a design, a deliverable — is judged by someone other than its
  author, against a few named questions about whether it does its job; not whether a step ran.
- Judgment (planning, evaluation) and execution run on different models, and a real session's
  record shows it.
- On a real session, a user can start, suspend, resume in a fresh conversation, and close, deciding
  only at plan, design, and evaluation via `/rn:ty` / `/rn:gm`; afterwards the session has left only
  `steering.md` and the deliverable, and the evaluation is on the PR.
- A session written under 0.8.0 resumes under 0.9.0 with nothing run by hand. (Checked on the real
  `.rn/20260830-issue-18/steering.md` from `origin/worktree-issue-18`.)
- 0.9.0 is released per `.claude/rules/plugin.md`: version and CHANGELOG finalized, both `--strict`
  validations pass, and after the user's merge `main` carries `rn-v0.9.0` with a GitHub Release.

# Assumptions

- **Fact**: the Agent tool takes `model`; agent definitions can also fix a model in frontmatter.
  Either satisfies the third principle — the criterion is the split, not the parameter.
- **Fact (read 2026-09-20)**: the issue-18 session reads `Rn version: 0.8.0` and is `paused`; it is
  read-only for this session.
- **Assumption**: a round can be tried without installing — `claude --plugin-dir rn` (interactive)
  or `claude -p "/rn:…" --plugin-dir rn` with `--resume` for the gate replies. If a gate cannot be
  driven headlessly, the try is done interactively and its transcript goes on the PR.
- **Assumption**: from round 2 this work itself runs under the new `rn` (self-hosting), which needs
  this conversation restarted with `--plugin-dir rn`; round 1 runs under 0.8.0.

# Rules

- commit and push every change; one completion marker per task
- Artifacts in English; console in Japanese.
- Write `rn/` fresh; the 0.8.0 text is evidence, not a draft. No `checks/`, no review boilerplate —
  evaluation is a third party's reading on the PR against the questions in the Acceptance criteria.
- A round is one task: write → try → evaluate → user verdict. Add rounds as tasks while the
  Acceptance criteria do not yet hold. Round 1's verdict is the design gate.
- `plugin.json` is bumped to `0.9.0` in round 1 so the 0.8.0 mismatch path fires for real. Never
  merge to `main` or tag before the user reports the merge; then tag `rn-v0.9.0` and publish the
  Release with the CHANGELOG section as notes.
- Never modify `origin/worktree-issue-18`; use scratch space for every try, and leave none of it in
  the repository.
- The rn text is written by the conductor itself in the conversation; subagents and headless tries
  run on opus (judgment) / sonnet (implementation), `claude -p … --model opus`.
- Tries run headlessly with `--plugin-dir rn --settings '{"enabledPlugins":{"rn@ccpm":false}}'` and
  `--resume` for gate replies, against a real GitHub remote so the PR path is exercised.

# Tasks

### #1: Round 1 — the smallest `rn` that runs

**Purpose**: Get a working 0.9.0 in front of the user and the evaluator, small enough that what is
wrong with it is visible.

**Prerequisites**: none

**Steps**:

- [x] Write: five `SKILL.md`s, whatever references they need, `plugin.json` at `0.9.0`, and
      `rn/docs/design.md` as one page saying what stays, what goes, where each principle lands
- [x] Try: resume the issue-18 session under it in scratch; run a small real goal through
      `on` → `dn` → `up` → the three gates in scratch
- [x] Evaluate: put both runs on the PR; a third party on the stronger model answers the Acceptance
      criteria's questions against them
- [x] Fix what the tries and evaluations exposed — as the shape `rn` should have, not patches on
      the lines named; re-try with a goal that places a "Design sign-off" task so the Design kind
      and the `Design:` line run for real; re-evaluate
- [x] Settle `viewpoints.md` with the user — what a prompt is judged on, per what it covers:
      structure, generation, evaluation, work steps
- [ ] Rewrite `rn` on `viewpoints.md`, carrying two requests from a real session
      (mamezou-devsite-2f, 2026-09-25):
  - `/rn:on` draws the goal out of the user — shows its reading one point at a time until the
    user's unspoken aim and the approach are agreed — and plans only up to the next decision,
    adding the rest once it is made
  - `/rn:ty`, `/rn:gm` and `/rn:dn` each record the user's decision (approve / revise / none),
    write `State` from the conversation, and stop — so `/clear` then `/rn:up` resumes with no
    added words; to go on without clearing, the user just says so
- [ ] Take the user's verdict via `/rn:ty` / `/rn:gm`

**Completion criteria**:

- Under the draft, the issue-18 session resumes with nothing run by hand, keeping every task,
  check-off, and `State` fact it held.
- Under the draft, a real goal goes start → suspend → resume → close with the user stopped only at
  the three gates.
- The third party's evaluation and the user's verdict on round 1 are on the PR.

### #2: Round 2 — self-hosted

**Purpose**: Fix what round 1 exposed, and find the next faults by running this work itself under
the new `rn`.

**Prerequisites**: #1

**Steps**:

- [ ] Restart this work under `--plugin-dir rn`; migrate this session through the real path
- [ ] Write: address round 1's verdict
- [ ] Try: rerun the two round-1 tries against a real GitHub remote; this session's own resume is
      the third
- [ ] Evaluate and take the verdict as in round 1

**Completion criteria**:

- Every point in round 1's verdict is either closed with grounds on the PR or carried as an open
  point into the next round.
- This session's `steering.md` resumed under 0.9.0 with nothing run by hand.

### #3: Release readiness

**Purpose**: Make the branch releasable as 0.9.0 once the rounds have converged.

**Prerequisites**: the last round

**Steps**:

- [ ] `rn/README.md` as a user sees 0.9.0; root `README.md` line in sync
- [ ] `rn/CHANGELOG.md` opens with `## [0.9.0] - <date>`, no empty `## [Unreleased]`
- [ ] `claude plugin validate rn --strict` and `claude plugin validate . --strict`

**Completion criteria**:

- A user reading `rn/README.md` can start, suspend, resume, and answer a gate without opening a
  prompt file.
- Version, CHANGELOG, and both validations are in the state `plugin.md` requires for a release.

### #4: Evaluation sign-off

**Purpose**: Have the user judge the Acceptance criteria run and release.

**Prerequisites**: #3

**Steps**:

- [ ] Run every Acceptance criterion against the real artifacts; record OK/NG with grounds on the PR
- [ ] Take the verdict via `/rn:ty` / `/rn:gm`; on approval mark the PR ready and ask the user to
      merge; after the merge report, tag `rn-v0.9.0` and publish the Release

**Completion criteria**:

- The Acceptance criteria run is approved by the user.
- After the merge report, `main` carries `rn-v0.9.0` and its GitHub Release.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
