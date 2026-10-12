# turn design

This document says what turn must achieve, how each part of that is checked, and how turn is built
to achieve it and why, for whoever changes turn. It serves the benefits the
[README](../../turn/README.md) promises. How to use turn is in the README, and the full form of the
task file in [ccs.md](../../turn/skills/up/ccs.md), since callers write to it; the wording of each
role's prompt, the steps and the file layout are in the code, and none is repeated here. A statement
on how an AI behaves is an assumption until the trials in Verification measure it, and is marked as
one.

The caller, a plugin's step or Claude in the user's conversation, hands turn one task as a CCS, the
task file of the README: a JSON file in which the caller writes what the work should be, the
checklists to measure it by among it. One run of turn goes from that CCS to a new one turn writes
back, whose `next` tells the caller what to do. A script makes the list from the checklists: every
item with its whole text, and each checklist's opening, which says who reads such work and what it
gives them. A run has one round or two. In each, turn's conductor has agents make the work (the
maker), read it in the place of the person it is for, its receiver (the reader), and show each item
the work meets, with its grounds (the judge): a Good. A Good counts once the conductor has seen, in
the lines it rests on, that the item is met. For the items left without one, an agent learns why no
Good came out (the learner), and the maker makes the work again from those causes in a second
round; only the returned CCS calls such an item More. The roles work from the facts: the work, the
reading and the records, the JSONL in which Claude Code keeps every conversation and agent. The
evidence is what turn keeps in its folder `.turn/` so that each item can be followed: the list, the
readings, the Goods with their grounds, the conductor's account of each item without a Good, and
the commit of each checklist. It works like a review by a first-time user, run as a set process.

## Goals

### Attractive quality

- Read in the receiver's place: the work comes back already read in the receiver's place, with what
  the reader missed made again from its cause, so the user can hand it on without first reading it
  as its receiver.
- Asked only what only the user can decide: the user is asked nothing that what the work should be,
  or its sources, already answers.
- Seeing the work as it goes: the user can tell from the console how far a run has come, and stop
  work on an intent they do not want before it is carried through, saying what they want instead.
- A plugin decides from what turn returns: a plugin hands turn one task and decides its next step
  from the returned CCS alone, without writing the loop of making, reading and making again itself.

### One-dimensional quality

Neither has a fixed limit; each must be no worse than in the version in use.

- The first-round share: the share of runs that end in the first round with every item Good. The
  more work is right when first made, the less the user waits and the less is spent.
- Time and tokens: what one run takes, from the call to the returned CCS.

### Must-be quality

- Repository untouched: during a run, turn changes nothing in the user's repository but the work and
  `.turn/`, and never commits or pushes.
- The user's own work alone: outside its runs, turn stops nothing the user or Claude does, in any
  session where it is installed, and a missing tool there breaks nothing.
- What the work should be unchanged: turn never rewrites what the caller wrote the work should be.
- Nothing unread: the work turn returns is the version the reader last read.
- Stop and start over: when the user stops a run with Esc and says what they want instead, the work
  is made from what they said, starting from the work as it stands; a run cut off before it returns
  anything leaves where the work goes untouched, and called again with the CCS the caller wrote, it
  starts over.
- Traceable: each Good can be followed to the lines of the work and the records it rests on, each
  item without a Good to the conductor's account of it, and each to the version of each checklist
  it was made by.
- Missing tools: when python3 or jq is missing, turn stops before any work and says what to
  install.

### Backward compatibility

- The call: plugins' steps call `turn:up` with two arguments, `in` (the CCS handed over) and `out`
  (where the new one goes); turn reads `in` and writes only `out`. This must keep holding. An
  argument may be added only if a call without it runs as before, since callers written for an
  earlier version do not pass it.
- The CCS: callers write and read its nine parts, the kinds of entry in each, and the values of
  `next`: `done`, `ask the user`, `to the caller: <reason>` and `stopped: <where>`. None of these
  may be added, removed or renamed, since a caller breaks on one it does not know as much as on one
  that is gone. The wording of the entries turn writes may change, since callers hand it on rather
  than read it by kind.
