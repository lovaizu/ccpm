# turn design

This document is for whoever builds or changes turn. It says what turn must achieve, how each
quality is checked, and how turn is built to achieve it, for the benefits turn's
[README](../../turn/README.md) promises. Its point: turn hands back a work already read as the
person it is for would read it, and judged question by question against the checklists it must
meet, each question counted as met only on lines the work holds; a single part of turn, the one
that runs the whole task, makes every such judgment from the whole work, and scripts and hooks hold
every step that must come out the same each time.

It leaves out how to use turn, which is in the README; the forms a caller writes and reads, which
are on the callers' page, ["Calling turn from a plugin's step"](../../turn/calling-from-a-plugin.md);
and the prompts' wording and steps, which are left to the code. A statement no trial has checked
yet is marked "(assumption)".

Terms used throughout:

- **The caller**: Claude in the user's conversation, or a step of the user's plugin. It hands turn
  one task in a **CCS**, a JSON file, and turn writes back a CCS with what the caller needs next, as
  a function takes arguments and returns a value. A CCS has the **caller's part**, which the caller
  writes, and **turn's part**, which turn writes.
- **A checklist** says what a work of one kind must give its receiver: an opening on what such work
  is for, then **items**, each one question. **The list** is a task's checklists put together.
- **The inputs** of a run, what the caller gives: where the work goes; the receiver it is for;
  their use of it, when named; what the receiver must be able to do with it; the checklists; the
  **content**, what the work says or does item by item of the checklists; the **references**, files
  or folders the work follows or draws on; and what the receiver opens with the work.
- **A Good**: an item decided as met by the work, with its **grounds**, the lines it rests on.
  **A way to a Good**: how an item without one would get it. A way lies in the work, in what the
  caller gave, or in how such work is made; one in how such work is made is returned as a **rule**,
  for the caller to judge whether to take it into later work.
- **A run** goes from one CCS to the one turn writes back: it makes the work, has it read, decides
  each item, and finds how each item without a Good would get one. A **round** is one pass of having
  the work read and deciding each item; a run has a first round and at most a second. **Unmet**: an
  item without a Good when a run returns.
- **The roles**: the **orchestrator** runs a run and alone decides each item. Its agents give it
  what it decides from: the **generator** makes the work, the **first user** reads it in the
  receiver's place and hands back its **reading**, what it took from the work for each item and
  where, the **evaluator** shows which items the work meets, and the **learner** finds how an item
  without a Good would get one.
- **A form**: what each role hands back, with one place per item.
- **`next`**: the entry in turn's part of the returned CCS that tells the caller what to do next.
  The callers' page gives its values and the caller's move on each; this document names a value
  only where an approach decides when a run returns it.
- **Coverage**: the lines of the work no grounds name, as test coverage finds the lines no test
  runs.
- **The run's aim**: what the work will let its receiver do, which the orchestrator writes in one
  sentence from the inputs before the work is written.
- **The console**: what shows the user the run step by step as it goes: where it is, its aim before
  the work is written, what the work does not yet give, and at the end where the work is and what
  the user must decide.
- **The run's evidence**: what a run keeps in the repository for the user and later runs: the work,
  its reading and decisions, each way to a Good, and the list with each checklist's name and
  version. The work stays there until the run returns.
- **The records**: the JSONL Claude Code keeps of every conversation and agent of a run.

## Goals

### Attractive quality

- **Read in the receiver's place**: the work comes back already read in the receiver's place by an
  agent that did not write it, with only what the receiver would open, each Good shown in its lines,
  and what that reading could not take made again on how it would be given. The user hands the work
  on without first reading it as its receiver.
- **Made from what the caller decided**: turn makes the work from the run's inputs alone, so the
  work follows what the caller decided rather than whatever turn happened to open, and each run of
  the same task works from the same inputs.
- **Asked only what only the user can decide, all at once at the end**: nothing is asked that the
  inputs already answer, and nothing is asked while the run works, so the user can leave turn at
  work.
- **Seeing the work as it goes**: the user can tell from the console how far a run has come, and
  stop a run whose aim they do not want before the work is written, saying what they want instead.
