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
  when named; what they must be able to do with it; the checklists; the decisions, what the caller
  decided the work must say or do, and leave out, item by item of the checklists, holding nothing a
  reference already holds; the references, files or folders the work follows or draws on, which
  turn reads in place of a copy, so a fact has one source; what the receiver opens with the work;
  and the constraints, such as the language to write in. These are the run's inputs.
- A checklist's Format gives the shape the work takes, first; its other items stand in the order
  the maker meets them writing the work from the top, those that hold over the whole last.
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
- The checklist form the README's Requirements gives, relied on by users and by plugins built on
  turn, such as rn, which write checklists in it: a checklist that opens with its name and version
  and gives its items as headings with IDs keeps being read. What turn takes from a checklist
  beyond that may change, as long as a checklist in that form needs nothing more.
- What a returned CCS points to, relied on by the user, who opens it to follow each item back:
  every place a returned CCS points to exists. The run's evidence is kept under `.turn/` at the top
  of the repository, since the README names that place to the user; how it is laid out inside
  `.turn/` may change.

### B-5: Non-goals
- Deciding what the work should say: the caller does it, knowing what was already agreed, and gives
  it as the decisions.
- Making the work from one already there: the caller reads it and puts what it says into the
  decisions, or gives it as a reference; turn makes new work only, since what it is handed it
  follows, wording and slips included.
- Deciding whether to run again after a run's second round: the caller does it from what the run
  returns, knowing what was agreed; a run ends after one second round. Serves: time and tokens.
- Finding what no item asks, which goes into the checklist; and holding checklists, which belong to
  whoever knows the kind of work, such as rn, a plugin built on turn.

### B-6: Constraints
- turn is used by Claude, on a person's behalf, in a conversation or a plugin's step.
- turn runs in Claude Code and holds only skills, agents, hooks and scripts; installing copies only
  its folder; its hooks run in every session where it is installed; a subagent can neither ask the
  user nor hear from its caller while it works.
- Users' machines run Python 3.9 or later with the standard library only, and jq.
- The work is in a git repository.
- Tests and builds a work needs run by shell commands, in a working copy of the repository, so the
  agents' shell stays open.

### B-7: Attractive quality verified
- Read in the place of the person the work is for: every item a run returns as Good is taken as
  given by a fresh agent outside the run, reading the returned work as the same receiver.
  - Checked by a trial in `dev/turn/trials/` on one of rn's or turn's own documents, since a
    made-up task shows only that it passes, the fresh agent given the same files and list.
- Made from what you decided: no role reads a file the inputs do not name, and the work says
  nothing the inputs do not give.
  - Checked by a trial in a repository holding files the inputs do not name, judged from the
    JSONL of every agent of the run.
- Asked only what only the user can decide, all at once at the end: nothing is asked while the
  run works, and the run ends asking only the choice the decisions leave open.
  - Checked by a trial on decisions that leave one choice open, judged from the JSONL.
- Seeing the work as it goes: the console alone tells the step the records show, and a run stopped
  on its aim has written no work of that aim and then makes what the user said.
  - Checked by a trial stopped as by Esc when the console shows the aim, judged from the console
    and the JSONL.
- A plugin decides from what turn returns: the move decided from the returned CCS alone is the one
  decided after also reading the records.
  - Checked on trials that end in each value of `next`.
- Following each item back: the run's evidence alone gives, for any item, the lines of its Good or
  how it would get one, and the version of its checklist.
  - Checked on the evidence the trials above leave.

### B-8: One-dimensional quality verified
- The first-run share: the share of tasks whose first run passes every item is no lower than on
  the version in use.
  - Measured from the records of the same tasks, run on this version and on the version in use
    from the same CCS, written in each version's kinds where they differ.
- Time and tokens: the minutes and tokens of each run are no more than on the version in use.
  - Measured from the records of the same runs.

### B-9: Must-be quality verified
- Nothing passes unshown: grounds naming lines the work lacks are refused.
  - Checked by a test on turn's scripts in `dev/turn/tests/`, run on every push with every line
    and branch counted, as is each test below.
- What the caller gave unchanged: a CCS written back whose caller parts differ from those received
  is refused.
  - Checked by a test on turn's scripts.
- Nothing unread: a write to the work after the first user was handed it is stopped.
  - Checked by a test on turn's hooks.
