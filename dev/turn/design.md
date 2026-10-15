# turn design

This document is for whoever builds or changes turn. It says what turn must achieve, how each
quality is checked, and the approach by which turn brings about what its
[README](../../turn/README.md) promises: the way of thinking behind it, and who takes part, with
their roles and what they depend on. Read it to judge whether a change keeps the design before you
make it.

Its point: turn makes a work from what its caller gave and nothing else, has it read by an agent
that did not write it, in the place of the one it is for, and counts an item as met only where one
part, which alone decides, sees lines of the work that meet it.

It leaves out how to use turn, which is in the README; the forms a caller writes and reads, which
are on the callers' page, [Calling turn from a plugin's step](../../turn/calling-from-a-plugin.md);
and the wording and steps of the prompts and how each script and hook behaves, which are left to
the code. A statement no trial has checked yet is marked "(assumption)".

The words below are used in the sense given here throughout.

- **The caller**: Claude in the user's conversation, or a step of the user's plugin. It hands turn
  one task in a **CCS**, a JSON file, and turn writes back a CCS with what the caller needs next, as
  a function takes arguments and returns a value.
- **The inputs** of a run, what the caller gives: where the work goes; **the receiver**, whom the
  work is for; their **use** of it, when named; what they must be able to do with it; the
  checklists; **the content**, what the work says or does, item by item of the checklists; **the
  references**, files or folders the work follows or draws on; the rules the caller gives the work
  to keep; and what the receiver opens with the work.
- **A checklist** says what a work of one kind must give its receiver: an opening on what such work
  is for, then **items**, each one question. **The list** is a task's checklists put together.
- **A run** goes from one CCS to the one turn writes back: it makes the work, has it read, decides
  each item, and finds how each item without a Good would get one. **A round** is one making,
  reading and deciding of the work within a run.
- **The orchestrator** runs a run and alone decides each item, as the one reviewer who approves a
  pull request decides it whatever the checks around it report. Its four agents give it what it
  decides from: **the generator** makes the work; **the first user** reads it in the receiver's
  place, as a newcomer in a usability test is given only what a real user would have, and hands
  back its reading; **the evaluator** shows which items the work meets; **the learner** finds how an
  item without a Good would get one. **A role** is the orchestrator or one of its agents.
- **A Good** is an item the orchestrator has decided the work meets, with its **grounds**, the lines
  it rests on, as a test assertion names what it checks. An item without a Good when a run returns
  is called **More**. **A way to a Good** is how, and where, the work or what the caller gave would
  change for an item to get one.
- **A form** is the answer a role writes: a JSON file with one place per item, which the agents read
  and change with `jq`. What a role hands back is its form. **The reading** is the first user's
  form: what it took from the work for each item, and where.
- **Coverage** is the lines of the work no grounds name, as test coverage finds the lines no test
  runs.
- **The run's evidence** is what a run keeps in the repository for the user and for later runs: the
  work, its reading and decisions, each way to a Good, and the list with each checklist's name and
  version. Until a run returns, the work is there only.
- **The records** are the JSONL files Claude Code keeps of every conversation and agent of a run.
- **The console** is what turn shows the user as a run goes, as a build prints its progress,
  starting with the run's **aim**: what the work will let its receiver do.
- **The parts of a CCS** are the pieces of state it is divided into.
  **The caller's part** is what the caller wrote: entries, each of a **kind** that says what the
  input it gives is for, such as the content, a reference, or the rules the caller gives the work to
  keep. turn writes the rest. **`next`** is the part of a returned CCS that tells the caller what is
  left to it; its values, such as `done` and `ask the user`, and the names of every part and kind,
  are on the callers' page.
- **writ** is the plugin that calls turn and holds the checklists the work is measured by.
- **The version in use** is the released version of turn that users run now; each measure of this
  version is compared with it.

## Goals

The qualities are sorted, and named, as in the Kano model of customer satisfaction: an attractive
quality is one the user chooses the product for, a one-dimensional quality is better the more of it
there is, and a must-be quality is taken for granted and noticed only when it breaks.

### Attractive quality

The benefits, of those the README promises, that the design must bring the user:

- **Read in the receiver's place**: the work comes back already read in the receiver's place by an
  agent that did not write it, with only what the receiver would open, each Good shown in its lines,
  and what that reading could not take made again on how it would be given. The user hands the work
  on without first reading it as its receiver.
