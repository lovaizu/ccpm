# What turn's design says

## Concept, agreed with the user (2026-10-23)

- User: the AI that runs a step of a plugin and calls turn from it.
- Purpose: the work comes back meeting every item of the checklists the calling AI gave, with
  nothing left for the calling AI to fix.
- Concept: an AI that did not make the work uses it in the receiver's place and goes back and forth
  with the generator until it finds each item's Good; through that back and forth the orchestrator
  reads no work and only passes what the flow gives. Each time the first user's reading ends, the
  orchestrator checks that each Good holds, and only the items that do not hold are made again in
  the next round. The orchestrator checks every round, so a run can end in one round.
- The calling AI deals only with the orchestrator.
- turn's own principles: (1) every role that makes or reads the work looks only for each item's
  Good and works only to give it; (2) each item is judged by what the receiver gets with what they
  have, never by whether the work matches its sources.

## design

### B-1: The stories the scenes rest on
- One story: as the calling AI, I want to hand turn the path of a CCS and get the work back, with
  each item's Good and the lines that give it. Reading, judging and making again are how the work is made,
  decided in the components.
- ACC and the CCS are rn's, closed inside it. In the paper, the compressor that makes the state is a
  model apart from the agent that acts on it, and the agent's output enters memory only through the
  next compression, after it is checked; so the compressor, the CCS's definition and the store, the
  repository, are the caller's, and turn is the agent that acts: it reads the CCS it is handed,
  follows it and writes its result where the call says.
- turn defines nothing of the CCS. A CCS is JSON: parts, each a list of entries, each entry a kind
  and its value. The caller hands turn, as JSON, the CCS's path, the kinds it uses for what turn
  takes from the task's state, and where turn writes its result:
  `{"ccs": "<path>", "kind": {"work": "<kind>", "checklist": "<kind>", "receiver": "<kind>",
  "use": "<kind>", "opens": "<kind>"}, "result": "<path>"}`. The kinds are where the work goes, the
  checklists, the receiver, who reads the work, what they read it for and what they open with it;
  the first three must each be named and have an entry, and the last two may be left out; a script takes
  every entry of each from the CCS and hands it to the roles that need it, so no AI copies it, and
  the hooks bound what each role reads by them. The generator reads the CCS whole. The values stay
  in the CCS alone, so the call and the CCS cannot differ. The result is not a kind: it is where
  this call's answer goes, not the task's state, which in ACC takes in the agent's output only at
  the next compression. It is one file, as one call gives one answer for the whole work.
- turn's result is where the work was written, each item's Good with its lines, the questions only
  the user can decide, and the items without Good, each with what the receiver gets once it is Good.
  A script writes it as a file and checks its shape as it writes: a reply would be copied into a
  file by the calling AI, where a slip goes unseen.

### B-2: Every logical component the stories need
- Five components: the generator, the first user, the evaluator, the learner and the orchestrator.
  The evaluator and the learner are there for the builder's reasons, so that the story is achieved
  reliably: the orchestrator alone did not settle its judgments, and the generator alone patched
  where a shortfall showed; each component's reason is written in the design.
- turn is for an AI alone: it deals only with the AI that calls it. Nothing is shown to a person
  watching, and nothing is stopped or said again by one, so the progress shown on the console, the
  stop with Esc and the start again from a person's words go.

### B-3: The stories achieved by interactions
- Only scripts doubt. Every role that is an AI looks, against the checklists, which say what the
  work should be, only for the Good each item gives and the lines that give it; a script doubts,
  such as by naming the lines no Good rests on. An AI that looks for what more the work needs
  finds more without end, and each find is patched in, so the work drifts from what it should be.
  Every role, the flow and how each judgment is made follow from this.
- The generator hands back only once it has read the work against each item and named the lines
  that give its Good; an item it cannot give, since only the user can decide what it needs,
  becomes a question, and what the decisions do not say is not filled in from its own guess. In
  the old turn's trials it filled the form from a grep of the headings within seconds, named lines
  for items it knew it fell short of, and said its doubts only in prose.
- The orchestrator reads the work first and sends back to the generator the items whose Good it
  does not find, each said as what the receiver gets once it is Good, not as the edit to make: a
  shortfall plain to see is sent back while it costs least, and in the old turn's trials an edit
  told to the generator broke another item. An item waiting on the user's answer is not sent back.
