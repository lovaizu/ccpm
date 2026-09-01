Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

`rn` states good rules that nothing enforces. When one is broken, no blank is left behind, no second
reader sees it, no command fails, no gate holds — so it is simply not followed. The previous session
is the proof: `steering-template.md` already said "write 'the residue no longer keeps the tree
dirty', not 'DESIGN.md exists'", and that session's acceptance criteria were written as artifacts
existing anyway, reaching the user with nobody having noticed.

So the fix is not more advice, and it is not confined to acceptance criteria. This session sweeps
every rule `rn` states, asks of each one **"if this is broken, does it become visible or does it
stop?"**, and rebuilds the ones that answer neither. The acceptance-criteria failure gets the same
treatment as one instance among them.

# Acceptance criteria

- Someone maintaining `rn` can point at any rule it states and be told what happens when it is
  broken: either the mechanism that makes the breach visible or stops the flow, or a recorded reason
  why that rule is deliberately left unenforced. Every normative statement in `rn/references/*.md`
  and `rn/skills/*/SKILL.md` has one of the two — none was left unjudged, and none was judged by
  sampling a file rather than reading it.
- For each rule that was rebuilt, a third party can name the concrete event that now follows a
  breach — a blank that stays unfilled, a reviewer who reads it, a command that fails, a gate that
  holds. No rule was "fixed" by being restated more firmly.
- A planner writing a `steering.md` after this change cannot land an acceptance criterion phrased as
  an artifact existing without visibly leaving something unanswered — the failure that started this
  session is caught while the plan is still being written, not after it ships.
- Someone using `rn` has nothing new to learn and nothing new to do: same commands, same three gates
  (plan / design / evaluation), same `/rn:ty` `/rn:gm` verdicts, and no additional point where the
  session stops for them.
- Sessions planned before this change keep working: their `steering.md` stays readable and is brought
  up to date only through the existing version-mismatch path, with no hand-run migration.
- `CHANGELOG.md`'s `## [Unreleased]` carries one entry per change a user of `rn` would notice,
  written as the benefit to them.
- The fix is shown to work by being run, not by being read: a rule that was actually broken in a past
  session, replayed under the rebuilt files, is visibly caught — and a planner who was not part of
  this session, writing under them for the first time, is caught too. Where a replay still slips
  through, that is recorded and closed rather than left as a known miss.
- This document is the first plan written under the finished rules, and re-reading it under them at
  the end turns up nothing to fix.

# Assumptions

- **Verified fact.** `.rn/20260705-improve-design-template/steering.md` states its acceptance criteria
  as artifacts existing, while `rn/references/steering-template.md` already forbids that shape. The
  guidance was present and still failed, so adding advice text is not the fix.
- **Verified fact.** `rn` already contains both kinds of rule. Enforced: the `Rn version:` stamp
  (a mismatch is detected mechanically and triggers migration), the `complete task #N` commit marker
  (`/rn:up` reconciles it against `git log`), the explicit `/rn:ty` `/rn:gm` verdicts (approval cannot
  be inferred). Unenforced: the acceptance-criteria shape rule, the doc-division rule ("rationale
  lives only in `design.md`"), the deviation-escalation rule ("raise anything that would change the
  agreed plan or design"). The devices needed to fix the second group are therefore already proven
  inside `rn`; none has to be invented.
- **Verified fact.** The failure repeats one level up, inside this session. `steering-template.md`'s
  Steps block requires a `Verification expert review` on every task; it appears zero times in
  `.rn/20260625-rn-lean/steering.md`, zero in `.rn/20260705-improve-design-template/steering.md`, and
  zero in the first draft of this document. Nothing compares a written Steps list against the
  template, and each session was written by copying the previous session's shape rather than the
  template — so the omission propagated across three sessions unnoticed. This is a second confirmed
  instance of the same mechanism, and #1 checks the whole file set for others of its kind.

- **Unverified.** The rules that turn out to be unenforced can be covered by the devices `rn` already
  uses, without inventing a new kind of enforcement. If the sweep turns up a rule that none of them
  fits, task #2 decides what to do about that rule specifically.
- **Unverified.** One extra subagent read between drafting a plan and showing it to the user is an
  acceptable cost. The plan is currently the only artifact in `rn` that reaches the user with no
  expert having read it.

# Rules

- commit and push every change; one completion marker per task
- do not close a gap by rewording the rule — every fix names the event that follows a breach
- read each file end to end when judging it; a rule missed by skimming is a rule left unenforced
- this document is the dogfood: as each rule lands, re-read this document under it
- keep `claude plugin validate rn --strict` and `claude plugin validate . --strict` passing

# Tasks

### #1: Sweep every rule `rn` states and judge whether anything enforces it

**Purpose**: Produce the exhaustive judgement the whole session builds on — for each normative
statement in `rn`, whether breaking it becomes visible, stops the flow, or passes unnoticed.

**Prerequisites**: none

**Steps**:

- [ ] read each of `rn/references/*.md` (8 files) and `rn/skills/*/SKILL.md` (5 files) end to end and
      extract every normative statement
- [ ] judge each one: visible on breach / stops the flow / neither — naming the mechanism where one
      exists
- [ ] record the judgement in `.rn/20260830-issue-17/rule-inventory.md`, one row per rule, with its
      source location
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)