- **Made from what the caller decided**: the work says only what the run's inputs give, not
  whatever turn happened to open, and each run of the same task works from the same inputs.
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

- **The first-run share**: the tasks whose first run ends with every item Good. The more work is
  right when first made, the less the user waits and the less is spent.
- **Time and tokens**: what one run takes, from the call to the returned CCS.

### Must-be quality

- **Nothing passes unshown**: an item counts as met only with a Good whose grounds are lines the
  work holds; every other item is returned as More, with how it would get a Good.
- **What the caller gave unchanged**: turn never rewrites the caller's part of the CCS or the files
  it names.
- **Nothing unread**: the work turn writes where the work goes is the version last read.
- **Repository untouched**: during a run, turn changes nothing in the repository but where the work
  goes and the run's evidence, and never commits or pushes, so the user takes turn's change as one
  diff and decides themselves what to commit. A file where the work goes is written over only when
  git holds it as it stands, or when it is the work a run returned and is unchanged since, so what
  was there can be got back. A change that a shell command of the run makes elsewhere, as a side
  effect, is named to the user. Outside its runs, turn blocks nothing.
- **Stop and start over**: a stopped run returns a CCS saying so; called again with the task
  rewritten from what the user said, turn makes the work anew from it. A run cut off leaves where
  the work goes untouched.
- **Missing tools**: without python3 or jq, turn ends before any work and says what to install;
  outside a run, a missing tool breaks nothing.

### Backward compatibility

- **The call**. Relied on by plugins, which call the skill `turn:up` with the arguments the callers'
  page gives, and name `turn` in their dependencies. Must keep holding: such a call runs. May
  change: an argument may be added, only if a call without it runs as before.
- **The CCS**. Relied on by every caller. Must keep holding: its parts, kinds of entry and values of
  `next`, as the callers' page gives them, are neither added to, removed nor renamed from 0.2.0 on,
  since a caller breaks on one it does not know as on one that is gone; and a CCS that an earlier
  version from 0.2.0 on returned is accepted, so a stopped task carries on after an update. May
  change: the wording in an entry, since callers do not act on it. A CCS of 0.1.0 is not accepted,
  since writ, turn's one caller, is released with 0.2.0 (decided by the user, 2026-10-15).
- **The checklist form** the README's Requirements give. Relied on by users and writ, who write
  checklists in it. Must keep holding: a checklist that opens with its name and version and gives
  its items as headings with IDs keeps being read. May change: what turn takes from a checklist
  beyond that, as long as a checklist in that form needs nothing more.
- **What a returned CCS points to**. Relied on by the user, who opens it to follow each item back.
  Must keep holding: every place a returned CCS points to exists. May change: where the run's
  evidence is kept, and the rest of it.

### Non-goals

- Deciding what the work should say: the caller does it, knowing what was already agreed, and gives
  it as the content.
- Making the work from one already there: the caller reads it and puts what it says into the
  content. turn makes new work only, since it follows what it is handed, wording and slips included.
- Deciding whether to run again after a run's second round: the caller does it from what the run
  returns, knowing what was agreed.
- Finding what no item asks, which goes into the checklist; and holding checklists, which belong to
  whoever knows the kind of work, such as writ.

### Constraints

- turn is used by Claude, on a person's behalf, in a conversation or a plugin's step.
- turn runs in Claude Code and holds only skills, agents, hooks and scripts. Installing copies only
  its folder; its hooks run in every session where it is installed; a subagent can neither ask the
  user nor hear from its caller while it works.
- Users' machines run Python 3.9 or later with the standard library only, and jq.
- The work is in a git repository.
- The tests and builds a work needs run by shell commands, so the agents' shell stays open.

## Verification

### Attractive quality

Each benefit is judged from the records, and tried apart from the others, so a failing trial names
one benefit. What the work gives its receiver is tried on real work, writ's and turn's own documents
and prompts, against the items in question, since a made-up task shows only that it passes. The flow
of a run, which role hands what to which and in what order, is tried apart from the work, on the
smallest task that still shows it, such as a short note against a checklist of a few items, each
item there to make a round end as the check needs.

