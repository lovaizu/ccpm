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
- The report: what the conductor writes from turn's evidence and returned CCS for each work: first
  what it decided for the user, each with its ground, each question and item turn left with the
  judgment on it, and each change the conductor made after turn; then each item of the checklists,
  met with the lines that give it or not met.
- A Good and a More: on each item, what the user gains, which a fix must not take away, and what
  the user will struggle with; a fatal More is one without whose fix the goal cannot be achieved
  and whose fix only the user can decide.
- What the purpose needs: the one test the conductor applies to each question and item turn
  returns: needed when the receiver's use, or a decision of the user's, rests on it; otherwise
  not, and it is left with why.
- `open/`: what is not yet settled, one file per item: a `report`, the user's `feedback` in their
  own words, or `notes` on a question being put to the user or where a paused task stands.
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
- The default branch changes only when the user merges.
- Every decision is committed and pushed as it is made, with a decision line, and every settled
  item of `open/` is whole in the commit that settles it.
- The record keeps the form every command and check reads it by: the plan, the names of the files
  in `open/`, the verification document, and every ID referred to exists.
- A sign-off is passed only by the user's `/rn:ty`, and is put to them with nothing unsettled
  behind it.
- Nothing reaches the user unread: each work the user sees was last read in its receiver's place
  by turn, or the conductor's change after that reading is in the report with its lines.
- Missing tools: without python3, jq or gh, rn stops before anything and says what to install;
  outside a session, rn's hooks do nothing.
- rn installs from the marketplace with turn, and passes strict validation.

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
  and judged from the records: the JSONL of the conversation and of every agent, the commits, the
  pull request and the product. Each passes on what happens to the user, not on the shape of what
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
- Decided from the proposal alone: the same session at its Plan sign-off and at its Design
  sign-off. Passes when the stand-in, given only the proposal, decides without asking back, and
  each item the proposal shows met is met at the lines it names.
- Goes on from where it stopped: the session paused with `/rn:dn` in the middle of a task and
  taken up with `/rn:up` in a fresh conversation. Passes when the fresh conversation goes on from
  the task's state with no question to the stand-in, and the task's result is the same as an
  unpaused run's by the deliverable's checklist.
- Read in its receiver's place before the user sees it: on each sign-off of the same session, the
  records show the plan, the three documents and the proposal made by turn and read by its first
  user before the stop commit, and each task's result used by it before the conductor decided.

### B-22: Where each benefit is tried
- The flow, from `/rn:up` through the plan, the design, one task and the Deliverable sign-off, is
  tried apart from what turn makes, on the smallest session that shows it: a one-line change in a
  repository of one file, with a plan of one attractive criterion, so the trial spends no real
  work's cost and fails only where the flow breaks.

### B-8: One-dimensional quality measured
- All three are measured from the records of the account session, run on this version and on the
  version in use: the questions the stand-in answered, the minutes and tokens to each sign-off,
  and the lines of each proposal.

### B-23: What a measure is compared with
- Each is compared with the same session on the version in use, rn 0.9.0.

### B-9: Must-be quality checked
- Each is a test on the hook or script that holds it, in the case that would break it: a commit
  without a decision line; a commit not pushed; a settled item not whole in its commit; a plan,
  an `open/` name or a verification document off its form, and an ID that does not exist; a
  sign-off passed without `/rn:ty` typed, feedback taken without `/rn:gm`, a pause without
  `/rn:dn`; a stop commit with more in `open/` than its kind allows, or at a sign-off without the
  default branch merged; a proposal naming an item met that turn's evidence does not; a commit or
  push by anyone but the conductor; an agent started in the background; a turn ended with nothing
  to decide; a last message in the wrong language; each tool missing, in a session and outside
  one; and rn's own hooks in a repository without `.rn/`.
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

### B-12: Who takes part
- The user, who decides; the conductor, which hears, writes the content, hands turn each task,
  judges what turn returns, proposes and uses git; turn, which makes each work, has it read in its
  receiver's place and checks it; rn's scripts, which find the checklists for a kind, write the
  task as a CCS, write the report from turn's evidence, and check the record's form; rn's hooks,
  which hold the conductor to the record and the session's course; git and GitHub, through `gh`,
  which hold the record and the pull request; Claude Code, which runs the conductor, the hooks and
  turn.

