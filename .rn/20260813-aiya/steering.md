Rn version: 0.8.0
Design: aiya/docs/design.md

# Goal

One expert delivers what used to take a team.

Getting there means AI running many work-streams at a single goal, with the human steering at a few
points rather than supervising. Two things break that today: what the directing agent has to hold
grows with the work until it collapses, and the work drifts off the goal with nobody noticing until
the end.

`aiya` is the Claude Code plugin that removes both.

# Acceptance criteria

**The purpose is reached — one person got real work delivered, and was not needed in between:**

- Real work came back from a goal alone: the human said what they wanted, and what arrived met that
  goal's own acceptance criteria, with any shortfall recorded rather than omitted.
- The human was asked to act only a few times, and every time it was a decision — approve or
  redirect — never watching work in progress.
- The work stayed on the goal: a deviation that arose during the run was caught during the run and
  corrected, not discovered at the end.
- Directing stayed affordable as the work grew: what the directing agent had to hold did not scale
  with the amount of work done.

Each of the four is shown by evidence a third party can open and re-read. None is asserted.

**The benefit is available to someone other than its author:**

- A reader who has never seen aiya can install it and drive one goal from start to finish, knowing at
  every stop what they are being shown and what to say back.
- The shipped artifacts describe one plugin, and no load-bearing term is left undefined.
- Every user-facing choice in the shipped plugin was ratified by the user; none traces back to an
  unratified inference.
- aiya installs from this marketplace and validates cleanly.

# Assumptions

- `claude plugin validate` and `claude -p … --plugin-dir` are available; if not, verification is done
  by hand and recorded as such.
- `dogfood/techting-requirements.md` is a carried-forward input whose source no longer exists on disk —
  the `worktree-techting` branch it came from is deleted. It is not regenerable.
- `aiya/docs/design.md` is the substance to build on, not a frozen input.

# Rules

How this session works. What aiya *is* lives in `design.md`; what a user sees lives in the plugin's
own artifacts; neither is restated here.

- **Agree the action before a task starts.** State the concrete actions the task will take — what gets
  decided, what gets written, and where — and get the user's agreement before taking them. This is not
  one of the three scheduled gates; it is a per-task alignment on *what will be done*, and no task
  starts without it.
- **A decision the user has not made is not a decision.** Where a task must pick a name, a surface, a
  default or a policy, it is put to the user — never inferred. A string already on disk is not evidence
  that anyone chose it.
- 1 task = 1 commit; commit and push every change; one completion marker per task.
- **UX first, then design, then implementation.** The experience decides the surface; the design answers
  to it; the build implements the design. A lower layer never silently overrides a higher one — a
  contradiction found while building goes back to the higher artifact.
- **Define a term before using it.** No load-bearing term enters an artifact undefined, and a term that
  cannot be defined concretely is replaced rather than kept.
- **Build from the final deliverable.** No intermediate memos or side notes — every task edits the real
  file it is about, and brushes it up there.
- **Curate, never invent.** Anything shipped as a standard or a checklist is drawn from established
  practice and carries its source; nothing is authored from a blank page.
- **The dogfood runs under `.rn/20260813-aiya/dogfood/`.** It is session material, not a plugin: nothing
  it produces ships, and keeping it in the repo is what lets a third party open the run's evidence.

# Tasks

Each task states what it must achieve and the state that means it is done. **Its Steps are agreed with
the user when the task starts** — the review steps below are rn's own process, the work steps are not.

### #1: Decide what using aiya is like

**Purpose**: Settle the human's experience of driving one goal from start to finish — the thing every
later artifact answers to.

**Prerequisites**: none.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/1.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)
- [ ] Design expert review (subagent)

**Completion criteria**:

- Someone who has never seen aiya can follow the decided experience end to end and knows, at every
  point where aiya stops for them, what they are shown and what to say back.
- Every user-facing choice it fixes was ratified by the user, and none is left for a later task to
  invent.
- Nothing it shows rests on a mechanism that was not confirmed to exist.

### #2: Complete the design against that experience

**Purpose**: Make the design a complete answer to the decided experience.

**Prerequisites**: #1.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/2.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)
- [ ] Design expert review (subagent)

**Completion criteria**:

- A reader can answer from the design alone what every term in it means and what the plugin is made
  of — nothing left to be inferred, no structural question unanswered.
- Nothing in the design contradicts the decided experience, and every carried-forward decision either
  still stands or its replacement is recorded with the intent behind it.

### #3: Design sign-off

**Purpose**: Take the user's sign-off on the experience and the design together, before anything is
built on them.

**Prerequisites**: #2.

**Steps**:

- [ ] Present both to the user on the PR and take the verdict via `/rn:ty` (approve) or `/rn:gm`
      (revise → address the feedback, re-present). Repeat until approved.

**Completion criteria**:

- The experience and the design are approved by the user.

### #4: Build the plugin so it runs

**Purpose**: Turn the approved design into a plugin that actually does what it describes.

**Prerequisites**: #3.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/4.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)
- [ ] Design expert review (subagent)

**Completion criteria**:

- Every contract in the approved design is present in what ships, and a third party can trace each one
  back to the design it came from.
- The plugin stands on its own: driving it end to end needs nothing it does not ship.
- No superseded decision survives anywhere in it.

### #5: Make it installable by someone else

**Purpose**: Put aiya where another person can get it and have it work.

**Prerequisites**: #4.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/5.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)

**Completion criteria**:

- Both strict validations pass with no warning, on output a third party can re-run.
- Everything that describes aiya to a prospective user describes the plugin that actually ships, and
  every path a reader can follow to it resolves.

### #6: Prove the purpose is reached

**Purpose**: Run aiya on real work and show the four purpose criteria hold. This is the point of the
whole build.

**Prerequisites**: #5.

**Steps**:

- [ ] Agree this task's work steps with the user, then replace this line with them.
- [ ] self-check (record OK/NG per criterion in `.rn/20260813-aiya/checks/6.md`)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing)
- [ ] Verification expert review (subagent, fact-check)

**Completion criteria**:

- Each of the four purpose criteria is backed by evidence from the run that a third party can open and
  re-read.
- The work aiya produced meets its own acceptance criteria, with any shortfall recorded as a delta
  rather than omitted.
- `dogfood/result.md` distinguishes what was measured from what was only asserted, and states what was
  not covered.

### #7: Evaluation sign-off

**Purpose**: Take the user's sign-off on the Acceptance criteria run — the session's closing gate.

**Prerequisites**: #6.

**Steps**:

- [ ] Present the Acceptance criteria run result to the user and take the verdict via `/rn:ty`
      (approve → session closes) or `/rn:gm` (revise → address the feedback, re-present).

**Completion criteria**:

- The Acceptance criteria run is approved by the user.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