- **Read in the receiver's place**: tried on work for a receiver who lacks what the generator knows,
  since there a writer checking their own work passes what a newcomer would miss (assumption). It
  passes when a fresh agent outside the run, reading the returned work as the same receiver, with
  the same files it opens and the same list, takes every item returned as Good, including each one
  an earlier run returned as More. Its flow is tried on a task whose first round leaves one item
  with a way in the work, there to call for a second round, and one question open, there to be asked
  at the end; it passes when one call reads and decides the work twice and asks the question at its
  end.
- **Made from what the caller decided**: tried in a repository holding files the inputs do not name,
  there to be passed over. It passes when the records show no role reading one, and the work says
  nothing the inputs do not give.
- **Asked only what only the user can decide, all at once at the end**: tried on content that
  settles some choices, there to go unasked, and leaves one open, there to be asked. It passes when
  nothing is asked while the run works, the run ends with `next` as `ask the user` and that one
  choice, and no question asked is answered by the inputs.
- **Seeing the work as it goes**: tried on the smallest flow task, with one run whose aim the user
  does not want, there to be stopped on its aim, since only a console that shows the aim before the
  work is written lets the user stop it in time. It passes when the console alone tells the step the
  records show, and when the stopped run has written no work of that aim and, called again, makes
  what the user said.
- **A plugin decides from what turn returns**: tried on runs that end in each value of `next`. It
  passes when the move decided from the returned CCS alone is the one decided after also reading the
  records.
- **Following each item back**: tried on any run whose evidence holds one item with a Good and one
  More, there to show that each kind is followed back, since only kept evidence lets an item be
  followed back after the run. It passes when the run's evidence alone gives, for each, the lines of
  its Good or how it would get one, and the version of its checklist.

### One-dimensional quality

- **The first-run share** and **Time and tokens** are both measured from the records of the same
  tasks, run on this version and on the version in use from the same CCS, and compared between the
  two. Where the two versions' kinds of CCS entry differ, as from 0.1.0 to 0.2.0, the CCS is written
  in each version's kinds.

### Must-be quality

Each is a test on the script or hook that holds it, run in the case that would break it.

- **Nothing passes unshown**: grounds naming lines the work lacks.
- **What the caller gave unchanged**: a returned CCS whose caller's part differs from the one
  received.
- **Nothing unread**: a version of the work written after the last reading.
- **Repository untouched**: a write outside where the work goes and the run's evidence; a commit or
  a push in a run; a shell command in a run that changes another file; a file where the work goes
  with changes git lacks; and each of these outside a run, with another session's run open, where
  nothing may be blocked.
- **Stop and start over**: a run stopped at each step, and one cut off.
- **Missing tools**: each tool missing, in a run and outside one.

Two attractive qualities are also held by such tests, as must-be qualities are, since the case that
would break them can be made:

- **Made from what the caller decided**: a role reading a file outside the run's inputs; a shell
  command of the orchestrator's that is not turn's script.
- **Following each item back**: a checklist without its name or version.

### Backward compatibility

For each released version from 0.2.0 on, a test calls turn as its callers did, and passes when:

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
   first, since a Good on one part does not show what the whole gives. Protects: Nothing passes
   unshown, Read in the receiver's place.
2. **Every role looks only for Goods and aims at every item being Good**, the orchestrator included.
   None finds fault, and none is set to find something, since one set to find something finds it
   whether it is there or not (assumption); coverage, a script, is the one place that looks for what
   may be wrong. Each role answers in a form with one place per item, as the orchestrator decides,
   since the form, not the wording, holds it to its aim. Protects: Nothing passes unshown, the
   first-run share.
3. **Every role works from the inputs it is handed alone.** Each prompt names them as the whole of
   what it reads, says in positive words to work from them, and gives why: so the work follows what
   the caller decided, without bias from what was not given. Each prompt sets as steps what its
   agent receives, hands back and must do in full, as instructions with their reasons, and leaves
   how it thinks within a step to it. Protects: Made from what the caller decided, Read in the
   receiver's place.
4. **A question for the user comes only from the roles given the content**: the orchestrator, the
   generator and the learner. The orchestrator decides each, showing where it is answered or leaving
   it open, and the run returns every open one at its end. The first user and the evaluator raise
   none, since without the content they cannot tell what only the user can decide, and a place for
   what they did not find would be a place for faults; what they did not take reaches the learner as
   an item without a Good. Protects: Asked only what only the user can decide.
