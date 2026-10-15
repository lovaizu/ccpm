# What dev/turn/design.md says

## doc

### B-9: The point from the opening
- turn keeps what its README (`../../turn/README.md`) promises by one idea: the work is read in its
  receiver's place by an agent that did not write it, and one orchestrator decides each item of the
  checklists from the whole work, so nothing passes that the work does not show.
- How to use turn is in that README, and the forms a caller writes and reads are on the callers'
  page (`../../turn/calling-from-a-plugin.md`).

### B-12: Who is responsible for what
- The user hands the work on, and answers, when the run returns, what only they can decide.
- The caller, Claude in the user's conversation or the user's plugin: says what the work should
  be, in a CCS of the callers' page's form, and decides from the CCS turn writes back what follows:
  finishing the work itself, calling turn again, asking the user, or moving on.
- The orchestrator, the skill `turn:up`: runs the run; decides each question the generator or the
  learner raises, showing where the inputs answer it or leaving it open for the user; sends the
  work back to the generator until every item passes or waits on a question left open, and only
  then hands it to the first user; alone decides whether each item passes, from the whole work,
  giving each that passes a Good with the lines that give it; takes the learner's ways in the work
  in one second round, and returns what the second round leaves, or what lies in what the caller
  gave, to the caller. It needs the CCS, turn's scripts and Claude Code to start its agents.
- The generator: makes the work in the run's copy of the repository to pass every item, from the
  content and the references, names where each item passes, and raises what the inputs do not
  settle as a question. It needs the inputs a script hands it and a shell for tests and builds.
- The first user: reads the work as the receiver, for the use, with only the work and what the
  receiver opens with it, and hands back what it took for each item and where; it raises no
  question, since without the content it cannot tell what only the user can decide. It needs the
  work and what the receiver opens.
- The evaluator: shows which items the work passes, each with its lines and grounds, judged from
  the first user's reading; it raises no question. It needs the reading and its records.
- The learner: finds, for each item not passed, how the work would pass it, from the purpose and
  for every line the same shape reaches, and where that way lies: in the work, or in what the
  caller gave; and raises what only the user can decide. It needs the work, the items not passed,
  the content and the references.
- turn's scripts: give the same result every time: check the CCS, lay out the list and the forms,
  make the run's copy and hand each agent its inputs once the steps before are done, find the
  lines of the work no grounds name (Coverage), make the console that shows the aim before the
  work is written and each step as it is reached, in the user's words with no item IDs, and write
  the work and the CCS back. They need python3 3.9 or later and jq.
- turn's hooks: keep each role to its steps and its inputs, stop a write outside the run's copy
  and the work's place, a commit or a push, and show the console; they act only in the session
  whose run is open. They need Claude Code to run them.
- Claude Code: runs the orchestrator, its agents and the hooks, and keeps the records.
- git: holds the repository as committed, from which the run's copy is made and what was where
  the work goes is got back. It needs the work in a git repository.
- One static figure shows each of these, its responsibility in one line, and what it cannot work
  without; beside it, only where the orchestrator runs: as a skill, where its caller runs, so in a
  conversation the user sees its console and presses Esc, and in a subagent the caller reads what
  it returns, at the cost of room in the caller's context.

### B-1: Attractive quality
- Said in the README's words, since the reader comes from it.
- Read in the place of the person the work is for: the work comes back already read, as that person
  would, by an AI that did not write it and has only what that person would open; each item passed
  is shown in the lines that give it, and what that reading could not take is made again. The user
  hands the work on without first reading it in that person's place.
- Made from what you decided: the work follows your notes and checklist, not whatever turn happened
  to open, and each run of the same request works from the same inputs.
- Asked only what only the user can decide, all at once at the end: nothing is asked that the notes
  and checklist already answer, and nothing is asked while turn works, so the user can leave it at
  work.
- Seeing the work as it goes: the user can tell from what turn shows how far it has come, and stop
  it, with Esc, when what the work will let its person do is not what they want, before the work is
  written, saying what they want instead.
- A plugin decides from what turn returns: a plugin's step hands turn one task and decides from the
  CCS turn writes back alone whether to finish the work itself, call turn again, ask the user or
  move on.
- Following each item back: the user can later find in `.turn/`, for each item, the lines that give
  it or how the work would give it, and the version of the checklist it was judged by.

### B-2: One-dimensional quality
- Each must be no worse than in the version in use.
- The first-run share: requests whose first run passes every item. The more work is right when first
  made, the less the user waits and the less is spent.
