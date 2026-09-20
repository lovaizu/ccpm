Rn version: 0.8.0
Design: rn/docs/design.md

# Goal

Let `rn` be improved from how its own sessions actually ran, using the conversation log as evidence
rather than memory. Today that is impractical for one specific reason: nothing in the Claude Code
conversation log (JSONL) says which task an entry belongs to, so cutting a session's log into
per-task intervals means correlating `git log` timestamps against the log by hand.

Finding the log is not the problem. Claude Code files a conversation under a project directory named
after its working directory, so a worktree's conversations have their own directory and sessions
running concurrently in sibling worktrees of one repository never mix. Reading it in time is not the
problem either — entries are appended as they happen and are greppable while the conversation is
still open. What is missing is the interval: `rn` stops for the user at exactly three gates, and
ordinary build tasks run start to finish without stopping, so nothing in the log marks where a task
began or ended.

Two things follow, in this order. First, `rn` writes a boundary marker at each task's start and
completion, carrying enough of its own context — which session, which task — to stay readable after
the task list has been revised. Second, on top of those boundaries, `rn` gains a retrospective —
deliberately split into two stages so the user is involved at exactly one point of their own
choosing: a **collection** stage that runs silently at each `/rn:dn` and only records friction that
actually left a trace, and a **stocktake** stage the user invokes, which surfaces only friction that
recurs across intervals, turns it into improvement proposals, and files them as issues on the user's
approval.

The separation is the point, not an implementation detail: asking for a proposal from one session's
worth of material forces noise into the shape of an improvement, and asking at every suspend makes the
retrospective a tax. Collecting facts silently and proposing only across accumulated material means a
retrospective with nothing to say naturally says nothing.

# Acceptance criteria

- A session's conversation record can be identified in full by machine, with no by-hand correlation
  work left to the user. (Checked by identifying this session's own record and comparing it against
  what the session actually produced.)
- A session's record never draws in another session's work — including sessions running at the same
  time against sibling worktrees of one repository.
- Any one task's work can be read back as its own stretch of the record, separated from the tasks
  either side of it.
- A stretch of record stays attributable to the task it came from after the task list has been
  revised: a later reader can tell what was being worked on, with no other file and no commit history
  open.
- The same holds for a recorded friction fact — what it was about survives the task list changing
  under it.
- All of the above are true while the session is still running, not only once it has ended.
- Suspending a session costs the user nothing extra — no question, no added output — and an interval
  that held no friction leaves nothing behind.
- The user chooses when to take stock. The retrospective proposes only friction it has seen more than
  once, always with the facts it rests on, and files nothing without that user's approval.
- A session spread over several conversations is still read back as one session.
- A user can tell, from the plugin's own documents, what the retrospective does around them and what
  changed for them.