- **A plugin decides from what turn returns**: a plugin hands turn one task and decides from the
  returned CCS alone whether to finish the work itself, call turn again, ask the user or move on.
- **Following each item back**: the user can later find, for each item, the lines its Good rests on
  or how it would get one, and the version of the checklist it was judged by.

### One-dimensional quality

Each must be no worse than in the version in use.

- **The first-run share**: the share of tasks whose first run ends with every item Good. The more
  work is right when first made, the less the user waits and the less is spent.
- **Time and tokens**: what one run takes, from the call to the returned CCS.

### Must-be quality

- **Nothing passes unshown**: an item counts as met only with a Good whose grounds are lines the
  work holds; every other item is returned as unmet, with its way to a Good.
- **What the caller gave unchanged**: turn never rewrites the caller's part of the CCS or the files
  it names.
- **Nothing unread**: the work turn writes where the work goes is the version last read.
- **Repository untouched**: during a run, turn changes nothing in the repository but where the work
  goes and the run's evidence, and never commits or pushes, so the user takes turn's change as one
  diff and decides themselves what to commit. A file where the work goes is written over only when
  git holds it as it stands, or it is the work a run returned and is unchanged since, so what was
  there can be got back. A change a shell command of the run makes elsewhere as a side effect is
  named to the user. Outside its runs, turn blocks nothing.
- **Stop and start over**: a stopped run returns a CCS saying so; called again with the task
  rewritten from what the user said, turn makes the work anew from it. A run cut off leaves where
  the work goes untouched.
- **Missing tools**: without python3 or jq, turn ends before any work and says what to install;
  outside a run, a missing tool breaks nothing.

### Backward compatibility

- **The call**. Relied on by plugins, writ among them, which call the skill `turn:up` with the
  arguments the callers' page gives and name `turn` in their dependencies. Must keep holding: such a
  call runs. May change: an argument may be added, only if a call without it runs as before.
- **The CCS**. Relied on by callers, which write it and act on what comes back. Must keep holding:
  its parts, its kinds of entry and the values of `next`, which the callers' page gives; from 0.2.0
  on none of them is added, removed or renamed, since a caller breaks on one it does not know as on
  one that is gone; and a CCS an earlier version from 0.2.0 on returned is accepted, so a stopped
  task carries on after an update. May change: the wording in an entry, since callers do not act on
  it. 0.2.0 changes the kinds so that each kind the caller writes says what its input is for, from
  which turn decides which role is handed it, and so that a learned rule comes back in turn's part,
  for the caller to judge, rather than in the caller's own constraints. A CCS of 0.1.0 is not
  accepted, since writ, turn's one caller, is rebuilt on 0.2.0 and released with it (decided by the
  user, 2026-10-15).
- **The checklist form** the README's Requirements gives. Relied on by users and writ, who write
  checklists in it. Must keep holding: a checklist in that form is read into the list.
- **What a returned CCS points to**. Relied on by the user, who opens it to follow each item back.
  Must keep holding: every place a returned CCS points to exists. May change: where the run's
  evidence is kept, and the rest of it.

### Non-goals

- **Deciding what the work should say**: the caller does it, knowing what was already agreed, and
  gives it as the content.
- **Making the work from one already there**: the caller reads it and puts what it says into the
  content; turn makes new work only, since what it is handed it follows, wording and slips
  included.
- **Deciding whether to run again after a run's second round**: the caller does it from what the
  run returns, knowing what was agreed.
- **Finding what no item asks**, which goes into the checklist; and **holding checklists**, which
  belong to whoever knows the kind of work, such as writ.

### Constraints

- turn is used by Claude, on a person's behalf, in a conversation or a plugin's step.
- turn runs in Claude Code and holds only skills, agents, hooks and scripts; installing copies only
  its folder; its hooks run in every session where it is installed; a subagent can neither ask the
  user nor hear from its caller while it works.
- Users' machines run Python 3.9 or later with the standard library only, and jq.
- The work is in a git repository.
- Tests and builds a work needs run by shell commands, so the agents' shell stays open.

