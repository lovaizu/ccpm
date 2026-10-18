# turn design

turn is built from five AI roles, a few scripts and hooks: one role makes the work, one reads it in
its receiver's place, and the rest decide from that reading which items get their Good and have the
work made again where one does not. The goal, the key results, and what a checklist, the receiver
and a Good are, are in [turn's UX](ux.md).

## User stories

- As the calling AI, I want to hand turn the path of a CCS and get the work back, with each item's
  Good and its lines, the questions only the user can decide, and each item still without Good; or,
  when the CCS cannot give an item its Good, the questions alone, before any work is made.

  The UX's first and last scenes are the calling AI's own work around this call.

## Architecture

### Logical view

```mermaid
flowchart LR
  caller["Calling AI"]
  orch["Orchestrator"]
  gen["Generator"]
  fu["First user"]
  ev["Evaluator"]
  le["Learner"]
  caller -->|1 calls with the CCS, which the orchestrator checks can give every item its Good| orch
  orch -->|2 has the work made| gen
  orch -->|3 has it read in the receiver's place| fu
  orch -->|4 has that reading's Goods held to their items, and the Goods it missed found| ev
  orch -->|5 has what makes the Good found, then 2 to 4 once more| le
  orch -->|6 returns the work and the result| caller
```

The orchestrator and the four roles it starts are AIs, each answering the orchestrator in its reply.

- Every role looks only for the Good each item gets and the lines that give it, or for how the work
  would give it; only a script, code that runs the same every time, doubts, and only by coverage:
  it names each item no role gave its Good.

  An AI that looks for what more the work needs finds more without end, and each find is patched
  in, so the work drifts from what it should be. Each role has one aim, so it works to the aim
  rather than to a list of steps.
- The calling AI hands the orchestrator the CCS's path, where the result goes, and the kinds it uses
  in the CCS for where the work goes, the checklists and the receiver, and, if it has them, what the
  receiver reads the work for and what they open with it.

  The CCS is the calling AI's, and turn defines nothing of it: what turn needs is found by these
  kinds, and the values stay in the CCS alone, so the call and the CCS cannot differ. Where the
  result goes is this call's answer, not the task's state, so it is not in the CCS.
- Before any work is made, the orchestrator reads the CCS, the files it names and the checklists,
  and finds for every item what in them gives its Good; where nothing does, it returns the
  questions alone, each with the items it settles, and no work is made.

  A Good the CCS cannot give, the generator cannot give either, and the making and the readings
  after it would be spent for nothing; an answer may also change how the whole work is laid out.
  The calling AI asks the user and calls turn again with the answer in the CCS.
- The generator first sets, from the whole CCS, the Good the receiver is to get from the work for
  each item and where the work gives it, then makes the work to give each, and hands back each
  item's Good with its lines and the questions only the user can decide.

  A work made to Goods set first gives each where it was meant; one written first and matched to
  the items after is patched item by item. It hands back once it has read the work and found each
  Good at its lines. What the CCS does not say becomes a question, not its own guess. Its Goods are
  its claim, not a judgment.
- The orchestrator reads the work, finding for every item the Good the receiver gets from it, and
  sends back the items whose Good it does not find, each said as what the receiver gets once it has it; once it sends nothing back, a script
  records its findings.

  A shortfall plain to see is sent back before the costly reading. How the work gets the Good is
  the generator's to decide, since an edit told per item broke other items. An item only the user's
  answer can give is not sent back; it is a question.
- The first user reads the work in the receiver's place, with what the receiver opens and the
  checklists, and gives for each item the Good it found in the work, with its lines.

  A reader that did not make the work finds only the Good its lines give; the maker finds the Good
  it meant.
- The evaluator, given the same and that reading, holds each Good of the reading to what its item
  asks, at its lines, and looks through the whole work for the Good of each item the reading gave
  none, giving every Good with its lines; the orchestrator decides each item where its findings and
  the evaluator's differ, finding at the lines each names the Good the receiver gets, and giving
  none where neither reader found one.

  The orchestrator's findings are recorded before the evaluator starts, as a judgment made after
  another's is pulled toward it. One reader misses a Good the work gives, and an item judged
  without it is made again for nothing; a Good held to its item is one the calling AI can rely on.
  A Good only the orchestrator found would be judged by one that read the work knowing what it
  meant, so a script stops it.
- When every item has its Good or is a question, the run returns; otherwise the learner looks
  through every item's finding and every role's record of the run for what makes the Good, and the
  generator makes the work again with what it found.

  For an item without Good it finds how the work would give it; for one with Good, what gives it,
  so the remake keeps it. What fell short often lies in what a role did, which only its record
  shows.
- The work made again is read once more, from the orchestrator's findings to its decision, and then
  the run returns, with each item still without Good and what the receiver gets once it has it.

  A second reading settles what the first found; what is left costs the calling AI less to fix than
  more readings would.

### Physical view

```
turn/                      the plugin, installed by Claude Code
├── agents/
│   ├── up.md              the orchestrator <agent>
│   ├── generator.md       <agent>
│   ├── first-user.md      <agent>
│   ├── evaluator.md       <agent>
│   └── learner.md         <agent>
├── scripts/               the call's check, each role's input, the findings, the result <Python 3, jq>
└── hooks/
    ├── hooks.json         one entry per event
    └── *.py               one check each <Python 3>
```

- turn runs on Claude Code, python3 3.9 or later, jq and git.
- The calling AI starts the orchestrator, `turn:up`, in the background with the call as JSON, so its
  context holds only what comes back.

  It can still take the user's pause while it waits, and stops a run by sending the orchestrator a
  message. The user sees the run's agents in the panel below the prompt input. `claude -p` is not
  used, since the docs say `--bare`, which reads no subscription login, will become its default.
- A script checks the call and takes every entry of each kind it names from the CCS, so no AI
  copies a value; it stops a call that names a missing file or leaves where the work goes, the
  checklists or the receiver without an entry.
- What each role is given: the generator, the whole CCS, what is sent back and what the learner
  found; the first user, the work, what the receiver opens, who the receiver is and what for, and
  the checklists; the evaluator, the same and the first user's reading; the learner, every item's
  finding and the JSONL of every role of its run.
- Each role replies in a JSON form of its own, not in a file, and a hook checks each role at both
  ends.

  Only the orchestrator holds the replies, so the first user cannot see the generator's claim. A
  hook lets a role start only with what it is to be given, and stops a reply that does not fill its
  form; the evaluator starts only once a script holds the orchestrator's findings.
- The hooks stop a read outside what a role is given, a write outside where the work goes, and a
  commit or a push; a stop says why and names what may be read.

  A role that reads only what it is given is not bent by what it was not meant to see.
- The hooks stop a role's reply, and the orchestrator's check, reading and decision, given before
  what its step reads is read whole since it last changed; the learner, whose records are too long
  for one read, is left to its scripts.

  An item judged on a part read is judged on a guess for the rest.
- A script writes the result where the call says, and checks its shape as it writes.

  A reply would be copied into a file by the calling AI, where a slip goes unseen.
- Several runs go at once, and the hooks tell them apart by the orchestrator's `agent_id`.

  Every agent of a conversation has the same `session_id`. A role's run is the `parentAgentId` in
  `subagents/agent-<agent_id>.meta.json` beside the conversation's transcript; tried with two runs
  at once, every role's tool use and reply was tied to its own orchestrator. The file is there from
  a role's first tool use, so what a role is started with is checked at the orchestrator's own call
  that starts it. The file is Claude Code's record, not a documented hook input, so the hooks'
  tests hold its shape.
- The work is made where it goes, and a run cut off leaves its writing as changes git shows.

  The calling AI undoes or finishes them and calls turn again on what is there. No run resumes part
  way, since being cut off is rare and a reading again costs less than a resume to build and keep
  right.

## Verification

### Units

- The scripts and the hooks: each check stops what it must and lets through what it must.
  - Flow: unittest in `dev/turn/tests/`, fed the calls, replies, events and records each receives,
    run by [`dev/check.sh`](../check.sh) in CI on every push, with lines and branches 100%
    covered, Ruff's lint and format, and Pyrefly's types for Python 3.9.
- The orchestrator: takes each step of the run in its order, from the call to the result.
  - Flow: on a task of one item, with the four roles stood in for by agents that read what their
    step reads and give a reply set beforehand, one set for each way a run goes: every item Good at
    the first reading, an item sent back, the evaluator differing from the findings, and an item
    left without Good through the learner and the second reading; and, on the same task with its
    decision taken out, the questions returned before any work is made. On Opus 5.5; passes when
    its JSONL shows each step in its order, each hook stopping where its check should, and the
    result as the set replies make it.
- Each of the four roles: works to its aim with what it is given, giving its form.
  - Flow: started on its own with a prompt set beforehand, as the orchestrator would give it, on a
    task of one item, on Opus 5.5; passes when its JSONL shows it read only and whole what its step
    reads, and its reply fills its form.
  - Content: what it makes in the acceptance trials below, read against its JSONL.

### Acceptance

Each trial runs in `lovaizu/playground`, one at a time, on a branch of its own removed after: a
stand-in for the calling AI is handed a small task's CCS and checklist and calls turn, and is judged
from the JSONL of every agent it started and from the work.

- Flow: a stand-in for the calling AI calls turn on a task of one item, with every role real, and
  the work comes back with the result in its form.
- The story: the work comes back where it goes, and every item has a Good with its lines, a
  question, or what the receiver gets once it has its Good.
  - Each Good is checked by reading its lines in the work.
- KR1.1: the items the calling AI fixes after the work comes back.
  - Counted from the stand-in's own check in its JSONL, and compared with the version in use on the
    same task, kept with the trial in `dev/turn/trials/`.
- KR1.2: the time from the call to the work coming back.
  - Taken from the JSONL's timestamps for a README-sized work, and compared with the version in use
    on the same task.
  - Read step by step from the same timestamps; time that adds nothing to the story or KR1.1 is
    cut first.

A change is taken when the story is still achieved and KR1.2 does not come closer at the cost of
KR1.1.
