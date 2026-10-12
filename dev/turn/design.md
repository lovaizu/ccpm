# turn design

This document says what turn must achieve, how each part of that is checked, and how turn is built
to achieve it and why, for whoever changes turn. It serves the benefits the
[README](../../turn/README.md) promises. How to use turn is in the README, and the full form of the
CCS in [ccs.md](../../turn/skills/up/ccs.md), since callers write to it; the wording of each role's
prompt, the steps and the file layout are in the code, and none is repeated here. A statement on how
an AI behaves is an assumption until the trials in Verification measure it, and is marked as one.

The caller, a plugin's step or Claude in the user's conversation, hands turn one task as a CCS, a
JSON file in which the caller writes what the work should be. turn writes back a new CCS, whose
`next` tells the caller what to do. In between, turn's conductor has agents make the work (the
maker), read it in the place of the person it is for, its receiver (the reader), and give each
checklist item a verdict, Good (met) or More (not yet met), each with its grounds (the judge). The
conductor checks every verdict against the facts, and for each More it confirms, an agent learns why
the reader did not take it (the learner), so that the maker makes the work again from that cause. It
works like a review by a first-time user, run as a set process.

## Goals

### Attractive quality

- Read in the receiver's place: the work comes back already read in the receiver's place, with what
  the reader missed made again from its cause, so the user can hand it on without first reading it
  as its receiver.
- Asked only what only the user can decide: the user is asked nothing that what the work should be,
  or its sources, already answers.
- Seeing the work as it goes: the user can tell how far turn has come and stop work on an intent
  they do not want before it is carried through.
- A plugin decides from what turn returns: a plugin hands turn one task and decides its next step
  from the returned CCS alone, without writing the loop of making, reading and making again itself.

### One-dimensional quality

Neither has a fixed limit; each must be no worse than in the version in use.

- The first-round share: the share of tasks that end in the first round with nothing missed. The
  more work is right when first made, the less the user waits and the less is spent.
- Time and tokens: what one task takes, from the call to the returned CCS.

### Must-be quality

- Repository untouched: turn changes nothing in the user's repository but the work and its own
  folder, `.turn/`, and never commits or pushes.
- What the work should be unchanged: turn never rewrites, during a task, what the caller wrote the
  work should be.
- Nothing unread: every version returned is the one the reader last read.
- Stop and start over: a task the user stops partway carries on from where it stopped when called
  again; one cut off before it returns anything starts over from the CCS the caller wrote.
- Traceable: each verdict can be followed to the lines of the work and the records it rests on, and
  to the version of each checklist it was made by.
- Missing tools: when python3 or jq is missing, turn stops before any work and says what to
  install.

### Backward compatibility

- The call: plugins' steps call `turn:up` with two arguments, `in` (the CCS handed over) and `out`
  (where the new one goes). Both must keep holding.
- The CCS: callers write and read its nine parts, the kinds of entry in each, and the values of
  `next`: `done`, `ask the user`, `to the caller: <reason>` and `stopped: <where>`. These must keep
  holding.
- Carrying on across an update: a later version must accept a CCS an earlier version returned, so
  that a stopped task carries on after an update.
- `.turn/`: the user and the next run open what a returned CCS points to there, and every such place
  must exist. What else is in `.turn/`, and how it is laid out, may change between versions.
- The console wording and the roles' prompts may change: nothing reads them but the user.

### Non-goals

- Deciding what the work should be. The caller writes it; turn measures against it and returns what
  it cannot decide.
- Talking to the user. turn returns its questions to the caller, which knows what was already agreed
  with the user and asks them.
- Running until nothing is missed. What a second round still misses points to a fault in turn, in
  the checklist or in what the work should be, which is fixed there, not looped over.
- Holding checklists. They belong to whoever knows the kind of work, such as writ; turn reads the
  ones it is given.
- Code. A program is checked by running its tests, not by reading.

### Constraints

- Who uses turn: Claude, on a person's behalf, in their conversation or in a plugin's step; a person
  never writes a call to turn.
- turn runs inside Claude Code, and is built only from what a plugin can hold: skills, agents, hooks
  and scripts. Installing copies only turn's own folder.
- What runs on users' machines is Python 3.9 or later with the standard library only, and jq.
- The work is in a git repository, since the reader starts from a fresh copy of it.