- Time and tokens: what one run takes, from the request to the result.

### B-3: Must-be quality
- Nothing passes unshown: an item counts as passed only where lines the work holds give it; every
  other item comes back as not passed, with how the work would give it.
- What the caller gave unchanged: turn never rewrites the task a caller hands it or the files the
  task names as inputs.
- Nothing unread: the work turn writes is the version last read.
- Repository untouched: during a run, turn writes nothing in the repository but where the work's
  files go and `.turn/`, names to the user any other file a run's commands changed, and never
  commits or pushes, so the user takes turn's change as one diff and decides what to commit; what
  was where each file of the work goes can always be got back. Outside its runs, turn blocks
  nothing.
- Stop and start over: a stopped run says so; asked again with the user's words, turn makes the work
  anew from them. A run stopped or cut off leaves where the work's files go as they were before
  the run.
- Missing tools: without python3 or jq, turn ends before any work and says what to install; outside
  a run, a missing tool breaks nothing.

### B-4: Backward compatibility
- The call: plugins call the skill `turn:up` with the arguments the callers' page gives, and name
  `turn` in their dependencies. An argument may be added only if a call without it runs as before.
- The CCS, relied on by every caller: its parts, kinds of entry and values of `next`, as the
  callers' page gives them, are neither added to, removed nor renamed from 0.2.0 on, since a caller
  breaks on one it does not know as on one that is gone; the wording in an entry may change, since
  callers do not act on it. A CCS an earlier version from 0.2.0 on returned is accepted, so a
  stopped task carries on after an update. A CCS of 0.1.0 is not accepted, since no caller relies
  on one.
- The checklist form the README's Requirements gives, relied on by users and writ, who write
  checklists in it: a checklist that opens with its name and version and gives its items as
  headings with IDs keeps being read. What turn takes from a checklist beyond that may change, as
  long as a checklist in that form needs nothing more.
- What a returned CCS points to, relied on by the user, who opens it to follow each item back:
  every place a returned CCS points to exists. The run's evidence is kept under `.turn/` at the top
  of the repository, since the README names that place to the user; how it is laid out inside
  `.turn/` may change.

### B-5: Non-goals
- Deciding what the work should say: the caller does it, knowing what was already agreed, and gives
  it as the content.
- Making the work from one already there: the caller reads it and puts what it says into the
  content; turn makes new work only, since what it is handed it follows, wording and slips included.
- Deciding whether to run again after a run's second round: the caller does it from what the run
  returns, knowing what was agreed.
- Finding what no item asks, which goes into the checklist; and holding checklists, which belong to
  whoever knows the kind of work, such as writ.

### B-6: Constraints
- turn is used by Claude, on a person's behalf, in a conversation or a plugin's step.
- turn runs in Claude Code and holds only skills, agents, hooks and scripts; installing copies only
  its folder; its hooks run in every session where it is installed; a subagent can neither ask the
  user nor hear from its caller while it works.
- Users' machines run Python 3.9 or later with the standard library only, and jq.
- The work is in a git repository.
- Tests and builds a work needs run by shell commands, in a working copy of the repository, so the
  agents' shell stays open.

### B-7: Attractive quality checked
- Each is judged from the records, the JSONL of every conversation and agent of the run. What the
  work gives its receiver is tried on real work, writ's and turn's own documents and prompts,
  against the items in question, since a made-up task shows only that it passes.
- Read in the receiver's place: tried on work for a receiver who lacks what the generator knows,
  where a writer checking their own work passes what a newcomer would miss (assumption). It passes
  when a fresh agent outside the run, reading the returned work as the same receiver with the same
  files it opens and the same list, takes every item returned as Good, including each an earlier
  run left without one.
- Made from what the caller decided: on a task in a repository holding files the inputs do not name,
  the records show no role reading one, and the work says nothing the inputs do not give.
- Asked only what only the user can decide, all at once at the end: on content that settles some
  choices and leaves one open, nothing is asked while the run works, the run ends with `ask the
  user` and that one choice; no question is answered by the inputs.
- Seeing the work as it goes: the console alone tells the step the records show; a run stopped on
  its aim has written no work of that aim, and then makes what the user said.
- A plugin decides from what turn returns: tried on runs that end in each value of `next`, the move
  decided from the returned CCS alone is the one decided after also reading the records.
- Following each item back: the run's evidence alone gives, for any item, the lines of its Good or
  how it would get one, and the version of its checklist.

