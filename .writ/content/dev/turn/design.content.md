# What dev/turn/design.md says

## doc

### B-9: The point from the opening
- turn keeps what its README (`../../turn/README.md`) promises by one idea: the work is read in its
  receiver's place by an agent that did not write it, and one orchestrator decides each item of the
  checklists from the whole work, so nothing passes that the work does not show.
- How to use turn is in that README, and the forms a caller writes and reads are on the callers'
  page (`../../turn/calling-from-a-plugin.md`).

### B-12: Every term known
- The caller: Claude in the user's conversation, or a step of the user's plugin. It hands turn one
  task in a CCS, a JSON file, and turn writes back what the caller needs next, as a function takes
  arguments and returns a value.
- The work: what one task makes for one purpose, one file or several, such as code and its tests,
  written, read and decided together, since what the receiver needs may be given only by them
  together.
- What the caller gives: where each file of the work goes; the receiver it is for; their use of it,
  when named; what they must be able to do with it; the checklists; the content, what the work says
  or does item by item of the checklists; the references, files or folders the work follows or
  draws on; what the receiver opens with the work; and the constraints, such as the language to
  write in. These are the run's inputs.
- A checklist says what a work of one kind must give its receiver: an opening on what such work is
  for, then items, each one question. The list is a task's checklists put together.
- A run goes from one CCS to the one turn writes back: it makes the work, has it read, decides each
  item and finds how each item without a Good would get one.
- The orchestrator runs a run and alone decides each item. Its agents give it what it decides from:
  the generator makes the work, the first user reads it in the receiver's place and hands back its
  reading, the evaluator shows which items the work meets, and the learner finds how an item
  without a Good would get one.
- A Good: an item the orchestrator has decided the work meets, with its grounds, the lines it rests
  on. More: an item without a Good when a run returns.
- A form: the answer a role writes, a JSON file with one place per item, which the agents read
  and change with jq; what the role hands back is its form. The reading: the first user's form,
  what it took from the work for each item and where.
- Coverage: the lines of the work no grounds name, as test coverage finds the lines no test runs.
- The run's evidence: what a run keeps in the repository for the user and later runs: the work, its
  reading and decisions, each way to a Good, and the list with each checklist's name and version.
  The work is made in a working copy of the repository as it is committed, kept in the evidence
  while the run goes, so the tests and builds the work needs run in place; the work stays in the
  evidence until the run returns, and the copy is gone by then.

## design

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
- The orchestrator alone decides, from the work itself: for each item it reads the whole work for
  where the item is given, and what agents and scripts hand back only shows it where to look first,
  since a Good on one part does not show what the whole gives. Protects: nothing passes unshown, read
  in the receiver's place.
- Every role, the orchestrator included, looks only for Goods and aims at every item being Good;
  none finds fault, and none is set to find something, since one set to find something finds it
  whether it is there or not (assumption). Coverage, a script, is the one place that looks for what
  may be wrong. Each answers, as the orchestrator decides, in a form with one place per item, since
  the form, not the wording, holds it to its aim. Protects: nothing passes unshown, the first-run
  share.
- Every role works from the inputs it is handed alone. Each prompt names them as the whole of what
  it reads, says in positive words to work from them, and gives why: so the work follows what the
  caller decided, without bias from what was not given. Each prompt sets as steps what its agent
  receives, hands back and must do in full, as instructions with their reasons, and leaves how it
  thinks within a step to it. Protects: made from what the caller decided, read in the receiver's
  place.
- A question for the user may come from the roles given the content: the orchestrator, the generator
  and the learner; the orchestrator decides each, showing where it is answered or leaving it open,
  and the run returns every open one at its end. The first user and the evaluator raise none, since
  without the content they cannot tell what only the user can decide, and a place for what they did
  not find would be a place for faults; what they did not take reaches the learner as an item
  without a Good. Protects: asked only what only the user can decide.
- turn asks nothing while it works, so it runs the same wherever it is called, a subagent included,
  and is stopped or corrected only from where it was called. Protects: asked only what only the user
  can decide, a plugin decides from what turn returns.
