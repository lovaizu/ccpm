Rn version: 0.7.0
Design: rn/docs/design.md

# Goal

Improve `rn`'s design-doc authoring convention so every design.md forces an explicit decision plus
the intent behind it for each question it answers — never a silent omission — modeled on the
question-driven structure of aiya's design.md
(https://github.com/lovaizu/ccpm/blob/feature/smith-plugin/aiya/docs/design.md). Alongside that,
close two gaps this work surfaced:

- `planning-workflow.md` only knows "create a fresh design.md" or "no design.md" — it has no branch
  for "an existing design.md already covers this area, update it instead." This session hits that
  branch itself: `rn/docs/design.md` already exists and needs updating to match its own new
  convention.
- `rn` itself will keep changing its own conventions (as it is doing right now). A session's
  `steering.md` / `design.md` / tasks, authored under an older `rn` version, should catch up
  automatically when a command runs under a newer one — without the user having to ask.

# Acceptance criteria

- `design-template.md`'s five sections (Background & Goals / Assumptions & Constraints / Design
  overview / Detailed design / Alternatives considered) each carry explicit h3 questions, generalized
  from aiya's design.md (its Conductor/CCS/Turn-specific content stripped).
- The per-section guidance requires every h3 question to be answered with a decision **and** the
  intent/reasoning behind it; silently dropping a question or section is disallowed (the current
  "a section with nothing to record can be dropped" allowance is removed).
- `planning-workflow.md`'s design-location step explicitly checks whether an existing design.md
  already covers the work's area before defaulting to a new path, and routes that case to an "update"
  procedure rather than "author fresh."
- `design-template.md` documents a distinct update procedure (revise existing sections under the same
  question+decision+intent contract) alongside the existing from-scratch authoring procedure.
- `steering-template.md`'s template block includes an `Rn version:` line, and
  `planning-workflow.md`'s persist step stamps it with the currently installed plugin version.
- A new `migration-workflow.md` reference exists: compares `steering.md`, then `design.md` (if any),
  then the remaining tasks, against the current templates/workflows, in that order; judges by LLM
  reasoning what has drifted (no per-version CHANGELOG bookkeeping); applies reconciling edits;
  commits them with no user gate; then updates the recorded `Rn version:` line.
- Each of the five command skills (`on`, `dn`, `up`, `ty`, `gm`) has a one-line step comparing the
  active session's recorded `Rn version:` against the installed plugin's version, invoking
  `migration-workflow.md` on a mismatch and doing nothing when they match.
- `rn/docs/design.md` is itself updated, under `design-template.md`'s new structure, to record all of
  the above decisions (the question-driven contract, the existing-design-update branch, the
  version-tracking/migration mechanism) — this session dogfoods the update procedure it adds.
- `CHANGELOG.md`'s `## [Unreleased]` section gets one entry per user-facing change above, in the
  user-benefit phrasing `plugin.md` requires.
- No regression: sessions whose `steering.md`/`design.md` predate this change keep working —
  reconciliation only triggers going forward on a version mismatch; there is no one-time mass-migration
  of past sessions.

# Assumptions

- aiya's design.md structure, once its Conductor/CCS/Turn-specific content is stripped, generalizes to
  arbitrary `rn` sessions — validated here only against `rn/docs/design.md` itself, not against a wide
  sample of past session design docs.
- The version check is plain string equality between the recorded and installed plugin version — no
  ordering/semver-range logic is needed, since the check only asks "has anything changed," not "by how
  much."
- `migration-workflow.md` runs with no user gate; an occasional wrong reconciliation is an accepted
  risk, caught via normal PR/git-log review rather than a live approval step (per
  `push-and-review.md`).
- Cutting the actual `0.8.0` release (version bump + finalizing `CHANGELOG.md`) is a separate,
  explicit follow-up instruction per `plugin.md`'s release procedure — not a task in this session.

# Rules

- commit and push every change; one completion marker per task
- no separate Design sign-off task: the design was settled through discussion before this steering was
  written, so its approval folds into the plan gate
- `migration-workflow.md`'s reconciliation commits carry no user gate (see Assumptions)
- structural changes to `rn`'s skills/references must keep `claude plugin validate rn --strict` and
  `claude plugin validate . --strict` passing

# Tasks

### #1: Restructure `design-template.md` into the question-driven five-section contract

