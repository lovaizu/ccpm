# What dev/turn/design.md says

## doc

### B-1: What it covers
- For whoever builds or changes turn: what turn must achieve, how each quality is checked, and how
  turn is built to achieve it, for the benefits turn's README (`../../turn/README.md`) promises.
- How to use turn is in that README; the forms a caller writes and reads are on the callers' page,
  "Calling turn from a plugin's step" (`../../turn/calling-from-a-plugin.md`); prompts' wording and
  steps are left to the code.
- A statement no trial has checked yet is marked "(assumption)".

### B-12: Every term known
- The caller: Claude in the user's conversation, or a step of the user's plugin. It hands turn one
  task in a CCS, a JSON file, and turn writes back what the caller needs next, as a function takes
  arguments and returns a value.
- What the caller gives: where the work goes; the receiver it is for; their use of it, when named;
  what they must be able to do with it; the checklists; the content, what the work says or does item
  by item of the checklists; the references, files or folders the work follows or draws on; and
  what the receiver opens with the work. These are the run's inputs.
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
- Coverage: the lines of the work no grounds name, as test coverage finds the lines no test runs.
- The run's evidence: what a run keeps in the repository for the user and later runs: the work, its
  reading and decisions, each way to a Good, and the list with each checklist's name and version.
  The work stays there until the run returns.

## design

### B-1: Attractive quality
- Read in the receiver's place: the work comes back already read in the receiver's place by an agent
  that did not write it, with only what the receiver would open, each Good shown in its lines, and
  what that reading could not take made again on how it would be given. The user hands the work on
  without first reading it as its receiver.
- Made from what the caller decided: turn makes the work from the run's inputs alone, so the work
  follows what the caller decided rather than whatever turn happened to open, and each run of the
  same task works from the same inputs.
- Asked only what only the user can decide, all at once at the end: nothing is asked that the
  inputs already answer, and nothing is asked while the run works, so the user can leave turn at
  work.
- Seeing the work as it goes: the user can tell from the console how far a run has come, and stop a
  run whose aim they do not want before the work is written, saying what they want instead.
- A plugin decides from what turn returns: a plugin hands turn one task and decides from the
  returned CCS alone whether to finish the work itself, call turn again, ask the user or move on.
- Following each item back: the user can later find, for each item, the lines its Good rests on or
  how it would get one, and the version of the checklist it was judged by.

### B-2: One-dimensional quality
- Each must be no worse than in the version in use.
- The first-run share: tasks whose first run ends with every item Good. The more work is right when
  first made, the less the user waits and the less is spent.
- Time and tokens: what one run takes, from the call to the returned CCS.

### B-3: Must-be quality
- Nothing passes unshown: an item counts as met only with a Good whose grounds are lines the work
  holds; every other item is returned as unmet, with how it would get a Good.
- What the caller gave unchanged: turn never rewrites the caller's parts of the CCS or the files they
  name.
- Nothing unread: the work turn writes where the work goes is the version last read.
- Repository untouched: during a run, turn changes nothing in the repository but where the work goes
  and the run's evidence, and never commits or pushes, so the user takes turn's change as one diff
  and decides themselves what to commit. A file where the work goes is written over only when git
  holds it as it stands, or it is the work a run returned and is unchanged since, so what was there
  can be got back. A change a shell command of the run makes elsewhere as a side effect is named to
  the user. Outside its runs, turn blocks nothing.
- Stop and start over: a stopped run returns a CCS saying so; called again with the task rewritten
  from what the user said, turn makes the work anew from it. A run cut off leaves where the work goes
  untouched.
- Missing tools: without python3 or jq, turn ends before any work and says what to install; outside
  a run, a missing tool breaks nothing.

### B-4: Backward compatibility
- The call: plugins call the skill `turn:up` with the arguments the callers' page gives, and name
  `turn` in their dependencies. An argument may be added only if a call without it runs as before.
- The CCS: its parts, kinds of entry and values of `next`, as the callers' page gives them. In
  0.2.0 the kinds change to say what each input is for: `viewpoint` becomes `checklist`; `source`
  becomes `content` and `reference`; `receiver_opens` is added; `answer` goes into the content;
  `difference` becomes `question` and `unmet`; a learned `rule` comes back in turn's part rather than
  in the caller's `constraints`. A CCS of 0.1.0 is not accepted, since writ, turn's one caller, is
  rebuilt on 0.2.0 and released with it (decided by the user, 2026-10-15). From 0.2.0 on, the kinds
  and values are neither added to, removed nor renamed, since a caller breaks on one it does not
  know as on one that is gone; the wording in an entry may change, since callers do not act on it.
  A CCS an earlier version from 0.2.0 on returned is accepted, so a stopped task carries on after an
  update.