- Repository untouched: in a run, a write outside the run's copy and the work's place, a commit and
  a push are stopped, and outside a run nothing is.
  - Checked by a test on turn's hooks.
- Stop and start over: a run stopped at each step, and one cut off, leaves where the work goes as it
  was before the run.
  - Checked by a test on turn's scripts.
- Missing tools: with each tool missing, a run ends before any work saying what to install, and
  outside a run nothing breaks.
  - Checked by a test on turn's scripts and hooks with each tool taken away.

### B-10: Backward compatibility verified
- The call: a call as the callers' page gives it runs.
  - Checked by a test in `dev/turn/tests/` that calls turn as the callers of each released version
    from 0.2.0 on did, run on every push, as is each test below.
- The CCS: a CCS each such version returned is accepted and carried on, and every `next` returned is
  one its callers know.
  - Checked by a test with a CCS of each such version.
- The checklist form: a checklist in the form the README gives yields a list with its opening and
  every item.
  - Checked by a test on a checklist in that form.
- What a returned CCS points to: every place a returned CCS points to exists.
  - Checked by a test on a returned CCS.

### B-11: Decisions to judge a change
- The orchestrator alone decides whether each item passes, from the whole work.
  - Serves: nothing passes unshown; read in the place of the person the work is for.
  - What a builder could get wrong: take an agent's word that an item passes, from the part it
    looked at, though the whole work does not give it.
- Every role looks only for where items pass, and answers in a form with one place per item;
  Coverage is the one place that looks for what may be wrong.
  - Serves: nothing passes unshown; the first-run share.
  - What a builder could get wrong: set a role to find faults, which finds them whether they are
    there or not (assumption), so the work is made again for faults it does not have.
- Each role works from the inputs it is handed alone.
  - Serves: made from what you decided; read in the place of the person the work is for.
  - What a builder could get wrong: let a role open whatever helps it, so the work follows what
    no one decided, and a first user who reads more than the receiver takes in what the receiver
    would miss.
- turn asks nothing while it works; every question comes back when the run returns.
  - Serves: asked only what only the user can decide, all at once at the end; a plugin decides
    from what turn returns.
  - What a builder could get wrong: ask the user as soon as a choice comes up, which cannot be
    heard in a subagent and keeps the user at the screen.
- Everything that makes or measures the work works by the same list, receiver and use, and each
  checklist says its own name and version.
  - Serves: read in the place of the person the work is for; the first-run share; following each
    item back; the checklist form.
  - What a builder could get wrong: hand each role only the items it needs, so the work is made
    to one bar and judged by another, and a Good cannot be followed back to its text.
- A run starts from its CCS alone and makes the work in a copy of the repository as committed,
  writing it where it goes only when the run returns.
  - Serves: what the caller gave unchanged; repository untouched; stop and start over; following
    each item back; what a returned CCS points to.
  - What a builder could get wrong: make the work in place, so a run stopped part way leaves
    half-made files where the work goes.
- What must come out the same every time is done by a script or held by a hook, not left to a
  prompt.
  - Serves: nothing passes unshown; what the caller gave unchanged; nothing unread; repository
    untouched; missing tools; seeing the work as it goes.
  - What a builder could get wrong: leave such a step to a prompt, which an AI does differently
    from run to run, so a slip shows only later, in a result that looks right.
- A caller reaches turn only through the call and the CCS; everything inside turn may change.
  - Serves: the call; the CCS; a plugin decides from what turn returns.
  - What a builder could get wrong: let a caller read the run's forms or evidence, which then
    cannot change without breaking it.
- What can be told before it happens is stopped then, and what cannot is named to the user when
  the run returns.
  - Serves: repository untouched.
  - What a builder could get wrong: stop every command that might do harm, which closes the tests
    and builds the work needs, or check only afterwards, when the harm is done.

### B-12: Who does what to what
- Structure opens with how turn divides, in one sentence: turn is one orchestrator, four agents
  and the scripts and hooks that hold them to their steps; the orchestrator and the agents share
  nothing but the files of the run's evidence under `.turn/`, where each finds its inputs and
  leaves its answer, and the caller reaches turn only through the CCS.