## Verification

Each check below shows one quality, so a failing check names the quality that broke. The flow of a
run, which role hands what to which and in what order, is tried apart from what the roles make, on
the smallest task that still shows it, such as a short note against a checklist of a few items, so
it neither spends the cost of real work nor fails where only a role's work falls short.

### Attractive quality

Each is judged from the records, and tried apart from the others. What the work gives its receiver
is tried on real work, writ's and turn's own documents and prompts, against the items in question,
since a made-up task shows only that it passes.

- **Read in the receiver's place**: tried on work for a receiver who lacks what the generator
  knows, where a writer checking their own work passes what a newcomer would miss (assumption). It
  passes when a fresh agent outside the run, reading the returned work as the same receiver, with
  the same files the receiver opens and the same list, takes every item returned as Good, including
  each an earlier run left without one. Its flow is tried on a task whose first round leaves one
  item with a way in the work, which calls for the second round, and one question open, which
  must wait for the end. It passes when one call reads the work twice and asks the question at its
  end.
- **Made from what the caller decided**: tried in a repository holding files the inputs do not
  name, which are there to be read by mistake. It passes when the records show no role reading one,
  and the work says nothing the inputs do not give. Tests on the hooks that hold it, each in the
  case that would break it: a read outside the run's inputs is stopped; a shell command of the
  orchestrator's that is not one of turn's scripts is stopped.
- **Asked only what only the user can decide, all at once at the end**: tried on content that
  settles some choices, which must not be asked, and leaves one open, which must be. It passes when
  nothing is asked while the run works, the run ends with `next` as `ask the user` and that one
  choice, and no question is answered by the inputs.
- **Seeing the work as it goes**: tried on the smallest task, which shows every step without the
  cost of real work; the run is stopped as the console shows its aim, the moment a user who does
  not want that aim would stop it, and called again on the task rewritten from what the user said,
  which shows the change of course carried through. It passes when the console alone tells the step
  the records show, the stopped run has written no work of that aim, and the run called again makes
  what the user said.
- **A plugin decides from what turn returns**: tried on runs that end in each value of `next`, so
  each move a plugin may make is decided once. It passes when the move decided from the returned
  CCS alone is the one decided after also reading the records.
- **Following each item back**: tried on a run that returns both an item with a Good and one
  without, so the run's evidence must give both. It passes when the evidence alone gives, for each
  item, the lines of its Good or its way to a Good, and the version of its checklist. A test on the
  script that reads checklists: a checklist without its name or version is refused.

### One-dimensional quality

Both are measured from the records of the same tasks, run on this version and on the version in
use from the same CCS, written in each version's kinds where they differ, as from 0.1.0 to 0.2.0,
and this version's measure is compared with that of the version in use.

- **The first-run share**: the share of those tasks whose first run returns every item Good.
- **Time and tokens**: the time and tokens of each run, from the call to the returned CCS.

### Must-be quality

Each is a test on the script or hook that holds it, in the case that would break it.

- **Nothing passes unshown**: grounds naming lines the work lacks.
- **What the caller gave unchanged**: a returned CCS whose caller's part differs from the one
  received.
- **Nothing unread**: a version of the work written after the first user last read it.
- **Repository untouched**: a write outside where the work goes and the run's evidence; a commit or
  a push in a run; a shell command in a run that changes another file, which must be named; a file
  where the work goes with changes git lacks; and each of these outside a run, with another
  session's run open, where nothing is blocked.
- **Stop and start over**: a run stopped at each step, and one cut off.
- **Missing tools**: each tool missing, in a run and outside one.

### Backward compatibility

For each released version from 0.2.0 on, a test calls turn as that version's callers did:

- **The call**: the call runs.
- **The CCS**: its CCS, a stopped one included, is accepted and carried on, and every `next`
  returned is one its callers know.
- **The checklist form**: its checklists give a list with every opening and item.
- **What a returned CCS points to**: every place a returned CCS points to exists.

## Architecture

### Principles

Each says what a change must keep, and the qualities it protects.