- The checklist form the README's Requirements gives, since users and writ write checklists in it.
- What a returned CCS points to: the user opens it to follow each item back, so every place a
  returned CCS points to exists; where the run's evidence is kept, and the rest of it, may change.

### B-5: Non-goals
- Deciding what the work should say: the caller does it, knowing what was already agreed, and gives
  it as the content.
- Making the work from one already there: the caller reads it and puts what it says into the
  content; turn makes new work only, since what it is handed it follows, wording and slips included.
- Deciding whether to run again after a run's second reading: the caller does it from what the run
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
- Tests and builds a work needs run by shell commands, so the agents' shell stays open.

### B-7: Attractive quality checked
- Each is judged from the records, the JSONL of every conversation and agent of the run, and tried
  apart from the others. What the work gives its receiver is tried on real work, writ's and turn's
  own documents and prompts, against the items in question, since a made-up task shows only that it
  passes; the flow of a run is tried on the smallest task that still shows it, such as a short note
  against a checklist of a few items.
- Read in the receiver's place: tried on work for a receiver who lacks what the generator knows,
  where a writer checking their own work passes what a newcomer would miss (assumption). It passes
  when a fresh agent outside the run, reading the returned work as the same receiver with the same
  files it opens and the same list, takes every item returned as Good, including each an earlier
  run left without one. Its flow passes when, on a task whose first reading leaves an item with a way
  in the work and a question open, one call reads the work twice and asks the question at its end.
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
- Both are measured from the records of the same tasks, run from the same CCS on this version and on
  the version in use.

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
- The orchestrator is a skill, so it runs where its caller runs and can start the agents there: in a
  conversation, the user sees its console and presses Esc; in a subagent, which may start agents of
  its own, the caller reads what it returns. The cost is room in the caller's context.

### B-25: What passes between them
- In order: the caller hands the orchestrator the CCS; a script checks it and reads the checklists
  into the list; the console shows the user the aim before the work is written; the orchestrator
  hands the generator the receiver, use, acceptance, list, content, references and the ways to a
  Good when there are any; the generator hands back the work, grounds and questions; a script gives
  coverage; the work is sent back until every item is seen met or waits on a question left open;
  the orchestrator hands the first user the work, what the receiver opens with it, the receiver, the
  use and the list; the first user hands back what it took and where; the evaluator is handed the
  work, the reading, the list and the acceptance, reads the records of the reading, and hands back
  Goods with grounds; a script gives coverage; the orchestrator decides every item on its form; the
  learner is handed the work, the items without a Good, the content and the references, and hands
  back ways to a Good, each with its items, and questions; a script keeps the decisions, ways,
  questions and rules as the run's evidence and writes the new CCS; the orchestrator hands the
  caller the new CCS, and the console shows the user where the work is and every question left open.
- During a run, turn's hooks, run by Claude Code, keep each role to its steps and its inputs, show
  the console, and stop what would change the user's work.

### B-13: An approach for each quality
- The checklist as the measure. Achieves: read in the receiver's place, the first-run share,
  following each item back, the checklist form. A work that meets every item of its checklists
  serves its purpose (assumption, which the attractive-quality trials test). Everything that
  measures the work, the orchestrator included, is given the same list, with every opening, and the
  same receiver and use, so all measure alike. When a run starts, a script reads each checklist into
  the list and refuses one that does not open with its name and version, since a checklist may be
  kept outside the repository, as a plugin's are, and only what it says of itself names the version
  a Good was judged by. Must hold: nothing measures the work by anything but the list, the receiver
  and the use. Weighed: letting the first user also report what it missed outside the items; not
  chosen, since unbounded by an item it becomes a search for faults that varies from run to run
  (assumption); the cost: what no item asks is not found until the checklist changes.
- Working from the inputs alone. Achieves: made from what the caller decided, read in the receiver's
  place. Each role is handed only the inputs it needs, by a script, as named under What passes
  between them. A hook, before a file is read or searched in a run, stops a read outside the role's
  inputs, turn's own files and the run's evidence, saying it is stopped so the work is made without
  bias from what was not given, and naming what the role may read. A hook stops a shell command of
  the orchestrator's that is not one of turn's scripts, since the orchestrator needs no other. The
  agents' shell stays open, since tests and builds need it; what they read by it shows in the
  records. Must hold: no role reads by Claude's file tools anything outside its inputs, turn's own
  files and the run's evidence. Weighed: telling the roles in words only; not chosen, since in
  trials the orchestrator read files not given (writ's design and turn's README, 2026-10-15, and
  turn's scripts on its callers' page, 2026-10-15), and what it read shaped the work. The cost: a
  file the work needs, left out of the CCS, stops the run's reading rather than being found; the
  caller names it and calls again.
