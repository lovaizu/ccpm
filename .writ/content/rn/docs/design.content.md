# What rn/docs/design.md says

## doc

### B-9: The point from the opening
- rn keeps what its README (`../README.md`) promises by one split: the conductor, the conversation
  with the user, decides everything, and turn, the plugin rn is built on, makes everything. The
  conductor hears what the user really wants one point at a time, writes what each piece of work
  must say, hands turn one task for it, judges what turn returns by the work's purpose, and
  proposes at each sign-off; turn makes the work, has it read or used by an AI that did not make
  it, as the person it is for would, and checks each item of its checklist. Nothing reaches the
  user that was not read in its receiver's place, and the user is asked nothing the conductor
  could look up.
- How to use rn is in its README; what turn does with a task is in turn's design
  (`../../dev/turn/design.md`) and how a caller hands it one is on turn's callers' page
  (`../../turn/calling-from-a-plugin.md`); what each kind of work must give is in rn's checklists
  (`../checklists/`).

### B-5: How far to rely
- A statement no trial has checked yet is marked "(assumption)".

### B-12: Who is responsible for what
- The user decides: what they want, at each sign-off, and what only they can know.
- The conductor, the conversation with the user: hears one point at a time until nothing is
  silently assumed; writes the content of each work from what was agreed; calls turn once for
  each work, and again only when the content must change much, finishing a small shortfall
  itself; judges each question and item turn returns by what the purpose needs; plans the tasks
  once the design is approved, attractive quality first, and judges each result on the real thing
  against its purpose; has the deliverable used once against the verification document; takes
  feedback back to before the sign-off it answers and stops there again; proposes at each
  sign-off with the final state, what it decided for the user first; and alone uses git.
- turn: makes each work from its CCS, has it read or used in its receiver's place, checks each
  item, and returns the questions only the user can decide and the items not met.
- rn's scripts: find the checklists for a kind; write the CCS from the parts the conductor gives;
  write the report from turn's evidence and the conductor's judgments, with each item's lines as
  they stand; build the record for the hooks.
- rn's hooks: stop, where it happens, a write that breaks the record's form, a commit without
  its decision line or a settled item whole, a commit on the default branch, a sign-off passed
  without the typed command, an agent started in the background, a turn ended with nothing for
  the user, or a message in the wrong language; they judge the course, never the work's worth.
- rn's checklists: say what each kind of work must give its receiver; one the user made at
  `.rn/checklists/<kind>.md` is used for its kind.
- The record: the session's folder, `steering.md`, `open/`, `content/`, `tasks/`, and the
  commits with their decision lines, on the session's branch with its draft pull request; turn's
  evidence under `.turn/` stays uncommitted.
- git and GitHub, through `gh`: hold the record and the pull request; Claude Code: runs the
  conductor, the hooks and turn.
- What each cannot work without: the conductor, the record, turn, rn's scripts and checklists,
  and git with its remote on GitHub; turn, the CCS, git, python3 and jq, as its README says; rn's
  scripts, python3 and jq; rn's hooks, python3 and Claude Code to run them; the pull request,
  `gh` logged in with push access.
- One static figure shows each of these, its responsibility in one line, and what it cannot work
  without; beside it, only where the conductor runs: in the user's conversation, the same one
  throughout the session.

### B-1: Attractive quality
- Said in the README's words, since the reader comes from it.
- What they really want from rough words: rn asks why the user wants the goal and what the result
  should do for them, one point at a time, looks up what the repository and the documentation can
  tell, and offers ways only after the user has said what they want, each with what it gives and
  costs and the one it recommends; so what they get is what they meant.
- Called only for decisions that are theirs: between sign-offs the user is asked only what the
  goal, the repository, the documentation and best practice cannot settle, and never watches the
  work.
- Decided from the proposal alone: at a sign-off the user sees how close the work has come to each
  thing they would choose it for, what changed since their last approval, what rn decided for
  them, and each item met with where, and says yes or no without reading the work over.
- Goes on from where it stopped: tomorrow, or a fresh conversation, takes up the session from its
  record without the user explaining anything again.
- Read in its receiver's place before the user sees it: every work, the plan, the three documents,
  each task's result and each proposal, is read or used by an AI that did not make it, as its
  receiver would, and checked item by item, and what falls short is made again or settled by the
  conductor before it reaches the user.

### B-2: One-dimensional quality
- Each must be no worse than in the version in use.
- Questions answered: how many questions the user answers in a session, beyond the sign-offs. Each
  one beyond what only they could decide is time they spend on what rn could have settled.
- Time and tokens to each sign-off: what a session takes from its start to each sign-off.
- What the user reads at a sign-off: the length of the proposal, which grows only with what the
  user decides, not with the work checked.

### B-3: Must-be quality
- The default branch changes only when the user merges.
- Every decision is committed and pushed as it is made, with a decision line, and every settled
  item of `open/` is whole in the commit that settles it: the commit that removes the item's file
  carries the item's text whole in its message, with the decision on each shortfall, so the record
  shows each finding beside what became of it.