**Completion criteria** (serves: exhaustive judgement)

- every normative statement in the 13 files carries a judgement with grounds; a reader can take any
  line of any of those files and find it accounted for
- the unenforced set is separated from the enforced set, so #2 has a definite list to work from
- no row asserts a mechanism that does not exist — each named mechanism is quoted from the file that
  implements it

### #2: Decide what to do with each unenforced rule, and record it in `rn/docs/design.md`

**Purpose**: Settle, per unenforced rule, which device carries it — or that it stays unenforced on
purpose — with the reasoning recorded where reasoning belongs.

**Prerequisites**: #1

**Steps**:

- [ ] group the unenforced rules by the device that fits (question in place of a blank field, a second
      reader, a mechanical check, a named link that leaves orphans visible, a checkbox, a gate)
- [ ] decide the acceptance-criteria case explicitly — it is the session's originating instance
- [ ] record each decision with its reasoning in `rn/docs/design.md`, following
      `design-template.md`'s "updating an existing design.md" procedure
- [ ] record, for each rule deliberately left unenforced, why enforcing it costs more than it saves
- [ ] desk-replay each candidate device against the known failure in
      `.rn/20260705-improve-design-template/steering.md` — state what would have happened there — and
      drop any device that would have let it through
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: concrete event per rule, exhaustive judgement, no new user steps)

- every rule #1 marked unenforced has either a named device or a recorded reason for staying that way
- for each device, the doc states the event that follows a breach — a reader can describe what
  happens without reading the implementation
- a reader who was not in this conversation can tell why "write the advice more clearly" was rejected
- no device survives that would have let the known past failure through — each is answered against
  that case before anything is built on it
- nothing in #4–#6 is left to improvisation: each has a stated shape to build to
- no decision adds a stop the user has to attend

### #3: Design sign-off

**Purpose**: The user approves the devices and their placement before any file is rewritten to them.

**Prerequisites**: #2

**Steps**:

- [ ] present `rn/docs/design.md`'s new and changed sections to the user on the PR
- [ ] take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria** (serves: every criterion below depends on this being the agreed shape)

- the recorded shape is the user's, confirmed by an explicit `/rn:ty` verdict — no part of #4–#6 rests
  on a shape the user has not seen

### #4: Enforce the planning rules — `steering-template.md` and `planning-workflow.md`

**Purpose**: Make the rules that govern how a plan is written hold on their own, including the one
that failed and started this session.

**Prerequisites**: #3

**Steps**:

- [ ] apply the decided devices to `steering-template.md`
- [ ] apply them to `planning-workflow.md`, so template and workflow ask the same questions in the
      same terms
- [ ] put the plan in front of a reviewer before the plan-gate ask, applying the same tests the writer
      was given, with revisions handled by the coordinator rather than a new user stop
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: originating failure caught while writing, concrete event per rule,
no new user steps)

- an artifact-existence acceptance criterion cannot be written without leaving something visibly
  unanswered
- no path through `planning-workflow.md` reaches the plan-gate ask with the plan unread by a reviewer
- a planner reading the template and the workflow is never told two different things
- the user still sees one plan gate, with the same commands and verdicts
- re-reading this session's own `steering.md` against the finished files turns up nothing that fails

### #5: Enforce the execution and verification rules — `task-execute-workflow.md` and `task-verify-workflow.md`

