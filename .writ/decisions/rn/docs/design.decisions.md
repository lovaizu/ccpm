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

## design

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
- The default branch: it changes only when the user merges.
- Every decision pushed: each decision is committed and pushed as it is made, with a decision line,
  and every settled item of `open/` is whole in the commit that settles it: the commit that removes
  the item's file carries the item's text whole in its message, with the decision on each More, so
  the record shows each finding beside what became of it.
- The record's form: the record keeps the form every command and check reads it by: the plan, the
  names of the files in `open/`, the verification document, and every ID referred to exists.
- Only the user passes a sign-off: the user alone passes a sign-off, gives feedback or pauses, by
  typing `/rn:ty`, `/rn:gm` or `/rn:dn`; a sign-off is put to them with nothing unsettled behind it
  and the latest default branch merged in.
- Nothing reaches the user unread: each work the user sees was last read in its receiver's place by
  turn, or the conductor's change after that reading is in the report with its lines.
- Missing tools: without python3, jq or gh, rn stops before anything and says what to install;
  outside a session, rn's hooks do nothing.
- Installs with turn: rn installs from the marketplace with turn, and passes strict validation.
- The conductor stays on course: while the user is away, it waits for every agent it starts, ends
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
  checklists; installing copies only its folder, with turn installed beside it. Serves: installs
  with turn.
- rn uses turn only as turn's callers' page gives it: the skill `turn:up` started with a CCS, and
  the CCS turn writes back, since turn may change everything inside.
- A subagent cannot ask the user, and turn asks nothing while it works.
- The repository has its remote on GitHub, and `gh` is logged in with push access; users' machines
  run Python 3.9 or later with the standard library only, and jq. Serves: missing tools.
- rn's hooks run in every session where rn is installed, in repositories without rn as well.

### B-7: Attractive quality verified
- How each is checked: as its user, on the practice repository `lovaizu/rn-try`, one run at a
  time, from a fixed state, with a stand-in playing the user from a part that says only what the
  user knows; judged from the run's records, the JSONL of the conversation and of every agent, with
  the commits, the pull request and the product; the scenes, their fixtures and trials are in the
  verification document (`rn/docs/verification.md`) and `dev/rn/trials/`. The flow, from `/rn:up`
  through the plan, the design, one task and the Deliverable sign-off, is tried apart from what
  turn makes, on the smallest change that shows it, first after any change.
- What they really want from rough words: from the stand-in's rough words, the plan it approves
  says what its part says the user wants, and no way was offered before it said what it wants.
- Called only for decisions that are theirs: every question the stand-in is asked between
  sign-offs is one only its part can answer.
- Decided from the proposal alone: at each sign-off, the stand-in decides from the proposal alone
  as it decides after also reading the work.
- Goes on from where it stopped: `/rn:up` in a fresh conversation on a paused session reaches the
  next stop with the stand-in explaining nothing.
- Read in its receiver's place before the user sees it: the records show every work the user sees
  read by turn's first user after its last change, or that change in the report.

### B-8: One-dimensional quality verified
- How each is measured: from the records of the same session, run on this version and on the
  version in use, which the trial's record names.
- Questions answered: the questions the stand-in answers beyond the sign-offs are no more than on
  the version in use.
- Time and tokens to each sign-off: the minutes and tokens to each sign-off are no more than on the
  version in use.
- What the user reads at a sign-off: the lines of each proposal are no more than on the version in
  use.

### B-9: Must-be quality verified
- How each is checked: by a test on the hook or script that holds it, in `dev/rn/tests/`, run on
  every push with every line and branch counted.
- The default branch: a commit on the default branch is stopped.
- Every decision pushed: a commit without its decision line, and one that removes an item of
  `open/` without its text whole, are stopped.
- The record's form: a write that breaks the plan's form, the names in `open/` or the verification
  document's form, or that refers to an ID that does not exist, is stopped.
- Only the user passes a sign-off: a commit that passes a sign-off without the typed command is
  stopped.
- Nothing reaches the user unread: the report rn's script writes names each change the conductor
  made after turn's last reading.
- Missing tools: with each tool missing, rn stops before anything saying what to install, and
  outside a session rn's hooks do nothing.
- Installs with turn: `claude plugin validate --strict` on rn and on the marketplace passes on
  every push.
- The conductor stays on course: an agent started in the background, a turn ended with nothing for
  the user, and a message in another language than the user's are stopped.

### B-10: Backward compatibility verified
- How each is checked: by a test in `dev/rn/tests/` or a trial in `dev/rn/trials/` that uses it as
  the earlier version left it.
- The commands: on the flow session, each command typed does what it did, and `/rn:on` says to use
  `/rn:up` with the same words.