1. **The orchestrator alone decides, from the work itself.** For each item it reads the whole work
   for where the item is given; what agents and scripts hand back only shows it where to look
   first, since a Good on one part does not show what the whole gives. Protects: nothing passes
   unshown, read in the receiver's place.
2. **Every role looks only for Goods and aims at every item being Good.** None finds fault, and
   none is set to find something, since one set to find something finds it whether it is there or
   not (assumption). The script that finds coverage is the one place that looks for what may be
   wrong. Each role answers, as the orchestrator decides, in a form with one place per item, since
   the form, not the wording, holds it to its aim. Protects: nothing passes unshown, the first-run
   share.
3. **Every role works from the inputs it is handed alone.** Each prompt names them as the whole of
   what it reads, says in positive words to work from them, and gives why: so the work follows what
   the caller decided, without bias from what was not given. Each prompt sets as steps what its
   agent receives, hands back and must do in full, as instructions with their reasons, and leaves
   how it thinks within a step to it. Protects: made from what the caller decided, read in the
   receiver's place.
4. **A question for the user comes only from the roles given the content**: the orchestrator, the
   generator and the learner. The orchestrator decides each, showing where it is answered or leaving
   it open, and the run returns every open one at its end. The first user and the evaluator raise
   none, since without the content they cannot tell what only the user can decide, and a place for
   what they did not find would be a place for faults; what they did not take reaches the learner as
   an item without a Good. Protects: asked only what only the user can decide.
5. **turn asks nothing while it works**, so it runs the same wherever it is called, a subagent
   included, and is stopped or corrected only from where it was called. Protects: asked only what
   only the user can decide, a plugin decides from what turn returns.
6. **What must come out the same every time is done by a script or a hook.** A script does what a
   step asks, and refuses a step whose steps before it are not done; a hook sees, as Claude Code runs
   the run, that a step was not left out or done otherwise, and stops it saying which step, what it
   needs, and why. Protects: nothing passes unshown, what the caller gave unchanged, repository
   untouched, made from what the caller decided, following each item back.
7. **turn's hooks act only in the session whose run is open**, and do nothing elsewhere, even
   without python3, since they run in every session where turn is installed. Protects: repository
   untouched, missing tools.

### Structure

Who takes part, what each does, and what each cannot work without:

| Who | What it does | Cannot work without |
| --- | --- | --- |
| The user | Hands the work on; stops a run and says what they want instead | The console, to see the run and stop it |
| The caller | Says what the work should be, in a CCS; decides what follows a run | The callers' page's forms |
| The orchestrator, the skill `turn:up` | Runs the run and decides each item | The CCS; turn's scripts; Claude Code to start its agents |
| The generator | Makes the work to meet every item | What a script writes for it from the inputs; a shell for tests and builds |
| The first user | Takes from the work what the receiver would | The work and the files the receiver opens with it |
| The evaluator | Gives Goods with grounds | The reading and its records |
| The learner | Finds each way to a Good | The work, the items without a Good, the content and the references |
| turn's scripts | Do each step that must come out the same every time | python3 3.9 or later, and jq |
| turn's hooks | Keep each role to its steps and inputs, show the console, stop what would change the user's work | Claude Code to run them; a run open in their session |
| Claude Code | Runs the agents and hooks and keeps the records | Nothing of turn's |
| git | Holds what was where the work goes before turn writes over it | The work being in a git repository |

What passes between them, in order:

1. The caller hands the orchestrator the CCS.
2. A script checks the CCS and reads the checklists into the list.
3. The console shows the user the run's aim before the work is written.
4. The orchestrator hands the generator the receiver, the use, what the receiver must be able to
   do, the list, the content, the references, and the ways to a Good when there are any.
5. The generator hands back the work, its grounds and its questions; a script gives coverage. The
   work is sent back until every item is seen met or waits on a question left open.
6. The orchestrator hands the first user the work, what the receiver opens with it, the receiver,
   the use and the list; the first user hands back its reading.
7. The evaluator is handed the work, the reading, the list and what the receiver must be able to
   do; it reads the records of the reading and hands back Goods with grounds; a script gives
   coverage.