- Each role's part is one aim, from the checklists and looking for the Good, so the AI works to
  the aim rather than to a list of steps: the orchestrator runs the turn so that the Good builds
  up; the generator passes the checklists; the first user uses the work and looks for the Good; the
  evaluator looks for the Good the first user found and for any other Good the work gives; the
  learner looks through every record of the run for what makes the Good. The first user is given
  the checklists. The evaluator is there because one reader misses Good the work gives, and an
  item judged not Good by that miss is made again for nothing.
- How the work becomes Good is the generator's to decide: the orchestrator tells what the receiver
  gets once an item is Good, and the learner tells what it learned about how to make the work,
  such as what to read and ask before writing, where no item already asks it. In the old turn's
  trials, edits told per item broke other items and added what the decisions do not hold, while
  the learnings about making were the most useful thing the learner gave.
- The generator makes the work and names, as its own check, the lines it meant to meet each item;
  that is its claim, not a judgment.
- The orchestrator does not take the claim on trust: it reads the work against every item of the
  checklists and sends back what it can see falls short before the first user reads, so the costly
  reading is not spent on it.
- The first user uses the work in the receiver's place; the evaluator shows from that reading the
  Good the work gives, with its lines; the orchestrator does not take those on trust either: it
  finds each item's Good in the work itself and decides each item; the learner finds what makes
  the Good, and the orchestrator hands that to the generator.
- The orchestrator is an agent definition, not a skill, so it runs as its own subagent and the
  calling AI's context holds only what comes back; the calling AI starts it in the background and
  waits, so it can still take the user's pause. The four roles are the orchestrator's own
  subagents. The progress a person sees is the subagent panel's.
- The calling AI stops a run by sending the orchestrator a message; the orchestrator can message
  the calling AI before it ends. Tried (Claude Code 2.1.301, Opus): two orchestrators started at
  once each started a worker, sent `main` a message that arrived while they ran, and took a stop
  sent to their ID after their next tool call.
- Several runs go at once, as rn starts them for work that can go in parallel: each run keeps its
  own state, and the hooks tell runs apart by `agent_id`, since every agent of a conversation has
  the same `session_id`. A hook ties a role to its run by the role's
  `<transcript_path without .jsonl>/subagents/agent-<agent_id>.meta.json`, whose `parentAgentId` is
  the orchestrator's `agent_id`: tried on Claude Code 2.1.302 (2026-10-17) with two orchestrators
  at once in the background, each starting roles, every role's tool use and reply was tied to its
  own orchestrator. The file is there from a role's first tool use, not yet at `SubagentStart`, so
  what a role is started with is checked at the orchestrator's own `Agent` call, which carries the
  orchestrator's `agent_id` and the prompt. The file is Claude Code's own record, not a documented
  hook input, so the hooks' tests hold its shape and a change to it is seen there.
- `claude -p` is not used: the docs say `--bare`, which reads no subscription login, will become
  its default, and moving its use to separate credits was announced and only paused.

### B-5: How each component is realized
- The orchestrator and the four roles are agent definitions. What must come out the same on every
  run is done by Python 3 scripts with jq, and the hooks are Python checks, one file each, with one
  entry file per hook event, as `plugin.md` sets.
- The console and the stop with Esc go, as turn deals with no person.

### B-6: Where each component is placed
- The work is made where it goes, in the user's repository, not in a copy. A copy was there so
  that a person's stop with Esc left where the work goes as it was; turn has no such stop now. A run
  cut off leaves its writing as changes git shows, which the calling AI undoes or finishes, and the
  calling AI checks and fixes the work in place in any case. Runs at once make different files, as
  rn starts them for work that can go in parallel. Nothing of a run is put outside the repository.
- The roles' answers to one another, the generator's claim, the first user's reading and the
  evaluator's lines, are not files: each role gives its answer as its reply to the orchestrator, so
  a run leaves nothing behind, and only the orchestrator holds them, so the first user cannot see
  the generator's claim.
- A run asked to stop ends with a reply saying the items decided so far and where it stopped. A
  run cut off leaves the work as written so far; the calling AI calls turn again, the generator
  makes the work again from what is there and the readings start again. No resuming part way:
  being cut off is rare, and a reading again costs less than a resume to build and keep right.

### B-7: What each component depends on outside
- Claude Code, python3 3.9 or later, jq and git.

### B-8: Each unit checked, and how far
- The scripts: unittest fed what the calling AI hands over, a case each stops and one each lets
  through, every line and branch counted in CI on every push.
- The hook checks: unittest fed what Claude Code hands each hook, a step stopped where it must be
  and let through where it must be, counted the same way.
- The orchestrator and the four roles: each run on its own on a small task, on Opus 5.5, and judged
  from the JSONL by whether it did what its steps say.