- The record: a session recorded by 0.9.0 and one by 0.8.0 are taken up from their fixtures.
- The pull request: on the flow trial, its body holds the links and it is marked ready at the
  Deliverable sign-off.
- rn's checklists: every checklist read by turn's own script yields its opening and every item.
- The verification document: turn uses the flow trial's deliverable against it.

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

### B-33: Every goal and decision placed
- Held by where the figure and the table place the parts, so nothing more is said: read in its
  receiver's place before the user sees it (turn); the default branch, every decision pushed, the
  record's form, only the user passes a sign-off and the conductor stays on course (rn's hooks);
  installs with turn and the commands (the table); the pull request (the conductor, through `gh`);
  rn's checklists (rn's checklists and rn's scripts).
- One sentence under the figure for each held inside one part, saying what the part holds:
  - The conductor holds what they really want from rough words: it hears why the user wants the
    goal and what the result should do for them before it offers any way.
  - The conductor holds called only for decisions that are theirs and questions answered: it
    settles whatever the goal, the repository, the documentation and best practice settle.
  - The conductor holds time and tokens to each sign-off: it finishes by hand what falls short
    after turn, rather than running turn again.
  - The record holds goes on from where it stopped: the decision line on the branch's last commit
    says where the session stands.
  - rn's scripts hold decided from the proposal alone and nothing reaches the user unread: the
    report they write puts first what rn decided for the user, and names each change the
    conductor made after turn's last reading.
  - rn's checklists hold what the user reads at a sign-off: the proposal's checklist asks for what
    the user decides, not for the work checked.
  - rn's scripts and rn's hooks hold missing tools: the scripts stop before anything when a tool
    is missing, and the hooks do nothing outside a session.

### B-11: Decisions to judge a change
- Attractive quality comes first: its checks are the fewest that confirm it, and must-be quality
  is checked by machine, fixed where a gap stands on the path the attractive criteria run along,
  and finished last.
  - Serves: what they really want from rough words; questions answered; time and tokens to each
    sign-off.
  - What a builder could get wrong: close every must-be gap first, so what would make the user
    choose the result comes last or not at all.
- Only the conductor decides what happens next, and only the conductor uses git.
  - Serves: decided from the proposal alone; every decision pushed; goes on from where it stopped.
  - What a builder could get wrong: let an agent or turn choose the next move or commit, without
    the goal and the conversation, leaving a record the user cannot stand behind.
- Every work the user sees is made by turn from what the conductor decided, and read in its
  receiver's place before the user sees it; what the conductor finishes after turn's last run is
  in the report.
  - Serves: read in its receiver's place before the user sees it; nothing reaches the user unread.
  - What a builder could get wrong: have the conductor write a small work itself, read only by its
    writer, who passes what its receiver would miss.
- The user is asked only what the goal, the repository, the documentation and best practice
  cannot settle, one point per message, what they want before any way.
  - Serves: what they really want from rough words; called only for decisions that are theirs;
    questions answered.
  - What a builder could get wrong: ask whatever comes up, or offer ways before the user has said
    what they want, so they get what was offered rather than what they meant.
- Everything is made and checked by the same checklists, and rn is improved by sharpening them,
  not by adding steps.
  - Serves: read in its receiver's place before the user sees it; what the user reads at a
    sign-off; rn's checklists.
  - What a builder could get wrong: add a step for each slip a trial shows, which meets only that
    case and is one more thing to keep right.
- Every reader is handed the paths of what it reads, never a summary of them, and every agent
  leaves its whole result in a file and returns only where it is.
  - Serves: what they really want from rough words; goes on from where it stopped.
  - What a builder could get wrong: hand a reader a summary, which drops what its writer thought
    did not matter, or keep a result only in a reply, lost with the conversation.
- Decisions are written into the record before the work that follows them, and the record holds
  only what holds now; how a thing was reached lives in the commit messages.
  - Serves: goes on from where it stopped; every decision pushed.
  - What a builder could get wrong: do the work first and write the decision after, so it is lost
    when the session stops, or keep the history in the record, read as if all of it held.
- What a machine can judge of the course is checked by a hook at the moment it could break, each
  stop naming the step and why (assumption: that a stop keeps the conductor to a step where a rule
  in words would not, taken from turn's design).
  - Serves: every decision pushed; the record's form; only the user passes a sign-off; the
    conductor stays on course.
  - What a builder could get wrong: leave the course to the prompts' words, so a slip shows only
    later, in a record that looks right.
- What others rely on, the commands, the record, the pull request, rn's checklists and the
  verification document, changes only by what earlier versions' users and sessions can still use.
  - Serves: the commands; the record; the pull request; rn's checklists; the verification document.
  - What a builder could get wrong: reshape the record for a new step, so a session an earlier
    version left can no longer be taken up.