8. The orchestrator decides every item on its form.
9. The learner is handed the work, the items without a Good, the content and the references, and
   hands back ways to a Good, each with its items, and questions. Where a way lies in the work, the
   work is made again on those ways and read and decided once more, as the second round.
10. A script keeps the decisions, ways, questions and rules as the run's evidence and writes the new
    CCS; the orchestrator hands the caller the new CCS, and the console shows the user where the
    work is and every question left open.

Throughout a run, turn's hooks, run by Claude Code, keep each role to its steps and its inputs, show
the console, and stop what would change the user's work.

The orchestrator is a skill, so it runs where its caller runs and can start the agents there: in a
conversation, the user sees its console and presses Esc to stop it; in a subagent, which may start
agents of its own, the caller reads what it returns. The cost is room in the caller's context.

### The checklist as the measure

Achieves: read in the receiver's place, the first-run share, following each item back, the
checklist form.

A work that meets every item of its checklists serves its purpose (assumption, which the trials of
the attractive qualities test). Everything that measures the work, the orchestrator included, is
given the same list, with every opening, and the same receiver and use, so all measure alike.

Parts:

- A script, when a run starts, reads each checklist into the list, looking at what its opening says
  of itself, and refuses one that does not open with its name and version, since a checklist may be
  kept outside the repository, as a plugin's are, and only what it says of itself names the version
  a Good was judged by.

Must hold: nothing measures the work by anything but the list, the receiver and the use.

Weighed: letting the first user also report what it missed outside the items. Not chosen, since,
unbounded by an item, it becomes a search for faults that varies from run to run (assumption). The
cost: what no item asks is not found until the checklist changes.

### Working from the inputs alone

Achieves: made from what the caller decided, read in the receiver's place.

Parts:

- A script hands each role only the inputs it needs, as Structure lists them.
- A hook, before a file is read or searched in a run, looks at the file against the role's inputs,
  turn's own files and the run's evidence, and stops a read outside them, saying it is stopped so
  the work is made without bias from what was not given, and naming what the role may read.
- A hook, before a shell command of the orchestrator's, looks at whether it is one of turn's
  scripts, and stops any other, since the orchestrator needs no other.
- The agents' shell stays open, since tests and builds need it; what they read by it shows in the
  records.

Must hold: no role reads by Claude's file tools anything outside its inputs, turn's own files and
the run's evidence.

Weighed: telling the roles in words only. Not chosen, since in two trials on 2026-10-15 the
orchestrator read files not given, writ's design and turn's README in one, and turn's scripts in
the run making its callers' page in the other, and what it read shaped the work. The cost: a
file the work needs, left out of the CCS, cannot be read in the run rather than being found; the
caller names it and calls again.

### Making it right first

Achieves: the first-run share, time and tokens, asked only what only the user can decide.

What can be seen before the first user reads the work costs a whole run when found in its reading,
so the work reaches the first user only once nothing in it is left open.

Parts:

- The orchestrator, before the work is first written, reads each item against the inputs, and
  leaves open as a question what they do not settle.
- The generator makes a work that meets every item, and names on its form the lines that meet each;
  what the inputs do not settle it keeps out of the work and raises as a question, which the
  orchestrator leaves open unless the work or the inputs answer it.
- A script, when the generator hands back, looks at the lines its form names against the work, and
  prints its coverage.
- The orchestrator reads the whole work for each item from the lines named and the coverage, and
  sends the work back with each item it does not see met, saying how it would be.
- A script hands the first user nothing until every item is seen met or waits on a question left
  open.
- When the run returns, each question left open goes to the caller as a `question`, and `next` is
  `ask the user`.

Must hold: no work reaches the first user with an item the orchestrator does not see met, but one
that waits on a question left open; no run returns `done` with a question left open.

Weighed: a limit on sending back. Not chosen, since a work sent on unsettled costs a run. The cost:
a generator that never settles runs until the user stops it, and time and tokens show it.

Weighed: asking each question as it is seen. Not chosen; every question comes at the end, since a
subagent cannot ask the user, so only a run that asks nothing runs the same wherever it is called,
and the user can leave it at work. The cost: the caller puts each answer into the work or into the
content and calls again.