- The record keeps the form every command and check reads it by: the plan, the names of the files
  in `open/`, the verification document, and every ID referred to exists.
- A sign-off is passed only by the user's `/rn:ty`, and is put to them with nothing unsettled
  behind it.
- Nothing reaches the user unread: each work the user sees was last read in its receiver's place
  by turn, or the conductor's change after that reading is in the report with its lines.
- Missing tools: without python3, jq or gh, rn stops before anything and says what to install;
  outside a session, rn's hooks do nothing.
- rn installs from the marketplace with turn, and passes strict validation.
- The conductor stays on course while the user is away: it waits for every agent it starts, ends
  its turn only with something for the user to decide, and speaks in the language the user chose.

### B-4: Backward compatibility
- The commands `/rn:up`, `/rn:ty`, `/rn:gm` and `/rn:dn`, relied on by users, who type them. Must
  keep holding: `/rn:up` starts a session from the words given it or takes up the one on the
  branch; `/rn:ty` approves the sign-off waited for; `/rn:gm` records feedback, from its words or
  from the pull request's comments; `/rn:dn` pauses. `/rn:on` of 0.9.0 is gone: typed, rn says to
  use `/rn:up` with the same words. May change: what each says.
- The record, relied on by every later version of rn and by users who read it: `steering.md` in
  the plan checklist's form, `open/` with its kinds and names, the decision lines and the stop
  commits. Must keep holding: a session recorded by 0.9.0 is taken up as it stands, since its form
  is the same; a session from before 0.9.0 has its goal worked out again, as 0.9.0 did. May
  change: what is added under `content/`.
- The pull request, relied on by the user and by GitHub: its body links `steering.md`, with
  `Closes #N`, `Refs #N` and the pull requests it replaces, and it is marked ready on the
  Deliverable sign-off. Must keep holding: those links and that mark.
- rn's checklists, relied on by turn, which reads each by the name and version it opens with, and
  by users who copied them. Must keep holding: each opens with its name and version in the form
  turn's README gives, an item's ID always means the same item, and a checklist's version goes up
  once for each release that changes it. A checklist the user made at `.rn/checklists/<kind>.md`
  is used for its kind.
- The verification document, relied on by whoever runs the product's checks again and by turn,
  which uses the deliverable against it. Must keep holding: its form as the verification checklist
  gives it, with a scene under `### A1:` for each attractive criterion and the machine checks as
  commands.

### B-5: Non-goals
- Making, reading and checking a work: turn's. rn holds no generator, no reader and no checker of
  its own; its builder judges turn's result rather than a second checker's.
- Hunting must-be gaps off the golden path: a must-be gap is fixed when it stands in the way on
  the path the attractive criteria run along, and otherwise let go with its reason in the record,
  since clearing every gap never ends and takes the time that raises the attractive quality.
- Keeping checklists for kinds of work beyond rn's own: a kind rn has no checklist for is made
  with the user against the checklist for checklists, at `.rn/checklists/<kind>.md`, and used
  from then on.
- Running `/clear`: a plugin cannot; the user runs it and then `/rn:up`.

### B-6: Constraints
- rn runs in Claude Code, on a person's behalf, and holds only skills, hooks, scripts and
  checklists; installing copies only its folder, with turn installed beside it.
- rn uses turn only as turn's callers' page gives it: the skill `turn:up` started with a CCS, and
  the CCS turn writes back, since turn may change everything inside.
- A subagent cannot ask the user, and turn asks nothing while it works.
- The repository has its remote on GitHub, and `gh` is logged in with push access; users' machines
  run Python 3.9 or later with the standard library only, and jq.
- rn's hooks run in every session where rn is installed, in repositories without rn as well.

### B-7: Attractive quality checked
- Each is tried as its user on the practice repository `lovaizu/rn-try`, one run at a time, from a
  fixed state, with a stand-in playing the user from a part that says only what the user knows,
  and judged from the run's transcripts, the JSONL Claude Code keeps of the conversation and of
  every agent, with the commits, the pull request and the product. Each passes on what happens to the user, not on the shape of what
  rn writes.
- What they really want from rough words: `/rn:up move src/account to TypeScript` on a repository
  whose account helpers show "undefined undefined" for a user with no name. Passes when, before any
  way is offered, rn asks why the user wants it and what the result should do for a user with no
  name, and the plan it stops with covers every form an absent name takes that the stand-in named,
  missing, `null` and `""`.
- Called only for decisions that are theirs: the same session, from the stand-in's reason recorded
  to the Plan sign-off. Passes when no question asks what the repository or a run could tell, each
  means question comes after the stand-in said what it wants and gives each way's cost, and each
  message asks one point.
- Decided from the proposal alone: the same session at its Plan sign-off and at its Deliverable
  sign-off. Passes when the stand-in, given only the proposal, decides without asking back, and
  each item the proposal shows met is met at the lines it names.
- Goes on from where it stopped: the coupon session, a second session on the same repository,
  paused with `/rn:dn` in the middle of a task and taken up with `/rn:up` in a fresh conversation. Passes when the fresh conversation goes on from
  the task's state with no question to the stand-in, and the task's result is the same as an
  unpaused run's by the deliverable's checklist.