- The mechanism is known to work on real material, not only in principle. (Demonstrated on this
  session's own record, with the commands and observed output recorded.)
- Installing and updating the plugin is not broken by the change. (`claude plugin validate --strict`
  passes for both the plugin and the marketplace root.)

# Assumptions

- **Measured, 2026-09-06**: Claude Code appends assistant text and tool calls to the conversation
  JSONL as they happen — text from a previous turn and a command string from the running turn were
  both greppable in the open conversation's file. Task #1 records the evidence and settles which
  emission points land.
- **Measured, 2026-09-06**: a conversation's JSONL lives at
  `~/.claude/projects/{working-directory-slug}/{sessionId}.jsonl`, and the slug is the working
  directory — so each worktree has its own directory
  (`…-ccpm--claude-worktrees-issue-18` and `…-issue-17` are separate). Worktrees of one repository do
  **not** share a project directory.
- No session-identifying string is emitted: the working directory already separates sessions, and
  the boundary marker carries the session's own name for the case where one directory hosts more
  than one session.
- Claude Code itself cannot be modified; every marker must be produced by `rn`'s own procedures
  through ordinary agent output or tool calls.
- `rn` stops for the user at three gates only (plan, design, evaluation); ordinary build tasks pass
  through without stopping, so the session-status block cannot serve as a task boundary.
- A task number is **not** a stable identifier. `steering.md`'s task list is revised during a session
  (`/rn:gm` re-does work and can rewrite or add tasks), so `#1` at one moment and `#1` later need not
  be the same task. Git history is not a fallback either: PRs land on `main` squashed, so the
  intermediate `steering.md` revisions that would say what `#1` meant do not survive — observed on
  `.rn/20260705-improve-design-template/steering.md`, which has exactly one commit on `main`.
- An `rn` session spans several conversations, so one session maps to N JSONL files in one directory.
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

### #1: Settle by measurement what the conversation log gives and what an emitted string does

**Purpose**: Put the log's location, its liveness, and the behaviour of each emission point on
recorded command-and-output evidence, so #2 decides the marker on measurement rather than reasoning.

**Prerequisites**: none

**Steps**:

- [x] record the location fact with its command and output: each worktree's conversations live in
      their own project directory, and sibling worktrees of one repository do not share one
- [x] record the liveness fact with its command and output: entries from the open conversation are
      greppable before it ends
- [x] enumerate the candidate emission points (assistant message text, a Bash command string, a Bash
      command's output, a tool result) and emit one distinct probe by each
- [x] compose each probe so its text appears nowhere in the instruction that requests it, and confirm
      each hit comes from the emission itself
- [x] record, per emission point, whether it landed, how soon, and in which JSONL fields
- [x] record how a session spanning several conversations appears in that directory
- [ ] fix the round-3 findings at their root: make every scan run over the whole population its
      sentence generalises to, and name that population in the sentence carrying the number, rather
      than patching the instances a review happened to name
- [ ] probe the hook channel: ship a hook from a plugin directory, emit through it a probe whose text
      appears nowhere in the instruction that requests it, and record whether it landed, how soon, and
      in which JSONL fields
- [ ] record whether a hook can emit a value it computes at run time by reading a file, so the emitted
      string can name the session and the task rather than being fixed
- [ ] record whether a hook entry's structure tells a real emission apart from text that merely quotes
      the marker — the discriminator the other four channels do not provide
- [x] self-check (OK/NG per completion criterion, record in checks/1.md)
- [x] QA expert review (subagent)
- [x] Craft expert review (writing, subagent)
- [x] Verification expert review (dry-run, subagent)

**Completion criteria**:

- The location and liveness facts are each recorded with the command run and the output observed, not
  asserted from reasoning.
- At least one emission method is shown by recorded evidence to put an arbitrary string into the live
  JSONL, greppable before the conversation ends.
- Each reported hit is attributable to the emission itself — a hit that only matches the requesting
  instruction is not counted as a landing.
- Methods that landed and methods that did not are separately recorded; no method is reported as
  working without its observed evidence.
- The hook channel is measured on the same terms as the other four — whether it landed, in which
  fields, and with its probe text traceable to the emission rather than to the instruction.
- Whether a hook emission can be told apart from text that quotes the same string is settled by
  recorded evidence — either a discriminator shown to work, or a recorded failure to find one.
- Every figure in the document states the population its scan covered, and that scan covers the
  population the surrounding sentence generalises to.

### #2: Record the decisions in `rn/docs/design.md`

**Purpose**: Settle the boundary marker and the two-stage retrospective as decisions with reasoning in
`rn`'s canonical design doc.

**Prerequisites**: #1

**Steps**:

- [x] state how a session's log files are located, and why no session-identifying string is emitted
- [x] decide the task-boundary marker's textual form and emission method, from #1's measurements
- [x] decide at which points it is emitted (task start, task completion) and what happens to a task
      that is abandoned or re-done
- [x] decide how a marker names its session and its task so it stays readable after the task list has
      been revised — the marker describes what was being worked on, not a row in a document that moves
- [x] decide where collected friction facts are stored, and their record shape
- [x] decide the bar for what counts as a friction fact worth recording
- [x] decide the stocktake command's name and its call sites (user invocation, `/rn:dn`, session end)
- [x] update `design.md` per `design-template.md`'s "Updating an existing design.md" procedure
- [x] self-check (OK/NG per completion criterion, record in checks/2.md)
- [x] QA expert review (subagent)
- [x] Craft expert review (writing, subagent)
- [x] Verification expert review (fact-check, subagent)
- [x] Design expert review (subagent)

**Completion criteria**:

- Every decision listed in Steps is present in `design.md` with its reasoning and the alternative it
  was chosen over; none is stated as a bare choice.
- The rejected alternatives include emitting a session-identifying string and reading task boundaries
  off the session-status block, each with the measured reason it was rejected.
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

- [x] push and present `design.md` on the PR
- [ ] take the verdict: `/rn:ty` (approve) or `/rn:gm` (revise → address the feedback, re-present)

**Completion criteria**:

- The user has approved `design.md` through an explicit verdict; no revision request from that review
  remains unaddressed.

### #4: Emit the boundary markers

**Purpose**: Make `rn`'s procedures write a task-boundary marker at the points the design fixes, so
every task's interval exists in the log without the user doing anything.

**Prerequisites**: #3

**Steps**:

- [ ] emit the boundary marker in the form and at the firing points the design fixes (continuous
      restamping of the current task on every coordinator tool call, not two discrete events)
- [ ] update the affected skills and references (`on`, `dn`, `up`, `task-execute-workflow`,
      `task-verify-workflow`) consistently, with the format defined in exactly one place
- [ ] confirm the markers ride on steps that already run, adding no prompt and no gate
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (writing, subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- For a task that has started and finished under the new steps, both boundaries are found by grep
  alone, and the interval between them contains that task's work — demonstrated with the command and
  its output.
- A marker line identifies its session and its task on its own, read with no other file open.
- The marker format is defined in one place; the skills and references that emit it cite that place
  rather than restating the format.
- Emitting the markers changes nothing the user sees in normal operation beyond the marker line
  itself — no new prompt, no new gate.

### #5: Build the collection stage

**Purpose**: At each `/rn:dn`, silently extract the interval's friction facts to the store, via a
subagent, recording nothing when there is no trace.

**Prerequisites**: #4

**Steps**:

- [ ] write the collection procedure as a reference: locate the session's log directory from the
      working directory, cut the interval by the boundary markers, extract only traced friction,
      append to the store
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

**Purpose**: Prove the whole path end to end on real material — locate this session's log, split it by
task, run collection and stocktake.

**Prerequisites**: #7

**Steps**:

- [ ] locate this session's JSONL files from the working directory alone
- [ ] split one of them into per-task intervals by the boundary markers alone
- [ ] run the collection stage over a real interval and inspect what it recorded
- [ ] run the stocktake command and inspect what it proposed
- [ ] record the commands and observed output in checks/8.md
- [ ] self-check (OK/NG per completion criterion, record in checks/8.md)
- [ ] QA expert review (subagent)
- [ ] Verification expert review (dry-run, subagent)

**Completion criteria**:

- Locating uses the working directory and splitting uses the markers alone; the record shows no
  fallback to `sessionId` matching or `git log` timestamps.
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
- **Date**: 2026-09-20
- **Last completed**: #2 — `design.md`'s decisions recorded and content-complete; round-3's two
  orphaned Craft findings fixed directly (`71f7ee0`); all reviews now PASS.
- **Next**: #3 — design sign-off. `design.md` is pushed and presentable on the PR; only the user's
  verdict is outstanding.
- **Notes**: branch `worktree-issue-18`, PR https://github.com/lovaizu/ccpm/pull/20 (draft). Resume
  by waiting for `/rn:ty` (approve → proceed to #4) or `/rn:gm` (revise `design.md`, re-present).
  `rn` issue https://github.com/lovaizu/ccpm/issues/30 (fix rounds patch only named findings, no
  iteration-count tracking) remains open, unrelated to this session's own build.