### Keeping each role to its steps

Achieves: nothing passes unshown, the first-run share.

Each role's steps are what make its answer usable, so a step left out or done otherwise is stopped
as it happens, rather than found later in an answer that looks right.

Parts:

- A script writes what each agent is handed, and refuses to while the steps before it are not done.
- A hook, before an agent of turn is called, looks at what the call hands it, and stops a call made
  with anything but what the script wrote for it.
- A hook, as an agent of the run stops, has a script look at its form, and keeps it at work until
  every place of the form is filled.
- A hook, as the orchestrator stops, looks at whether the run is open, and keeps it at work while
  it is; it says so once, so the orchestrator is never held in a loop.

Must hold: every answer the orchestrator decides from fills every place of its form.

### Reading in the receiver's place

Achieves: read in the receiver's place.

Parts:

- The first user reads the work with only what the receiver opens with it, which the caller names,
  so it stops where the receiver would (assumption). It is given the work, those files, the
  receiver, the use and the list, and nothing of how the work was made, its content or references,
  or what the receiver must be able to do. Its reading says, for each item, what it took and where.

Must hold: the first user reads nothing the receiver would not open.

Weighed: a fresh copy of the whole repository. Not chosen, since a receiver opens the work and what
it links, not every file, and the copy let the reader take from the sources what the work did not
give. The cost: the caller names what the receiver opens and checks it before calling.

Weighed: telling the first user what the receiver must be able to do. Not chosen, since it would
look for that rather than take what the work gives (assumption). The cost: only the evaluator and
the orchestrator weigh the reading against it.

### Deciding every item

Achieves: nothing passes unshown, read in the receiver's place, following each item back, what a
returned CCS points to.

Parts:

- The evaluator, after the first user's reading, gives a Good with grounds for each item the work
  meets, judged from the reading against what the receiver must be able to do, and looks at the
  records of the reading for the lines it took each item from. Its form has places for Goods only,
  since in a trial an evaluator told in words to write Goods only still wrote on other items.
- A script, when the evaluator hands back, prints the coverage of the Goods' grounds. A line no
  grounds name does nothing for the receiver or holds a slip, since every useful line meets some
  item (assumption).
- The orchestrator reads the whole work for each item, from the grounds and the coverage, and
  decides each on its form, naming the lines of each Good.
- A script keeps every form in the run's evidence, and the returned CCS points to the decisions,
  the ways to a Good and the list, so each item can be followed back.

Must hold: every Good names lines the work holds and is decided by the orchestrator; no run returns
before every item of every document is decided on its form.

Weighed: an agent set to look for slips, against the script that finds coverage. The script chosen,
since a script comes out the same every time. The cost: a slip in a line some grounds name is found
only by the orchestrator.

### Making again toward a Good

Achieves: read in the receiver's place, nothing unread.

A change made from the place a slip showed fixes that place and leaves the same shape elsewhere, so
a way to a Good is made from the purpose: what the whole work gives the receiver once the item is
met, every line the same shape reaches, and the change of shape taken at each of them.

Parts:

- The learner, after the orchestrator decides, gives that way for each item left without a Good,
  says whether it lies in the work, in what the caller gave, or in how such work is made, and
  groups the items one way serves. Where a way needs what only the user can decide, it raises a
  question, which the orchestrator leaves open unless the work or the inputs answer it.
- A script, when the learner hands back, looks at each way and refuses one said of lines rather
  than of the whole work.
- A script, when the first round leaves an item without a Good whose way lies in the work, starts
  the second round: the work is made again on those ways, from the work as it stands, and read and
  decided once more. A question the first round left open stays open into the second.
- When the run returns, each item still without a Good goes back as `unmet` with its way, and
  `next` is `ask the user`; a way in how such work is made goes back as a `rule` in turn's part,
  for the caller to judge; a way in what the caller gave goes back with `next` as `to the caller`.
  The caller decides what follows: finishing the work itself, calling turn again with changed
  inputs, which makes the work anew, or putting it to the user.

Must hold: a run has the work read and decided at most twice, and returns the version last read.

