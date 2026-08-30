Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

When someone runs `/rn:on`, the plan it produces should aim at what that person actually wants, and
the session must not be able to end with every box ticked while the goal itself is unmet. Today it
can: the previous `rn` session's own acceptance criteria read like "`design-template.md`'s five
sections each carry explicit h3 questions" — a check on an artifact, which can hold while the person
who asked for the work is still unserved. The advice against exactly that is *already written* in
`steering-template.md` ("write 'the residue no longer keeps the tree dirty', not 'DESIGN.md exists'")
and was still not followed. So the change is to the shape the planner fills in and to who reads the
plan before the user does — not to the wording of the advice.

# Acceptance criteria

- Reading a `steering.md` written after this change, a third party can say for each acceptance
  criterion **whose situation changes and how**; none of them is satisfied by an artifact merely
  existing.
- No acceptance criterion can hold while the goal is unmet — each one survives the question "could
  this be true and the person still not have what they asked for?"
- A planner cannot park a conclusion that a task is supposed to reach in `Assumptions`: whatever a
  task is meant to determine has a home outside that section, and each surviving assumption is marked
  as verified fact or as unverified.
- Each task's completion criteria state the condition under which that task's **purpose** is
  fulfilled and name which acceptance criterion it serves, so a task that serves none is visible as
  such rather than passing unnoticed.
- The `steering.md` a user is shown at the plan gate has already been read once by a reviewer applying
  these same tests; an unreviewed plan never reaches the user.
- Someone using `rn` has nothing new to learn: the commands, the three gates (plan / design /
  evaluation) and the `/rn:ty` `/rn:gm` verdicts are unchanged.
- Sessions planned before this change keep working: their `steering.md` stays readable, and it is
  brought up to date only through the existing version-mismatch path — nobody has to run a migration
  by hand.
- `CHANGELOG.md`'s `## [Unreleased]` section carries one entry per user-facing change here, written as
  the benefit to the person using `rn`.
- This session's own `steering.md` passes every test above — it is the first plan written under them,
  and re-reading it under the finished tests turns up nothing to fix.

# Assumptions

- **Verified fact.** `.rn/20260705-improve-design-template/steering.md` states its acceptance criteria
  as artifact-existence statements, while `rn/references/steering-template.md` already forbids that
  shape. The guidance failed in use, not by being absent — so adding more advice text is not the fix.
- **Unverified.** The question-driven shape that replaced `design.md`'s free-form sections in 0.8.0
  works here for the same reason it worked there. Only one session has run under it, so there is no
  comparison to draw on.
- **Unverified.** One extra subagent review between drafting the plan and showing it to the user is an
  acceptable cost at the plan gate — it is the only place in `rn` where an artifact currently reaches
  the user with no expert having read it.
- **Not an assumption — a question this session answers.** Which questions replace the free-form
  fields, how the two tests are worded, how a completion criterion is tied to an acceptance criterion,
  and which expert axis reviews the plan are all undecided here on purpose. Task #1 decides them and
  task #2 takes the user's sign-off; nothing below is built on a guess about them.

# Rules

- commit and push every change; one completion marker per task
- do not solve this by adding advice text alone — that approach is already in the file and already
  failed
- this session's own `steering.md` is the dogfood: as each test lands, re-read this document under it
- keep `claude plugin validate rn --strict` and `claude plugin validate . --strict` passing

# Tasks

### #1: Decide the new plan shape and record it in `rn/docs/design.md`

**Purpose**: Settle what the planner is asked instead of a blank field, how the two tests are worded,
how a completion criterion is tied to an acceptance criterion, and where the plan review sits — and
record each decision with its reasoning in `rn`'s canonical design doc.

**Prerequisites**: none

**Steps**:

- [ ] establish why the existing guidance did not take effect (compare what `steering-template.md`
      already says against what the last two sessions' `steering.md` actually wrote)
- [ ] update `rn/docs/design.md` via `design-template.md`'s "updating an existing design.md"
      procedure, recording the four decisions with their reasoning
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: falsification test, assumptions, traceability, reviewer):

- `rn/docs/design.md` answers, with reasoning, all four: what the planner is asked in place of each
  free-form field, how the two tests are stated so writer and reviewer apply the same one, how a
  completion criterion is tied to an acceptance criterion, and at what point the plan is reviewed
- a reader who was not in this conversation can tell from the doc why "write clearer advice" was
  rejected as the fix, and what is expected to make the new shape hold where advice did not