- Making it right first. Achieves: the first-run share, time and tokens, asked only what only the
  user can decide. What can be seen before the reading costs a whole run when found in it, so the
  work reaches the first user only once nothing in it is left open. Before the work is first
  written, the orchestrator reads each item against the inputs, and leaves open as a question what
  they do not settle. The generator makes a work that meets every item, and names on its form the
  lines that meet each; what the inputs do not settle it keeps out of the work and raises as a
  question, which the orchestrator leaves open unless the work or the inputs answer it. When the
  generator hands back, a script prints its coverage, and the orchestrator reads the whole work for
  each item from the lines named and coverage, and sends the work back with each item it does not
  see met, saying how it would be. A script hands the first user nothing until every item is seen
  met or waits on a question left open. When the run returns, each question left open goes to the
  caller as a `question`, and `next` is `ask the user`. Must hold: no work reaches the first user
  with an item the orchestrator does not see met, but one that waits on a question left open; no run
  returns `done` with a question left open. Weighed: sending back has no limit, since a work sent on
  unsettled costs a run; the cost: a generator that never settles runs until the user stops it, and
  time and tokens show it. Weighed: every question at the end, not each as it is seen, since a
  subagent cannot ask the user, so only a run that asks nothing runs the same wherever it is called,
  and the user can leave it at work; the cost: the caller puts each answer into the work or into the
  content and calls again.
- Keeping each role to its steps. Achieves: nothing passes unshown, the first-run share. Each role's
  steps are what make its answer usable, so a step left out or done otherwise is stopped as it
  happens, not found later in an answer that looks right. A script writes what each agent is handed,
  and refuses to while the steps before it are not done. A hook, before an agent of turn is called,
  stops a call made with anything but what the script wrote for it. A hook, as an agent of the run
  stops, keeps it at work until a script sees every place of its form filled. A hook, as the
  orchestrator stops, keeps it at work while the run is open; it says so once, so the orchestrator
  is never held in a loop. Must hold: every answer the orchestrator decides from fills every place of
  its form.
- Reading in the receiver's place. Achieves: read in the receiver's place. The first user reads the
  work with only what the receiver opens with it, which the caller names, so it stops where the
  receiver would (assumption). It is given the work, those files, the receiver, the use and the
  list, and nothing of how the work was made, its content or references, or what the receiver must
  be able to do. Its reading says, for each item, what it took and where. Must hold: the first user
  reads nothing the receiver would not open. Weighed: a fresh copy of the whole repository; not
  chosen, since a receiver opens the work and what it links, not every file, and the copy let the
  reader take from the sources what the work did not give; the cost: the caller names what the
  receiver opens and checks it before calling. Weighed: telling it what the receiver must be able to
  do; not chosen, since it would look for that rather than take what the work gives (assumption);
  the cost: only the evaluator and the orchestrator weigh the reading against it.
- Deciding every item. Achieves: nothing passes unshown, read in the receiver's place, following
  each item back. The evaluator gives a Good with grounds for each item the work meets, judged from
  the reading against what the receiver must be able to do, and reads the records for the lines the
  reading took each item from. Its form has places for Goods only, since in a trial an evaluator
  told in words to write Goods only still wrote on other items. A script prints the coverage of the
  Goods' grounds; a line no grounds name does nothing for the receiver or holds a slip, since every
  useful line meets some item (assumption). The orchestrator reads the whole work for each item,
  from the grounds and coverage, and decides each on its form, naming the lines of each Good. A
  script keeps every form in the run's evidence, and the returned CCS points to the decisions, the
  ways to a Good and the list, so each item can be followed back. Must hold: every Good names lines
  the work holds and is decided by the orchestrator; no run returns before every item of every
  document is decided on its form. Weighed: coverage over an agent set to look for slips, since a
  script comes out the same every time; the cost: a slip in a line some grounds name is found only
  by the orchestrator.