**Purpose**: Replace the current thin five-section template (Context & constraints / Approach /
Structure / Flow / Open questions) with the aiya-derived, generalized five-section structure
(Background & Goals / Assumptions & Constraints / Design overview / Detailed design / Alternatives
considered), each with explicit h3 questions and a per-section contract requiring decision + intent
for every question, no silent drops.

**Prerequisites**: none

**Steps**:

- [x] rewrite `rn/references/design-template.md`'s template block and per-section guidance
- [x] remove the "a section with nothing to record can be dropped" allowance; replace with "state the
      decision and the reasoning even when the answer is 'not applicable' or 'not considered'"
- [x] self-check (OK/NG per completion criterion, record in checks/1.md)
- [x] QA expert review (subagent)
- [x] Craft expert review (subagent, writing medium)
- [x] Design expert review (subagent)

**Completion criteria**:

- `design-template.md`'s five sections each carry h3 questions generalized from aiya's design.md, with
  no Conductor/CCS/Turn-specific wording remaining
- the per-section guidance states, for every question, that it must be answered with a decision and
  the intent behind it, and that "not applicable" is itself an answer requiring the same treatment —
  a reader following the guidance cannot produce a section with an unexplained gap
- the old "drop an empty section" allowance is gone from the file (grep confirms no trace)

### #2: Add the "update an existing design.md" branch to `planning-workflow.md` and `design-template.md`

**Purpose**: Planning must check whether an existing design.md already covers the session's area
before defaulting to a new path, and route that case through an update procedure rather than
from-scratch authoring.

**Prerequisites**: #1

**Steps**:

- [ ] add a check to `planning-workflow.md`'s design-location step: look for an existing design.md
      already covering the work's area; if found, point `Design:` at it and treat the work as an
      update
- [ ] add an "updating an existing design.md" procedure to `design-template.md`, distinct from the
      "copy the template verbatim" fresh-authoring steps, preserving the question+decision+intent
      contract while revising only what changed
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria**:

- `planning-workflow.md`'s design-location step explicitly instructs checking for a covering existing
  design.md before defaulting to a new path
- `design-template.md` contains a clearly separate update procedure from the fresh-authoring one
- following the update procedure on `rn/docs/design.md` (task #6) does not require discarding and
  rewriting sections that did not change

### #3: Add `Rn version:` to `steering-template.md`, stamped at creation

**Purpose**: Give every session a recorded version of the `rn` plugin it was authored under, so a
later mismatch is detectable.

**Prerequisites**: none

**Steps**:

- [ ] add an `Rn version: <version>` line to `steering-template.md`'s template block, alongside
      `Design:`
- [ ] update `planning-workflow.md`'s persist step (Step 5) to stamp this line with the currently
      installed plugin's version when writing a new `steering.md`
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)

**Completion criteria**:

- `steering-template.md`'s template block includes `Rn version:` and per-field guidance for it
- `planning-workflow.md`'s persist step names where the stamped value comes from (the installed
  plugin's version)

### #4: Author `migration-workflow.md`

**Purpose**: A new reference workflow that reconciles a session's `steering.md` / `design.md` /
remaining tasks against the currently installed `rn` templates and workflows when a version mismatch
is found, using LLM judgment rather than per-version bookkeeping.

**Prerequisites**: #1, #2, #3

**Steps**:

- [ ] write `rn/references/migration-workflow.md`: compare `steering.md` against
      `steering-template.md`, then `design.md` (if present) against `design-template.md`, then each
      remaining task against `task definition requirements`, in that order; for each, judge what has
      drifted from current convention and reconcile it
- [ ] specify: apply the reconciling edits and commit them directly — no user gate — then update the
      session's `Rn version:` line to the installed plugin version
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria**:

- `migration-workflow.md` names, in order, the three artifacts it reconciles (steering, design,
  remaining tasks) and what each is compared against
- the file states explicitly that reconciliation commits without a user gate and updates the recorded
  `Rn version:` line afterward
- the file does not rely on reading `CHANGELOG.md` version ranges — the comparison is always
  current-artifact-vs-current-template, regardless of which version the session started from

### #5: Wire the version check into each command skill

**Purpose**: Every `rn` command detects a version mismatch on an active session and triggers
`migration-workflow.md` before proceeding.

**Prerequisites**: #4

**Steps**:

- [ ] add a one-line step to `rn/skills/on/SKILL.md`, `dn/SKILL.md`, `up/SKILL.md`, `ty/SKILL.md`,
      `gm/SKILL.md`: compare the active session's `Rn version:` to the installed plugin's version;
      on a mismatch, run `${CLAUDE_PLUGIN_ROOT}/references/migration-workflow.md` first
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)

**Completion criteria**:

- all five `SKILL.md` files contain the version-check step, each citing `migration-workflow.md` rather
  than restating its procedure
- a command run against a session with a matching recorded version takes no extra action (the check is
  a no-op on match)

### #6: Update `rn/docs/design.md` under the new structure

**Purpose**: Dogfood the update procedure from #2 on `rn/docs/design.md` itself, recording the
decisions from #1–#5 (question-driven design.md contract, existing-design-update branch,
version-tracking/migration mechanism) under `design-template.md`'s new five-section shape.

**Prerequisites**: #1, #2, #3, #4, #5

**Steps**:

- [ ] follow `design-template.md`'s update procedure (from #2) to revise `rn/docs/design.md`
- [ ] record, with decision + intent per question: why the question-driven contract replaces the old
      thin template; why an existing-design.md-update branch was missing and how it's closed; why
      version-tracking has no user gate; what open questions remain
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria**:

- `rn/docs/design.md` follows the new five-section, h3-question structure with no unanswered question
  and no undocumented decision
- the doc's own "Open questions" entry about "default home for a session's design.md" (existing line)
  is either resolved by #2's branch or explicitly carried forward with updated reasoning
- `claude plugin validate rn --strict` and `claude plugin validate . --strict` both pass after this
  change

### #7: Evaluation sign-off

**Purpose**: Present the Acceptance criteria run to the user and take their verdict.

**Prerequisites**: #1, #2, #3, #4, #5, #6

**Steps**:

- [ ] run through every Acceptance criteria item above and record evidence for each
- [ ] present the results to the user
- [ ] take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- every Acceptance criteria item has recorded evidence
- the user has issued an explicit `/rn:ty` verdict on the run

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-07-05
- **Last completed**: #1 — restructure design-template.md (checked off, `checks/1.md` finalized)
- **Next**: #2 — finish verification. Round-1 fixes are committed (`984e3fe`); round-2 re-review came
  back QA PASS, Craft FAIL, Design FAIL. Concrete fixes still needed in
  `rn/references/design-template.md`'s "Updating an existing design.md" section before finalizing
  `checks/2.md`:
  1. The sentence "this reconciliation may already be current if `migration-workflow.md` has run since
     the document's last version-mismatch" (~line 123) is factually wrong: per task #3/#4's actual
     design, `Rn version:` lives on `steering.md` only — `design.md` has no version stamp of its own —
     and migration only fires for an active session with a stale stamp, so a dormant/closed session
     (e.g. `.rn/20260625-rn-lean/`) never re-triggers it. Remove/rewrite this claim rather than assert a
     per-document "last version-mismatch" that doesn't exist. Doing this also resolves Craft's dangling
     `migration-workflow.md` reference finding — no separate Invalid triage needed once the sentence is
     gone.
  2. Step 5's open-content routing (~lines 126-133) branches on "if there is no session `steering.md`
     exists" — but the whole Updating procedure is only ever invoked from inside an active session's
     `planning-workflow.md` Step 2, so a `steering.md` always exists at the moment it runs; that branch
     is dead code (self-contradicting), confirmed against `rn/docs/design.md`'s own task #6. Replace the
     branch condition with "is this `design.md` scoped to the current session alone, vs a canonical
     doc shared across sessions past and future (e.g. `rn/docs/design.md`)" — session-scoped → that
     session's `steering.md` Notes; canonical/cross-session → track outside `design.md` (e.g. a repo
     issue), since no single session's Notes survives once that session closes.
  This is iteration 2 of task #2's fix-triage cycle (cap 3). Next action on resume: dispatch the
  implementation expert with these two fixes, then re-run Craft + Design + QA (QA's criterion-3
  evidence quotes the exact prose being changed), then finalize `checks/2.md` and check off task #2.
- **Notes**: PR #16, branch `worktree-improve-design-template`. Tasks #3-#7 not yet started
  (prerequisites on #2). No open blockers beyond the task #2 fix above; no user-deferred paths.
