Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

Let `rn` be improved from how its own sessions actually ran, using the conversation log as evidence
rather than memory. Today that is impractical: nothing in the Claude Code conversation log (JSONL)
says which `rn` session or which task an entry belongs to, so finding a session's log and cutting it
into per-task intervals means matching `sessionId` / `cwd` / `gitBranch` and `git log` timestamps by
hand, and sessions running concurrently in worktrees of one repository cannot be told apart from
inside the log at all.

Two things follow, in this order. First, `rn` writes markers into the JSONL so a session's log can be
located by a value unique to that session, split by task, and read **while the session is still
open**. Second, on top of those markers, `rn` gains a retrospective — deliberately split into two
stages so the user is involved at exactly one point of their own choosing: a **collection** stage that
runs silently at each `/rn:dn` and only records friction that actually left a trace, and a
**stocktake** stage the user invokes, which surfaces only friction that recurs across intervals, turns
it into improvement proposals, and files them as issues on the user's approval.

The separation is the point, not an implementation detail: asking for a proposal from one session's
worth of material forces noise into the shape of an improvement, and asking at every suspend makes the
retrospective a tax. Collecting facts silently and proposing only across accumulated material means a
retrospective with nothing to say naturally says nothing.

# Acceptance criteria

- A session's JSONL is locatable by grepping a single session-identifying marker, without inspecting
  `sessionId`, `cwd`, or `gitBranch`.
- The session-identifying value is unique per session (e.g. a commit hash), so two sessions never
  share it.
- Every task's interval boundary is discoverable inside the JSONL by grep alone — no correlation
  against `git log` timestamps.
- A boundary marker names its task from the marker line alone — which session, and which task —
  without consulting `steering.md` at any revision or any commit history. A bare task number does
  not satisfy this.
- The same holds for a collected friction record: it names its task without depending on
  `steering.md`'s task list as it stands later.
- Sessions running concurrently against worktrees of one repository are distinguishable by grepping
  their JSONLs.
- All of the above hold mid-session, before the session ends — not only after it closes.
- The collection stage runs with no user interaction and no user-visible output, and records nothing
  when the interval left no friction trace.
- The stocktake stage runs only when invoked, presents only friction recurring across intervals, and
  files an issue only after the user approves it.
- One `rn` session spanning several conversations (several JSONL files) is still locatable and
  splittable as one session.
- `rn/docs/design.md` records the decisions and their rejected alternatives; `rn/README.md` describes
  what a user sees and does; `rn/CHANGELOG.md` carries the entries under `## [Unreleased]`.
- The mechanism is demonstrated against this session's own JSONL, with the commands and observed
  output recorded — not argued from reasoning alone.
- `claude plugin validate` passes `--strict` for both the plugin and the marketplace root.

# Assumptions

- Claude Code appends assistant text and tool calls/results to the conversation JSONL as they happen,
  so a string emitted during a turn is greppable before the conversation ends. **Unverified** — task
  #1 measures it, and if it proves false the marker design changes.
- A conversation's JSONL lives at `~/.claude/projects/{project-slug}/{sessionId}.jsonl`. Observed
  today: this worktree's project slug is `-Users-kiyo-work-lovaizu-ccpm`, the main checkout's path —
  so worktrees of one repository may share a project directory, which is exactly why `cwd` alone does
  not separate concurrent sessions.
- Claude Code itself cannot be modified; every marker must be produced by `rn`'s own procedures
  through ordinary agent output or tool calls.
- The `chore: start session` commit gives each session a value that is unique by construction.
- A task number is **not** a stable identifier. `steering.md`'s task list is revised during a session
  (`/rn:gm` re-does work and can rewrite or add tasks), so `#1` at one moment and `#1` later need not
  be the same task. Git history is not a fallback either: PRs land on `main` squashed, so the
  intermediate `steering.md` revisions that would say what `#1` meant do not survive — observed on
  `.rn/20260705-improve-design-template/steering.md`, which has exactly one commit on `main`.
- An `rn` session spans several conversations, so one session maps to N JSONL files.
- Reading and analysing a JSONL is delegated to a subagent, so it does not consume the coordinator's
  remaining context — which is what makes collection affordable at `/rn:dn`, where context is by
  definition nearly exhausted.

# Rules

- commit and push every change; one completion marker per task
- artifacts in English (`.claude/rules/language.md`); console exchanges in the user's language
- never write a marker's literal trigger substring in ordinary prose or bookkeeping commits — it makes
  the marker fire on itself
- no version bump and no release here: user-facing changes accumulate under `CHANGELOG.md`'s
  `## [Unreleased]`

# Tasks

### #1: Measure how a string actually reaches the JSONL