### B-9: The whole checked
- Trials in `lovaizu/playground`, one at a time, each on a branch of its own removed after: a stand-in for the calling AI is handed a
  small task's decisions and checklist and calls turn; judged from the JSONL and the work. The
  story is achieved when the work comes back where it goes with an answer and lines for every
  item, each answer checked by reading the work.

### B-10: Key results measured
- From every trial, measured and compared with the targets in turn's UX and the last version: the
  items the stand-in fixes in the work after it comes back, counted from its own check in its
  JSONL; the time from the call to the return, from the JSONL's timestamps.
### Inside turn
- Each role is checked at both ends, in its own form: a hook lets a role start only with the input the orchestrator is to give it, and stops a role's reply that
  does not fill its form, each line named in the work.
- The orchestrator settles its own finding of every item's Good, from its own reading of the work,
  before it sees the evaluator's: a script records it, and a hook lets the evaluator start only once
  it is recorded. The script then names the items where the two differ, and the orchestrator
  decides each of them against the first user's JSONL, what it opened and where it stopped. A
  judgment made after another's is pulled toward it, which words alone do not prevent.
- The learner looks at every item, with Good and without, in the work and in the JSONL of every
  role the run started: for an item without Good, how the work would give it; for an item with
  Good, what in the work gives it, so that making again keeps it. What fell short often lies in what
  a role did, which only the JSONL shows, and a Good is lost by a remake that does not know what
  gives it. What it learns is used within the run.
- A reading is one pass of the work through the first user, the orchestrator's own finding, the
  evaluator and the orchestrator's decision. The orchestrator reads the work against every item
  once the generator hands it back, sends back what it can see has no Good, and once nothing is
  sent back, its findings are recorded and the first user reads. When the reading gives every item
  its Good or a question, the run returns; otherwise the learner looks and the generator makes the
  work again, and a second reading follows, after which the run returns with what is still without
  Good. A question waits for the calling AI: it puts it to the user, and writes the answer into the
  work itself or into the CCS and calls turn again.
- What each role is given: the generator, the CCS whole, what is sent back and what the learner
  found; the first user, the work, what the receiver opens, who the receiver is and what for, and
  the checklists; the evaluator, the same and the first user's reading; the learner, every item's
  finding and the JSONL of every role of the run, which the hooks let it read by `parentAgentId`.
  The JSON forms are the builder's to settle.

## Moved out of the architecture, for tests and steps (2026-10-23)