## Verification

### Attractive quality

Each is tried on real work: writ's documents and prompts, and turn's own, are made through turn,
and whoever builds turn reads every conversation and agent record (JSONL) of the run. A made-up
task shows only that the made-up task passes.

- Read in the receiver's place: the returned work, read again by a fresh reader on the same
  checklist, shows nothing missed that the judge let through as Good.
- Asked only what only the user can decide: no returned question can be answered from what the
  work should be or from its sources.
- Seeing the work as it goes: given a task whose intent the user does not want, the user, reading
  the console alone, stops it with Esc after the intent is shown, and no work has been written.
- A plugin decides from what turn returns: the next step decided from the returned CCS alone is the
  same as the one decided after also reading the records.

### One-dimensional quality

Both are measured from the records of the same tasks, each run from the same CCS on this version and
on the version in use: the first-round share, and the time and tokens per task.

### Must-be quality

Each is checked by a test that runs the script or hook that keeps it:

- Repository untouched: a write outside the work and `.turn/`, a commit and a push are each
  stopped.
- What the work should be unchanged: a returned CCS in which what the work should be differs from
  what was received is stopped.
- Nothing unread: a run whose last version was written after the last reading cannot be returned.
- Stop and start over: a stopped run returns `stopped`, and a run called again with it carries on
  from that point; a run called again with the same CCS after being cut off starts from the
  beginning.
- Traceable: every verdict, Good as well as More, names the lines it rests on and they exist, and
  the evidence names the commit of each checklist.
- Missing tools: with python3 or jq missing, turn stops and says what to install.

### Backward compatibility

For each released version, a test calls turn as that version's callers call it:

- The call and the CCS: a CCS of that version's form is accepted, and every value of `next` it
  could return is one this version can return.
- Carrying on across an update: a `stopped` CCS that version returned carries on.
- `.turn/`: every place a CCS that version returned points to exists after the run.

## Architecture

### Principles

- Every verdict and decision is measured against what the work should be, and nothing else.
  Protects: read in the receiver's place, what the work should be unchanged.
- Each role is given one aim it can work toward, set inputs and a set output, and no role is set to
  find something. Protects: read in the receiver's place, the first-round share. Assumption: an AI
  works toward the aim it is given; told the steps instead, it follows them and loses the aim, and
  set to find something, it finds it whether it is there or not.
- A shortfall is sent back to where it was made, as early as it can be seen. Protects: the
  first-round share, time and tokens. What the conductor can see in the maker's work, the reading and
  the verdicts would show only a round later.
- The conductor decides each move of the work, sending it back, passing it on, running another
  round or returning, from the work and the records, not from a role's report alone. Protects: read
  in the receiver's place, asked only what only the user can decide. A report taken on trust passes
  its slip on to the user.

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
  S-->>O: CCS checked; the list of every item
  O-->>U: the plan, then what turn means to make (console)
  loop round 1, and round 2 only if round 1 leaves a More the conductor confirmed
    O->>M: what the work should be, sources, list (round 2: the confirmed More and their causes)
    M-->>O: the work, and for each item where in it the item is met
    Note over O,M: sent back until the conductor sees every item met
    O->>R: the work, the receiver, its use, the list (in a fresh copy)
    R-->>O: for each item, what was taken, and where
    O->>J: the list, the work, the reading, the records, what the work should be
    J-->>O: Good or More for each item, each with its grounds; questions for the user
    Note over O,J: every Good and every More checked against the facts, sent back if they do not bear it out
    O-->>U: what the reader could not take (console)
    opt a More the conductor confirmed
      O->>L: the confirmed More with their grounds, the list, the work, the reading, the records
      L-->>O: for each, why it was not taken, with the items each cause explains
    end
  end
  O->>S: records, verdicts, checklists, new CCS
  S-->>O: evidence written; new CCS checked
  O-->>U: where the work is, and what the user must decide (console)
  O-->>C: new CCS
  C-->>U: the questions only the user can answer
