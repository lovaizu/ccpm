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
- [test: flow] Each role's reply is held to its JSON Schema in `forms/`; the flow reads it once the orchestrator runs `turn.py next`; a role sent more work writes its reply again, and `turn.py next` waits until it has been written since the send, as the reply of a subagent sent a message comes back later, not with the send; tried: an orchestrator that ended its turn after the send never got the reply, one that waited on a script reading what was kept got it word for word.
- [step: orchestrator] It gives the flow the agent ID each Agent call returns, by which the flow names the role to send more work to and the learner is given each role's record; the Agent tool gives a subagent no name to be messaged by.
- [test: flow] The flow finds each role's record by the agent ID the orchestrator gives it, as `<conversation>/subagents/agent-<ID>.jsonl`, the place the hooks reference gives, and the orchestrator's own as the `turn:up` record beside them whose call names the result; the orchestrator is told no ID of its own, and lane hands a script nothing from a hook's event, so the flow finds them itself (2026-10-23).
- [step: orchestrator] It replies with a question and ends its turn; the calling AI's SendMessage to its agent ID resumes it, as `lane:up` is reached.
- [step: orchestrator] The lines go by SendMessage to `main`, loaded with ToolSearch: called from the main conversation, the calling AI is told them; called from an agent, they reach the main conversation above it, as that agent cannot be messaged by a name; tried with an agent started by an agent started in the background, its message to `main` reached the conversation while the agent that started it was still running.
- [test: lanes] The lanes run values taken from what each agent starts from: on each role, read_only and read_whole on `{given}`, write_only on `{work}` and `{reply}`, in_form on `{reply}` and its form, end_when on `{reply}`, and hands_off on `git commit` and `git push` on each role that runs commands; on the orchestrator, start_with on `turn.py start`, read_only and read_whole on the `{given}` that `turn.py start` prints, the CCS, the files it names but the work, and the checklists, follow_next on `turn.py next`, which holds the lines it prints as moves, as_printed on a generator's question it hands on, and hands_off as on the roles.
- [step: generator, first user, orchestrator] The generator's running what it wrote, and the first user's and the orchestrator's running what the receiver runs, are held by their steps alone: what is run is found in the work and in what the receiver does with it, and the CCS names no kind for a command, so turn has none to give test_after.
- [test: lanes] No lane on every item answered or on the result made: the flow reads the result and every reply itself, and lane sees a write only in the call that makes it, where the flow writes the result inside its own run.
- [test: lanes] Each lane acts in its own agent alone, by `agent_type`, and reads that agent's own record and what it started from, so runs at once are told apart without turn tracing them; turn keeps no hooks of its own.
- [test: flow] The flow's unit cases: the call's check stops what it must; an item gets its Good only where the first user gave one and the orchestrator said yes; a reply giving a Good at lines the work does not hold is stopped; a question is sent at the move it is found; an item two rounds leave without Good becomes a question; a stopped run goes on from its last move; the result and each reply are held to their forms.
- [test: orchestrator] The orchestrator unit's sets of replies, by the counts: an item sent back three times going on without Good; an item two rounds leave without Good sent as a question and the run going on with the answer; a question the generator replies with before making anything sent at once and its answer sent to the generator, which then makes the work; each with the learner once after the run.

- The user decided (2026-10-25, D1): only the first user looks for Good; the orchestrator's check
  of each Good goes and no checker takes its place, as that is what turn should be. Settled from
  base Principle 3: the orchestrator still judges what the run needs, the CCS's check and the items
  left. In the readme trials r10 to s12 the check stopped three Goods of the first
  user and passed the five the calling AI judged unmet.

## turn's code against the architecture (2026-10-23)

- Kept: `scripts/call.py`; `forms.py` but `GOOD`, `taken` and the lessons' roles; `records.py`; in `run.py` the start, resume, moves, lines, reply wait, send bound and
  paging; the three roles' core steps; the tests of start, forms, properties, kept rounds and resume;
  the trials' `kept.py`, `baseline.py`, `shared.py`, `stand.py`.