- Read in its receiver's place before the user sees it: on each sign-off of the same session, the
  records show the plan, the three documents and the proposal made by turn and read by its first
  user before the stop commit, and each task's result used by it before the conductor decided.
- The flow, from `/rn:up` through the plan, the design, one task and the Deliverable sign-off, is
  tried apart from what turn makes, on the smallest session that shows it: a one-line change in a
  repository of one file, with a plan of one attractive criterion, so the trial spends no real
  work's cost and fails only where the flow breaks.

### B-8: One-dimensional quality measured
- All three are measured from the records of the account session, run on this version and on the
  version in use: the questions the stand-in answered, the minutes and tokens to each sign-off,
  and the lines of each proposal.
- Each is compared with the same session on the version in use, rn 0.9.0.

### B-9: Must-be quality checked
- Each is a test on the hook or script that holds it, in the case that would break it: a commit
  made on the default branch, and a push to it; a commit without a decision line; a commit not pushed; a settled item not whole in its commit; a plan,
  an `open/` name or a verification document off its form, and an ID that does not exist; a
  sign-off passed without `/rn:ty` typed, feedback taken without `/rn:gm`, a pause without
  `/rn:dn`; a stop commit with more in `open/` than its kind allows, or at a sign-off without the
  default branch merged; a proposal naming an item met that turn's evidence does not; each tool
  missing, in a session and outside one; rn's own hooks in a repository without `.rn/`; and, for
  the conductor staying on course, an agent started in the background, a turn ended with nothing
  to decide, and a last message in the wrong language.
- rn installs with turn: `claude plugin validate --strict` passes for rn and for the marketplace
  on every push, and rn's manifest names turn among its dependencies.

### B-10: Backward compatibility checked
- The commands: a trial types each, and `/rn:on`, on the flow session, and passes when each does
  what Backward compatibility says.
- The record: a test takes up a session recorded by 0.9.0 from a fixture and passes when `/rn:up`
  goes on from its last decision line; a session from 0.8.0 passes when its goal is worked out
  again.
- The pull request: the flow trial passes when the body holds the links and the request is marked
  ready on the Deliverable sign-off.
- The checklists: a test has turn's own script read every checklist rn keeps into its list and
  finds each one's name, version and items; a test on the script that finds the checklists for a
  kind finds `.rn/checklists/<kind>.md`.
- The verification document: the flow trial's deliverable is used by turn against the session's
  verification document, and the test on the record's form reads one.

### B-12: Who is responsible for what
- The user, who decides; the conductor, which hears, writes the content, hands turn each task,
  judges what turn returns, proposes and uses git; turn, which makes each work, has it read in its
  receiver's place and checks it; rn's scripts, which find the checklists for a kind, write the
  task as a CCS, write the report from turn's evidence, and check the record's form; rn's hooks,
  which hold the conductor to the record and the session's course; git and GitHub, through `gh`,
  which hold the record and the pull request; Claude Code, which runs the conductor, the hooks and
  turn.

### B-11: Principles to judge a change
- Attractive quality is the goal: its checks are the fewest that confirm it, each improvement
  goes where it raises it soonest; must-be quality is checked by machine, fixed where a gap stands
  in the way on the golden path, and finished last. Protects: what they really want, questions
  answered, time and tokens.
- Only the conductor decides what happens next, and only the conductor uses git: a decision is
  made where the goal and the whole conversation are known, and every commit records one someone
  made. Protects: decided from the proposal alone, every decision pushed, goes on from where it
  stopped.
- Every work is made by turn from what the conductor decided, and read in its receiver's place
  before the user sees it; the conductor makes nothing the user sees itself but the record and
  what it finishes after turn's last run, each change in the report. Protects: read in its
  receiver's place, nothing reaches the user unread.
- The user is asked only what the goal, the repository, the documentation and best practice
  cannot settle, one point per message, what they want before any way, with the ways' costs and
  the one recommended; what only the user knows and they do not know is an assumption, shown as a
  shortfall until checked. Protects: what they really want, called only for decisions that are
  theirs.
- Everything is made and checked by the same checklists, and rn is improved by sharpening them,
  not by adding steps; a checklist asks what the receiver gets, so it fits situations no one
  foresaw. Protects: read in its receiver's place, what the user reads at a sign-off.
- Every reader is handed the paths of what it reads, never a summary of them, and every agent
  leaves its whole result in a file and returns only where it is. Protects: what they really
  want, goes on from where it stopped.
- Decisions are written into the record before the work that follows them, and the record holds
  only what holds now; how a thing was reached lives in the commit messages. Protects: goes on
  from where it stopped, every decision pushed.
- What a machine can judge of the course is checked by a hook at the moment it could break, each
  stop naming the step and why (assumption: that a stop keeps the conductor to a step where a
  rule in words would not, taken from turn's design). Protects: every decision pushed, the
  record's form, a sign-off passed only by approval, the conductor stays on course.