- What must come out the same every time is done by a script or a hook: a script does what a step
  asks, and refuses a step whose steps before it are not done; a hook sees, as Claude Code runs the
  run, that a step was not left out or done otherwise, and stops it saying which step, what it needs,
  and why. Protects: nothing passes unshown, what the caller gave unchanged, repository untouched,
  made from what the caller decided, following each item back.
- turn's hooks act only in the session whose run is open, and do nothing elsewhere, even without
  python3, since they run in every session where turn is installed. Protects: repository untouched,
  missing tools.

### B-12: Who takes part
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

### B-25: What passes between them
- The caller and the orchestrator: the caller hands the CCS; the orchestrator hands back a new CCS.
- The orchestrator and the generator: the orchestrator hands the receiver, the use, what the
  receiver must be able to do, the list, the content, the references, and the ways to a Good when
  there are any; the generator hands back the work, its form and its questions.
- The orchestrator and the first user: the orchestrator hands the work, what the receiver opens with
  it, the receiver, the use and the list; the first user hands back the reading.
- The orchestrator and the evaluator: the orchestrator hands the work, the reading and its records,
  the list and what the receiver must be able to do; the evaluator hands back Goods with grounds.
- The orchestrator and the learner: the orchestrator hands the work, the items without a Good, the
  content, the references and the records; the learner hands back ways to a Good and questions.
- turn's scripts and the user: the console, which shows the aim, where the run is, and at the end
  where the work is and every question left open. turn's scripts keep every form as the run's
  evidence.
- turn's hooks, run by Claude Code, keep each role to its steps and its inputs, show the console,
  and stop what would change the user's work.

### B-13: An approach for each quality
- The checklist as the measure. Brings about: read in the receiver's place, the first-run share,
  following each item back, the checklist form. Idea: a work that meets every item of its checklists
  serves its purpose (assumption, which the attractive-quality trials test), so everything that
  measures the work, the orchestrator included, measures by the same list, with every opening, and
  the same receiver and use, and so all measure alike. A checklist says its own name and version, so
  a Good can be followed back to the text it was judged by, wherever the checklist is kept. Who
  takes part: the caller, who names the checklists; turn's scripts, which read them into the list;
  every role. Weighed: letting the first user also report what it missed outside the items; not
  chosen, since unbounded by an item it becomes a search for faults that varies from run to run
  (assumption).
- Working from the inputs alone. Brings about: made from what the caller decided, read in the
  receiver's place. Idea: each role is handed only the inputs it needs, and reads nothing else, so
  the work follows what the caller decided, without bias from what was not given. Who takes part:
  turn's scripts, which hand each role its inputs; turn's hooks, which hold each role to them and
  the orchestrator to turn's own commands; the agents' shell stays open, since tests and builds need
  it, and what they read by it shows in the records. Weighed: telling the roles in words only; not
  chosen, since in a trial on 2026-10-15 the orchestrator read files not given, and what it read
  shaped the work.
- Making it right first. Brings about: the first-run share, time and tokens, asked only what only
  the user can decide. Idea: what can be seen before the reading costs a whole run when found in it,
  so the work reaches the first user only once the orchestrator sees every item met or waiting on a
  question left open; what the inputs do not settle is kept out of the work and asked at the end.
  Who takes part: the orchestrator, which reads each item against the inputs before the work is
  written and reads the whole work when it comes back; the generator, which makes the work to meet
  every item and names where; turn's scripts, which give coverage and hold the work back from the
  first user until then. Weighed: a limit on sending back; not chosen, since a work sent on
  unsettled costs a run. Weighed: asking each question as it is seen; not chosen, since a subagent
  cannot ask the user, so only a run that asks nothing runs the same wherever it is called.
- Keeping each role to its steps. Brings about: nothing passes unshown, the first-run share. Idea:
  each role's steps are what make its answer usable, so a step left out or done otherwise is stopped
  as it happens, not found later in an answer that looks right. Who takes part: turn's scripts,
  which hand an agent its inputs only once the steps before it are done; turn's hooks, which hold
  each agent and the orchestrator to their steps and say which step and why when they stop one.
  Weighed: telling each role its steps in words only; not chosen, since a step left out still gives
  an answer that looks right (assumption).