5. **turn asks nothing while it works**, since only a run that asks nothing runs the same wherever
   it is called, a subagent included; it is stopped or corrected only from where it was called.
   Protects: Asked only what only the user can decide, A plugin decides from what turn returns.
6. **What must come out the same every time is done by a script or a hook.** A script does what a
   step asks, and refuses a step whose steps before it are not done; a hook sees, as Claude Code
   runs the run, that a step was not left out or done otherwise, and stops it, as a check before a
   commit refuses the commit, saying which step, what it needs, and why. Protects: Nothing passes
   unshown, What the caller gave unchanged, Repository untouched, Made from what the caller
   decided, Following each item back.
7. **turn's hooks act only in the session whose run is open**, and do nothing elsewhere, even
   without python3, since they run in every session where turn is installed. Protects: Repository
   untouched, Missing tools.

### Structure

Who takes part, what each does, and what each cannot work without:

| Who | What it does | Cannot work without |
| --- | --- | --- |
| The user | Hands the work on to its receiver; watches the console and may stop a run | — |
| The caller | Says what the work should be | The callers' page's form |
| The orchestrator, the skill `turn:up` | Runs the run and decides each item | The CCS, turn's scripts, and Claude Code to start its agents |
| The generator | Makes the work to meet every item, and names where | The inputs a script hands it, and a shell for tests and builds |
| The first user | Takes from the work what the receiver would | The work and what the receiver opens with it |
| The evaluator | Gives Goods with grounds | The reading and its records |
| The learner | Finds how each item without a Good would get one | The work, the items without a Good, the content and the references |
| turn's scripts, on python3 and jq | Do what must come out the same every time | python3 3.9 or later, and jq |
| turn's hooks | Keep each role to its steps and its inputs, show the console, and stop what would change the user's work | Claude Code to run them, and a run open in their session |
| Claude Code | Runs the agents and hooks, and keeps the records | — |
| git | Holds the user's files as they stood, so what turn writes over can be got back | The work being in a git repository |

What passes between them:

| Between | What is handed | What comes back |
| --- | --- | --- |
| The caller and the orchestrator | The CCS | A new CCS, with the questions left open and the ways that lie in what the caller gave |
| The orchestrator and the generator | The receiver, the use, what the receiver must be able to do, the list, the content, the references, and the ways to a Good when there are any | The work, its form and its questions |
| The orchestrator and the first user | The work, what the receiver opens with it, the receiver, the use and the list | The reading |
| The orchestrator and the evaluator | The work, the reading and its records, the list, and what the receiver must be able to do | Goods with grounds |
| The orchestrator and the learner | The work, the items without a Good, the content, the references and the records | Ways to a Good, and questions |
| turn's scripts and the orchestrator | Each form | Coverage, and each role's inputs |
| turn's scripts and the user | — | The console: the aim, where the run is, and at the end where the work is and the questions left open |

The orchestrator is a skill, so it runs where its caller runs and can start the agents there: in a
conversation, the user sees its console and presses Esc to stop it; in a subagent, which may start
agents of its own, the caller reads what it returns. The cost is room in the caller's context.

### The checklist as the measure

- **Brings about**: Read in the receiver's place, Following each item back (Attractive quality); the
  first-run share (One-dimensional quality); The checklist form (Backward compatibility).
- **Idea**: a work that meets every item of its checklists serves its purpose (assumption, which the
  attractive-quality trials test). So everything that measures the work, the orchestrator included,
  measures by the same list, with every opening, and by the same receiver and use, and so all
  measure alike, as everyone who checks a piece of code runs the same test suite. A checklist says
  its own name and version, so a Good can be followed back to the text it was judged by, wherever
  the checklist is kept.
- **Who takes part**: the caller, who names the checklists; turn's scripts, which read them into the
  list; every role.
- **Must hold**: nothing measures the work by anything but the list, the receiver and the use.
- **Weighed**: letting the first user also report what it missed outside the items. Not chosen,
  since, unbounded by an item, it becomes a search for faults that varies from run to run
  (assumption). The cost of the choice: what no item asks is not found until the checklist changes.

### Working from the inputs alone

- **Brings about**: Made from what the caller decided, Read in the receiver's place (Attractive
  quality).
- **Idea**: principle 3 is held by turn, not left to each role's word: a script hands each role only
  the inputs it needs, and a hook stops a read of anything else.
