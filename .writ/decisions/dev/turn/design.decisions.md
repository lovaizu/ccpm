# What dev/turn/design.md says

## doc

### B-9: The point from the opening
- The opening is the idea of design B-37, with a link to the README (`../../turn/README.md`).
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

### B-37: The idea that holds the promises
- The work is read in its receiver's place by an agent that did not write it, and one orchestrator
  decides each item of the checklists from the whole work, so nothing passes that the work does
  not show.

### B-12: Who does what to what
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

### B-38: Every promise placed
- Held by where the figures place the parts, with no item under the figure: read in the place of
  the person the work is for (the first user, apart from the generator); made from what you
  decided, repository untouched and no commit or push (turn's hooks); seeing the work as it goes
  and stopping before the work is written (the orchestrator, a skill where its caller runs);
  following each item back and what a returned CCS points to (the run's evidence); the call and a
  plugin decides from what turn returns (only the CCS between the caller and the orchestrator).
- One item under the logical figure for each held inside one part:
  - The orchestrator holds nothing passes unshown: it alone decides each item, from the whole
    work, every item in every round.
  - The orchestrator holds asked only what only the user can decide: it puts no question while
    the run goes and returns every one when it ends.
  - The orchestrator holds time and tokens: a run has at most one second round.
  - turn's agents hold the first-run share: each looks only for where items pass, in a form with
    one place per item, and Coverage, which turn's scripts find, is the one place that looks for
    what may be wrong.
  - turn's scripts hold what the caller gave unchanged and the CCS written back: the CCS received
    is never written over, and the one written back has the parts and values the callers' page
    gives.
  - turn's scripts hold a stopped task carries on: they accept a CCS each version from 0.2.0 on
    returned.
  - turn's scripts hold the checklist layout: they make the list from each checklist's name,
    version, opening and items.
  - turn's scripts hold nothing lost when made again: they lay out every item of the list for
    each round.
  - turn's scripts hold stop leaves things as they were and start over: the work is made in the
    run's copy and written where it goes only when the run returns.
  - turn's scripts hold other changes named: they name each file a run's commands changed outside
    the work.
  - turn's hooks hold nothing unread: they stop a write to the work once the first user has been
    handed it.
  - turn's hooks hold nothing in the way outside a run: they act only in the session whose run is
    open, and do nothing where python3 is missing.
  - The orchestrator and turn's scripts hold missing tools: the orchestrator says to install
    python3 when it is not found, and the scripts end a run before any work when jq is missing.

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
  that called it; nothing of turn runs in CI.

### B-25: What the product depends on
- Arrows, each labelled: turn's scripts → python3 3.9 or later and jq: run on; turn's scripts →
  git: make the run's copy and get back what was where the work goes; turn's hooks → Claude Code:
  run in every session where turn is installed; turn's skill and agents → Claude Code: run as a
  skill and as subagents; a plugin built on turn → turn: names it in its dependencies.

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
- Seeing the work as it goes: the console alone tells the step the records show.
  - Checked on the trials above, from the console and the JSONL.
- Stopping before the work is written: a run stopped on its aim has written no work of that aim,
  and then makes what the user said.
  - Checked by a trial stopped as by Esc when the console shows the aim.
- A plugin decides from what turn returns: the move decided from the returned CCS alone is the one
  decided after also reading the records.
  - Checked on trials that end in each value of `next`.
- Following each item back: the run's evidence alone gives, for any item, the lines of its Good or
  how it would get one, and the version of its checklist.
  - Checked on the evidence the trials above leave.

### B-8: One-dimensional quality verified
- The first-run share: no lower than on the version in use.
  - Measured from the records of the same tasks, run on this version and on the version in use
    from the same CCS, written in each version's kinds where they differ.
- Time and tokens: the minutes and tokens of each run are no more than on the version in use.
  - Measured from the records of the same runs.

### B-9: Must-be quality verified
- Nothing passes unshown: grounds naming lines the work lacks are refused.
  - Checked by a test on turn's scripts in `dev/turn/tests/`, run on every push with every line
    and branch counted, as is each test below.
- Nothing lost when made again: a second round lays out and decides every item of the list, not
  only those left without a Good.
  - Checked by a test on turn's scripts.
- What the caller gave unchanged: a CCS written back whose caller parts differ from those received
  is refused.
  - Checked by a test on turn's scripts.
- Nothing unread: a write to the work after the first user was handed it is stopped.
  - Checked by a test on turn's hooks.
- Repository untouched: in a run, a write outside the run's copy and where the work goes is
  stopped.
  - Checked by a test on turn's hooks.
- No commit or push: in a run, a commit and a push are stopped.
  - Checked by a test on turn's hooks.
- Other changes named: a file a shell command changed in a run outside the work is named in what
  the run returns.
  - Checked by a test on turn's scripts.
- Stop leaves things as they were: a run stopped at each step, and one cut off, leaves where the
  work goes as it was before the run.
  - Checked by a test on turn's scripts.
- Start over: after a stop, a run started with the user's words makes the work from them.
  - Checked by a test on turn's scripts.
- Missing tools: with each tool missing, a run ends before any work saying what to install.
  - Checked by a test on turn's scripts with each tool taken away.
- Nothing in the way outside a run: with no run open, or with a tool missing, the hooks stop
  nothing.
  - Checked by a test on turn's hooks.

### B-10: Backward compatibility verified
- The call: a call as the callers' page gives it runs, as does one without an argument added since.
  - Checked by a test in `dev/turn/tests/` that calls turn as the callers of each released version
    from 0.2.0 on did, run on every push, as is each test below.
- The CCS written back: every part, kind of entry and value of `next` written back is one 0.2.0's
  callers know; the wording in an entry may differ.
  - Checked by a test on a CCS written back.
- A stopped task carries on: a CCS each version from 0.2.0 on returned is accepted and carried on,
  and one of 0.1.0, which no caller relies on, is refused.
  - Checked by a test with a CCS of each such version.
- The checklist layout: a checklist so laid out yields a list with its opening and every item.
  - Checked by a test on a checklist so laid out.
- What a returned CCS points to: every place a returned CCS points to exists, under `.turn/`.
  - Checked by a test on a returned CCS.
