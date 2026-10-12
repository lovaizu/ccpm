# turn design

This document is for whoever changes turn. It says what turn must achieve, how each quality is
checked, and how turn is built to achieve it and why, in service of the benefits the
[README](../../turn/README.md) promises. It leaves out how to use turn and the forms callers write,
the call, the CCS and the checklist, which are in the README where callers read them; here they are
named only as what must keep holding. It also leaves out each prompt's wording, the steps and the
file layout, which are in the code. A statement on how an AI behaves is an assumption until the
trials in Verification measure it, and is marked "(assumption)".

The words used throughout:

- The caller: Claude in the user's conversation, or a step of the user's plugin; it hands turn one
  task.
- The CCS: the JSON file in which the caller writes the task, what the work should be, and in which
  turn writes back what the caller needs next.
- The receiver: the person the work is for, as the caller names them in the CCS. The use: what the
  receiver uses the work for, as the CCS names it.
- A checklist, its opening and its items: a checklist says what a work of one kind must give its
  receiver. Its opening says what such work is for, and each item asks one thing. The list is what a
  script makes from the checklists the CCS names: each opening, and every item with its whole text.
- A run goes from one CCS to the one turn writes back. A round makes, reads and judges the work
  once; a run has one round or two.
- The conductor: the part of turn that runs a run, decides each move and writes the console. It has
  four agents work: the maker makes the work, the reader reads it as the receiver, for the use, and
  hands back its reading, the judge shows each item the work meets, and the learner finds why an
  item was not shown met.
- Grounds: the lines an answer to an item rests on, with their words. The maker's grounds are lines
  of the work; a Good's are lines of the work and of the reading.
- A Good: an item the work meets, given by the judge with its grounds. The conductor counts a Good
  only once it has seen, in those lines, that the item is met.
- More: an item left without a counted Good when the run returns; the word belongs to the CCS alone.
- Coverage: the lines of the work that no item's grounds name, counted by a script, as test coverage
  counts the lines no test runs.
- The intent: what turn means the work to let its receiver do, shown before the maker writes.
- The records: the JSONL in which Claude Code keeps every conversation and agent.
- The evidence: what turn keeps in its folder `.turn/` so that each item can be followed back.

## Goals

### Attractive quality

- Read in the receiver's place: the work comes back read by an agent that did not write it, in the
  receiver's place, with each item it counts as met shown in the lines of the work, and what the
  reading could not take made again from its cause; so the user can hand the work on without first
  reading it as its receiver.
- Asked only what only the user can decide: nothing is asked that what the work should be, or its
  sources, already answers.
- Seeing the work as it goes: the user can tell from the console how far a run has come, and stop a
  run whose intent they do not want before the work is written, saying what they want instead.
- A plugin decides from what turn returns: a plugin hands turn one task and decides its next move
  from the returned CCS alone, without writing the loop of making, reading and making again itself.
- Following each item back: the user can later tell, for each item, the lines its Good rests on or
  why it has none, and the version of each checklist the work was made and judged by.

### One-dimensional quality

Neither has a fixed limit; each must be no worse than in the version in use.

- The first-round share: the share of runs whose first round ends with every item Good. The more
  work is right when first made, the less the user waits and the less is spent.
- Time and tokens: what one run takes, from the call to the returned CCS.

### Must-be quality

- Nothing passes unshown: no item counts as met unless the conductor has seen, in the lines its Good
  rests on, that it is met.
- Repository untouched: during a run, turn changes nothing in the user's repository but the work and
  `.turn/`, and never commits or pushes.
- The user's own work alone: outside its runs, turn stops nothing the user or Claude does in any
  session where it is installed, and a missing tool there breaks nothing.
- What the work should be unchanged: turn never rewrites what the caller wrote the work should be.
- Nothing unread: the work turn returns is the version the reader last read.
- Stop and start over: when the user stops a run with Esc and says what they want instead, the work
  is made from what they said, starting from the work as it stands. A run cut off before it returns
  leaves where the work goes untouched, and called again with the same CCS it starts over.
- Missing tools: when python3 or jq is missing, turn stops before any work and says what to
  install.

### Backward compatibility