### B-8: One-dimensional quality measured
- Both are measured from the records of the same tasks, run on this version and on the version in
  use from the same CCS, written in each version's kinds where they differ, as from 0.1.0 to 0.2.0.

### B-9: Must-be quality checked
- Each is a test on the script or hook that holds it, in the case that would break it: grounds naming
  lines the work lacks; a returned CCS whose caller part differs; a version written after the last
  reading; a write outside the work and the run's evidence, a commit or a push in a run; a read
  outside the run's inputs; a shell command of the orchestrator's that is not turn's script; a shell
  command in a run that changes another file; a file where the work goes with changes git lacks; the
  same outside a run, with another session's run open; a run stopped at each step, and one cut off;
  each tool missing, in a run and outside one; a checklist without its name or version.

### B-10: Backward compatibility checked
- For each released version from 0.2.0 on, a test calls turn as its callers did: the call runs; its
  CCS, a stopped one included, is accepted and carried on; every `next` returned is one its callers
  know; its checklists give a list with every opening and item; every place a returned CCS points to
  exists.

### B-11: Principles to judge a change
- The orchestrator alone decides whether each item passes, from the work itself: for each item it
  reads the whole work for where the item is given, and what agents and scripts hand back only
  shows it where to look first, since an item shown passing in one part does not show what the
  whole gives. Protects: nothing passes unshown, read in the receiver's place.
- Every role looks only for where items pass and aims at every item passing; none finds fault,
  and none is set to find something, since one set to find something finds it whether it is there
  or not (assumption); Coverage, a script, is the one place that looks for what may be wrong; each
  role answers in a form with one place per item, since the form, not the wording, holds it to
  its aim. Protects: nothing passes unshown, the first-run share.
- Every role works from the inputs it is handed alone; each prompt names them as the whole of what
  it reads, says in positive words to work from them and gives why, sets as steps what its agent
  receives, hands back and must do in full, and leaves how it thinks within a step to it.
  Protects: made from what the caller decided, read in the receiver's place.
- turn asks nothing while it works, so it runs the same wherever it is called, a subagent
  included, and is stopped or corrected only from where it was called; every question comes back
  at once when the run returns. Protects: asked only what only the user can decide, a plugin
  decides from what turn returns.
- Everything that measures the work measures by the same list, with every checklist's opening,
  the same receiver and the same use; a checklist says its own name and version, so a Good is
  followed back to the text it was judged by. Protects: read in the receiver's place, the
  first-run share, following each item back, the checklist form.
- A run starts from its CCS alone, makes the work in a copy of the repository as committed, and
  keeps the work in the run's evidence until the run returns; the received CCS is never written
  over and the caller's parts come back the same. Protects: what the caller gave unchanged,
  repository untouched, stop and start over, the CCS.
- What must come out the same every time is done by a script or a hook: a script does what a
  step asks and refuses a step whose steps before it are not done; a hook stops a step left out or
  done otherwise, saying which step, what it needs and why, and acts only in the session whose
  run is open, even without python3. Protects: nothing passes unshown, what the caller gave
  unchanged, repository untouched, missing tools, following each item back.
- What can be told before it happens is stopped then, and what cannot is named to the user when
  the run returns: stopped, a write outside the run's copy and the work's place, a commit or a
  push, a write over a file where the work goes unless git holds what is there or it is a work
  an earlier run returned, unchanged since; named, a shell command's side effect. Protects:
  repository untouched.

### B-12: Who is responsible for what
- The user, who hands the work on; the caller, who says what the work should be; the orchestrator,
  the skill `turn:up`, which decides each item; the generator, which meets every item; the first
  user, which takes what the receiver would; the evaluator, which gives Goods with grounds; the
  learner, which finds how to a Good; turn's scripts, on python3 and jq, for the same result every
  time; Claude Code, which runs the agents and hooks and keeps the records; and git.
- What each cannot work without: the caller, the callers' page's form; the orchestrator, the CCS,
  turn's scripts and Claude Code to start its agents; the generator, the inputs a script hands it
  and a shell for tests and builds; the first user, the work and what the receiver opens with it;
  the evaluator, the reading and its records; the learner, the work, the items without a Good, the
  content and the references; turn's scripts, python3 3.9 or later and jq; turn's hooks, Claude
  Code to run them and a run open in their session; git, the work being in a git repository.
- The orchestrator is a skill, so it runs where its caller runs and can start the agents there: in a
  conversation, the user sees its console and presses Esc; in a subagent, which may start agents of
  its own, the caller reads what it returns. The cost is room in the caller's context.