- **Who takes part**: turn's scripts, which hand each role its inputs; turn's hooks, which hold each
  role to them and the orchestrator to turn's own commands. The agents' shell stays open, since
  tests and builds need it, and what they read by it shows in the records.
- **Must hold**: no role reads, by Claude's file tools, anything outside its inputs, turn's own files
  and the output of its own commands.
- **Weighed**: telling the roles in words only. Not chosen, since in two trials on 2026-10-15 the
  orchestrator read files it was not given, and what it read shaped the work. The cost of the
  choice: a file the work needs, left out of the CCS, cannot be read in the run; the caller names it
  and calls again.

### Making it right first

- **Brings about**: Asked only what only the user can decide, all at once at the end (Attractive
  quality); the first-run share, Time and tokens (One-dimensional quality).
- **Idea**: what can be seen before the reading costs a whole run when it is found in the reading,
  as a type check run before a long test suite catches in seconds what the suite finds only at its
  end. So the work goes to the first user only once the orchestrator sees every item met or waiting
  on a question left open, and what the inputs do not settle is kept out of the work for a question,
  which keeps Asked only what only the user can decide.
- **Who takes part**: the orchestrator, which reads each item against the inputs before the work is
  written, and reads the whole work when it comes back; the generator, which makes the work to meet
  every item and names where; turn's scripts, which give coverage and hold the work back from the
  first user until then.
- **Must hold**: no work reaches the first user with an item the orchestrator does not see met,
  unless it waits on a question left open; no run returns `done` with a question left open.
- **Weighed**: a limit on sending the work back to the generator. Not chosen, since a work sent on
  unsettled costs a run. The cost of the choice: a generator that never settles runs until the user
  stops it, and Time and tokens show it.
- **Weighed**: asking each question as it is seen. Not chosen, since a subagent cannot ask the user
  (Constraints), and principle 5 holds for that reason. The cost of the choice: the caller puts
  each answer into the content and calls again.

### Keeping each role to its steps

- **Brings about**: Nothing passes unshown (Must-be quality); the first-run share (One-dimensional
  quality).
- **Idea**: principle 6 applied to each role's steps: those steps are what make its answer usable,
  so a step left out or done otherwise is stopped as it happens, not found later in an answer that
  looks right.
- **Who takes part**: turn's scripts and hooks, each as principle 6 sets; each agent and the
  orchestrator, held to their steps.
- **Must hold**: every answer the orchestrator decides from fills every place of its form.
- **Weighed**: telling each role its steps in words only. Not chosen, since a step left out still
  gives an answer that looks right, as when a generator named lines for an item the work left out
  (one flow trial, 2026-10-15). The cost of the choice: a check on each call and each hand-back, and
  a stop the role must act on.

### Reading in the receiver's place

- **Brings about**: Read in the receiver's place (Attractive quality).
- **Idea**: the first user reads the work with only what the receiver opens with it, so it stops
  where the receiver would (assumption), and takes from the work only what the work gives.
- **Who takes part**: the caller, who names what the receiver opens; the first user, given the work,
  those files, the receiver, the use and the list, and nothing of how the work was made, its content
  or references, or what the receiver must be able to do.
- **Must hold**: the first user reads nothing the receiver would not open.
- **Weighed**: a fresh copy of the whole repository. Not chosen, since a receiver opens the work and
  what it links, not every file, and the copy let the reader take from the sources what the work did
  not give. The cost of the choice: the caller names what the receiver opens, and checks it before
  calling.
- **Weighed**: telling the first user what the receiver must be able to do. Not chosen, since it
  would look for that rather than take what the work gives (assumption). The cost of the choice:
  only the evaluator and the orchestrator weigh the reading against it.

### Deciding every item

- **Brings about**: Read in the receiver's place, Following each item back (Attractive quality);
  Nothing passes unshown (Must-be quality); What a returned CCS points to (Backward compatibility).
- **Idea**: the evaluator shows, for each item the work meets, the lines and why, judged from the
  reading; coverage shows the lines no Good names, since every useful line meets some item
  (assumption); the orchestrator alone decides each item from the whole work, and every decision is
  kept, so each item can be followed back from the returned CCS, which points to them.
- **Who takes part**: the evaluator, turn's scripts, the orchestrator.
- **Must hold**: every Good names lines the work holds and is decided by the orchestrator; no run
  returns before every item is decided; every place a returned CCS points to exists.