- [test: flow] Where the call names a missing file or leaves a kind without an entry, the flow says so and the orchestrator returns it, with no run started.
- [test: flow] A call naming a result whose state is there goes on from the move the state was last at; each role the run goes on with, one kept started included, is started anew, given what it was given and what was sent to it since, and reads its inputs again; a role's context is lost with its conversation, so what it is given and sent is kept in the state to give again, and a run gone on costs that reading and reaches the same place.
- [step: orchestrator] Before any work is made, it reads the CCS, the files it names but the work, and the checklists, finds for every item what in them gives its Good, and checks that what the receiver has lets the first user do with the work what the receiver does, such as running its tests; each item that lacks it waits on a question saying what is lacking with the items it settles; an answer may also change how the whole work is laid out.
- [step: orchestrator] It words a question found as it checks the CCS from its own reading, and one for an item the rounds leave without Good from the findings the flow shows it, each with the answer it recommends, and hands on a generator's question, with the answer the generator recommends, as the generator wrote it; each question is worded by the one that holds what it rests on, and a generator's question retold would ask what the generator did not.
- [step: calling AI] The calling AI fills what it can from its sources and asks the user the rest, sends the answer back and keeps it in its CCS, where a call again reads it.
- [test: flow] The flow gives the answer to the generator by message where the generator asked, and in what it is given where it is started next, and the run goes on from there.
- [test: flow] The line for the user says what the move will do, how far and how, or what is done and what comes next; the orchestrator sends it to `main` as a move of its own; no one answers it, and no role tells it.
- [test: flow] What a machine can judge of a reply, the flow checks from it (Principle 5).
- [test: flow] Scope: `its part` is answered at the lines that give it, `each part` in every part of the work on its own with a Good for each, `whole` of the work at once; the flow splits the work into its parts, a document's sections under its top headings with the title and opening as one, and each other file whole; it stops a reply that gives an each-part item without every part, and takes such an item's Good from a reader only where every part has one; a remake that breaks one part for another item would otherwise go unseen, and the checklist says it once, so every role and run answers at the same place.
- [test: flow] The flow stops a reply that gives a Good at lines the work does not hold: a file not of the work, lines past its end, or, for an each-part item, lines outside the part; the calling AI checks each Good by reading its lines, and a Good at lines that are not there cannot be checked.
- [step: generator] It first sets, from the whole CCS, the Good the receiver is to get from the work for each item and where the work gives it; a work made to Goods set first gives each where it was meant, one written first and matched after is patched item by item.
- [step: generator] Where only the user's answer can give an item its Good, it replies with the questions, each with the answer it recommends, before making anything, and goes on once the answers reach it; what the CCS does not say becomes a question, not its own guess, and asked before the making its answer shapes the work rather than a remake.
- [step: generator] It makes the work to give each Good, runs what it wrote as the receiver would, and replies with each item's Good with its lines, and with any question found while making; what is not run is not known to work, and its Goods are its claim, not a judgment.
- [step: generator] Where a path of the work already holds a file, it makes the work from it rather than from nothing, so what already gives its Good stays as it is.
- [step: generator] Sent back, it changes only what is sent back, without reading the sources again.
- [step: first user] It uses the work with everything the receiver has, doing all they do with it, and gives for each item the Good it found with its lines, and for each it finds none, the places it looked, what it did there and what it did not get; a reader with less misses a Good the receiver gets, one that only reads passes what a run shows to fail, and a place alone does not show the maker what was missing.
- [step: first user] Sent the work made again, it reads again whether the places it stopped at now give the Good, so what is left only shrinks.
- [test: flow] In a round, the generator and the first user stay started; the generator is sent each item the first user found no Good for, as the first user gave it, and the first user the work made again, with no reading between, until it finds every item's Good, each item left waits on a question, or it has been sent back three times in the round; the bound keeps a reading that does not settle from going on without end, and what it leaves goes on without Good to the orchestrator's check.
- [test: flow] The first user is not given the generator's reply, and the generator gets only what the first user, or the orchestrator's check, found lacking.
- [step: orchestrator] Its check of each Good: it reads the work whole, reads each Good at its lines as the receiver the CCS names, runs what the Good says the receiver gets, as the receiver would, and says yes where the receiver gets what the item asks, or, where not, what the receiver does not get and where; with the sources it knows what the work does, which a claim may overstate.
- [test: flow] In the next round the generator, started anew, is given each item without Good with what the first user or the orchestrator's check found lacking, and the first user is started anew, until every item has its Good or waits on a question.
- [test: flow] An item two rounds leave without Good waits on a question: what the user is to decide for the receiver to get it; the rounds are bound as the sending back in a round is.
- [step: learner] It reads the record of every agent of the run, the orchestrator's included, and gives what fell short and why, each lesson with the words it rests on quoted and said to be the project's own or general, or that it found none and what it checked.
- [step: calling AI] The calling AI puts each lesson to the user: a project's own into the user's checklists or rules, a general one to turn's makers as an issue, shown to the user whole and opened only on their yes, as The caller approves what is theirs says; the calling AI, not turn, reaches the user, as with a question.
- [test: lanes] Each role, the orchestrator included, reads what it is given alone, and whole; writes only its work and its reply, its reply in its form; commits and pushes nothing; and ends only once its reply is there; a role that reads only what it is given is not bent by what it was not meant to see, an item judged on a part read is judged on a guess for the rest, and the calling AI keeps the work in git on its own judgment, after checking it.
- [test: lanes] On the orchestrator, the lanes hold that it begins with the flow, makes only the move the flow gave, a line for the user among them, and hands on a generator's question as the flow printed it.
- [test: flow] That every item is answered, that each Good's lines are in the work, and that the result is there, the flow checks itself.
- [test: flow] `turn.py` prints each next move as one JSON line `{"tool": ..., "input": {...}}`, last in its output: an Agent call starting a role, a SendMessage to a role kept started, or a SendMessage to `main` with a line for the user; a role's prompt is a JSON object of what it is given, the files it reads, the work, the reply file and the checklists, each a path, and the flow's message what is sent back; the move printed as the tool call itself is a form lane holds the orchestrator to, and a role given its inputs as JSON is held by lanes on the values it starts from.
- [test: flow] Each role's reply is held to its JSON Schema in `scripts/`; the flow reads it once the orchestrator runs `turn.py next`; a role sent more work writes its reply again, and `turn.py next` waits until it has been written since the send, as the reply of a subagent sent a message comes back later, not with the send; tried: an orchestrator that ended its turn after the send never got the reply, one that waited on a script reading what was kept got it word for word.
- [step: orchestrator] It gives the flow the agent ID each Agent call returns, by which the flow names the role to send more work to and the learner is given each role's record; the Agent tool gives a subagent no name to be messaged by.
- [test: flow] The flow finds each role's record by the agent ID the orchestrator gives it, as `<conversation>/subagents/agent-<ID>.jsonl`, the place the hooks reference gives, and the orchestrator's own as the `turn:up` record beside them whose call names the result; the orchestrator is told no ID of its own, and lane hands a script nothing from a hook's event, so the flow finds them itself (2026-10-23).
- [step: orchestrator] It replies with a question and ends its turn; the calling AI's SendMessage to its agent ID resumes it, as `lane:up` is reached.
- [step: orchestrator] The lines go by SendMessage to `main`, loaded with ToolSearch: called from the main conversation, the calling AI is told them; called from an agent, they reach the main conversation above it, as that agent cannot be messaged by a name; tried with an agent started by an agent started in the background, its message to `main` reached the conversation while the agent that started it was still running.
- [test: lanes] The lanes run values taken from what each agent starts from: on each role, read_only and read_whole on `{given}`, write_only on `{work}` and `{reply}`, in_form on `{reply}` and its form, end_when on `{reply}`, and hands_off on `git commit` and `git push` on each role that runs commands; on the orchestrator, start_with on `turn.py start`, read_whole on the `{given}` that `turn.py start` prints, the CCS, the files it names but the work, and the checklists, follow_next on `turn.py next`, which holds the lines it prints as moves, as_printed on a generator's question it hands on, and hands_off as on the roles.
- [step: generator, first user, orchestrator] The generator's running what it wrote, and the first user's and the orchestrator's running what the receiver runs, are held by their steps alone: what is run is found in the work and in what the receiver does with it, and the CCS names no kind for a command, so turn has none to give test_after.
- [test: lanes] No lane on every item answered or on the result made: the flow reads the result and every reply itself, and lane sees a write only in the call that makes it, where the flow writes the result inside its own run.
- [test: lanes] Each lane acts in its own agent alone, by `agent_type`, and reads that agent's own record and what it started from, so runs at once are told apart without turn tracing them; turn keeps no hooks of its own.
- [test: flow] The flow's unit cases: the call's check stops what it must; an item gets its Good only where the first user gave one and the orchestrator said yes; a reply giving a Good at lines the work does not hold is stopped; a question is sent at the move it is found; an item two rounds leave without Good becomes a question; a stopped run goes on from its last move; the result and each reply are held to their forms.
- [test: orchestrator] The orchestrator unit's sets of replies, by the counts: an item sent back three times going on without Good; an item two rounds leave without Good sent as a question and the run going on with the answer; a question the generator replies with before making anything sent at once and its answer sent to the generator, which then makes the work; each with the learner once after the run.