**Purpose**: Determine by measurement — not by reasoning — which way of emitting a string lands in the
live conversation JSONL and can be grepped while the conversation is still open.

**Prerequisites**: none

**Steps**:

- [ ] enumerate the candidate emission points (assistant message text, a Bash command string, a Bash
      command's output, a tool result)
- [ ] emit a distinct probe string by each candidate in this conversation
- [ ] grep the live JSONL for each probe and record whether it landed, how soon, and in which fields
- [ ] confirm each hit came from the emission itself, not from the instruction that requested it
- [ ] determine what distinguishes the JSONLs of concurrent worktree sessions of one repository
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- At least one emission method is shown by recorded command-and-output evidence to put an arbitrary
  string into the live JSONL, greppable before the conversation ends.
- Methods that landed and methods that did not are separately recorded; no method is reported as
  working without its observed evidence.
- Each reported hit is attributable to the emission itself — a hit that only matches the requesting
  instruction is not counted as a landing.
- The question "what tells two concurrent worktree sessions apart from inside the JSONL" has a
  measured answer, not a presumed one.

### #2: Record the decisions in `rn/docs/design.md`

**Purpose**: Settle the marker format and the two-stage retrospective as decisions with reasoning in
`rn`'s canonical design doc.

**Prerequisites**: #1

**Steps**:

- [ ] decide the session marker's value and textual form, from #1's measurements
- [ ] decide the task-boundary marker's form, and at which points it is emitted
- [ ] decide how a marker names its task so it stays readable after the task list has been revised —
      the marker describes what was being worked on, not a row in a document that moves
- [ ] decide where collected friction facts are stored, and their record shape
- [ ] decide the bar for what counts as a friction fact worth recording
- [ ] decide the stocktake command's name and its call sites (user invocation, `/rn:dn`, session end)
- [ ] update `design.md` per `design-template.md`'s "Updating an existing design.md" procedure
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (fact-check, subagent)
- [ ] Design expert review (subagent)

**Completion criteria**:

- Every decision listed in Steps is present in `design.md` with its reasoning and the alternative it
  was chosen over; none is stated as a bare choice.
- `design.md` still answers each of `design-template.md`'s h3 questions after the update, with no
  question left silently unanswered.
- No statement in `design.md` contradicts #1's measured results.
- The document reads as one design, not as a new section bolted onto the old one — the existing
  sections that the new mechanism touches are updated rather than duplicated.
- The marker form and the friction record shape both survive a revised task list: `design.md` states
  what each carries to stay self-describing, and why a bare task number was rejected.

### #3: Design sign-off

**Purpose**: The user approves the design before anything is built on it.

**Prerequisites**: #2

**Steps**:

- [ ] push and present `design.md` on the PR
- [ ] take the verdict: `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The user has approved `design.md` through an explicit verdict; no revision request from that review
  remains unaddressed.

### #4: Emit the markers

**Purpose**: Make `rn`'s procedures write the session marker and the task-boundary markers into the
JSONL at the points the design fixes.

**Prerequisites**: #3

**Steps**:

- [ ] emit the session marker where the design places it (`/rn:on`, and on resume so every one of the
      session's JSONL files carries it)
- [ ] emit the task-boundary markers at task start and task completion
- [ ] update the affected skills and references (`on`, `dn`, `up`, `task-execute-workflow`,
      `task-verify-workflow`) consistently, with the format defined in exactly one place
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- Grepping this repository's JSONLs for the session marker returns this session's log and no other
  session's, demonstrated with the command and its output.
- For a task that has started and finished under the new steps, both boundaries are found by grep
  alone, and the interval between them contains that task's work.
- The marker format is defined in one place; the skills and references that emit it cite that place
  rather than restating the format.
- Emitting the markers changes nothing the user sees in normal operation beyond the marker line
  itself — no new prompt, no new gate.

### #5: Build the collection stage

**Purpose**: At each `/rn:dn`, silently extract the interval's friction facts to the store, via a
subagent, recording nothing when there is no trace.

**Prerequisites**: #4

**Steps**:

- [ ] write the collection procedure as a reference: locate the JSONL by marker, cut the interval,
      extract only traced friction, append to the store
- [ ] fix the extraction bar in that reference so an interval with no trace yields no record
- [ ] wire the call into `/rn:dn` so it runs without asking the user anything
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- Running `/rn:dn` produces no question and no retrospective output to the user, and `/rn:dn`'s own
  existing behaviour is unchanged.
- Every recorded fact cites the JSONL evidence it came from; a record with no citable trace is not
  producible under the procedure.
- An interval with no friction trace results in no record — the empty outcome is the procedure's
  normal path, not an error.
- The coordinator's context is not spent reading the JSONL — the reading happens in a subagent.

### #6: Build the stocktake stage

**Purpose**: Give the user one command that reads the accumulated facts, proposes only recurring
friction as improvements, and files approved ones as issues.

**Prerequisites**: #5

**Steps**:

- [ ] add the command skill, and the stocktake procedure as a reference
- [ ] make the procedure surface only friction recurring across intervals, each with its evidence
- [ ] take the user's approval per proposal, and file issues only for approved ones
- [ ] wire the same procedure into the end of a session, per the design
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- The command runs only when invoked; nothing in the session triggers it on its own except the
  session-end point the design fixes.
- A proposal is shown only for friction appearing in more than one interval, and each carries the
  facts it rests on.
- No issue is filed without an explicit user approval for that proposal.
- With no accumulated facts, the command reports that plainly and files nothing — it does not
  manufacture a proposal.
- `claude plugin validate --strict` passes for the plugin and the marketplace root with the new
  command present.

### #7: Update `README.md` and `CHANGELOG.md`

**Purpose**: Describe the retrospective as a user experiences it, and record the user-facing changes.

**Prerequisites**: #6

**Steps**:

- [ ] update `rn/README.md` — what the user sees, when, and what they are asked
- [ ] add the entries under `CHANGELOG.md`'s `## [Unreleased]`, one line each: what changed and why it
      helps
- [ ] self-check (OK/NG per completion criterion, record in checks/7.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (fact-check, subagent)

**Completion criteria**:

- The README describes the retrospective in scenario form, and a reader can tell from it that
  collection is silent and stocktake is theirs to invoke.
- Every user-facing change from #4-#6 has a `## [Unreleased]` entry; no entry describes a change that
  was not made.
- No version bump and no released `CHANGELOG` section were introduced.

### #8: Demonstrate on this session's own JSONL

**Purpose**: Prove the whole path end to end on real material — locate this session's log by marker,
split it by task, run collection and stocktake.

**Prerequisites**: #7

**Steps**:

- [ ] locate this session's JSONL files by the session marker alone
- [ ] split one of them into per-task intervals by the boundary markers alone
- [ ] run the collection stage over a real interval and inspect what it recorded
- [ ] run the stocktake command and inspect what it proposed
- [ ] record the commands and observed output in checks/8.md
- [ ] self-check (OK/NG per completion criterion, record in checks/8.md)
- [ ] QA expert review (subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- Locating and splitting are done with the markers alone; the record shows no fallback to `sessionId`,
  `cwd`, `gitBranch`, or `git log` timestamps.
- The collection run's output is consistent with what the interval actually contains — recorded
  friction is traceable to the interval, and no friction visible in the interval is silently dropped.
- The stocktake run either proposes something backed by recurring facts, or reports nothing to
  propose; a proposal without supporting facts counts as a failure.
- The demonstration happens while this session is still open.

### #9: Evaluation sign-off

**Purpose**: The user approves the Acceptance criteria run.

**Prerequisites**: #8

**Steps**:

- [ ] run every Acceptance criterion and record the result per criterion
- [ ] present the run on the PR
- [ ] take the verdict: `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- Every Acceptance criterion has a recorded pass/fail with its evidence; none is skipped or sampled.
- The user has approved the run through an explicit verdict; no revision request from it remains
  unaddressed.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-09-05
- **Last completed**: none — no task has started
- **Next**: #1, but only after the steering rewrite below and the plan-gate verdict
- **Notes**: branch `worktree-issue-18`, PR https://github.com/lovaizu/ccpm/pull/20 (draft).
  **Blocker**: the plan gate is still open — no `/rn:ty` or `/rn:gm` verdict on this steering.
  **Pending decision, asked and unanswered**: whether to rewrite this steering to drop the
  invent-a-marker route. The discussion converged on adding nothing: `cwd` / `gitBranch` already
  carry `issue-18`, so the conversation log is locatable by grep, and rn's session-status block
  already prints session, task ids and task labels at every stop, so intervals are readable by
  collecting those blocks in time order. Cost of that route: blocks appear only at stop points, so a
  task finishing without stopping leaves no boundary. Under it, #1 changes from "measure whether a
  new string reaches the JSONL" to "prove the existing log alone yields this conversation's
  friction", and the Acceptance criteria plus #2 / #4 need rewriting — as written they still
  describe the invent-a-marker route, including the `cf13fc9` additions.
  **Unverified premise that survives either route**: whether entries are written to the JSONL before
  the conversation ends. Measured so far: `assistant` entries do exist in stored logs (26 in
  `8dca6935`), but this conversation's own file had not yet appeared in
  `~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm/`. Worktrees of this repo share that one project
  directory. No user-deferred paths.