- Reading in the receiver's place. Brings about: read in the receiver's place. Idea: the first user
  reads the work with only what the receiver opens with it, so it stops where the receiver would
  (assumption), and takes from the work only what it gives. Who takes part: the caller, who names
  what the receiver opens; the first user, given the work, those files, the receiver, the use and
  the list, and nothing of how the work was made, its content or references, or what the receiver
  must be able to do. Weighed: a fresh copy of the whole repository; not chosen, since a receiver
  opens the work and what it links, not every file, and the copy let the reader take from the
  sources what the work did not give. Weighed: telling the first user what the receiver must be able
  to do; not chosen, since it would look for that rather than take what the work gives (assumption).
- Deciding every item. Brings about: nothing passes unshown, read in the receiver's place, following
  each item back, what a returned CCS points to. Idea: the evaluator shows, for each item the work
  meets, the lines and why, judged from the reading; coverage shows the lines no Good names, since
  every useful line meets some item (assumption); the orchestrator alone decides each item from the
  whole work, and every decision is kept so each item can be followed back, from the returned CCS,
  which points to them. Who takes part: the evaluator, turn's scripts, the orchestrator. Weighed: an
  agent set to look for slips; not chosen, since one set to find something finds it whether it is
  there or not, and a script comes out the same every time.
- Making again toward a Good. Brings about: read in the receiver's place, nothing unread. Idea: a
  change made from the place a slip showed fixes that place and leaves the same shape elsewhere, so
  a way to a Good is made from the purpose: what the whole work gives once the item is met, every
  line the same shape reaches, and the change taken at each. A way in the work is taken in a second
  round within the same call; a way in what the caller gave, or in how such work is made, goes back
  to the caller, who decides what follows. Who takes part: the learner, which finds each way and
  where it lies; the generator, which takes the ways in the work; the caller. Weighed: no second
  round by default; not chosen, since the first round is where the generator first sees where the
  receiver stops, and in every run of writ's rebuild it left ways in the work. Weighed: a third
  round; not chosen, since the caller knows what was agreed and decides from what a second round
  leaves, while further rounds without that knowledge raise finer points the purpose does not need
  (assumption; three calls on a CSV tool's README, 2026-10-14, each raised finer questions than the
  last). Weighed: adding each rule learned to the caller's `constraints`; not chosen, since rules
  piled up over runs and pushed into the work what the caller had not asked (eleven rules on writ's
  README, 2026-10-15).
- The console. Brings about: seeing the work as it goes. Idea: the console serves a user who looks
  in now and then: where the run is, what the work will let its receiver do before it is written, so
  a wrong aim is stopped before a run is spent, what the work does not yet give, in plain words, and
  at the end where the work is and what the user must decide; no item IDs or counts, since the user
  would have to learn the checklist. Who takes part: the orchestrator, which writes the aim; turn's
  scripts and hooks, which make and show the console. Weighed: the orchestrator telling the user
  where it is in its own words; not chosen, since in four trials of four (2026-10-12) it did not
  write the aim between its tool calls.
- The CCS. Brings about: a plugin decides from what turn returns, what the caller gave unchanged,
  stop and start over, the call, the CCS. Idea: the CCS (Compressed Cognitive State) takes the nine
  parts that ACC (Agent Cognitive Compressor, https://arxiv.org/abs/2601.11653) sets as the state
  the next step needs; each kind the caller writes says what the input is for, so turn decides from
  it which role is handed it; every change of course goes through the caller as a new run, which
  starts from its CCS alone; until a run returns, the work is only in the run's evidence. Who takes
  part: the caller, the orchestrator, turn's scripts. Weighed: handing agents the CCS itself; not
  chosen, since a change made for one agent would change what callers rely on.
- Leaving the user's work alone. Brings about: repository untouched, missing tools. Idea: what can
  be told before it happens is stopped then: a write outside where the work's files go and the run's
  evidence, a commit or a push, and a write over a file where the work goes unless git holds it as
  it stands or it is the work a run returned, unchanged since; what cannot, a side effect of a shell
  command, is named to the user when the run returns; a missing tool ends the run before any work.
  Who takes part: turn's scripts and hooks, git. Weighed: checking afterwards only; not chosen,
  since the harm is done by then. Weighed: python3 alone for the agents' changes to the forms; not
  chosen, since agents already know jq.