## turn's code against the architecture (2026-10-23)

- Kept: `scripts/call.py`; `forms.py` but `GOOD`, `taken` and the lessons' roles; `records.py`; in `run.py` the start, resume, moves, lines, reply wait, send bound and
  paging; the three roles' core steps; the tests of start, forms, properties, kept rounds and resume;
  the trials' `kept.py`, `baseline.py`, `shared.py`, `stand.py`.
- Rebuilt: `run.py`'s round middle and end (`first_read`, `compare`, `decide`, `settle`, `offer`,
  `taking`, `took`, `remade`) to the Good check; questions sent as met, not kept in the result;
  `up.md` steps 5-6 to the check of each Good, running what it says; the generator asking before
  making; the learner once after the run, its lessons in the result, own or general; the decision
  tests and the flow trial's reply sets; the KR1.1 judge kept in `dev/turn/trials/`.
- Removed: `agents/evaluator.md`, `forms/goods.json`, the evaluator's hooks, the take step, lessons
  fed to the roles.
- The trials' false Goods (`dev/turn/trials/readme/results.json`, 89142d1 to 8c78852) came from the
  decision and the evaluator arguing the first user's stops away; the flow and roles trials held.
- Settled from the purpose, no user decision: a round's first user and the Good check read every
  item again, as a remake may break one that held; the rounds' bound is two; the records found by
  the flow from the agent IDs (`records.find`, `records.orchestrator` kept); the orchestrator's
  reading no work in a round held by its step alone, with no read_only on the orchestrator, until a
  trial shows it drift, as lane reads a run's values only from the prompt and the start_with
  script (`lane/README.md:91-93`) and build only what a trial shows is needed (2026-10-23).