- The call: plugins' steps call the skill `turn:up` with the two arguments the README gives, `in`
  and `out`, and name `turn` in their dependencies. These must keep holding. An argument may be
  added only if a call without it runs as before, since callers written for an earlier version do
  not pass it.
- The CCS: callers write and read it in the form the README gives: its nine parts, the kinds of
  entry in each, and the values of `next`. None may be added, removed or renamed, since a caller
  breaks on one it does not know as much as on one that is gone. This holds for `viewpoint`, the
  CCS's name for a checklist, though this document's word differs. What turn writes in its entries,
  other than `next`, may change in wording, since callers hand it on rather than read it by kind.
- Carrying on across an update: a later version must accept a CCS an earlier version returned, so
  that a stopped task, or one with the user's answers, carries on after an update.
- The checklist form: users and writ write checklists in the form the README's Requirements gives.
  This must keep holding. How the list is made from it may change, since only turn's agents read
  the list.
- `.turn/`: the user and the next run open what a returned CCS points to there, and every such place
  must exist. What else is in `.turn/`, and how it is laid out, may change between versions.
- The console's wording and the agents' prompts may change: no program reads them.

### Non-goals

- Deciding what the work should be. The caller writes it; turn measures against it and returns what
  it cannot decide.
- Talking to the user. turn returns its questions to the caller, which knows what was already agreed
  with the user and asks them.
- Running until every item is Good. What a second round still leaves without a Good is returned as
  More: a sign of a fault in turn, in the checklist or in what the work should be, to be fixed there
  (assumption).
- Finding what no item asks. A gap of that kind belongs in the checklist, where every later work is
  measured by it.
- Holding checklists. What they ask belongs to whoever knows the kind of work, such as writ.
- Code. A program is checked by running its tests, not by reading.

### Constraints

- turn is used by Claude, on a person's behalf, in their conversation or in a plugin's step.
- turn runs inside Claude Code and is built only from what a plugin can hold: skills, agents, hooks
  and scripts. Installing copies only turn's own folder. A plugin's hooks run in every session where
  it is installed, not only during its runs. An agent cannot start other agents (Claude Code's
  documentation on subagents).
- What runs on users' machines is Python 3.9 or later with the standard library only, and jq, as
  this repository's plugin rules set.
- The work is in a git repository.

## Verification

### Attractive quality

Each is tried on real work: writ's documents and prompts, and turn's own, are made through turn,
and whoever builds turn reads the records of every conversation and agent of the run. A made-up task
shows only that the made-up task passes.

- Read in the receiver's place: tried on work written for a receiver who lacks what the maker knows,
  where a writer checking their own work passes what a newcomer would miss (assumption). It passes
  when a fresh reader with no part in the run, reading the returned work as the same receiver, for
  the same use, on the same list, takes from it every item the run counted Good. It also passes only
  when each item round 1 left without a Good has one on that reading, as has every other item its
  cause explains, so it was made again from its cause and not patched.
- Asked only what only the user can decide: tried on a task whose sources settle some choices and
  leave one open. It passes when the open choice is asked and no returned question can be answered
  from what the work should be or from its sources.
- Seeing the work as it goes: it passes when, at any point in a run, the user, reading the console
  alone, can tell which round and step it is at, as the records show, and when, given a task whose
  intent they do not want, the user stops it with Esc after the intent is shown, no work of that
  intent has been written, and the work then made is what they said.
- A plugin decides from what turn returns: it passes when the next move decided from the returned
  CCS alone is the same as the one decided after also reading the records.
- Following each item back: it passes when, for any item of a returned work, the user finds in
  `.turn/` alone the lines its Good rests on or why it has none, and the commit of the checklist it
  was judged by.

### One-dimensional quality

Both are measured from the records of the same tasks, each run from the same CCS on this version and
on the version in use: the first-round share, and the time and tokens per run.

### Must-be quality

Each is checked by a test:

- Nothing passes unshown: a Good that names lines the work does not hold is not counted, and its
  item is returned as More.
- Repository untouched: during a run, a write outside the work and `.turn/`, a commit and a push are
  each stopped.
- The user's own work alone: outside a run, including while one runs in another session, a write
  anywhere, a commit and a push each go through, with python3 missing as well as present.
- What the work should be unchanged: a returned CCS in which what the work should be differs from
  what was received is stopped.