### B-26: What each one depends on
- The conductor cannot work without the record, turn, rn's scripts and checklists, and git with
  the remote on GitHub; turn, without the task as a CCS, git, python3 and jq, as its README says;
  rn's scripts, without python3 and jq; rn's hooks, without python3 and Claude Code to run them;
  the pull request, without `gh` logged in with push access.

### B-25: What passes between them
- The user and the conductor: rough words and answers, one point at a time; proposals, questions
  and the decision line where rn stopped.
- The conductor and the record: each decision written as it is made, committed and pushed; on
  `/rn:up`, the plan, `open/` and the last decision line read back.
- The conductor and turn: for each work, the task as a CCS; back, the CCS with the next move, the
  questions, the items not met, and where the evidence is.
- The conductor and rn's scripts: the kind, and back its checklists; the task's parts, and back
  the two lines to call turn with; turn's evidence, the returned CCS and the conductor's
  judgments, and back the report.
- The conductor and the pull request: the record pushed, the body's links, the comments read as
  feedback, and the mark ready.
- rn's hooks and the conductor: each stop, naming the step and why.

### B-32: The whole in one place
- One figure, a sequence diagram, with the user, the conductor, rn's scripts, turn, rn's hooks and
  git with GitHub, each with what it is for in its label, and the passes above in the order of a
  session: the words, the hearing, the plan made by turn and proposed, the approval, the design
  made by turn and proposed, the tasks each made by turn and judged, the deliverable used by turn
  against the verification document, the proposal, and the pull request marked ready; after the
  figure, only what it cannot show: where the conductor runs and what each cannot work without.

### B-11: Principles to judge a change
- Attractive quality is the goal: its checks are the fewest that confirm it, and each improvement
  goes where it raises it soonest; must-be quality is checked by machine and fixed where a gap
  stands in the way on the golden path, and finished last. Protects: what they really want,
  questions answered, time and tokens.
- Only the conductor decides what happens next, and only the conductor uses git: a decision is
  made where the goal and the whole conversation are known, and every commit records one someone
  made. Protects: decided from the proposal alone, every decision pushed, goes on from where it
  stopped.
- Every work is made by turn from what the conductor decided, and read in its receiver's place
  before the user sees it; the conductor makes nothing the user sees itself but the record and
  what it finishes after turn's last run, each change in the report. Protects: read in its
  receiver's place, nothing reaches the user unread.
- turn runs once on a work, and again only when what it was given must change much; a small
  shortfall the conductor fixes itself, after turn's last run, since turn on the same inputs
  returns the same judgments, and turn writes over a file only when git holds it. Protects: time
  and tokens, nothing reaches the user unread.
- The user is asked only what the goal, the repository, the documentation and best practice
  cannot settle, one point per message, what they want before any way, with the ways' costs and
  the one recommended; what only the user knows and they do not know is an assumption, shown as a
  shortfall until checked. Protects: what they really want, called only for decisions that are
  theirs.
- Everything is made and checked by the same checklists, and rn is improved by sharpening them,
  not by adding steps; a checklist asks what the receiver gets, so it fits situations no one
  foresaw. Protects: read in its receiver's place, what the user reads at a sign-off.
- Every role is handed the paths of what it reads, never a summary of them, and every agent leaves
  its whole result in a file and returns only where it is. Protects: what they really want, goes on
  from where it stopped.
- Decisions are written into the record before the work that follows them, and the record holds
  only what holds now; how a thing was reached lives in the commit messages. Protects: goes on from
  where it stopped, every decision pushed.