Weighed: no second round by default. Not chosen, since the first round is where the generator
first sees where the receiver stops, and in every run of writ's rebuild it left items whose way lay
in the work, so the caller called again without deciding
anything new. The cost: a run takes up to twice as long.

Weighed: no second round while a question or a way in what the caller gave is left. Not chosen,
since an answer or a change of the caller's touches a part of the work, and the rest made right
first leaves less to do after. The cost: a part the answer changes may be made twice.

Weighed: a third round. Not chosen, since the caller knows what was agreed and decides from what a
second round still leaves whether to fix the work, its inputs or a checklist, and each further
run raised finer points the purpose did not need (seen in three runs on one CSV tool's README,
2026-10-14). The cost: the caller reads what the run returns before deciding.

Weighed: adding each rule to the caller's `constraints`. Not chosen, since rules piled up over runs
and pushed into the work what the caller had not asked (eleven rules over the runs on writ's
README, 2026-10-15). The cost: a rule reaches later work only when the
caller takes it in.

### The console

Achieves: seeing the work as it goes.

The console serves a user who looks in now and then. It shows where the run is by step; the run's
aim before the work is written, so a wrong aim is stopped before a run is spent; what the work does
not yet give, said in plain words as what the receiver will be able to do once it does; and at the
end where the work is and what the user must decide. Item IDs and counts are not shown, since the
user would have to learn the checklist.

Parts:

- A script refuses the generator its brief until the run's aim is set.
- A hook, after each shell command of the run, shows the user the lines of the console not yet
  shown, which a script makes from the run's evidence, and the run's last lines once it ends or
  stops.

Must hold: no work is written whose aim the console has not shown first.

Weighed: the console as what the orchestrator writes between its tool calls. Not chosen, since that
does not reach the user on every run (seen in trials).

### The CCS

Achieves: a plugin decides from what turn returns, what the caller gave unchanged, stop and start
over, the call, the CCS.

The CCS (Compressed Cognitive State) takes the nine parts that ACC (Agent Cognitive Compressor,
https://arxiv.org/abs/2601.11653) sets as the state the next step needs. Each kind the caller
writes says what the input is for, so turn decides from it which role is handed it. Every change of
course the user makes by stopping a run goes through the caller as a new run, which starts from
nothing but its CCS and the files it names. Until a run returns, the work is only in the run's
evidence, so a stopped or cut-off run leaves where the work goes untouched. A run that returns keeps
the work it returned in its evidence, so a later run may write over it while it is unchanged.

Parts:

- A script checks the CCS when a run starts and when it returns, and writes the returned one with
  the caller's part as received.
- A script, when the user stops a run, writes a CCS saying where it stopped.

Must hold: the received CCS is never written over; the caller's part comes back the same.

Weighed: handing agents the CCS itself. Not chosen, since a change made for one agent would change
what callers rely on. The cost: the orchestrator's scripts write each agent's inputs from the CCS.

### Leaving the user's work alone

Achieves: repository untouched, missing tools.

Parts:

- The orchestrator, before any work, ends the run saying what to install if python3 is missing.
- A script, before any work, ends the run if jq is missing, or if a file where the work goes has
  changes git does not hold, unless it is the work a run returned, unchanged since, which that
  run's evidence keeps. Such a file is otherwise written over, since git or the evidence keeps the
  version before it.
- A hook, before a file is written or edited in a run, looks at where, and stops a write anywhere
  but where the work goes and the run's evidence.
- A hook, before a shell command in a run, stops a git commit or push.
- A script, when the run returns, names each file changed since the run started anywhere but where
  the work goes and the run's evidence, since what a shell command changes as a side effect, such as
  a file its tests leave, cannot be told before it runs.

Must hold: during a run, the only changes are where the work goes and the run's evidence, or they
are named to the user.

Weighed: checking afterwards rather than blocking. Not chosen wherever the change can be told
beforehand, since the harm is done by then. The cost: a check on each write, read and shell command.

Chosen: jq for the agents' changes to parts of the CCS, since agents know it. The cost: one more
tool to install.