- Nothing unread: with a version of the work written after the last reading, the work returned is
  the last-read version.
- Stop and start over: a run stopped at each of its steps returns `stopped` with where, and a run
  called with it and the user's words starts from the work as it stands. With a run cut off, where
  the work goes is untouched, and a run called again with the same CCS starts from the beginning.
- Missing tools: with python3 or jq missing, turn stops before any work and says what to install.

### Backward compatibility

For each released version, a test calls turn as that version's callers call it:

- The call: `turn:up` called in that version's form runs, writes the new CCS to `out`, and leaves
  `in` as it was.
- The CCS: a CCS of that version's form is accepted, and every value of `next` this version can
  return is one that version's callers know.
- Carrying on across an update: a `stopped` CCS that version returned is accepted, and the run
  starts from the work it points to.
- The checklist form: the checklists that version's README points to give a list with each
  checklist's opening and every item, each with its whole text.
- `.turn/`: every place a CCS that version returned points to exists after the run.

## Architecture

### Principles

- Every agent aims only at every item being Good. Each thinks forward, from what would make an item
  Good, not from what is wrong. The place where an agent answers an item holds only what meets it
  and its grounds, so no agent can write a shortfall. No agent is set to find something. The
  conductor too aims at more items reaching Good, not at doubting them. Protects: read in the
  receiver's place, the first-round share. Assumption: an AI works toward the aim it is given, and
  one set to find something finds it whether it is there or not. The form, not the wording, holds
  an agent to Goods, since a judge told in words to write Goods only still wrote on items without
  one in a trial.
- Every agent that measures the work measures from the same list, receiver and use. Each agent
  reads nothing beyond the inputs set for it, since what it reads besides changes the standpoint it
  measures from. Protects: read in the receiver's place, the first-round share.
- A shortfall goes back to where it was made, as soon as it can be seen. Protects: the first-round
  share, time and tokens. What can be seen in the maker's work costs a whole round when it is found
  in a reading instead.
- The conductor decides each move from the work and the records, not from an agent's report alone.
  Protects: nothing passes unshown, asked only what only the user can decide. Assumption: a report
  can say more than the work holds, and what it says beyond the work would pass on to the user.
- What must come out the same every time is done by a script or a hook, not by an agent. Protects:
  nothing passes unshown, the CCS, repository untouched, following each item back.

### Structure

```mermaid
sequenceDiagram
  actor U as User
  participant C as Caller
  participant O as Conductor (turn:up)
  participant S as Scripts
  participant M as Maker
  participant R as Reader
  participant J as Judge
  participant L as Learner
  C->>O: CCS
  O->>S: CCS, checklists
  S-->>O: CCS checked; the list
  O-->>U: the plan (console)
  loop round 1; round 2 only if round 1 leaves an item without a Good
    O-->>U: the intent (console)
    O->>M: what the work should be, the sources, the list (round 2: the learner's causes)
    M-->>O: the work; for each item, the lines that meet it; questions
    O->>S: the work, the maker's lines for each item
    S-->>O: the lines no item's grounds name
    Note over O,M: sent back until every item is seen met and no line is left over
    O->>R: the work, the receiver, the use, the list (in a fresh copy)
    R-->>O: for each item, what was taken, and where
    O->>J: the list, the work, the reading, the records
    J-->>O: a Good with its grounds for each item the work meets
    O->>S: the work, the Goods
    S-->>O: the lines no Good names
    Note over O,J: a Good counted once its lines are seen to meet the item
    O-->>U: what the reader could not take (console)
    opt an item without a counted Good
      O->>L: those items, the list, the work, the reading, the records
      L-->>O: for each, why no Good came out, in the work and in the process
    end
  end
  O->>S: Goods, causes, checklists, new CCS
  S-->>O: evidence written; new CCS checked
  O-->>U: where the work is, and what the user must decide (console)
  O-->>C: new CCS
  C-->>U: the questions only the user can answer
  opt at any point: the user presses Esc and says what they want instead
    O-->>C: a CCS with `stopped` and where
    C->>O: the CCS with the user's words added, for a new run
  end
```