**Purpose**: Make the rules governing how a task is carried out and checked hold on their own — most
of all the deviation-escalation rule, which today fires only if someone happens to notice.

**Prerequisites**: #3

**Steps**:

- [ ] apply the decided devices to `task-execute-workflow.md`
- [ ] apply them to `task-verify-workflow.md`
- [ ] give the escalation rule a trigger that does not depend on noticing
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: concrete event per rule, no new user steps)

- each rule these two files state either has a named device or is recorded as deliberately unenforced
- a change to the agreed plan or design cannot reach the user's branch without having been surfaced
- the per-task review structure the user never sees is unchanged in what it costs them: still no
  per-task sign-off

### #6: Enforce the session-operation rules — `status-display.md`, the five `SKILL.md`s, `design-template.md`, `migration-workflow.md`, `pr-feedback-workflow.md`

**Purpose**: Close the remaining files so the sweep is whole rather than confined to the two
workflows that happened to fail.

**Prerequisites**: #3

**Steps**:

- [ ] apply the decided devices to each of the nine remaining files
- [ ] leave a recorded reason wherever a rule is kept unenforced
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)
- [ ] Design expert review (subagent)

**Completion criteria** (serves: exhaustive judgement, backward compatibility, no new user steps)

- no rule in these nine files is left both unenforced and unexplained
- a `steering.md` written before this change still reads correctly and still updates only through the
  version-mismatch path
- `claude plugin validate rn --strict` and `claude plugin validate . --strict` both pass

### #7: Run the rebuilt rules and see whether they actually catch what advice did not

**Purpose**: Establish by execution — not by reading — that the rebuilt rules stop the failures they
were built for, and close whatever still slips through.

**Prerequisites**: #4, #5, #6

**Steps**:

- [ ] replay the known failure: take the goal of `.rn/20260705-improve-design-template` and write its
      plan again under the rebuilt template and workflow, then compare what comes out against the
      artifact-existence criteria that session actually shipped
- [ ] run a planner that was not part of this session — `claude -p "/rn:on <a small throwaway goal>"
      --plugin-dir rn` — and read the `steering.md` it produces cold
- [ ] try to break each rebuilt rule on purpose and record what happens: which blank stays unfilled,
      which reviewer objects, which command fails, which gate holds
- [ ] walk a deviation scenario through `task-verify-workflow.md` and point at the line where the
      escalation trigger fires
- [ ] record every miss, fix it in the file it belongs to, and re-run that replay
- [ ] self-check (OK/NG per completion criterion, record in checks/7.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)

**Completion criteria** (serves: shown to work by being run, originating failure caught while writing,
concrete event per rule)

- the replayed past failure is caught under the rebuilt files, and the transcript shows where — a
  reader can see the point at which the old plan could no longer have been written
- the cold planner's `steering.md`, read by someone applying the new tests, has no acceptance
  criterion satisfied by an artifact merely existing
- every deliberate breach produced a named, observed event; any rule whose breach produced nothing was
  fixed and re-run, and none is left recorded as a known miss
- the run's limits are stated — one replay and one cold run are evidence, not proof, and the record
  says so rather than overclaiming

### #8: Record the change in `CHANGELOG.md`

**Purpose**: Someone reading the changelog learns what is different for them, in their terms.

**Prerequisites**: #4, #5, #6, #7

**Steps**:

- [ ] add one entry per user-noticeable change under `## [Unreleased]`, as `<what changed> — <why it
      helps the user>`
- [ ] self-check (OK/NG per completion criterion, record in checks/8.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, writing medium)
- [ ] Verification expert review (subagent, writing medium)

**Completion criteria** (serves: changelog entries)

- each entry names a difference the person using `rn` will notice, with no file names or internal
  steps they never see
- no entry exists for a change nobody notices

### #9: Evaluation sign-off

**Purpose**: Present the Acceptance criteria run to the user and take their verdict.

**Prerequisites**: #1, #2, #3, #4, #5, #6, #7, #8

**Steps**:

- [ ] run through every Acceptance criteria item above and record the evidence for each
- [ ] present the results to the user
- [ ] take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria** (serves: the goal itself)

- every Acceptance criteria item has recorded evidence, the dogfood and replay items included — this document read
  back under the finished rules
- the user has issued an explicit `/rn:ty` verdict on the run

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