```

Hooks watch every agent throughout: they stop a write outside the work and `.turn/`, a commit or a
push, and an output with an item unfilled.

| Part | Aim | Hands back | Depends on |
|---|---|---|---|
| Caller | What the work should be, written once for the task | The CCS; the user's answers in a new CCS | The CCS's form |
| Conductor | The final decision: the work meets what it should be | The maker's work sent back until every item is met; every Good and More checked against the facts; the next round or the CCS to return | Claude Code, which runs it as a skill |
| Maker | A work that meets every item | The work, and for each item where in it the item is met | What the work should be, the sources, the list |
| Reader | Use the work as its receiver | For each item, what was taken from the work, and where | A fresh copy made from git, removed when it is done |
| Judge | Whether each item is met, without bias, from the reading and the facts | Good or More for each item, each with its grounds; the questions only the user can answer | The reader's reading; the records (JSONL) Claude Code keeps |
| Learner | Why each More the conductor confirmed was not taken | Each cause, with the items it explains | The conductor's confirmed More; the records (JSONL) |
| Scripts | What must come out the same every time | The list; the CCS checked on receiving and returning; the evidence | python3, jq |
| Hooks | Slips caught as an agent makes them | A stop, with what is missing | Claude Code's hook events |

Each round's work, lists, readings, records and the evidence are kept in `.turn/`.

### The checklist as the measure

Achieves: read in the receiver's place, the first-round share.

The checklists are written so that a work meeting every item serves its purpose. Every role works
against the same list, made by a script from them with each item's whole text and each checklist's
opening, which says who reads the work and what it gives them; so the maker, the conductor and the
reader measure from the same standpoint. A gap found that no item asks about belongs in the
checklist, not in a role's answer.

- Must hold: every role's output has an entry for every item of the list, and nothing outside it.
- Weighed: letting the reader also say what it could not take outside the items was not chosen;
  with no item to bound it, it reads as a search for faults, and its answers vary from run to run
  (assumption). The cost: what no item asks is not found until the checklist is changed.

### Making it right first

Achieves: the first-round share, time and tokens, asked only what only the user can decide.

The maker makes a work that meets every item, saying for each where in the work it is met. The
conductor reads the work against the list and sends it back with each item not met, as many times
as it takes, since settling it is the conductor's work. What the sources do not settle goes to the
user as a question and stays out of the work.

- Must hold: no work reaches the reader with an item the conductor sees unmet.
- Weighed: passing the maker's work straight to the reader was not chosen, since every shortfall
  it leaves then costs a full round to find. The cost: the conductor reads every item of the work
  before each reading.

### Reading in the receiver's place

Achieves: read in the receiver's place.

The reader starts where the receiver starts, as a new team member starts from a fresh clone: a copy
of the repository with only the work added. It is told only who the receiver is, what they use the
work for, and the list; not how the work was made, nor what the receiver must be able to do with it,
nor the sources. So it stops where the receiver would. For each item it says what it took from the
work and where.

- Must hold: the reader's copy holds nothing the receiver would not have.
- Weighed: reading in the working repository was not chosen, since files the receiver lacks would
  help the reader along and hide what is missing. The cost: a copy is made for each reading.

### Judging every item

Achieves: read in the receiver's place, asked only what only the user can decide, traceable.

Once the reader has read, the judge decides, from the reading, the work and the records, whether
each item is met, as an examiner marks every answer, not only the wrong ones. It gives each item Good
or More with its grounds, the lines of the work and of the reading it rests on, and a Good is
grounded as fully as a More. A question goes to the user only when neither what the work should be
nor its sources answer it. The conductor then checks every Good and every More, and each question,
against the work, the reading and the records, sends one the facts do not bear out back to the judge
with what does not hold, and decides only on verdicts the facts bear out.

- Must hold: every verdict, Good or More, names the lines it rests on; no verdict is acted on before
  the conductor has checked it.
- Weighed: grounding only the More was not chosen, since a Good without grounds cannot be checked,
  and a wrong Good is the slip nothing looks at again: the work reaches the user with it unmet. The
  cost: grounds written and checked for every item. Having the judge work from the learner's causes,
  with the learner before it, was not chosen: a learner on every item is set to find what was
  missed, and a verdict resting on its account judges the account rather than the work. The cost: a
  wrong Good gets no cause, and only the conductor's check of every Good catches it.

### Making again from the cause

Achieves: read in the receiver's place, nothing unread, traceable.

Like a post-mortem that asks why something failed rather than where, the learner takes only the More
the conductor confirmed, and learns why the reader did not take each, in the work and in the
process, putting items that share a cause together. The maker then makes the work again in round 2
from those causes, keeping what was Good, and it is read, judged and checked once more, and what is
still More is learned from once more. What round 2 leaves as More is returned as it is, with the
judge's grounds and the learner's cause. A cause found in the process rather than in the work is
returned as a rule, which the caller carries into the CCS of its later tasks.

- Must hold: the learner is given only More the conductor confirmed; nothing is written to the work
  after its last reading.
- Weighed: fixing each missed item where it shows was not chosen, since a patch at the spot leaves
  the cause to show again elsewhere; the cost is the learner's pass in each round that leaves a
  More. Having the judge also give the causes was not chosen, since one who explains a More as it
  judges it holds to that explanation, as an author reviewing their own change does (assumption);
  the cost is one more agent in such a round. Running until nothing is missed, and having the
  conductor fix round 2's More before returning, were not chosen: a loop that does not settle hides
  a fault that belongs to turn or the checklist, and a fix after the last reading reaches the user
  unread. The cost of both: some work comes back with More, for the user to decide on.

### The console

Achieves: seeing the work as it goes.

The console serves a user who looks in now and then. The conductor shows the plan once, before the
first round, so each later line, grouped by round, can be placed in it at a glance. What the maker
means to make is shown before it writes, so a wrong intent is stopped before a round is spent on it.
What the reader could not take is told in plain words, and each line gives the path of what it is
about, so the user can open the work or the reading. Three marks, each with one meaning, tell at a
glance that something was missed, that nothing was, or that the user must decide.

- Must hold: no work is written whose intent the console has not shown first.
- Weighed: item IDs and counts were not shown, since the user would have to learn the checklist to
  read them; the cost is that a user who wants the item reads it in `.turn/`.

### The CCS

Achieves: a plugin decides from what turn returns, what the work should be unchanged, stop and start
over, traceable, the call, the CCS, carrying on across an update, `.turn/`.

A CCS (Compressed Cognitive State) is one JSON file in the nine parts that [ACC (Agent Cognitive
Compressor)](https://arxiv.org/abs/2601.11653) sets as the state the next step needs, each a list of
entries of a fixed kind. The caller writes what the work should be: where it goes, its receiver,
what they use it for, what the receiver must be able to do with it (`acceptance`), the checklists
(`viewpoint`), the sources, and `constraints`, which holds the language, rules and the user's
answers. turn writes the rest: `next`, the questions only the user can answer, each item still More
with why, the rules it learned, added after the caller's lines in `constraints`, and where the
evidence is. The caller adds the user's answers in `constraints` and calls again. A run the user
stops returns `stopped` with where, and the next run starts from that CCS and the work alone; a run
cut off returns nothing, and the caller calls again with the same CCS, which turn never rewrites.

- Must hold: what the work should be is the same in the returned CCS, except lines added after the
  old in `constraints`; every part and kind is one of those defined; every place the CCS points to
  exists. A script checks these on receiving and on returning, and stops with what does not match.
- The CCS is the caller's interface only. Inside turn, the conductor hands each role the parts it
  needs in forms set for that role, and changes them without touching the CCS.
- Weighed: ACC's nine parts were taken since ACC defines them as the state the next step needs;
  adding a part departs from ACC, and every reader of the CCS would have to change with it. Handing
  each role the CCS itself was not chosen, since a change made for one role would change what
  callers rely on; the cost is that the conductor writes each role's inputs from the CCS. A
  free-form handover was not chosen, since the caller and the next run find what they need by kind,
  and a form an AI chooses afresh breaks them. Copying the work into the CCS was not chosen; only
  places are written, since a copy drifts from the real thing. The cost: the caller writes JSON in a
  set form, which a script may refuse.

### Leaving the user's work alone

Achieves: repository untouched, missing tools.

Hooks stop, as an agent tries them, a write outside the work and `.turn/`, and any commit or push;
the caller decides whether to commit. Before anything starts, a check looks for python3 and jq.

- Must hold: after every operation, the only changes in the repository are the work and `.turn/`.
- Weighed: checking afterwards was not chosen, since the harm is done by then. The cost: a check on
  each write, commit and push an agent tries.