- Carrying on across an update: a later version must accept a CCS an earlier version returned, so
  that a stopped task, or one with the user's answers, carries on after an update.
- The checklist form: users and writ write checklists that turn reads, each a Markdown file that
  opens with who reads such work and what it gives them, followed by each item under a heading
  `### <ID>: <title>`. This must keep holding. How turn makes the list from it may change, since
  only turn's roles read the list.
- `.turn/`: the user and the next run open what a returned CCS points to there, and every such place
  must exist. What else is in `.turn/`, and how it is laid out, may change between versions.
- The console wording and the roles' prompts may change: nothing reads them but the user.

### Non-goals

- Deciding what the work should be. The caller writes it; turn measures against it and returns what
  it cannot decide.
- Talking to the user. turn returns its questions to the caller, which knows what was already agreed
  with the user and asks them.
- Running until every item is Good. What a second round still leaves without a Good is returned as
  More, not looped over: turn takes it as a sign of a fault in turn, in the checklist or in what the
  work should be, to be fixed there (assumption).
- Holding checklists. What they ask belongs to whoever knows the kind of work, such as writ; turn
  reads the ones it is given, in the form it relies on.
- Code. A program is checked by running its tests, not by reading.

### Constraints

- Who uses turn: Claude, on a person's behalf, in their conversation or in a plugin's step; a person
  never writes a call to turn.
- turn runs inside Claude Code, and is built only from what a plugin can hold: skills, agents, hooks
  and scripts. Installing copies only turn's own folder. A plugin's hooks run in every session where
  it is installed, not only during its runs.
- What runs on users' machines is Python 3.9 or later with the standard library only, and jq.
- The work is in a git repository, since the reader starts from a fresh copy of it.

## Verification

### Attractive quality

Each is tried on real work: writ's documents and prompts, and turn's own, are made through turn,
and whoever builds turn reads every conversation and agent record (JSONL) of the run. A made-up
task shows only that the made-up task passes.

- Read in the receiver's place: the returned work, read again by a fresh reader on the same list,
  shows nothing missed that the conductor counted as Good; and each item round 1 left without a
  Good has one on that reading, as has every other item its cause explains, so it was made again
  from its cause and not patched where it showed.
- Asked only what only the user can decide: no returned question can be answered from what the
  work should be or from its sources.
- Seeing the work as it goes: at any point in a run, the user, reading the console alone, can tell
  which round and step it is at, as the records show. Given a task whose intent the user does not
  want, the user stops it with Esc after the intent is shown and says what they want instead; no
  work of that intent has been written, and the work then made is what they said.
- A plugin decides from what turn returns: the next step decided from the returned CCS alone is the
  same as the one decided after also reading the records.

### One-dimensional quality

Both are measured from the records of the same tasks, each run from the same CCS on this version and
on the version in use: the first-round share, and the time and tokens per run.

### Must-be quality

Each is checked by a test:

- Repository untouched: during a run, a write outside the work and `.turn/`, a commit and a push
  are each stopped.
- The user's own work alone: outside a run, including while one runs in another session, a write
  anywhere, a commit and a push each go through, with python3 missing as well as present.
- What the work should be unchanged: a returned CCS in which what the work should be differs from
  what was received is stopped.
- Nothing unread: with a version of the work written after the last reading, the work returned is
  the last-read version.
- Stop and start over: a run stopped at each of its steps returns `stopped` with where, and a run
  called with it and the user's words starts from the work as it stands. With a run cut off, where
  the work goes is untouched, and a run called again with the same CCS starts from the beginning.
- Traceable: every Good names the lines it rests on and they exist, every item without a Good has
  the conductor's account, and the evidence names the commit of each checklist.
- Missing tools: with python3 or jq missing, turn stops and says what to install.

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

- Every Good and every decision is measured against what the work should be, and nothing else.
  Protects: read in the receiver's place, what the work should be unchanged.
- Each role aims only at every item being Good and thinks forward, from what would make an item Good
  rather than from what is wrong, with set inputs and a set output; what a role fills has a place
  for a Good and its grounds only, so no role can write a shortfall, and no role is set to find
  something. Protects: read in the receiver's place, the first-round share. Assumption: an AI works
  toward the aim it is given; told the steps instead, it follows them and loses the aim, and set to
  find something, it finds it whether it is there or not.