- no decision below (#3–#5) is left to improvisation: each has a stated shape to build to

### #2: Design sign-off

**Purpose**: The user approves the plan's new shape before the templates and workflow are rewritten to
it.

**Prerequisites**: #1

**Steps**:

- [ ] present `rn/docs/design.md`'s new/changed sections to the user on the PR
- [ ] take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria** (serves: every criterion below depends on this shape being the agreed one):

- the shape recorded in `rn/docs/design.md` is the user's, confirmed by an explicit `/rn:ty` verdict —
  no part of #3–#5 rests on a shape the user has not seen

### #3: Turn `steering-template.md`'s free-form fields into questions the planner must answer

**Purpose**: Make it unnatural to answer with an artifact's name — the planner is asked what changes
for whom, not asked to fill a section called "Acceptance criteria".

**Prerequisites**: #2

**Steps**:

- [ ] rewrite the template block and per-section guidance to the shape approved in #2
- [ ] state the two tests by name in the template, so the writer and the #5 reviewer apply the same
      wording
- [ ] require each completion criterion to name the acceptance criterion it serves
- [ ] give whatever a task must discover a home outside `Assumptions`, and require each remaining
      assumption to be marked verified or unverified
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: "whose situation changes", falsification test, assumptions,
traceability):

- a planner following the template cannot produce an acceptance criterion phrased as an artifact
  existing without visibly leaving a question unanswered
- the two tests appear in the template in the exact wording the reviewer will use — one place, not two
- `Assumptions` has no room for a conclusion a task is meant to reach: the template says where such an
  item goes instead
- re-reading this session's own `steering.md` against the finished template turns up nothing that
  fails the new tests

### #4: Rewrite `planning-workflow.md` to walk the planner through those questions

**Purpose**: The procedure that produces a plan asks the questions in order and does not let a
free-form field come back in through the workflow's own wording.

**Prerequisites**: #3

**Steps**:

- [ ] revise the goal / criteria / assumptions / decomposition steps to drive from the questions in
      #3 rather than from field names
- [ ] remove or rewrite any step wording that invites artifact-shaped answers
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: "whose situation changes", falsification test, assumptions):

- the workflow's planning steps and the template ask the same questions in the same terms — a planner
  reading both is never told two different things
- the workflow no longer contains guidance that only exhorts ("state the end-state, never actions")
  without a question or test that makes the failure visible

### #5: Put a review between the drafted plan and the plan gate

**Purpose**: Close the one place in `rn` where an artifact reaches the user with no expert having read
it — the plan itself.

**Prerequisites**: #3

**Steps**:

- [ ] add the review step to `planning-workflow.md` before the plan-gate ask, with the reviewer
      applying the two tests from #3 and the traceability link
- [ ] specify what happens on a finding: the coordinator revises the plan and re-reviews before the
      user sees it — no new user gate is introduced
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: reviewer before the gate, nothing new to learn):

- no path through `planning-workflow.md` reaches the plan-gate ask without the plan having been
  reviewed
- the user's experience is unchanged: still three gates, same commands, same verdicts — the review is
  not a fourth stop
- `claude plugin validate rn --strict` and `claude plugin validate . --strict` both pass

### #6: Record the change in `CHANGELOG.md`

**Purpose**: Someone reading the changelog learns what is different for them, in their terms.

**Prerequisites**: #3, #4, #5

**Steps**:

- [ ] add one entry per user-facing change under `## [Unreleased]`, in `<what changed> — <why it helps
      the user>` form
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)

**Completion criteria** (serves: changelog entries):

- each entry names a difference the person using `rn` will notice, with no reference to file names or
  internal steps they never see
- no entry exists for a change nobody notices (refactors, wording-only edits)

### #7: Evaluation sign-off

**Purpose**: Present the Acceptance criteria run to the user and take their verdict.

**Prerequisites**: #1, #2, #3, #4, #5, #6

**Steps**:

- [ ] run through every Acceptance criteria item above and record the evidence for each
- [ ] present the results to the user
- [ ] take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria** (serves: the goal itself):

- every Acceptance criteria item has recorded evidence, including the dogfood item — this document
  read back under the finished tests
- the user has issued an explicit `/rn:ty` verdict on the run

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-08-30
- **Last completed**: none — planning only; no task has been started
- **Next**: #1 Decide the new plan shape and record it in `rn/docs/design.md`
- **Notes**: branch `worktree-issue-17`, draft PR https://github.com/lovaizu/ccpm/pull/21. The plan
  gate is still open — the user has not issued a `/rn:ty` or `/rn:gm` verdict on this plan yet, so
  take that verdict before starting #1. The four moves agreed with the user (question-driven fields,
  two named tests, completion↔acceptance traceability, a review before the plan gate) are the
  approach; their concrete wording is deliberately undecided and is #1's job.
