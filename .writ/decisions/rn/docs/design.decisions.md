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

### B-12: Every term known
- A session: one goal carried through to the end, on its own branch with a draft pull request,
  recorded in `.rn/{yyyymmdd}-{slug}/`.
- The conductor: the main conversation with the user, the same one throughout the session; it
  alone decides every next move and uses git.
- A sign-off: where the user looks at the work before it goes past that point, and approves with
  `/rn:ty` or gives feedback with `/rn:gm`. There are three: the plan, the design, the
  deliverable.
- The plan: `steering.md`, the goal and why, the acceptance criteria, the facts and assumptions
  the work rests on, the rules, and the tasks.
- The acceptance criteria: split after the Kano model (Kano, Seraku, Takahashi and Tsuji,
  "Attractive quality and must-be quality", 1984) into attractive quality, what would make the
  user choose the result, `A1`..., and must-be quality, what they take for granted, `M1`...; each
  task, check and judgment refers to a criterion by its ID.
- The design: the README, the design document and the verification document the plan names, as
  they will stand once the goal is achieved; they belong to the product and stay after the
  session.
- The deliverable: everything the session changed apart from its directory under `.rn/`.
- A work: one thing turn makes for one purpose, one file or several, such as the plan, one of the
  three documents, a task's result, or a proposal.
- The content: what a work must say or do, item by item of its checklists, written by the
  conductor from what was agreed; turn makes the work from it.
- A task for turn: the content, the checklists, where each file of the work goes, its receiver and
  their use, what they must be able to do, what the work follows and what the receiver opens with
  it, handed to turn as a CCS, the JSON file turn's callers' page gives, and returned as one that
  names the next move, each question only the user can decide, each item not met with how it
  would be met, and where turn keeps its evidence.
- The report: what the conductor writes, with rn's script, from turn's evidence and returned CCS
  for each work: first what it decided for the user, each with its ground, each question and item
  turn left with the judgment on it, and each change the conductor made after turn; then each
  item of the checklists, met with the lines that give it as they stand, or not met. It is an item
  of `open/` until the commit that settles it; the proposal at a sign-off gives each item as the
  latest report shows it, so the user never opens a report.
- A Good and a More: on each item, what the user gains, which a fix must not take away, and what
  the user will struggle with; a fatal More is one without whose fix the goal cannot be achieved
  and whose fix only the user can decide.
- What the purpose needs: the one test the conductor applies to each question and item turn
  returns: needed when the receiver's use, or a decision of the user's, rests on it; otherwise
  not, and it is left with why.
- `open/`: what is not yet settled, one file per item, of three kinds: a `report` on a work, the
  user's `feedback` in their own words, or `notes` on a question being put to the user or where a
  paused task stands. What each stop may leave there: at a sign-off and after `/rn:ty`, nothing;
  after `/rn:gm`, the `feedback` item; on `/rn:dn`, whatever is unsettled and the `notes` item on
  where the task stands.
- The decision line: the last line of every commit the conductor makes,
  `● {#id task name | plan | design | deliverable} ── {what was decided} → {next move}`; the one
  on the branch's last commit is where the session stands. A stop commit is one where rn stops
  for the user: at a sign-off, after `/rn:ty` or `/rn:gm`, or on `/rn:dn`.

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
  carries the item's text whole in its message, with the decision on each More, so the record
  shows each finding beside what became of it.
- The record keeps the form every command and check reads it by: the plan, the names of the files
  in `open/`, the verification document, and every ID referred to exists.
- Only the user passes a sign-off, gives feedback or pauses, by typing `/rn:ty`, `/rn:gm` or
  `/rn:dn`; a sign-off is put to them with nothing unsettled behind it and the latest default
  branch merged in.
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
  change: what is added under `decisions/`.
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
  every agent, with the commits, the pull request and the product. Each passes on what happens to
  the user, not on the shape of what rn writes. The scenes, their fixtures and their trials are in
  the verification document (`verification.md`), the one place that holds them; the design says
  only what each passes on.
- What they really want from rough words: passes when rn's first call to the user asks why they
  want the goal, and when, after feedback that one form of an absent name is shown wrong, the plan
  put up covers every form an absent name takes.
- Called only for decisions that are theirs: passes when, before any way is offered, a call asks
  what the user wants the result to do for them; the ways then offered each give what they said,
  with their costs; none asks what the repository or running its code could tell; and each
  message asks one point.
- Decided from the proposal alone: passes when a stand-in given only the proposal decides without
  asking back, and decides the same as one that reads the pull request and its branch.
- Goes on from where it stopped: passes when a fresh conversation, after a pause in the middle of
  a task, goes on from the task with no question to the user and carries it to its decision line.
- Read in its receiver's place before the user sees it: passes when the transcripts show the plan,
  the three documents and each proposal made by turn and read by its first user before the stop
  commit, and the deliverable used by turn's first user before the conductor decided.
- The flow, from `/rn:up` through the plan, the design, one task and the Deliverable sign-off, is
  tried apart from what turn makes in the flow session, the smallest that shows it: a one-line
  change to the practice repository's README, so the trial spends no real work's cost and fails
  only where the flow breaks; it is run first after any change.