- Rebuilt: `run.py`'s round middle and end (`first_read`, `compare`, `decide`, `settle`, `offer`,
  `taking`, `took`, `remade`); questions sent as met, not kept in the result; the generator asking
  before making; the learner once after the run, its lessons in the result, own or general; the decision
  tests and the flow trial's reply sets; the KR1.1 judge kept in `dev/turn/trials/`.
- Removed: `agents/evaluator.md`, `forms/goods.json`, the evaluator's hooks, the take step, lessons
  fed to the roles.
- The trials' false Goods (`dev/turn/trials/readme/results.json`, 89142d1 to 8c78852) came from the
  decision and the evaluator arguing the first user's stops away; the flow and roles trials held.
- Settled from the purpose, no user decision: a round's first user reads every item again, as a
  remake may break one that held; the rounds' bound is two; the records found by the flow from the
  agent IDs (2026-10-23).
- Settled in the flow's code, where the documents leave it open (2026-10-23): the calling AI's
  answer reaches the flow as `turn.py next <result>` with the answer as it came on standard input,
  kept in the state with its questions; after the answer to an item the rounds left, its items are
  made again in a new round, the rounds counted anew; the result is `{"work", "items", "lessons",
  "checked"}`, so a run with no lesson still says what the learner checked; a lesson's `whose` is
  `own` or `general`; `dev/turn/cosmic-ray.toml` type-checks `turn/scripts` alone, as checking
  `turn` followed the link to lane's code, failed, and so caught every mutant.
- The orchestrator reads only the `{given}` `turn.py start` prints, held by read_only, and an answer
  that changes what the CCS names makes the flow print `{"anew": ...}`, the orchestrator running
  `turn.py start` again so the lane takes the files the CCS now names (2026-10-25): in the flow
  trial's eight ways at 4afc6a8 it twice ran `cat` of README.md or the roles' replies in a round,
  stopped only because a move was printed and not yet taken (`dev/turn/trials/flow/results.json`,
  ways `sent` and `left`), and in the readme trials r10 and r12 it read README.md and LICENSE; with
  the Good check gone (D1) it has no work to read, and a bound its tool calls show is a hook's to
  hold (prompt.md B-3).
- The flow gives no role the run's own files beside the result, a folder holding them given as its
  other entries (2026-10-23): in the roles trial the first user, under `has` `.`, read the
  generator's reply and the state, as its read_only lane lets it read anything under a folder it is
  given; the files stay beside the result, as Claude Code asks permission for each write outside the
  working directory, also under acceptEdits
  (https://code.claude.com/docs/en/permissions.md), and the README promises the state there.
- The result names each lesson's record by its path, not by its number among the texts the learner
  read, as those texts are removed once the run returns and the calling AI checks each lesson
  against its record (2026-10-23).
- KR1.1's judge reads the whole work each version returns, not its result (2026-10-23): turn
  0.1.0's result gives lines without paths in a form of its own, so lines alone cannot be given
  both by one bar, and a Good's words would lean the judge.
- [test: flow] On every answer, and on a call again, the flow reads the CCS again; where it gives
  the run other than the run was begun with, such as a file added to the work, the run goes back to
  the CCS check with every answer and record kept (2026-10-23): in five of six acceptance runs on
  the readme task the answer adding LICENSE to the work was kept in the CCS while the run held its
  first work, so the generator, held to it, asked the same question again and again.
- [step: generator, first user, orchestrator] A Good holds at its lines only where each thing they
  tell the receiver is so: each command they give run and its print compared with what they say,
  each thing they say the code does tried on an input it is about, each file and link they point
  to looked up (2026-10-23): in the acceptance runs at 7edc487 READMEs came back with untrue words
  on a byte order mark and a link to a LICENSE not there, each passed by the first user and the
  check, which ran what the Good's own words said alone.
- [step: generator] Where an item's Good needs a file the work does not hold, the item waits on a
  question whether to add it to the work, recommending it be added under the CCS's kind for the
  work (2026-10-23): an answer kept in the decisions alone left the run unable to write LICENSE.