### B-13: An approach for each quality
- Hearing what the user really wants. Brings about: what they really want, called only for
  decisions that are theirs, questions answered. Idea: the conductor works out the plan itself, in
  the conversation it holds, before anything else, and the plan has its own sign-off, since a
  design worked out on a wrong goal is wasted. It asks the way of a careful interviewer working
  down a tree of decisions, as in mattpocock's `grilling` skill (MIT, commit `d81f3a1`): only a
  point whose prerequisites are settled is asked; an intent question asks why the user wants the
  goal and what a result should do for them, with no way offered and no recommended answer, and
  its answer is written in the user's words as an attractive criterion; a means question offers
  ways only where the criteria allow ways that give different things, each with what it gives and
  costs and the one recommended; facts the repository, the official documentation or best
  practice can show are looked up, and a fact none can show, such as what the user's records hold
  or every form an input takes where the product runs, is asked; done when nothing is silently
  assumed, and what the user does not know but says to go on with is an assumption. Each point is
  written into the plan's content as it is agreed, committed and pushed, so a pause loses none;
  the languages the record and the talk are in, and the issues the work closes, are among the
  points. Who takes part: the user, the conductor, the record. Weighed: depending on `grilling`
  instead of taking its way in; not chosen, since installing it brings many skills, it starts on
  any mention of "grill", and its tags cannot pin a version. Weighed: every ready question at
  once; not chosen, since with several the user answers the one they follow and the rest go
  half-decided (the user's own experience).
- Making a work through turn. Brings about: read in its receiver's place, nothing reaches the user
  unread, decided from the proposal alone, time and tokens. Idea: for each work, the plan at the
  Plan sign-off, the three documents at the Design sign-off, each task's result, the deliverable's
  use and each proposal, the conductor writes the content, what the work must say or do item by
  item of its checklists, from what was agreed and nothing else, at
  `.rn/{session}/content/<the work's path>.content.md`; hands turn the task with a script, as a
  CCS naming the content, the checklists for the kind, where each file goes, the receiver, their
  use and what they must be able to do, what the work follows and what the receiver opens with
  it; waits for turn, which asks nothing while it works; then judges each question and item turn
  returns by what the purpose needs: where serving the purpose needs a large change in the
  content, it corrects the content and runs turn again, and only then; otherwise it finishes the
  work itself after turn's last run, each change kept for the report; a question the purpose needs
  and only the user can decide is asked, one per message. A script writes the report from turn's
  evidence, the returned CCS and the conductor's judgments, and stops until every question and
  item turn returned is judged, so nothing turn returned is dropped. The report goes to `open/`
  and is settled whole in the commit that settles it. Who takes part: the conductor, rn's scripts,
  turn, the user. Weighed: running turn until every item is met; not chosen, since each run raised
  finer questions the purpose did not need (seen in three runs on a CSV tool's README,
  2026-10-14). Weighed: an agent of rn's own set to check turn's result; not chosen, since a fresh
  agent set to check a README judged beyond the README's scope and disagreed with turn (seen once,
  2026-10-14), and only the conductor knows what was agreed. Weighed: the conductor asking the user
  each question as it is seen; not chosen, since turn asks nothing while it works, so all its
  questions come at once at the end.