- **Weighed**: an agent set to look for slips. Not chosen, since one set to find something finds it
  whether it is there or not, and a script comes out the same every time. The cost of the choice: a
  slip in a line some Good names is found only by the orchestrator.

### Making again toward a Good

- **Brings about**: Read in the receiver's place (Attractive quality); Nothing unread (Must-be
  quality).
- **Idea**: a change made from the place a slip showed fixes that place and leaves the same shape
  elsewhere, as fixing a bug's symptom leaves its cause to show again. So a way to a Good is made
  from the purpose, as a fix is made at the cause: what the whole work gives once the item is met,
  every line the same shape reaches, and the change taken at each. A way in the work is taken
  in a second round within the same call; a way in what the caller gave, or in how such work is
  made, goes back to the caller, who decides what follows.
- **Who takes part**: the learner, which finds each way and where it lies; the generator, which takes
  the ways in the work; the caller.
- **Must hold**: a run has the work read and decided at most twice; Nothing unread (Must-be
  quality).
- **Weighed**: no second round by default. Not chosen, since the first round is where the generator
  first sees where the receiver stops, and in every run made while writ was being rebuilt it left
  ways in the work. The cost of the choice: a run takes up to twice as long.
- **Weighed**: a third round. Not chosen, since the caller knows what was agreed and decides from
  what a second round leaves, and further rounds raised finer points the purpose did not need (three
  runs on a CSV tool's README, 2026-10-14). The cost of the choice: the caller reads what the run
  returns before deciding.
- **Weighed**: adding each rule learned to the rules the caller gives the work to keep. Not chosen,
  since rules piled up over runs and pushed into the work what the caller had not asked (eleven
  rules on writ's README, 2026-10-15). The cost of the choice: a rule reaches later work only when
  the caller takes it in.

### The console

- **Brings about**: Seeing the work as it goes (Attractive quality).
- **Idea**: the console serves a user who looks in now and then. It shows where the run is; what the
  work will let its receiver do, before the work is written, so a wrong aim is stopped before a run
  is spent; what the work does not yet give, in plain words; and at the end, where the work is and
  what the user must decide. It shows no item IDs or counts, since the user would have to learn the
  checklist to read them.
- **Who takes part**: the orchestrator, which writes the aim; turn's scripts and hooks, which make
  and show the console.
- **Must hold**: no work is written whose aim the console has not shown first.
- **Weighed**: the orchestrator telling the user where it is in its own words. Not chosen, since
  what it writes between its tool calls did not reach the user on every run (seen in trials; how
  many was not kept). The cost of the choice: the console says only what its script makes of the
  run's evidence.

### The CCS

- **Brings about**: A plugin decides from what turn returns (Attractive quality); What the caller
  gave unchanged, Stop and start over (Must-be quality); The call, The CCS (Backward compatibility).
- **Idea**: the CCS (Compressed Cognitive State) is divided, after ACC (the Agent Cognitive
  Compressor, https://arxiv.org/abs/2601.11653), into the pieces of state the next step needs, so
  whoever reads it next, the caller or a new run, needs nothing beside it. turn decides from each
  entry's kind which role is handed its input. Every change of course goes through the caller as a
  new run, which starts from its CCS alone.
- **Who takes part**: the caller, the orchestrator, turn's scripts.
- **Must hold**: What the caller gave unchanged (Must-be quality); and the received CCS itself is
  never written over.
- **Weighed**: handing the agents the CCS itself. Not chosen, since a change made for one agent would
  change what callers rely on. The cost of the choice: turn's scripts write each agent's inputs from
  the CCS.

### Leaving the user's work alone

- **Brings about**: Repository untouched, Missing tools (Must-be quality).
- **Idea**: Repository untouched is kept by stopping each change before it happens wherever it can
  be told then, and naming the rest when the run returns; Missing tools, by looking for each tool
  before any work.
- **Who takes part**: turn's scripts and hooks, git.
- **Must hold**: Repository untouched and Missing tools (Must-be quality).
- **Weighed**: checking afterwards only. Not chosen, since the harm is done by then. The cost of the
  choice: a check on each write, read and shell command.
- **Weighed**: python3 alone for the agents' changes to the forms. Not chosen, since agents already
  know jq. The cost of the choice: one more tool to install.