| Part | Aim | Hands back | Depends on |
|---|---|---|---|
| Caller | What the work should be, written once for the task | The CCS; the user's answers or words added to it, for a new run | The CCS's form |
| Conductor | More items reaching Good | The maker's work sent back with each item not yet met and each line no item names; each Good counted once seen in its lines; the next round, or the CCS to return | Claude Code, which runs it as a skill in the caller's conversation |
| Maker | A work that meets every item | The work; for each item, the lines that meet it; what the sources do not settle, as questions | What the work should be, the sources, the list |
| Reader | Take from the work what the receiver would | For each item, what was taken, and where | The receiver; the use; the list; a fresh copy made from git, removed when done |
| Judge | Every item the work meets, shown | A Good with its grounds for each | The list; the work; the reading; the records |
| Learner | Why no Good came out for each item without one | Each cause, with the items it explains | Those items; the records |
| Scripts | What must come out the same every time | The list; the lines no grounds name; the CCS checked on receiving and returning; the evidence | python3, jq |
| Hooks | A slip in the process caught as it is made, during a run only | A stop that names the step and what it needs | Claude Code's hook events |

### The checklist as the measure

Achieves: read in the receiver's place, the first-round share, the checklist form.

The checklists are written so that a work meeting every item serves its purpose (assumption, which
the attractive-quality trials test). A script makes one list from the checklists the CCS names,
carrying each checklist's opening with the items. The maker, the conductor and the reader are each
given that list, and the receiver and the use the CCS names, so they measure under the same
condition. The opening says what such work is for. The receiver says whose place the work is read
in, and the use says what the receiver comes to it for. What no item
asks goes into the checklist, not into an agent's answer.

- Must hold: every agent that measures the work has the list with every opening, and the same
  receiver and use. No agent answers outside the list's items.
- Weighed: letting the reader take its standpoint from the openings alone was not chosen. Some
  openings name no reader (the document checklist says only that a document is read by the reader
  it is written for), so the reader would have no place to read from, and the benefit is read in
  this receiver's place. The cost: the CCS must name the receiver. Letting the reader also say what
  it could not take outside the items was not chosen, since with no item to bound it, it reads as a
  search for faults and varies from run to run (assumption). The cost: what no item asks is not
  found until the checklist is changed.

### Making it right first

Achieves: the first-round share, time and tokens, asked only what only the user can decide.

The maker makes a work that meets every item. For each item it gives the lines of the work that
meet it, with their words, not the heading they sit under, so the conductor weighs the words
themselves. What the sources do not settle goes to the user as a question and stays out of the
work. The conductor reads the work against the list, with the coverage count beside it. It sends
the work back with each item it does not yet see met and each line no item's grounds name, and says
for each how a Good would be reached. It sends the work back as many times as it takes, since
settling the work is its own work. A question the work or its sources answer is dropped.

- Must hold: no work reaches the reader with an item the conductor sees unmet or a line no item's
  grounds name.
- Weighed: passing the maker's work straight to the reader was not chosen, since every item it
  leaves unmet then costs a round to find. The cost: the conductor reads every item before each
  reading. A limit on sending back was not chosen, since a work sent on unsettled costs a round. The
  cost: a round's length is not bounded, which time and tokens measure.

### Coverage

Achieves: read in the receiver's place, nothing passes unshown, the first-round share.

The coverage count is a script. Its unit is a line of the work, as in test coverage, and as a
Good's grounds are lines. It runs twice in each round. The first time is when the maker hands the
work over, from the maker's lines for each item, before any reading. The second is when the judge
hands back its Goods, from their grounds, before the conductor checks them. A line the count finds
either does nothing for the receiver or holds a slip, since a line that does something meets some
item. What slips through both counts is of a kind no item asks about, and goes into the checklist.

- Must hold: no work reaches the reader, and no Good is counted, before the conductor has the count.
- Weighed: an agent set to look for slips was not chosen, since it would be set to find something,
  while a count needs no AI and comes out the same every time. The cost: a slip inside a line some
  item's grounds name is not counted.

### Reading in the receiver's place

Achieves: read in the receiver's place.

The reader starts where the receiver starts, as a new team member starts from a fresh clone: a copy
of the repository with the work added, made from git and removed after the reading. It is given the
receiver, the use and the list, since the receiver comes to the work with that use, and reading in
their place means reading for it. It is given nothing of how the work was made, of the sources, or
of what the receiver must be able to do with it, so that it stops where the receiver would
(assumption). For each item it says what it took from the work and where.

