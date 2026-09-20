Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

Rebuild `rn` from scratch instead of patching it further (issue #31). `rn` today is five commands
(`on` / `up` / `dn` / `ty` / `gm`) driven by 1,160 lines of prompt that grew by accretion over seven
sessions; its nine open issues share two roots — steps are written as procedure with no stated
purpose, and evaluation checks "did the step run" rather than "does the output do its job." The one
attempt to fix that inside the current structure produced 26 commits and no change to `rn`.

The rewrite stands on three principles and one kept mechanism:

- **Work is instructed by purpose and intent.** Every step `rn` asks the coordinator to take states
  what it is for; a step whose purpose cannot be stated does not exist.
- **Results are evaluated by a third party against essential viewpoints** — the small, named set of
  questions that decide whether an output does its job (e.g. for a plan: does satisfying the
  criteria achieve the goal; does the wording survive a change of means), applied by someone other
  than the author.
- **Judgment and execution use different models.** Planning and evaluation run on the stronger
  model; implementation on the faster one, via the Agent tool's `model` parameter.
- **Mechanism kept, not redesigned:** `steering.md` in git is the session contract — suspendable,
  resumable, with the user deciding at three points (plan / design / evaluation) via `/rn:ty` and
  `/rn:gm`. A session leaves two things: `steering.md` and the deliverable. Evaluation lives on the
  PR.

Two constraints on how it is built. Migration is verified first, not last: a `steering.md` written
under 0.8.0 resumes under the rewrite through the existing version-mismatch path with no hand-run
step. And the rewrite is built in stages: first a one-page statement of what it is — what stays,
what goes, where each principle lands — agreed at a design gate; only then the tasks to write it.

The rewrite ships as release **0.9.0** (the user's instruction on 2026-09-20): a pre-1.0 breaking
change, so a minor bump per `.claude/rules/plugin.md`. The user's existing sessions (e.g.
`.rn/20260830-issue-18/`) are not rewritten by hand — they migrate when the user next runs an `rn`
command under 0.9.0.

# Acceptance criteria

- The five commands (`on` / `up` / `dn` / `ty` / `gm`) are written fresh, not edited from the 0.8.0
  text, and the whole of `rn`'s prompt text (all `SKILL.md`s and references) can be read top to
  bottom in one sitting — it meets the size bound the agreed one-page statement sets, against
  today's 1,160 lines as the reference.
- For any step `rn` asks the coordinator to take, a reader can point to what that step is for, in
  the step itself; no step exists whose purpose is not stated.
- Every output `rn` evaluates (plan, design, deliverable) is judged against a few named viewpoints
  that ask whether the output does its job — not whether the step ran, not whether it can be broken
  — and the judgment is made by a party other than the one that produced the output.
- Planning and evaluation run on the stronger model and implementation on the faster one, and a
  real run shows it: the Agent calls made during a session carry the `model` the statement assigns
  to each role.
- The kept mechanism still holds end to end: a session can be started, suspended, resumed in a
  fresh conversation, and closed, with the user signing off exactly at plan, design, and
  evaluation via `/rn:ty` / `/rn:gm`, and `steering.md` in git is the only state that carries
  across.
- A session directory holds `steering.md` and nothing else; evaluation results are on the PR, and no
  process residue (`checks/*.md` or equivalent) is left behind.
- The 0.8.0 session `.rn/20260830-issue-18/steering.md` (on `origin/worktree-issue-18`) resumes
  under the rewrite through the version-mismatch path with no hand-run step, and this is
  demonstrated before the rest of the rewrite is built — the record of the run (command and observed
  output) is on the PR.
- The rewrite is release-ready as 0.9.0 per `.claude/rules/plugin.md`: `plugin.json` reads
  `0.9.0`, `CHANGELOG.md` opens with `## [0.9.0] - <date>` naming the breaking change (no empty
  `## [Unreleased]` left behind), and `claude plugin validate --strict` passes for both `rn/` and
  the marketplace root. The tag `rn-v0.9.0` and the GitHub Release follow the user's merge, per
  the release procedure.
- `rn/docs/design.md` is the agreed one-page statement — a reader of it alone can tell what stays,
  what goes, and where each principle lands — and `README.md` tells a user what changed for them.
- The build was staged: the statement was approved at a design gate before any command was written,
  and the build tasks that follow were derived from the approved statement, not from this plan's
  first guess.

# Assumptions

- **Fact (this session's tool schema)**: the Agent tool takes a `model` parameter
  (`sonnet` / `opus` / `haiku` / `fable`), so a prompt can direct the coordinator to run a role on
  a chosen model; a `fork` ignores it. The statement decides which roles get which model.
- **Fact (read 2026-09-20)**: `.rn/20260830-issue-18/steering.md` on `origin/worktree-issue-18`
  reads `Rn version: 0.8.0` / `Design: rn/docs/design.md`, has nine tasks and `Status: paused` —
  a genuine 0.8.0 artifact to migrate. It is read-only for this session; that branch is never
  modified.
- **Fact**: the 0.8.0 version-mismatch path is a plain string comparison of `steering.md`'s
  `Rn version:` line against `plugin.json`'s `version`, done at the top of each command. The rewrite
  must keep a trigger that fires on that line for 0.8.0 sessions to enter migration at all.
- **Fact (user's instruction, 2026-09-20)**: the release instruction is already given — the rewrite
  ships as 0.9.0. So `plugin.json` is bumped to `0.9.0` in task #2, and the mismatch path is
  demonstrated against the real `plugin.json`, not a scratch copy: run the rewrite headlessly
  (`claude -p ... --plugin-dir rn`) in a scratch checkout holding the issue-18 session. If headless
  runs cannot exercise the mismatch path, the demonstration is done interactively and the
  transcript is attached to the PR.
- **Assumption**: the user's existing sessions are migrated by the user, by running their next `rn`
  command after installing 0.9.0 — the path proven in #2 is what they will hit, so #2 must run on
  the real issue-18 file, not a fixture.
- **Assumption**: "a session leaves `steering.md` and the deliverable" means design content no
  longer needs its own session file — where the design gate's subject lives (in `steering.md`, in
  the deliverable's own docs, or elsewhere) is a decision the statement makes, not this plan.
- **Assumption**: this session runs under 0.8.0 conventions (this file follows the 0.8.0 template,
  tasks carry the 0.8.0 review steps) even though its deliverable replaces them; the rewrite is not
  applied to its own session mid-flight.

# Rules

- commit and push every change; one completion marker per task
- Artifacts (prompts, docs, commit messages, PR text) in English; console in Japanese.
- Write the rewrite fresh in `rn/`; do not start from the 0.8.0 files and edit them down. The
  0.8.0 text is evidence of what went wrong, not a draft.
- Release as 0.9.0 per `plugin.md`: bump `plugin.json` in #2, finalize `CHANGELOG.md` as
  `## [0.9.0] - <date>` in #5 with no empty `## [Unreleased]`. Never merge to `main` and never tag
  before the user reports the merge; after that report, tag `main` `rn-v0.9.0` (annotated) and
  publish the GitHub Release with the CHANGELOG section as notes.
- Never modify `origin/worktree-issue-18`; read the issue-18 session from it into scratch space.
- Bookkeeping commits (state, tidy-ups) must not contain the string `complete task #`, even in
  prose — only a task's completion marker carries it.
- After task #1 is approved, revise tasks #2–#6 against the agreed statement before starting #2 —
  the statement, not this plan's first guess, defines the build tasks.
- Leave no temp files, scratch copies, or process residue in the repository.

# Tasks

### #1: Write the one-page statement and take the design sign-off

**Purpose**: Settle, on one page in `rn/docs/design.md`, what the rewrite is — what stays, what goes,
where each of the three principles lands, and the size bound — and have the user approve it before
any command is written.

**Prerequisites**: none

**Steps**:

- [ ] Read the 0.8.0 `rn/` in full and the evidence in the superseded issues (#17, #22–#26, #28,
      #29) to name what stays and what goes with grounds
- [ ] Replace `rn/docs/design.md` with the statement, in the design-template's five-section shape
      kept to one page: what stays / what goes / where each principle lands / the size bound / how
      migration and the model split work
- [ ] Revise the draft of tasks #2–#6 against the statement and record the revision in this file
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, writing)
- [ ] Design expert review (subagent)
- [ ] Push and present the statement on the PR; take the verdict via `/rn:ty` (approve) or
      `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The user has approved `rn/docs/design.md` via `/rn:ty`.
- A reader of `rn/docs/design.md` alone can answer, for each of the five commands and eight
  references of 0.8.0, whether it stays, goes, or is replaced, and by what.
- Each of the three principles is placed: the statement names where in the rewrite it is enforced by
  structure, not by a rule asking the coordinator to remember it.
- The statement names a size bound for the rewrite's prompt text and the reason for it.
- The statement fits on one page (no more than ~80 lines), and no section is a restatement of
  another.

### #2: Build the migration path and prove a 0.8.0 session resumes through it

**Purpose**: Make the rewrite's version-mismatch path exist first and show that the real 0.8.0
session `.rn/20260830-issue-18/` resumes through it with no hand-run step — the breaking change is
proven safe before the rest is built.

**Prerequisites**: #1

**Steps**:

- [ ] Bump `rn/.claude-plugin/plugin.json` `version` to `0.9.0`
- [ ] Write the rewrite's `up` command and its version-mismatch path as the statement places them
- [ ] In scratch space, check out the issue-18 session from `origin/worktree-issue-18` and run the
      rewrite's `up` against it from `--plugin-dir rn`
- [ ] Record the command and observed output on the PR; fix the path until the session resumes
      cleanly
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, writing)
- [ ] Design expert review (subagent)

**Completion criteria**:

- The issue-18 `steering.md` resumes under the rewrite: its next unchecked task is identified and
  offered for execution, with no step the user had to run by hand, and the recorded run on the PR
  shows it.
- The migrated `steering.md` keeps every task, check-off, and `State` fact the 0.8.0 file held —
  nothing the session recorded is lost or silently rewritten.
- The session's `Rn version:` line reads `0.9.0` after the run, so the path does not fire again on
  the next command.

### #3: Write the remaining commands and references per the statement

**Purpose**: Write `on` / `dn` / `ty` / `gm` and whatever references the statement keeps, so that
every step states its purpose, evaluation is by a third party against named viewpoints, and each
role runs on its assigned model.

**Prerequisites**: #2

**Steps**:

- [ ] Write each command's `SKILL.md` and the references the statement keeps, fresh
- [ ] Remove the 0.8.0 files the statement retires
- [ ] `claude plugin validate rn --strict` and `claude plugin validate . --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, writing)
- [ ] Design expert review (subagent)

**Completion criteria**:

- Every step in every `SKILL.md` and reference states what it is for; a reviewer reading any step in
  isolation can say what it serves.
- Each evaluation point names its viewpoints and assigns them to a party other than the producer,
  and the total set of viewpoints is small enough to list on one screen.
- Each Agent dispatch in the prompts names the `model` for its role as the statement assigns.
- The prompt text's total line count is within the statement's size bound.
- Both `--strict` validations pass.

### #4: Run the rewrite on real material end to end

**Purpose**: Show the kept mechanism works under the rewrite on a real session, not in principle —
start, suspend, resume in a fresh conversation, sign off at the three gates, and leave only
`steering.md` plus the deliverable.

**Prerequisites**: #3

**Steps**:

- [ ] Run a real session with the rewrite from `--plugin-dir rn` on a small goal, through `on`,
      `dn`, `up`, and the three gates
- [ ] Record on the PR: the commands, the session-status stops, which model each Agent call used,
      and the session directory's final contents
- [ ] Fix what the run exposes and re-run the affected part
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Verification expert review (subagent, writing)

**Completion criteria**:

- The recorded run shows a session started, suspended, resumed in a fresh conversation, and closed,
  with the user stopped exactly at plan, design, and evaluation.
- The recorded Agent calls show planning and evaluation on the stronger model and implementation on
  the faster one.
- The session directory after close holds `steering.md` only, and the evaluation record is on the PR.

### #5: Update `README.md` and finalize `CHANGELOG.md` for 0.9.0

**Purpose**: Tell a user what the rewrite changes for them, and make the branch release-ready as
0.9.0 per `plugin.md`.

**Prerequisites**: #4

**Steps**:

- [ ] Rewrite `rn/README.md` as the user sees the rewrite (scenario and console, not a mechanism list)
- [ ] Add the `## [0.9.0] - <date>` section to `rn/CHANGELOG.md` naming the breaking change; leave
      no empty `## [Unreleased]`; confirm `plugin.json` reads `0.9.0`
- [ ] Sync the root `README.md` line for `rn` if its one-line description changed
- [ ] `claude plugin validate rn --strict` and `claude plugin validate . --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, writing)

**Completion criteria**:

- A user reading `rn/README.md` can start, suspend, resume, and answer a gate without reading a
  prompt file.
- `rn/CHANGELOG.md` opens with `## [0.9.0] - <date>` naming the breaking change and its benefit,
  with no empty `## [Unreleased]`; `plugin.json` reads `0.9.0`; both `--strict` validations pass.
- Nothing in the README or CHANGELOG describes a 0.8.0 behavior the rewrite removed.

### #6: Evaluation sign-off

**Purpose**: Have the user judge the Acceptance criteria run and approve the session's result.

**Prerequisites**: #5

**Steps**:

- [ ] Run every Acceptance criterion against the real artifacts and record OK/NG with grounds on the PR
- [ ] Present the run to the user; take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise →
      address the feedback, re-present)
- [ ] On approval, mark the PR ready and request the user to merge it to `main`; once the user
      reports the merge, tag `main` `rn-v0.9.0` (annotated) and publish the GitHub Release with the
      CHANGELOG 0.9.0 section as notes

**Completion criteria**:

- The Acceptance criteria run is approved by the user via `/rn:ty`.
- After the user's merge report, `rn-v0.9.0` exists on `main` and a GitHub Release for it is
  published with the CHANGELOG section as its notes.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