- Making again toward a Good. Achieves: read in the receiver's place, nothing unread. A change made
  from the place a slip showed fixes that place and leaves the same shape elsewhere, so a way to a
  Good is made from the purpose: what the whole work gives the receiver once the item is met, every
  line the same shape reaches, and the change of shape taken at each of them. The learner gives, for
  each item left without a Good, that way, and says whether it lies in the work, in what the caller
  gave, or in how such work is made; it groups the items one way serves. A script refuses a way said
  of lines rather than of the whole work. Where a way needs what only the user can decide, the
  learner raises a question, which the orchestrator leaves open unless the work or the inputs answer
  it. When the first reading leaves an item without a Good whose way lies in the work, a script
  starts the run's second reading: the work is made again on those ways, from the work as it
  stands, and read and decided once more. A question the first reading left open stays open into the
  second. Each item still without a Good is returned as `unmet` with its way, and `next` is `ask the
  user`; a way in how such work is made is returned as a `rule` in turn's part, for the caller to
  judge; one in what the caller gave goes back to the caller with `to the caller`. The caller
  decides what follows: finishing the work itself, calling turn again with changed inputs, which
  makes the work anew, or putting it to the user. Must hold: a run has the work read and decided at
  most twice, and returns the version last read. Weighed: a second reading by default, since the
  first reading is where the generator first sees where the receiver stops, and in every run of
  writ's rebuild it left items whose way lay in the work, so the caller called again without
  deciding anything new; the cost: a run takes up to twice as long. Weighed: a second reading even
  with a question or a way in what the caller gave left, since an answer or a change of the caller's
  touches a part of the work, and the rest made right first leaves less to do after; the cost: a
  part the answer changes may be made twice. Weighed: no third reading, since the caller knows what
  was agreed and decides from what a second reading still leaves whether to fix the work, its inputs
  or a checklist, and each further run raised finer points the purpose did not need (seen in three
  runs on a CSV tool's README, 2026-10-14); the cost: the caller reads what the run returns before
  deciding. Weighed: adding each rule to the caller's `constraints`; not chosen, since rules piled up
  over runs and pushed into the work what the caller had not asked (eleven on writ's README,
  2026-10-15); the cost: a rule reaches later work only when the caller takes it in.
- The console. Achieves: seeing the work as it goes. The console serves a user who looks in now and
  then: it shows where the run is by step, what the work will let its receiver do before it is
  written, so a wrong aim is stopped before a run is spent, what the work does not yet give, said as
  what the receiver will be able to do once it does, in plain words, and at the end where the work
  is and what the user must decide. Item IDs and counts are not shown, since the user would have to
  learn the checklist. A script refuses the generator its brief until the run's aim is set. A hook,
  after each shell command of the run, shows the user the lines of the console not yet shown, made
  by a script from the run's evidence, and the run's last lines once it ends or stops. What the
  orchestrator writes between its tool calls does not reach the user on every run (seen in trials),
  so the console does not rest on it. Must hold: no work is written whose aim the console has not
  shown first.
- The CCS. Achieves: a plugin decides from what turn returns, what the caller gave unchanged, stop
  and start over, the call, the CCS. The CCS (Compressed Cognitive State) takes the nine parts that
  ACC (Agent Cognitive Compressor, https://arxiv.org/abs/2601.11653) sets as the state the next step
  needs. Each kind the caller writes says what the input is for, so turn decides from it which role
  is handed it. Every change of course the user makes by stopping a run goes through the caller as
  a new run, which starts from nothing but its CCS and the files it names. A script checks the CCS
  when a run starts and when it returns, and writes the returned one with the caller's part as
  received. Until a run returns, the work is only in the run's evidence, so a stopped or cut-off run
  leaves where the work goes untouched. When the user stops a run, a script writes a CCS saying
  where it stopped. A run that returns keeps the work it returned in its evidence, so a later run
  may write over it while it is unchanged. Must hold: the received CCS is never written over; the
  caller's part comes back the same. Weighed: handing agents the CCS itself; not chosen, since a
  change made for one agent would change what callers rely on; the cost: the orchestrator's scripts
  write each agent's inputs from the CCS.
- Leaving the user's work alone. Achieves: repository untouched, missing tools. Before any work, the
  orchestrator ends the run saying what to install if python3 is missing, and a script, if jq is
  missing or a file where the work goes has changes git does not hold, unless it is the work a run
  returned, unchanged since, which that run's evidence keeps. Such a file is otherwise written
  over, since git or the evidence keeps the version before it. A hook, before a file is written or
  edited in a run, stops a write anywhere but where the work goes and the run's evidence. A hook,
  before a shell command in a run, stops a git commit or push. What a shell command changes as a side
  effect, such as a file its tests leave, cannot be told before it runs, so a script, when the run
  returns, names each file changed since the run started anywhere but where the work goes and the
  run's evidence. Must hold: during a run, the only changes are where the work goes and the run's
  evidence, or they are named to the user. Weighed: blocking, not checking afterwards, wherever the
  change can be told beforehand, since the harm is done by then; the cost: a check on each write,
  read and shell command. jq for the agents' changes to parts of the CCS, since agents know it; the
  cost: one more tool to install.