- Work that does not yet reach a Good is sent back to where it was made, as early as it can be
  seen. Protects: the first-round share, time and tokens. What the conductor can see in the maker's
  work, the reading and the Goods would show only a round later.
- The conductor aims at more items reaching Good, and decides each move of the work, sending it
  back, passing it on, running another round or returning, from the work and the records, not from
  a role's report alone. Protects: read in the receiver's place, asked only what only the user can
  decide. Assumption: a report can say more than the work holds, and what it says beyond the work
  would pass on to the user.

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
  O-->>U: the plan (console)
  loop round 1, and round 2 only if round 1 leaves an item without a Good
    O-->>U: what turn means to make (console)
    O->>M: what the work should be, sources, list (round 2: the learner's causes)
    M-->>O: the work, and for each item the words of it that give what the item asks
    O->>S: the work, the words for each item
    S-->>O: the parts of the work no item's words rest on
    Note over O,M: sent back until the conductor sees every item met and no part left over
    O->>R: the work, the receiver, its use, the list (in a fresh copy)
    R-->>O: for each item, what was taken, and where
    O->>J: the list, the work, the reading, the records, what the work should be
    J-->>O: a Good with its grounds for each item the work meets; questions for the user
    O->>S: the work, the Goods
    S-->>O: the parts of the work no Good rests on
    Note over O,J: a Good counted once its lines meet the item; for the rest, what was seen
    O-->>U: what the reader could not take (console)
    opt an item without a Good
      O->>L: those items, the list, the work, the reading, the records
      L-->>O: for each, why no Good came out, with the items each cause explains
    end
  end
  O->>S: records, Goods, the items without one, checklists, new CCS
  S-->>O: evidence written; new CCS checked
  O-->>U: where the work is, and what the user must decide (console)
  O-->>C: new CCS
  C-->>U: the questions only the user can answer
  opt at any point: the user presses Esc and says what they want instead
    O-->>C: a CCS with `stopped` and where; the user's words
    C->>O: the CCS with the user's words added, for a new run
  end
```

| Part | Aim | Hands back | Depends on |
|---|---|---|---|
| Caller | What the work should be, written once for the task | The CCS; the user's answers or words added to it, for a new run | The CCS's form |
| Conductor | The final decision: the work meets what it should be | The maker's work sent back until every item is met and no part is left over; every Good counted once its lines are seen to meet the item, and for each item without one, what it saw in the lines; the next round or the CCS to return | Claude Code, which runs it as a skill |
| Maker | A work that meets every item | The work, and for each item the words of it that give what the item asks, not the heading they sit under | What the work should be, the sources, the list |
| Reader | Use the work as its receiver | For each item, what was taken from the work, and where | A fresh copy made from git, removed when it is done |
| Judge | Show each item the work meets, from the reading and the facts | A Good with its grounds for each item met; the questions only the user can answer | The reader's reading; the records (JSONL) Claude Code keeps |
| Learner | Why no Good came out for each item without one | Each cause, with the items it explains | Those items; the records (JSONL) |
| Scripts | What must come out the same every time | The list; the parts of the work no item's grounds rest on; the CCS checked on receiving and returning; the evidence | python3, jq |
| Hooks | Slips caught as an agent makes them, during a run only | A stop, with what is missing | Claude Code's hook events |

Each round's work, lists, readings, records and the evidence are kept in `.turn/`.

- Must hold: no role reads anything beyond the inputs set for it, since what it reads besides
  changes the standpoint it measures from.

### The checklist as the measure

Achieves: read in the receiver's place, the first-round share, the checklist form.

The checklists are written so that a work meeting every item serves its purpose. Every role works
against the same list, made by a script from them, in the form users and writ write, with each
item's whole text and each checklist's opening; so the maker, the conductor and the reader measure
from the same standpoint. A gap found that no item asks about belongs in the checklist, not in a
role's answer.

- Must hold: no role writes anything outside the list.
- Weighed: letting the reader also say what it could not take outside the items was not chosen;
  with no item to bound it, it reads as a search for faults, and its answers vary from run to run
  (assumption). The cost: what no item asks is not found until the checklist is changed.

### Coverage

Achieves: read in the receiver's place, the first-round share.

As tests are measured by the lines they run, the work is measured by the parts of it that some
item's grounds rest on. A script counts the parts no item's grounds rest on, at two points, and
shows them to the conductor: when the maker hands the work over, from the words it gives for each
item, before any reading; and when the judge hands back its Goods, from their grounds, before the
conductor reads their lines. A part no Good rests on either has no job or holds a slip. What still
slips through is of a kind no item asks about, and goes into the checklist.

- Must hold: no work reaches the reader, and no Good is counted, before the conductor has seen the
  parts no item's grounds rest on.
- Weighed: a role set to look for slips was not chosen, since it would be set to find something; a
  count needs no AI and comes out the same every time. The cost: a slip inside a part some item's
  grounds rest on is not counted.

### Making it right first

Achieves: the first-round share, time and tokens, asked only what only the user can decide.

The maker makes a work that meets every item, and gives for each the words of the work that give
what it asks, not the heading they sit under, so the conductor weighs the words themselves. The
conductor reads the work against the list and sends it back with each item not met, and with each
part no item's words rest on, as many times as it takes, since settling it is the conductor's work.
What the sources do not settle goes to the user as a question and stays out of the work.

- Must hold: no work reaches the reader with an item the conductor sees unmet.
- Weighed: passing the maker's work straight to the reader was not chosen, since every item it
  leaves unmet then costs a full round to find. The cost: the conductor reads every item of the work
  before each reading.

### Reading in the receiver's place

Achieves: read in the receiver's place.

The reader starts where the receiver starts, as a new team member starts from a fresh clone: a copy
of the repository with only the work added. It is told only who the receiver is, what they use the
work for, and the list; not how the work was made, nor what the receiver must be able to do with it,
nor the sources, so that it stops where the receiver would (assumption). For each item it says what
it took from the work and where.

- Must hold: the reader's copy holds nothing the receiver would not have.
- Weighed: reading in the working repository was not chosen, since files the receiver lacks could
  help the reader along and hide what is missing (assumption). The cost: a copy is made for each
  reading. Telling the reader what the receiver must be able to do was not chosen, since it would
  then look for that rather than take what the work gives. The cost: the reader may not try the
  work for the use that matters most; only the judge weighs the reading against it.

### Judging every item

Achieves: read in the receiver's place, asked only what only the user can decide, traceable.

Once the reader has read, the judge shows, from the reading, the work and the records, each item the
work meets, as a Good with its grounds: the lines of the work and of the reading it rests on; an
item it cannot ground is left without a Good. A question goes to the user only when neither what the
work should be nor its sources answer it. The conductor then reads, for every Good, the lines it
rests on, with the parts no Good rests on before it, and counts the Good once it sees there that the
item is met, as a teacher gives the mark once the working shows the answer: coverage shows the parts
no Good rests on, but not a Good whose lines do not meet its item. An item whose Good is not counted
is left without one, like any other, and the conductor keeps what it saw in the lines as its
account, for the evidence and the CCS. A question the work or its sources answer is dropped. Only
when the run returns are the items without a Good written into the CCS, as More.

- Must hold: every Good names the lines it rests on; an item is Good only once the conductor has
  seen, in those lines, that it is met.
- Weighed: having the judge also give More was not chosen, since one asked for shortfalls finds them
  whether they are there or not (assumption); the cost is that the judge says nothing of why an
  item has no Good, which the learner asks. A Good without grounds was not allowed, since it could
  not be seen in its lines; the cost is grounds written and read for every Good. Putting the learner
  before the judge was not chosen, since a Good resting on its account would judge the account
  rather than the work (assumption); the cost is that a Good that does not hold gets no cause, and
  only the conductor's reading of its lines keeps it from counting.

### Making again from the cause

Achieves: read in the receiver's place, nothing unread, traceable.

Like a post-mortem that asks why something failed rather than where, the learner takes only the
items left without a Good, and asks why no Good came out for each, in the work and in the process,
putting items that share a cause together. The maker then makes the work again in round 2 from those
causes alone, keeping what was Good, and it is read and judged once more, and what is still without
a Good is learned from once more. What round 2 leaves without a Good is returned as it is, as More,
with the conductor's account and the learner's cause. A cause found in the process rather than in
the work is returned as a rule, which the caller carries into the CCS of its later tasks.

- Must hold: the learner is given only items without a Good; the work returned is the version last
  read.
- Weighed: fixing each missed item where it shows was not chosen, since a patch at the spot leaves
  the cause to show again elsewhere; the cost is the learner's pass in each round that leaves an
  item without a Good. Having the conductor also say how a Good is reached was not chosen, since two
  sources of how to make the work again would differ; the cost is that what the conductor saw in the
  lines serves only the evidence and the CCS. Running until every item is Good, and having the
  conductor fix round 2's items without a Good before returning, were not chosen: a loop that does
  not settle hides a fault that belongs to turn or the checklist, and a fix after the last reading
  reaches the user unread. The cost of both: some work comes back with More, for the user to decide
  on.

### The console

Achieves: seeing the work as it goes.

The console serves a user who looks in now and then. The conductor shows the plan once, before the
first round, and every later line, grouped by round, names its step in the plan, so the user tells
at a glance how far the run has come. What the maker means to make is shown before it writes, so a
wrong intent is stopped with Esc before a round is spent on it. What the reader could not take is
told in plain words, and each line gives the path of what it is about, so the user can open the
work or the reading. Three marks, each with one meaning, tell at a glance that something was
missed, that nothing was, or that the user must decide.

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
answers. turn writes the rest: `next`, the questions only the user can answer, each item still
without a Good, as More, with why, the rules it learned, added after the caller's lines in
`constraints`, and where the work and the evidence are. A script checks the CCS on receiving and on
returning, and stops with what does not match.

Every change of course goes through the caller as a new run. When the user answers, or stops a run
with Esc and says what they want instead, turn returns a CCS, `stopped` with where in the second
case, and the caller adds the user's words in `constraints` and calls again; the new run starts from
the work as it stands. A run starts from nothing of an earlier run but the CCS it is given and the
places that CCS points to, so a CCS an earlier version returned carries on however the rest of
`.turn/` was laid out. Where the work goes is changed only when a run returns, so a run cut off
leaves it untouched, and the caller calls again with the CCS it wrote.

- Must hold: `in` is never written; what the work should be is the same in the returned CCS, except
  lines added after the old in `constraints`; every part, kind and `next` value is one of those
  defined; every place the CCS points to exists; where the work goes changes only on a return.
- The CCS is the caller's interface only. Inside turn, the conductor hands each role the parts it
  needs in forms set for that role, and changes them without touching the CCS.
- Weighed: ACC's nine parts were taken since ACC defines them as the state the next step needs;
  adding a part departs from ACC, and every reader of the CCS would have to change with it. Handing
  each role the CCS itself was not chosen, since a change made for one role would change what
  callers rely on; the cost is that the conductor writes each role's inputs from the CCS. A
  free-form handover was not chosen, since the caller and the next run find what they need by kind,
  and a form an AI chooses afresh would not stay the same from run to run (assumption). Copying the
  work into the CCS was not chosen; only places are written, since a copy drifts from the real
  thing. The cost: the caller writes JSON in a set form, which a script may refuse. Folding the
  user's words into the run they stopped was not chosen, since turn never rewrites what the caller
  wrote; the cost is that the change is made in a new run, with rounds of its own.

### Leaving the user's work alone

Achieves: repository untouched, the user's own work alone, missing tools.

During a run, hooks stop, as an agent tries them, a write outside the work and `.turn/`, and any
commit or push; the caller decides whether to commit. Outside its runs turn's hooks stop nothing,
since they run in every session where turn is installed and the user's own work is theirs. Before
anything starts, a check looks for python3 and jq.

- Must hold: during a run, the only changes in the repository are the work and `.turn/`; outside
  one, turn stops nothing and a missing tool breaks nothing.
- Weighed: checking afterwards was not chosen, since the harm is done by then. The cost: a check on
  each write, commit and push an agent tries.