- Must hold: the reader's copy holds nothing the receiver would not have.
- Weighed: reading in the working repository was not chosen, since files the receiver lacks could
  carry the reader past what is missing (assumption). The cost: a copy for each reading. Telling
  the reader what the receiver must be able to do was not chosen, since it would then look for that
  rather than take what the work gives (assumption). The cost: only the judge weighs the reading
  against what the receiver must be able to do.

### Judging every item

Achieves: read in the receiver's place, nothing passes unshown, following each item back.

After the reading, the judge gives, from the reading, the work and the records, a Good for each item
the work meets, with its grounds. It writes nothing for an item it cannot ground. The conductor has
the lines no Good names before it, and reads, for every Good, the lines it rests on. It counts the
Good once it sees there that the item is met, as a teacher gives the mark once the working shows
the answer. This reading is needed beside coverage, which shows the lines no Good names but not a
Good whose lines do not meet its item. An item without a counted Good is More once the run returns.
One judge is used.

- Must hold: every Good names the lines it rests on. An item is Good only once the conductor has
  seen, in those lines, that it is met.
- Weighed: having the judge also give More was not chosen, since one asked for shortfalls finds them
  whether they are there or not (assumption). The cost: the judge says nothing of why an item has
  no Good, which the learner asks. A Good without grounds was not allowed, since it could not be
  seen in its lines. The cost: grounds written and read for every Good. Several judges were not
  chosen, since the checklists are written so that two judges give the same answers (assumption,
  which turn's trials check). The cost: a judge's slip is caught only by the conductor's reading of
  the lines.

### Making again from the cause

Achieves: read in the receiver's place, nothing unread, following each item back.

Like a post-mortem that asks why something failed rather than where, the learner asks why no Good
came out, in the work and in the process. It takes only the items the conductor has confirmed
without a Good, after the judge, and puts items that share a cause together. One learner is used.
If round 1 leaves such items, the maker makes the work again in round 2 from those causes, keeping
what was Good. The work is then read, judged and learned from once more. What round 2 leaves
without a Good is returned as it is, as More, with its cause. A cause found in the process rather
than in the work is returned as a rule, which the caller carries into its later tasks. A cause
found in what the caller wrote the work should be is returned to the caller, since turn never
rewrites it.

- Must hold: the learner is given only items the conductor has confirmed without a Good. A run has
  at most two rounds. The work returned is the version last read.
- Weighed: fixing each item where it showed was not chosen, since a patch at the spot leaves the
  cause to show again elsewhere. The cost: the learner's pass in each round that leaves an item
  without a Good. Putting the learner before the judge was not chosen, since the learner would then
  be set to find something, and a Good resting on its account would judge the account rather than
  the work (assumption). Running until every item is Good was not chosen, since a loop that does
  not settle hides a fault in turn or the checklist. Fixing round 2's items before returning was
  not chosen, since a change after the last reading reaches the user unread. The cost of both: some
  work comes back with More, for the user to decide on.

### Holding each agent to its steps

Achieves: read in the receiver's place, the first-round share.

Each agent's prompt is a Role and numbered Steps: what it receives, what it hands back and what it
must do in full are steps, and how it thinks within a step is left to it. Each agent answers in the
list itself, in a place set for its answer to each item, laid out before the work begins, so that
no item is passed over. During a run, hooks check that each agent keeps the process its steps set,
as this repository's plugin rules ask, and stop a file read beyond the agent's inputs, which makers
did in trials.

- Must hold: no agent reads beyond its inputs or hands back without answering every item.
- Weighed: leaving the process to the prompts alone was not chosen, since a slip in the process then
  shows only later, in a result that looks right. The cost: a check on each tool an agent uses
  during a run.

### The console

Achieves: seeing the work as it goes.

The console serves a user who looks in now and then. The conductor shows the plan once, before the
first round, and every later line, grouped by round, names its step in the plan. The intent is shown
before the maker writes, so a wrong one is stopped with Esc before a round is spent on it. What the
reader could not take is told in plain words, and each line gives the path of what it is about, so
the user can open the work or the reading. At the end, the console says where the work is and what
the user must decide. Three marks are used, each with one meaning: ⚠️ what the reader could not
take, ✅ nothing missing, ❓ what the user must decide.

- Must hold: no work is written whose intent the console has not shown first.
- Weighed: item IDs and counts were not shown, since the user would have to learn the checklist to
  read them. The cost: a user who wants the item reads it in `.turn/`.

### The CCS

Achieves: a plugin decides from what turn returns, what the work should be unchanged, stop and start
over, the call, the CCS, carrying on across an update.

A CCS (Compressed Cognitive State) is one JSON file in the nine parts that [ACC (Agent Cognitive
Compressor)](https://arxiv.org/abs/2601.11653) sets as the state the next step needs, each a list of
entries of a fixed kind. The caller writes what the work should be. turn adds the rest, and adds its
rules after the caller's in `constraints`. A script checks the CCS on receiving and on returning,
and stops with what does not match. Inside turn, the conductor hands each agent the parts it needs
in a form set for that agent, and changes those forms without touching the CCS.

Every change of course goes through the caller as a new run. When the user answers, or stops a run
with Esc and says what they want instead, turn returns a CCS, `stopped` with where in the second
case. The caller adds the user's words and calls again, and the new run starts from the work as it
stands. turn returns `to the caller` with its reason when the CCS it is given cannot be run, or when
a cause lies in what the caller wrote the work should be, which turn never rewrites. A run starts
from nothing of an earlier run but the CCS it is given and the places that CCS points to, so a CCS
an earlier version returned carries on however the rest of `.turn/` was laid out. Where the work
goes is changed only when a run returns.

- Must hold: `in` is never written. What the work should be is the same in the returned CCS, except
  entries added after the received ones in `constraints`. Every part, kind and `next` value is one
  of those the README gives. Every place the CCS points to exists. Where the work goes changes only
  on a return.
- Weighed: ACC's nine parts were taken since ACC defines them as the state the next step needs.
  Adding a part departs from ACC, and every reader of the CCS would have to change with it. Handing
  each agent the CCS itself was not chosen, since a change made for one agent would change what
  callers rely on. The cost: the conductor writes each agent's inputs from the CCS. A
  free-form handover was not chosen, since the caller and the next run find what they need by kind,
  and a form an AI chooses afresh would not stay the same from run to run (assumption). Copying the
  work into the CCS was not chosen, since a copy drifts from the real thing, so only places are
  written. Folding the user's words into the run they stopped was not chosen, since turn never
  rewrites what the caller wrote. The cost: the change is made in a new run, with rounds of its
  own.

### The conductor in the caller's conversation

Achieves: seeing the work as it goes, a plugin decides from what turn returns.

The conductor is a skill, so it runs in the caller's conversation: it starts the four agents, which
an agent could not do, and its console lines and the user's Esc are where the user already is.

- Must hold: the conductor starts every agent of a run, and no agent starts another.
- Weighed: running the conductor as an agent was not chosen, since it could not start the others.
  The cost: the run takes up room in the caller's conversation.

### The evidence

Achieves: following each item back, `.turn/`.

A script writes into `.turn/`, for each run: each round's work, list and reading, each counted Good
with its grounds, each More with its cause, and the commit of each checklist, since git already
keeps every version and a commit names one exactly.

- Must hold: every Good, every More and every checklist of a run can be found in `.turn/`, and
  every place a returned CCS points to exists.
- Weighed: copying each checklist into `.turn/` was not chosen, since the commit names the same text
  without a second copy. The cost: following a checklist back needs the repository's history.

### Leaving the user's work alone

Achieves: repository untouched, the user's own work alone, missing tools.

During a run, hooks stop, as an agent tries them, a write outside the work and `.turn/`, and any
commit or push. The caller decides whether to commit. Outside its runs turn's hooks stop nothing,
since they run in every session where turn is installed and the user's own work is theirs. Before
anything starts, a check looks for python3 and jq.

- Must hold: during a run, the only changes in the repository are the work and `.turn/`. Outside
  one, turn stops nothing and a missing tool breaks nothing.
- Weighed: checking afterwards was not chosen, since the harm is done by then. The cost: a check on
  each write, commit and push an agent tries. jq was chosen for the agents' reading and changing of
  parts of the CCS, since agents already know it. Python with the standard library was chosen for
  the scripts, by the constraint above.