### B-8: One-dimensional quality measured
- All three are measured from the transcripts of the account session, run on this version and on the
  version in use: the questions the stand-in answered, the minutes and tokens to each sign-off,
  and the lines of each proposal.
- Each is compared with the same session on the version in use, which the trial's record names.

### B-9: Must-be quality checked
- Each is a test on the hook or script that holds it, in the case that would break it: a commit
  made on the default branch, and a push to it; a commit without a decision line; a commit not pushed; a settled item not whole in its commit; a plan,
  an `open/` name or a verification document off its form, and an ID that does not exist; a
  sign-off passed without `/rn:ty` typed, feedback taken without `/rn:gm`, a pause without
  `/rn:dn`; a stop commit with more in `open/` than its kind allows, or at a sign-off without the
  default branch merged, each under only the user passes a sign-off; a proposal naming an item met that turn's evidence does not; each tool
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

### B-12: Who does what to what
- Structure opens with how rn divides, in one sentence: rn is the conductor, which alone decides
  each next move and uses git, and turn, which makes every work; they meet only in the record,
  where the conductor writes what each work must say and turn's task, and rn's scripts and hooks
  hold the conductor to the record's form and course.
- One figure, a box for each one that takes part holding its name alone, and an arrow from each to
  what it reads, writes, copies or calls, labelled with that relation:
  - the user → the conductor: asks, answers one point at a time, types `/rn:ty`, `/rn:gm` or
    `/rn:dn`
  - the user → the pull request: reads each proposal, comments
  - the conductor → the record: writes the decisions for each work, the items of `open/` and the
    plan's machine parts; reads where the session stands
  - the conductor → turn: calls with the CCS of each work, reads the CCS turn writes back
  - the conductor → rn's scripts: calls, to find the checklists for a kind, write the CCS and
    write the report
  - the conductor → git and GitHub: commits and pushes each decision, opens the pull request and
    marks it ready, through `gh`
  - turn → the record and the product: writes each work where its task says: the plan, the
    proposals and the reports' grounds in the record, the three documents and the deliverable in
    the product
  - turn → rn's checklists: reads each the CCS names
  - rn's scripts → rn's checklists: find those for a kind, and the user's own under
    `.rn/checklists/`
  - rn's scripts → the record: write the CCS under `tasks/` and the report under `open/`, from
    turn's evidence and the conductor's judgments
  - rn's hooks → the record: read it to build what each check judges
  - rn's hooks → the conductor: stop a write that breaks the record's form, a commit without its
    decision line or a settled item whole, a commit on the default branch, a sign-off passed
    without the typed command, an agent started in the background, a turn ended with nothing for
    the user, or a message in the wrong language
  - git and GitHub → the record and the pull request: hold them
- Beside the figure, only what it cannot show: the conductor is the user's conversation, the same
  one throughout the session, and turn's evidence under `.turn/` stays uncommitted.

### B-34: What kind of thing each part is
- A table of the parts inside rn, one row each, with its kind: the conductor, prompts, the skills
  `rn:up`, `rn:ty`, `rn:gm` and `rn:dn` with the steps they follow; rn's scripts, python3 scripts
  with jq; rn's hooks, `sh` entries that run python3 checks; rn's checklists, data, one markdown
  file per kind of work; the record, data, the session's folder under `.rn/` and the commits on
  its branch; the pull request, data held by GitHub; turn, a plugin of its own, used as its
  callers' page gives it.

### B-35: Where each part is kept
- In the same table: the prompts, scripts, hooks and checklists are shipped with rn and copied to
  the user's machine at install; a checklist the user made is theirs, at `.rn/checklists/<kind>.md`
  in their repository; the record is in the user's repository, committed on the session's branch,
  and `.turn/` beside it uncommitted; the pull request is on GitHub; turn is installed beside rn.

### B-36: Where each part runs
- In the same table: the conductor, the scripts, the hooks and turn run on the user's machine,
  inside the Claude Code session the user talks in; nothing of rn runs in CI, and the product's
  own checks run where its verification document says.

### B-33: Each goal brought about by a part
- Each quality in Goals is brought about by the parts named for it, read from the figure and the
  table: what they really want from rough words, the conductor; called only for decisions that
  are theirs, the conductor and the checklists, which settle what a good work gives so no
  question of it goes to the user; decided from the proposal alone, turn, which makes the
  proposal, the scripts' report, and the conductor; goes on from where it stopped, the record and
  the hooks that keep every decision pushed with its decision line; read in its receiver's place,
  turn; questions answered, the conductor; time and tokens to each sign-off, turn and the
  conductor; what the user reads at a sign-off, the proposal checklist and the scripts' report;
  the default branch, the hooks; every decision pushed, the hooks and the conductor; the record's
  form, the hooks; only the user passes a sign-off, the hooks; nothing reaches the user unread,
  turn and the report's lines as they stand; missing tools, the scripts and the hooks' guard;
  installs with turn, rn's manifest, shipped with it; the conductor stays on course, the hooks;
  the commands, the conductor; the record, the record and the hooks; the pull request, the
  conductor; the checklists, the checklists and the scripts; the verification document, turn and
  the hooks.

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
  More until checked. Protects: what they really want, called only for decisions that are
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
  record's form, only the user passes a sign-off, the conductor stays on course.