- The logical figure, a box for each one that takes part holding its name alone, the four agents
  grouped as turn's agents, and an arrow from each to what it reads, writes, copies or calls,
  labelled with that relation:
  - the user → the caller: asks for the work, and answers what the run returns
  - the user → the orchestrator: watches the console, stops it with Esc
  - the caller → the orchestrator: hands the CCS
  - the orchestrator → the caller: writes the CCS back
  - the orchestrator → turn's scripts: calls, for every step that must come out the same
  - the orchestrator → each agent: starts with its brief
  - the orchestrator → the run's evidence: reads the work and every form, writes its decision on
    each item
  - the generator → the run's evidence: reads its brief, writes the work in the run's copy and
    names where each item passes in its form
  - the first user → the run's evidence: reads the work and what the receiver opens, writes its
    reading
  - the evaluator → the run's evidence: reads the reading and the work, writes which items pass
    with their lines
  - the learner → the run's evidence: reads the work, the forms, the decisions and the
    references, writes how each item left would pass and where that lies
  - turn's scripts → the run's evidence: lay out the list, the forms and the briefs, make the
    run's copy, find Coverage, show the console
  - turn's scripts → git: copy the repository as committed, and get back what was where the work
    goes
  - turn's scripts → where the work goes: write the work when the run returns
  - turn's hooks → the orchestrator and its agents: stop a read outside the role's inputs, a write
    outside the run's copy and where the work goes, a commit or a push, and a step done out of
    order

### B-33: Every goal and decision placed
- Held by where the figures place the parts, so nothing more is said: read in the place of the
  person the work is for (the first user, apart from the generator); made from what
  you decided and repository untouched (turn's hooks); seeing the work as it goes and how a
  checklist is written (turn's scripts); following each item back and what a returned CCS points
  to (the run's evidence); the call (the orchestrator, the skill `turn:up`).
- One sentence under the logical figure for each held inside one part, saying what the part holds:
  - The orchestrator holds nothing passes unshown: it alone decides each item, from the whole
    work.
  - The orchestrator holds asking only at the end: it puts no question while the run goes and
    returns every one when it ends.
  - The orchestrator holds time and tokens: a run has at most one second round.
  - The generator holds the first-run share: it makes the work to every item of the list from the
    first round; the learner holds it for the second, finding how each item left would pass.
  - turn's scripts hold what the caller gave unchanged and the CCS: the CCS received is never
    written over, and the one written back has the parts and values the callers' page gives.
  - turn's scripts hold a plugin deciding from what turn returns: the CCS they write back names
    the next move and every question.
  - turn's scripts hold Coverage: they find the lines of the work no grounds name.
  - turn's hooks hold nothing unread: they stop a write to the work once the first user has been
    handed it.
  - The orchestrator, turn's scripts and turn's hooks hold missing tools: the orchestrator says to
    install python3 when it is not found, the scripts end a run before any work when jq is
    missing, and the hooks do nothing where python3 is missing.

### B-26: What kind of thing each unit is
- The physical figure names each unit by its kind: turn's skill, the orchestrator's prompt; turn's
  agents, the prompts of the generator, the first user, the evaluator and the learner; turn's
  scripts, python3 with jq; turn's hooks, `sh` entries that run python3 checks; the CCS, one JSON
  file; the run's evidence, JSON files and a working copy of the repository; the work, files.

### B-23: Where each part is kept
- Frames: shipped with turn, copied to the user's machine at install, holding turn's skill,
  agents, scripts and hooks; the user's repository, holding the CCS where the caller puts it, the
  run's evidence under `.turn/`, uncommitted and left to the user, and the work where the task
  says.

### B-24: Where each part runs
- A frame for the user's machine, where every unit of turn runs, inside the Claude Code session
  that called it: the orchestrator where its caller runs, so in a conversation the user sees its
  console and presses Esc, and in a subagent the caller reads what it returns, at the cost of room
  in the caller's context; each agent as a subagent; nothing of turn runs in CI.

### B-25: What the product depends on
- Arrows, each labelled: turn's scripts → python3 3.9 or later and jq: run on; turn's scripts →
  git: make the run's copy and get back what was where the work goes; turn's hooks → Claude Code:
  run in every session where turn is installed; turn's skill and agents → Claude Code: run as a
  skill and as subagents; a plugin built on turn → turn: names it in its dependencies.
