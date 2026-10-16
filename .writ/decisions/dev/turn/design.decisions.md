# What dev/turn/design.md says

## doc

### B-9: The point from the opening
- The opening is the idea of design B-37, with a link to the README (`../../turn/README.md`) and
  to the callers' page (`../../turn/calling-from-a-plugin.md`).

### B-12: Every term known
- The terms the README and the callers' page give, such as the caller, the CCS, the work, a
  checklist and the run's inputs, are used as they give them and not said again; the reader opens
  both.
- The orchestrator runs a run and alone decides each item; turn's agents give it what it decides
  from: the generator makes the work, the first user reads it in the receiver's place, the
  evaluator shows which items the work meets, and the learner finds how an item without a Good
  would get one.
- A Good: an item the orchestrator has decided the work meets, with its grounds, the lines it rests
  on.
- A round: the work made, read and decided; a run has a first round and, when items are left
  without a Good, a second, which makes the work again.
- A form: the answer an agent writes, a JSON file with one place per item. The reading: the first
  user's form.
- Coverage: the lines of the work no grounds name, as test coverage finds the lines no test runs.
- The run's evidence: what a run keeps under `.turn/` for the user and later runs, the run's copy
  among it, a working copy of the repository as committed, where the work is made so the tests and
  builds it needs run in place.

## design

### B-37: The idea that holds the promises
- The work is read in its receiver's place by an agent that did not write it, and one orchestrator
  decides each item of the checklists from the whole work, so nothing passes that the work does
  not show.

### B-12: Who does what to what
- The logical figure, a box for each one that takes part holding its name alone, the four agents
  grouped as turn's agents, and an arrow from each to what it reads, writes, copies or calls,
  labelled with that relation alone; what each stops or holds is the criteria's and the items':
  - the user → the caller: asks for the work, and answers what the run returns
  - the user → the orchestrator: watches the console, stops it with Esc
  - the caller → the orchestrator: hands the CCS
  - the orchestrator → the caller: writes the CCS back
  - the orchestrator → turn's scripts: calls
  - the orchestrator → each agent: starts with its brief
  - the orchestrator → the run's evidence: reads the work, every form and Coverage, writes its
    decision on each item
  - the generator → the run's evidence: writes the work in the run's copy, and its form
  - the first user → the run's evidence: reads the work and what the receiver opens, writes the
    reading
  - the evaluator → the run's evidence: reads the reading and the work, writes its form
  - the learner → the run's evidence: reads the work, the forms and the inputs, writes its form
  - turn's scripts → the run's evidence: lay out the list, the forms and the briefs, find Coverage
  - turn's scripts → git: copy the repository as committed
  - turn's scripts → where the work goes: write the work when the run returns
  - turn's hooks → the orchestrator and its agents: stop a step

### B-38: Every promise placed
- One item under the logical figure for each promise, by its name in the criteria:
  - The first user holds where the work fails the person it is for: it reads the work it did not
    write, with only what the receiver opens.
  - turn's hooks hold the work follows what you decided: they stop a read of a file the inputs do
    not name.
  - The orchestrator holds a pass you can check: it alone decides each item, from the whole work,
    every item in every round, and keeps each Good's grounds in the run's evidence.
  - turn's scripts hold made again, keeping every item it gave: they lay out every item of the
    list for the second round, not only those left.
  - The orchestrator holds leave turn at work and answer everything at once: it asks nothing while
    the run goes and returns every question when it ends.
  - The orchestrator holds seeing each step and stopping before turn writes: it runs as a skill in
    the caller's session, so the user sees its console and can press Esc there.
  - turn's scripts hold a plugin decides from what turn returns, the CCS written back and what the
    caller gave unchanged: they write back a CCS with the parts and values the callers' page gives
    and never write over the one received.
  - turn's agents hold the first-run share: each looks only for where the work meets items, and
    Coverage is the one place that looks for what may be wrong.
  - The orchestrator holds time and tokens: a run has at most one second round.
  - turn's scripts hold stop leaves things as they were and start over: the work is made in the
    run's copy and written where it goes only when the run returns.
  - turn's scripts hold other changes named: they name each file a run's commands changed outside
    the work.
  - turn's hooks hold nothing unread, repository untouched and no commit or push: they stop a
    write to the work once the first user has it, a write outside the run's copy and where the work
    goes, and a commit or a push.
  - turn's hooks hold nothing in the way outside a run: they act only in the session whose run is
    open, and do nothing where python3 is missing.
  - The orchestrator and turn's scripts hold missing tools: the orchestrator says to install
    python3 when it is not found, and the scripts end a run before any work when jq is missing.
  - turn's scripts hold a stopped task carries on and the checklist layout: they accept a CCS each
    version from 0.2.0 on returned, and make the list from each checklist's name, version, opening
    and items.
  - The run's evidence holds what a returned CCS points to: every place a returned CCS names is in
    it, under `.turn/`.
  - The orchestrator holds the call: it is the skill `turn:up`.

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
- Each criterion names a promise of the README in its words, and each check is a trial in
  `dev/turn/trials/`, judged from the JSONL of every agent of the run.
- Where the work fails the person it is for: every item a run returns as Good is taken as given by
  a fresh agent outside the run, reading the returned work as the same receiver.
  - Checked by a trial on one of rn's or turn's own documents, since a made-up task shows only that
    it passes, the fresh agent given the same files and list.
- The work follows what you decided: no part of turn reads a file the inputs do not name, and the
  work says nothing the inputs do not give.
  - Checked by a trial in a repository holding files the inputs do not name.
- A pass you can check: the run's evidence alone gives, for any item with a Good, the lines of the
  work that give it, and the version of its checklist.
  - Checked on the evidence the trials here leave.
- Made again, keeping every item it gave: a run whose first round leaves an item without a Good
  makes the work again in the same run, and every item the first round gave a Good has one again.
  - Checked by a trial whose first round leaves an item the work can give.
- Leave turn at work and answer everything at once: nothing is asked while the run works, and the
  run ends asking only the choice the decisions leave open.
  - Checked by a trial on decisions that leave one choice open.
- Seeing each step: the console alone tells the step the records show.
  - Checked on the trials here, from the console and the records.
- Stopping before turn writes: a run stopped when the console shows what the work will let its
  receiver do has written no work of it, and then makes what the user said.
  - Checked by a trial stopped as by Esc at that line.
- A plugin decides from what turn returns: the move decided from the returned CCS alone is the one
  decided after also reading the records.
  - Checked on trials that end in each value of `next` the callers' page gives.

### B-8: One-dimensional quality verified
- The first-run share: the share of tasks whose first round gives every item a Good is no lower
  than on the version last released.
  - Measured from the records of the same tasks, run on both versions from the same CCS, written
    in each version's kinds where they differ.
- Time and tokens: the minutes and tokens of each run are no more than on the version last
  released.
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
- The checklist layout: a checklist laid out as the README of 0.2.0 gives, with a name, a version,
  an opening and items, yields a list with its opening and every item.
  - Checked by a test on a checklist so laid out.
- What a returned CCS points to: every place a returned CCS points to exists, under `.turn/`, for
  a CCS of each version from 0.2.0 on.
  - Checked by a test on a returned CCS.