- Sign-offs and proposals. Brings about: decided from the proposal alone, what the user reads at a
  sign-off, a sign-off passed only by approval. Idea: at a sign-off, every report and feedback is
  settled, the branch has the latest default branch merged in, and the conductor writes the
  proposal's content, the final state only: what it proposes next and why, how far the work gives
  each attractive criterion and what came closer, what changed since the last approval and what
  the design takes away, what it decided for the user, each shortfall left, each assumption as a
  shortfall, and each item of the work's checklists as turn's evidence shows it; turn makes the
  proposal against the proposal checklist, read as the user would, and the conductor commits it as
  the stop commit's body, with the decision line last, and gives the user that body translated
  into the conversation language, adding nothing and leaving nothing out. The points and fixes
  along the way are left out, since the user approves the final state; a must-be gap let go off
  the golden path stays in the record, not in the proposal. Who takes part: the conductor, turn,
  the record, the user. Weighed: a report of where things stand; not chosen, since it leaves the
  user to work out what to do next, which is the work they left to rn. Weighed: every Good and
  More of every use listed; not chosen, since the proposal then grew with the work checked, not
  with what the user decides (#46).
- Feedback. Brings about: what they really want, decided from the proposal alone. Idea: feedback is
  the user's words with `/rn:gm`, or, when none are given, every comment the `gh` user wrote on
  the pull request after the stop commit; it is kept whole in a `feedback` item in `open/`, and
  the session goes back to working out the plan or the design, taking the mismatch behind the
  words as the first point, since fixing only what the words say leaves the mismatch in place;
  feedback on the deliverable gets tasks for it, or goes back to the design when it changes what
  the product should be; work that went back always stops at that sign-off again. Once approved,
  the plan and the documents go back through their sign-off only when what they say changes
  without the user having decided it. Who takes part: the user, the conductor, the pull request.
  Weighed: acting on feedback point by point as worded; not chosen, since the mismatch behind the
  words stayed in place.
- Tasks and the deliverable. Brings about: what they really want, called only for decisions that
  are theirs. Idea: the tasks are planned only once the design is approved, since tasks planned
  before it would mostly be rewritten, in the way of `wayfinder` in the same repository: decisions
  settled one at a time, each before the tasks that rest on it, what cannot yet be stated kept
  under Not yet specified; each task names its purpose, the criteria it serves and completion
  criteria split by Kano quality, and tasks raise attractive quality first. Each task is a work
  made through turn, with the design and the repository's rules as what it follows and the code
  checklist, or the kind's, as its measure; the conductor checks what turn returned against the
  task's purpose on the real thing, in one decision line, sends it back with the content corrected
  where the purpose is not fulfilled, goes back to the design where the design does not let it be
  fulfilled, and asks the user what only they can decide. When the tasks planned after the last
  Design sign-off are done, the deliverable is used once: turn uses the product as its user would
  against the verification document, whose scenes are its items, and the conductor runs the machine
  checks; each More to fix becomes a task before the Deliverable sign-off, and the whole is not
  used again, since each fresh use raises points that are not essential. Who takes part: the
  conductor, turn, the record. Weighed: a generator and a first user of rn's own for each task;
  not chosen, since turn makes, reads and checks every work one way, and rn's own reading was the
  second copy of it.
- The record and the pull request. Brings about: goes on from where it stopped, every decision
  pushed, the default branch untouched. Idea: a session works on its own branch from the latest
  default branch, with a draft pull request whose body links `steering.md` and the issues, and
  never takes in the user's uncommitted changes; every decision is committed and pushed as it is
  made, with a decision line, so `/rn:up` takes up the next move from the last one; `open/` holds
  what is not yet settled, and a settled item leaves it in the commit that settles it, copied whole
  into the message with what was decided on each point, so the record lives in git and shows each
  finding beside what became of it; the content of each work stays under `content/` so each item
  met traces back to what was asked of it; turn's evidence under `.turn/` is left uncommitted, since
  the report holds what the record needs. When a session is taken up, and before each sign-off,
  the branch is brought up to the latest default branch, and what that changes is worked out again
  before the sign-off. When Claude Code summarizes the conversation partway, a hook has the
  conductor read the record again, since a summary drops details the record holds whole. Who takes
  part: the conductor, git and GitHub, rn's hooks. Weighed: findings kept as files under `.rn/`;
  not chosen, since the record then held what was read past, and the commit messages already hold
  each finding beside its decision.
- The commands. Brings about: goes on from where it stopped, a sign-off passed only by approval.
  Idea: `/rn:up` starts a session from the words given it when the branch has none, and otherwise
  takes up the one on the branch from its record, so one command serves both and the user need
  not remember which; `/rn:ty` and `/rn:gm` record the user's answer and stop, so the user can
  clear the conversation at any sign-off; `/rn:dn` records how far the session has come, a task
  under way included, and stops. Each command runs only when the user types it. Who takes part:
  the user, the conductor, the record. Weighed: keeping `/rn:on` beside `/rn:up`; not chosen,
  since the record tells whether a session is there, and two commands for one move are one more
  thing to learn.
- Hooks check rn's rules as it goes. Brings about: every decision pushed, the record's form, a
  sign-off passed only by approval, nothing reaches the user unread, called only for decisions that
  are theirs. Idea: what a machine can judge is checked by hooks, so a breach is stopped where it
  happens, and each stop says which step and why: the record's form after each write; the decision
  line, a settled item whole, a stop commit's `open/` and merged default branch, and a sign-off
  passed only after `/rn:ty` typed, on each commit before it is pushed; only the conductor commits
  or pushes; no agent in the background; every commit pushed and the last message in the
  conversation language at each end of the turn; and a turn ended with nothing to decide sent on
  once. A proposal naming an item met that turn's evidence does not is stopped. Who takes part:
  rn's hooks, Claude Code, the conductor. Weighed: telling the conductor its rules in words only;
  not chosen, since a rule in words is kept on some runs only (assumption, from turn's design).
- Installing with turn. Brings about: rn installs with turn. Idea: rn's manifest names turn among
  its dependencies, so installing rn installs turn, and the manifest passes
  `claude plugin validate --strict`, alone and in the marketplace. Who takes part: rn's manifest,
  Claude Code. Weighed: telling the user to install turn as well; not chosen, since a user who
  misses it gets an rn that cannot work.
